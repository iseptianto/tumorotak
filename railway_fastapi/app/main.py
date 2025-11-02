import os, numpy as np
from PIL import Image
from fastapi import FastAPI, UploadFile, File, HTTPException
from huggingface_hub import hf_hub_download
import tflite_runtime.interpreter as tflite

HF_REPO   = os.getenv("HF_REPO", "palawakampa/tumorotak")
HF_FILE   = os.getenv("HF_FILENAME", "brain_tumor.tflite")
MODEL_DIR = os.getenv("MODEL_DIR", "/app/models")
MODEL_PATH = os.path.join(MODEL_DIR, HF_FILE)

os.makedirs(MODEL_DIR, exist_ok=True)
if not os.path.exists(MODEL_PATH):
    local = hf_hub_download(repo_id=HF_REPO, filename=HF_FILE,
                            local_dir=MODEL_DIR, local_dir_use_symlinks=False,
                            token=os.getenv("HF_TOKEN") or None)
    if local != MODEL_PATH:
        import shutil; shutil.copy2(local, MODEL_PATH)

interpreter = tflite.Interpreter(model_path=MODEL_PATH, num_threads=1)
interpreter.allocate_tensors()
in_det, out_det = interpreter.get_input_details(), interpreter.get_output_details()

app = FastAPI(title="Tumor Otak API (Railway)")

@app.get("/health")
def health():
    return {"status": "ok", "model_ready": True}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        img = Image.open(file.file).convert("RGB").resize((224,224))
        x = np.expand_dims(np.array(img, dtype=np.float32)/255.0, 0)
        interpreter.set_tensor(in_det[0]['index'], x)
        interpreter.invoke()
        y = interpreter.get_tensor(out_det[0]['index'])
        prob = float(y[0][0])
        label = "Tumor Otak" if prob > 0.5 else "NORMAL"
        return {"prediction": label, "probability": prob}
    except Exception as e:
        raise HTTPException(400, f"Bad image: {e}")
