import os
import numpy as np
from PIL import Image
import gradio as gr
from huggingface_hub import hf_hub_download

# ====== ENV / Konfigurasi ======
HF_REPO   = os.getenv("HF_REPO", "palawakampa/tumorotak")  # brain tumor repo
HF_FILE   = os.getenv("HF_FILENAME", "brain_tumor.tflite")  # brain tumor model file
MODEL_DIR = os.getenv("MODEL_DIR", "models")
MODEL_PATH = os.path.join(MODEL_DIR, HF_FILE)

# ====== Download model ======
os.makedirs(MODEL_DIR, exist_ok=True)
if not os.path.exists(MODEL_PATH):
    local = hf_hub_download(
        repo_id=HF_REPO,
        filename=HF_FILE,
        local_dir=MODEL_DIR,
        local_dir_use_symlinks=False,
        token=os.getenv("HF_TOKEN") or None,
    )
    if local != MODEL_PATH:
        import shutil; shutil.copy2(local, MODEL_PATH)

# ====== Load model (TFLite) ======
import tflite_runtime.interpreter as tflite
interpreter = tflite.Interpreter(model_path=MODEL_PATH, num_threads=1)
interpreter.allocate_tensors()
in_details  = interpreter.get_input_details()
out_details = interpreter.get_output_details()

def infer(image: Image.Image):
    """Brain Tumor Inference Function"""
    if image is None:
        return {"error": "No image provided"}

    try:
        # Preprocess
        img = image.convert("RGB").resize((224, 224))
        x = np.expand_dims(np.array(img, dtype=np.float32) / 255.0, axis=0)

        # Inference
        interpreter.set_tensor(in_details[0]["index"], x)
        interpreter.invoke()
        y = interpreter.get_tensor(out_details[0]["index"])

        # Handle different output shapes
        if y.shape == (1, 2):
            # Softmax output
            prob_tumor = float(y[0][1])  # Assuming [normal, tumor]
        elif y.shape == (1,):
            # Sigmoid output
            prob_tumor = float(y[0])
        else:
            return {"error": f"Unexpected model output shape: {y.shape}"}

        # Determine prediction
        label = "TUMOR OTAK" if prob_tumor > 0.5 else "TIDAK TUMOR OTAK"
        confidence = max(prob_tumor, 1 - prob_tumor)

        return {
            "prediction": label,
            "probability_tumor": round(prob_tumor, 4),
            "probability_normal": round(1 - prob_tumor, 4),
            "confidence": round(confidence, 4)
        }

    except Exception as e:
        return {"error": f"Inference failed: {str(e)}"}

# Custom CSS for dark mode and styling
css = """
.gradio-container {
    background: var(--background-fill-primary);
    color: var(--body-text-color);
}

.dark .gradio-container {
    --background-fill-primary: #1a1a1a;
    --background-fill-secondary: #2d2d2d;
    --body-text-color: #ffffff;
    --body-text-color-subdued: #cccccc;
    --border-color-primary: #444444;
}

.contact-links {
    display: flex;
    gap: 10px;
    margin-top: 10px;
    justify-content: center;
}

.contact-links a {
    padding: 8px 16px;
    border-radius: 5px;
    text-decoration: none;
    font-weight: bold;
    transition: all 0.3s ease;
}

.contact-links .email-link {
    background: #2196f3;
    color: white;
}

.contact-links .email-link:hover {
    background: #1976d2;
}

.contact-links .whatsapp-link {
    background: #25d366;
    color: white;
}

.contact-links .whatsapp-link:hover {
    background: #128c7e;
}
"""

# Gradio Interface with enhanced features
with gr.Blocks(title="🩺 Brain Tumor Predictor", theme=gr.themes.Soft(), css=css) as demo:
    gr.Markdown("# 🩺 Brain Tumor Predictor (TFLite)")

    # Dark mode toggle
    with gr.Row():
        dark_mode = gr.Checkbox(label="🌙 Dark Mode", value=False, elem_id="dark-mode-toggle")

    gr.Markdown("""
    Upload an MRI or CT scan image to predict brain tumor presence using AI.

    **Labels:**
    - TIDAK TUMOR OTAK (No Brain Tumor)
    - TUMOR OTAK (Brain Tumor)

    **Note:** This is for demonstration purposes only. Always consult medical professionals for actual diagnosis.

    This Space exposes a REST API at `/api/predict/` for programmatic access.
    """)

    # Main interface
    with gr.Row():
        with gr.Column():
            input_image = gr.Image(type="pil", label="Upload MRI/CT Scan")
            submit_btn = gr.Button("🔍 Analyze Image", variant="primary")

        with gr.Column():
            output_json = gr.JSON(label="Diagnosis Result")

    # Contact links
    gr.Markdown("### 📞 Contact Us")
    with gr.Row(elem_classes=["contact-links"]):
        gr.HTML("""
        <a href="mailto:indraseptianto18@gmail.com?subject=Brain Tumor Predictor Inquiry" class="email-link" target="_blank">
            📧 Email Support
        </a>
        <a href="https://wa.me/628983776946" class="whatsapp-link" target="_blank">
            💬 WhatsApp Support
        </a>
        """)

    # Submit action
    submit_btn.click(
        fn=infer,
        inputs=input_image,
        outputs=output_json
    )

    # Dark mode JavaScript
    dark_mode.change(
        fn=None,
        inputs=dark_mode,
        outputs=None,
        js="""
        (dark) => {
            const container = document.querySelector('.gradio-container');
            if (dark) {
                container.classList.add('dark');
            } else {
                container.classList.remove('dark');
            }
        }
        """
    )

if __name__ == "__main__":
    demo.launch()