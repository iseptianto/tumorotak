# 🚀 Deploy ke Google Cloud Run

Panduan lengkap untuk deploy aplikasi Brain Tumor Detection ke Google Cloud Run.

## Prerequisites

1. **Google Cloud Account** dengan billing enabled
2. **gcloud CLI** terinstall ([Install Guide](https://cloud.google.com/sdk/docs/install))
3. **Docker** terinstall
4. **Git** terinstall

## Setup Awal

### 1. Login ke Google Cloud

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 2. Enable Required APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 3. Configure Docker untuk GCR

```bash
gcloud auth configure-docker
```

## Deployment Methods

### Method 1: Manual Deployment (Recommended untuk pertama kali)

#### Step 1: Build Docker Image

```bash
docker build -t gcr.io/YOUR_PROJECT_ID/tumorotak:latest .
```

#### Step 2: Test Locally (Optional)

```bash
docker run -p 8080:8080 -e PORT=8080 gcr.io/YOUR_PROJECT_ID/tumorotak:latest
```

Buka browser: http://localhost:8080/health

#### Step 3: Push ke Google Container Registry

```bash
docker push gcr.io/YOUR_PROJECT_ID/tumorotak:latest
```

#### Step 4: Deploy ke Cloud Run

```bash
gcloud run deploy tumorotak \
  --image gcr.io/YOUR_PROJECT_ID/tumorotak:latest \
  --platform managed \
  --region asia-southeast2 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0 \
  --port 8080
```

### Method 2: Using Deploy Script

```bash
chmod +x deploy-cloudrun.sh
./deploy-cloudrun.sh YOUR_PROJECT_ID asia-southeast2
```

### Method 3: Using Cloud Build (CI/CD)

```bash
gcloud builds submit --config cloudbuild.yaml
```

## Configuration

### Resource Limits

- **Memory**: 2Gi (bisa dikurangi ke 1Gi jika perlu hemat)
- **CPU**: 2 (bisa dikurangi ke 1 jika perlu hemat)
- **Timeout**: 300s (5 menit untuk cold start + model loading)
- **Max Instances**: 10 (sesuaikan dengan traffic)
- **Min Instances**: 0 (auto scale to zero untuk hemat biaya)

### Environment Variables (Optional)

Jika perlu custom config:

```bash
gcloud run deploy tumorotak \
  --image gcr.io/YOUR_PROJECT_ID/tumorotak:latest \
  --set-env-vars "HF_TOKEN=your_token_here"
```

## Testing Deployment

### 1. Health Check

```bash
curl https://tumorotak-xxxxx-xx.a.run.app/health
```

Expected response:
```json
{
  "status": "ok",
  "model_loaded": true,
  "model_load_time": "2.45",
  "tflite_available": true
}
```

### 2. Model Metadata

```bash
curl https://tumorotak-xxxxx-xx.a.run.app/debug/model_meta
```

### 3. Prediction Test

```bash
curl -X POST https://tumorotak-xxxxx-xx.a.run.app/predict \
  -F "file=@test_image.jpg"
```

## Monitoring

### View Logs

```bash
gcloud run services logs read tumorotak --region asia-southeast2
```

### View Metrics

```bash
gcloud run services describe tumorotak --region asia-southeast2
```

Atau buka Cloud Console: https://console.cloud.google.com/run

## Troubleshooting

### Error: Container failed to start

**Penyebab**: Aplikasi tidak bind ke PORT yang benar

**Solusi**: Pastikan Dockerfile menggunakan `${PORT}` environment variable:
```dockerfile
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
```

### Error: Timeout during startup

**Penyebab**: Model loading terlalu lama

**Solusi**: 
1. Increase timeout: `--timeout 600`
2. Increase memory: `--memory 4Gi`
3. Use lazy loading (sudah implemented)

### Error: Out of memory

**Penyebab**: Model terlalu besar untuk memory yang dialokasikan

**Solusi**: Increase memory:
```bash
gcloud run services update tumorotak --memory 4Gi --region asia-southeast2
```

### Error: Permission denied

**Penyebab**: Service account tidak punya akses

**Solusi**:
```bash
gcloud run services add-iam-policy-binding tumorotak \
  --region asia-southeast2 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

## Cost Optimization

### 1. Auto Scale to Zero
```bash
--min-instances 0
```

### 2. Reduce Resources
```bash
--memory 1Gi --cpu 1
```

### 3. Set Max Instances
```bash
--max-instances 5
```

### 4. Use Request-based Pricing
Cloud Run charges only for:
- Request time (billed per 100ms)
- Memory allocated during request
- CPU allocated during request

**Estimasi Biaya** (per bulan):
- 1000 requests/day × 2s avg = ~$1-2/month
- 10000 requests/day × 2s avg = ~$10-20/month

## Update Deployment

### Update Image Only
```bash
docker build -t gcr.io/YOUR_PROJECT_ID/tumorotak:latest .
docker push gcr.io/YOUR_PROJECT_ID/tumorotak:latest
gcloud run services update tumorotak --region asia-southeast2
```

### Update Configuration Only
```bash
gcloud run services update tumorotak \
  --memory 4Gi \
  --region asia-southeast2
```

## Delete Service

```bash
gcloud run services delete tumorotak --region asia-southeast2
```

## Next Steps

1. ✅ Setup custom domain
2. ✅ Add authentication
3. ✅ Setup monitoring alerts
4. ✅ Implement rate limiting
5. ✅ Add caching layer

## Support

Jika ada masalah:
- 📧 Email: indraseptianto18@gmail.com
- 💬 WhatsApp: +628983776946
- 🐛 GitHub Issues: https://github.com/iseptianto/tumorotak/issues
