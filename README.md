# 🩺 Brain Tumor Predictor

A machine learning model for brain tumor detection using MRI/CT scan images. Built with TensorFlow Lite and FastAPI, ready for deployment on Google Cloud Run.

[![Deploy to Cloud Run](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run)

## 📚 Documentation

- **[⚡ Quick Start](QUICKSTART.md)** - Deploy in 5 minutes
- **[🚀 Cloud Run Deployment](DEPLOY_CLOUDRUN.md)** - Detailed deployment guide
- **[🔐 GitHub Actions Setup](GITHUB_SETUP.md)** - CI/CD automation

## Features

- **AI-Powered Diagnosis**: Uses deep learning to analyze MRI/CT scans
- **Real-time Prediction**: Fast inference with TFLite optimized model
- **REST API**: FastAPI-based API with automatic documentation
- **Cloud-Ready**: Optimized for Google Cloud Run deployment
- **Auto-Scaling**: Scales to zero when not in use
- **Health Checks**: Built-in health and debug endpoints

## Model Details

- **Model**: Custom CNN trained on brain tumor dataset
- **Framework**: TensorFlow Lite
- **Input**: RGB images (224x224)
- **Output**: Binary classification (Tumor/No Tumor)
- **Accuracy**: ~83.36%

## Quick Start

### Local Development

```bash
# Build Docker image
docker build -t tumorotak .

# Run locally
docker run -p 8080:8080 -e PORT=8080 tumorotak

# Test health endpoint
curl http://localhost:8080/health
```

### Deploy to Google Cloud Run

See [DEPLOY_CLOUDRUN.md](DEPLOY_CLOUDRUN.md) for detailed instructions.

Quick deploy:
```bash
gcloud run deploy tumorotak \
  --source . \
  --region asia-southeast2 \
  --allow-unauthenticated
```

## API Usage

### Health Check

```bash
curl https://your-service.run.app/health
```

### Predict

```bash
curl -X POST https://your-service.run.app/predict \
  -F "file=@brain_scan.jpg"
```

**Response Format:**
```json
{
  "labels": ["No Tumor", "Tumor"],
  "probs": [0.1235, 0.8765],
  "prediction": "Tumor",
  "confidence": 0.8765,
  "threshold": 0.5,
  "model_accuracy": 0.96,
  "processing_times": {
    "preprocessing_ms": 45.2,
    "inference_ms": 123.5,
    "total_ms": 168.7
  }
}
```

### API Documentation

Once deployed, visit:
- Swagger UI: `https://your-service.run.app/docs`
- ReDoc: `https://your-service.run.app/redoc`

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