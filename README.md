# 🩺 Brain Tumor Predictor

A machine learning model for brain tumor detection using MRI/CT scan images. Built with TensorFlow Lite and deployed on Hugging Face Spaces.

## Features

- **AI-Powered Diagnosis**: Uses deep learning to analyze MRI/CT scans
- **Real-time Prediction**: Fast inference with TFLite optimized model
- **REST API**: Programmatic access via `/api/predict/` endpoint
- **Web Interface**: User-friendly Gradio interface
- **Indonesian Labels**: Results in Bahasa Indonesia

## Model Details

- **Model**: Custom CNN trained on brain tumor dataset
- **Framework**: TensorFlow Lite
- **Input**: RGB images (224x224)
- **Output**: Binary classification (Tumor/No Tumor)
- **Accuracy**: ~83.36%

## Usage

### Web Interface
1. Upload an MRI/CT scan image
2. Click "Submit" to get prediction
3. View results with confidence scores

### REST API

```bash
curl -X POST \
  -F "data=@/path/to/brain_scan.jpg" \
  https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME/api/predict/
```

**Response Format:**
```json
{
  "prediction": "TUMOR OTAK",
  "probability_tumor": 0.8765,
  "probability_normal": 0.1235,
  "confidence": 0.8765
}
```

## Labels

- `TIDAK TUMOR OTAK`: No brain tumor detected
- `TUMOR OTAK`: Brain tumor detected

## Important Notice

⚠️ **This is for demonstration purposes only.** Always consult qualified medical professionals for actual diagnosis and treatment decisions.

## Technical Details

- **Model Source**: `palawakampa/tumorotak`
- **Model File**: `brain_tumor.tflite`
- **Runtime**: TFLite Runtime
- **Dependencies**: See `requirements.txt`

## License

This project is for educational and research purposes.