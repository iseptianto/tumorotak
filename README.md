# 🩺 Brain Tumor Detection System

Production-ready brain tumor detection system with FastAPI backend and Streamlit frontend, optimized for Google Cloud Run deployment with automated CI/CD.

[![Deploy to Cloud Run](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run)
[![CI/CD](https://github.com/iseptianto/tumorotak/actions/workflows/deploy-cloudrun.yml/badge.svg)](https://github.com/iseptianto/tumorotak/actions)

## 🏗️ Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   Streamlit     │─────▶│   FastAPI        │─────▶│  TFLite Model   │
│   Frontend      │      │   Backend        │      │  (Lazy Load)    │
│  (Cloud Run)    │      │  (Cloud Run)     │      │  (HuggingFace)  │
└─────────────────┘      └──────────────────┘      └─────────────────┘
        │                         │
        │                         │
        ▼                         ▼
   Port: 8080              Port: 8080
   ENV: API_URL            ENV: PORT, CORS_ORIGINS
```

## ✨ Features

- **🚀 Production-Ready**: Optimized for Google Cloud Run with auto-scaling
- **🔄 CI/CD Pipeline**: Automated deployment via GitHub Actions
- **🧠 Lazy Loading**: Model loads on first request to prevent cold start timeout
- **🔒 Security**: Non-root containers, CORS configuration, health checks
- **📊 Monitoring**: Request latency tracking, health endpoints
- **🎨 Modern UI**: Streamlit frontend with real-time predictions
- **📡 REST API**: FastAPI backend with automatic OpenAPI documentation

## 📚 Documentation

| Document | Description | Priority |
|----------|-------------|----------|
| **[⚡ Quick Start](#-quick-start)** | Deploy in 15 minutes | ⭐⭐⭐ |
| **[🔐 GitHub Secrets Setup](#-github-secrets-setup)** | Required for CI/CD | ⭐⭐⭐ |
| **[🚀 Manual Deployment](#-manual-deployment)** | Deploy without CI/CD | ⭐⭐ |
| **[🧪 Testing](#-testing)** | Verify deployment | ⭐⭐ |
| **[📖 API Documentation](#-api-documentation)** | API reference | ⭐ |

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

## ⚡ Quick Start

### Prerequisites

1. **Google Cloud Account** with billing enabled
2. **GitHub Repository** forked/cloned
3. **gcloud CLI** installed ([Install Guide](https://cloud.google.com/sdk/docs/install))

### Step 1: Setup GCP Project

```bash
# Set project
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Create Artifact Registry repository
gcloud artifacts repositories create tumorotak \
  --repository-format=docker \
  --location=us-west1 \
  --description="Brain tumor detection containers"
```

### Step 2: Create Service Account for CI/CD

```bash
# Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions Deployer"

# Get service account email
export SA_EMAIL="github-actions@${PROJECT_ID}.iam.gserviceaccount.com"

# Grant required roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser"

# Create and download key
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=$SA_EMAIL

# Display key (copy this for GitHub secrets)
cat github-actions-key.json
```

### Step 3: Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `GCP_PROJECT` | `your-project-id` | Your GCP project ID |
| `GCP_SA_KEY` | `{...json content...}` | Service account JSON key |
| `GCP_REGION` | `us-west1` | Deployment region |
| `ARTIFACT_REPO` | `tumorotak` | Artifact Registry repo name |

### Step 4: Deploy via GitHub Actions

```bash
# Push to main branch to trigger deployment
git add .
git commit -m "Deploy to Cloud Run"
git push origin main

# Or manually trigger workflow
# Go to Actions tab → Deploy to Cloud Run → Run workflow
```

### Step 5: Access Your Application

After deployment completes (5-10 minutes):

- **Backend API**: Check GitHub Actions output for URL
- **Frontend UI**: Check GitHub Actions output for URL
- **API Docs**: `https://backend-url/docs`

## 🚀 Manual Deployment

If you prefer to deploy without GitHub Actions:

### Deploy Backend

```bash
# Build and push image
gcloud builds submit --tag us-west1-docker.pkg.dev/$PROJECT_ID/tumorotak/backend:latest

# Deploy to Cloud Run
gcloud run deploy tumorotak-backend \
  --image us-west1-docker.pkg.dev/$PROJECT_ID/tumorotak/backend:latest \
  --platform managed \
  --region us-west1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --set-env-vars "CORS_ORIGINS=*"

# Get backend URL
BACKEND_URL=$(gcloud run services describe tumorotak-backend \
  --region us-west1 --format 'value(status.url)')
echo "Backend URL: $BACKEND_URL"
```

### Deploy Frontend

```bash
# Build and push image
gcloud builds submit --tag us-west1-docker.pkg.dev/$PROJECT_ID/tumorotak/frontend:latest \
  -f Dockerfile.streamlit

# Deploy to Cloud Run
gcloud run deploy tumorotak-frontend \
  --image us-west1-docker.pkg.dev/$PROJECT_ID/tumorotak/frontend:latest \
  --platform managed \
  --region us-west1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --set-env-vars "API_URL=$BACKEND_URL"

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe tumorotak-frontend \
  --region us-west1 --format 'value(status.url)')
echo "Frontend URL: $FRONTEND_URL"
```

## 🧪 Testing

### Test Backend Health

```bash
curl https://backend-url/health
```

Expected response:
```json
{"status": "ok"}
```

### Test Prediction API

```bash
curl -X POST https://backend-url/predict \
  -F "file=@test_brain_scan.jpg"
```

Expected response:
```json
{
  "success": true,
  "prediction": "Tumor",
  "confidence": 0.8765,
  "probabilities": {
    "No Tumor": 0.1235,
    "Tumor": 0.8765
  },
  "threshold": 0.5,
  "processing_times": {
    "preprocessing_ms": 45.2,
    "inference_ms": 123.5,
    "total_ms": 168.7
  }
}
```

### Test Frontend

1. Open frontend URL in browser
2. Upload a brain MRI/CT scan image
3. Click "Analyze Image"
4. View prediction results

## 📖 API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check (always returns 200) |
| POST | `/predict` | Predict brain tumor from image |
| GET | `/debug/model_meta` | Model metadata and configuration |
| GET | `/docs` | Interactive API documentation (Swagger) |
| GET | `/redoc` | Alternative API documentation (ReDoc) |

### Request Format

**Multipart Form Data:**
```bash
curl -X POST https://backend-url/predict \
  -F "file=@image.jpg"
```

**JSON with Base64:**
```bash
curl -X POST https://backend-url/predict \
  -H "Content-Type: application/json" \
  -d '{"image_base64": "iVBORw0KGgoAAAANS..."}'
```

### Response Format

```json
{
  "success": true,
  "prediction": "Tumor" | "No Tumor",
  "confidence": 0.8765,
  "probabilities": {
    "No Tumor": 0.1235,
    "Tumor": 0.8765
  },
  "threshold": 0.5,
  "model_sha": "abc12345",
  "processing_times": {
    "preprocessing_ms": 45.2,
    "inference_ms": 123.5,
    "total_ms": 168.7
  }
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