from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio, io, time, os, logging, hashlib, json
from PIL import Image
import numpy as np
from typing import Optional
import base64

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Fallback imports for environments without TFLite
try:
    from huggingface_hub import hf_hub_download
    import tflite_runtime.interpreter as tflite
    TFLITE_AVAILABLE = True
except ImportError:
    TFLITE_AVAILABLE = False
    logger.warning("TFLite not available - using mock model for testing")

# Configuration from environment
HF_REPO_ID = os.environ.get("HF_REPO_ID", "palawakampa/tumorotak")
HF_FILENAME = os.environ.get("HF_FILENAME", "brain_tumor.tflite")
ASSETS_FILENAME = "assets.json"
MODEL_GCS_PATH = os.environ.get("MODEL_GCS_PATH", "")  # Optional GCS path
PORT = int(os.environ.get("PORT", 8080))
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")

# Global model state (singleton pattern for lazy loading)
INTERP = None
IN_DET = None
OUT_DET = None
READY = asyncio.Event()
MODEL_LOAD_TIME = 0.0
MODEL_SHA = None
LABELS = ["No Tumor", "Tumor"]
THRESH = 0.5
MODEL_CONFIG = {}
MODEL_LOADING = False
MODEL_LOAD_LOCK = asyncio.Lock()

def preprocess(img: Image.Image, size=(224,224)):
    """Preprocess image for ResNet50 model."""
    img = img.convert("RGB").resize(size)
    x = np.asarray(img).astype("float32") / 255.0
    return np.expand_dims(x, axis=0)

async def load_model_lazy():
    """
    Lazy load model on first request (singleton pattern).
    Supports both Hugging Face and GCS sources with retry logic.
    """
    global INTERP, IN_DET, OUT_DET, MODEL_LOAD_TIME, LABELS, THRESH, MODEL_CONFIG, MODEL_SHA, MODEL_LOADING
    
    # If already loaded, return immediately
    if READY.is_set():
        return
    
    # Prevent concurrent loading
    async with MODEL_LOAD_LOCK:
        # Double-check after acquiring lock
        if READY.is_set():
            return
        
        if MODEL_LOADING:
            # Wait for ongoing load
            while not READY.is_set():
                await asyncio.sleep(0.1)
            return
        
        MODEL_LOADING = True
        start_time = time.time()
        
        if not TFLITE_AVAILABLE:
            logger.warning("TFLite not available - using mock model")
            READY.set()
            MODEL_LOAD_TIME = time.time() - start_time
            MODEL_LOADING = False
            return
        
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Loading model (attempt {attempt + 1}/{max_retries})...")
                
                # Try GCS first if configured
                if MODEL_GCS_PATH and MODEL_GCS_PATH.startswith("gs://"):
                    logger.info(f"Downloading model from GCS: {MODEL_GCS_PATH}")
                    # TODO: Implement GCS download using google-cloud-storage
                    # For now, fall back to Hugging Face
                    logger.warning("GCS download not implemented, falling back to Hugging Face")
                
                # Download from Hugging Face
                logger.info(f"Downloading model from Hugging Face: {HF_REPO_ID}/{HF_FILENAME}")
                model_path = hf_hub_download(
                    repo_id=HF_REPO_ID,
                    filename=HF_FILENAME,
                    cache_dir="/tmp",
                    token=os.environ.get("HF_TOKEN")
                )
                
                # Try to load assets.json
                try:
                    assets_path = hf_hub_download(
                        repo_id=HF_REPO_ID,
                        filename=ASSETS_FILENAME,
                        cache_dir="/tmp",
                        token=os.environ.get("HF_TOKEN")
                    )
                    with open(assets_path, 'r') as f:
                        MODEL_CONFIG = json.load(f)
                    LABELS = MODEL_CONFIG.get("labels", ["No Tumor", "Tumor"])
                    THRESH = MODEL_CONFIG.get("threshold", 0.5)
                    logger.info(f"Loaded model config: {MODEL_CONFIG}")
                except Exception as e:
                    logger.warning(f"Could not load assets.json: {e}, using defaults")
                
                # Load TFLite model
                logger.info(f"Loading TFLite interpreter from {model_path}")
                INTERP = tflite.Interpreter(
                    model_path=model_path,
                    num_threads=1
                )
                INTERP.allocate_tensors()
                
                # Cache input/output details
                IN_DET = INTERP.get_input_details()[0]
                OUT_DET = INTERP.get_output_details()[0]
                
                # Calculate model SHA
                with open(model_path, 'rb') as f:
                    MODEL_SHA = hashlib.sha256(f.read()).hexdigest()[:8]
                
                MODEL_LOAD_TIME = time.time() - start_time
                READY.set()
                MODEL_LOADING = False
                logger.info(f"✅ Model loaded successfully in {MODEL_LOAD_TIME:.2f}s (SHA: {MODEL_SHA})")
                return
                
            except Exception as e:
                logger.error(f"Model loading attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error("All model loading attempts failed")
                    # Set ready anyway to prevent blocking
                    READY.set()
                    MODEL_LOADING = False
                    MODEL_LOAD_TIME = time.time() - start_time
                    raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    logger.info(f"🚀 Starting FastAPI application on port {PORT}")
    logger.info(f"CORS origins: {CORS_ORIGINS}")
    logger.info(f"Model will be lazy-loaded on first request")
    yield
    logger.info("Shutting down application")

app = FastAPI(
    title="Brain Tumor Detection API",
    description="FastAPI backend for brain tumor detection using TFLite model",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware with configurable origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "message": "Brain Tumor Detection API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "predict": "/predict",
            "model_meta": "/debug/model_meta"
        }
    }

@app.get("/health")
def health():
    """
    Health check endpoint for Cloud Run.
    Returns 200 OK if service is running.
    """
    return {"status": "ok"}

@app.get("/debug/model_meta")
async def model_meta():
    """Debug endpoint to verify model metadata and preprocessing consistency."""
    # Trigger lazy loading if not loaded
    if not READY.is_set():
        try:
            await load_model_lazy()
        except Exception as e:
            return {"error": f"Model loading failed: {str(e)}"}
    
    output_shape = OUT_DET['shape'].tolist() if OUT_DET else None
    input_shape = IN_DET['shape'].tolist() if IN_DET else None

    return {
        "labels": LABELS,
        "output_shape": output_shape,
        "input_shape": input_shape,
        "preprocess": {
            "size": MODEL_CONFIG.get("input_size", [224, 224, 3])[:2],
            "rgb": True,
            "scale": MODEL_CONFIG.get("scale", "x/255.0")
        },
        "tflite_sha": MODEL_SHA or "unknown",
        "threshold": THRESH,
        "model_config": MODEL_CONFIG,
        "model_load_time": f"{MODEL_LOAD_TIME:.2f}s",
        "model_loaded": READY.is_set(),
        "tflite_available": TFLITE_AVAILABLE,
        "version": "2.0.0"
    }

@app.post("/predict")
async def predict(
    file: Optional[UploadFile] = File(None),
    image_base64: Optional[str] = None
):
    """
    Predict brain tumor from image.
    Accepts either multipart/form-data (file) or JSON with base64 image.
    """
    request_start = time.time()
    
    # Lazy load model on first request
    if not READY.is_set():
        logger.info("Model not loaded, triggering lazy load...")
        try:
            await load_model_lazy()
        except Exception as e:
            logger.error(f"Model loading failed: {e}")
            raise HTTPException(
                status_code=503,
                detail="Model loading failed. Please try again later."
            )
    
    # Parse image from either file upload or base64
    try:
        if file:
            # Validate file type
            allowed_types = {"image/jpeg", "image/png", "image/jpg"}
            if file.content_type not in allowed_types:
                raise HTTPException(
                    status_code=400,
                    detail="File must be JPG or PNG image."
                )
            
            # Read file
            contents = await file.read()
            if len(contents) == 0:
                raise HTTPException(status_code=400, detail="Empty file uploaded.")
            
            # Check file size (max 10MB)
            max_size = 10 * 1024 * 1024
            if len(contents) > max_size:
                raise HTTPException(
                    status_code=400,
                    detail="File too large. Maximum 10MB allowed."
                )
            
            img = Image.open(io.BytesIO(contents))
            
        elif image_base64:
            # Decode base64 image
            try:
                image_data = base64.b64decode(image_base64)
                img = Image.open(io.BytesIO(image_data))
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid base64 image: {str(e)}"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="Either 'file' or 'image_base64' must be provided."
            )
        
        # Validate image dimensions
        if img.size[0] < 32 or img.size[1] < 32:
            raise HTTPException(
                status_code=400,
                detail="Image too small. Minimum 32x32 pixels."
            )
        if img.size[0] > 4096 or img.size[1] > 4096:
            raise HTTPException(
                status_code=400,
                detail="Image too large. Maximum 4096x4096 pixels."
            )
        
        # Preprocess with timing
        preprocess_start = time.time()
        x = preprocess(img)
        preprocess_time = time.time() - preprocess_start
        
        # Inference with timing
        inference_start = time.time()
        if TFLITE_AVAILABLE and INTERP:
            INTERP.set_tensor(IN_DET["index"], x)
            INTERP.invoke()
            probs = INTERP.get_tensor(OUT_DET["index"])[0]
        else:
            # Mock prediction for testing
            logger.warning("Using mock prediction (TFLite not available)")
            probs = np.array([0.7, 0.3])
        inference_time = time.time() - inference_start
        
        # Handle different output shapes
        if len(probs.shape) == 2 and probs.shape[1] == 2:
            probs_list = [float(probs[0][0]), float(probs[0][1])]
        elif len(probs.shape) == 1 and probs.shape[0] == 2:
            probs_list = [float(probs[0]), float(probs[1])]
        elif len(probs.shape) == 1 and probs.shape[0] == 1:
            # Sigmoid output
            p_tumor = float(probs[0])
            probs_list = [1.0 - p_tumor, p_tumor]
        else:
            logger.error(f"Unexpected model output shape: {probs.shape}")
            probs_list = [0.5, 0.5]
        
        # Get prediction
        p_tumor = probs_list[1]
        prediction = LABELS[1] if p_tumor >= THRESH else LABELS[0]
        confidence = max(probs_list)
        
        total_time = time.time() - request_start
        
        logger.info(
            f"Prediction: {prediction} (confidence: {confidence:.4f}, "
            f"total_time: {total_time*1000:.2f}ms)"
        )
        
        return {
            "success": True,
            "prediction": prediction,
            "confidence": round(confidence, 4),
            "probabilities": {
                LABELS[0]: round(probs_list[0], 4),
                LABELS[1]: round(probs_list[1], 4)
            },
            "threshold": THRESH,
            "model_sha": MODEL_SHA or "unknown",
            "processing_times": {
                "preprocessing_ms": round(preprocess_time * 1000, 2),
                "inference_ms": round(inference_time * 1000, 2),
                "total_ms": round(total_time * 1000, 2)
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )
