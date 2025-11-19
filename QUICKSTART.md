# ⚡ Quick Start Guide

Deploy aplikasi Brain Tumor Detection ke Google Cloud Run dalam 5 menit!

## 🚀 Super Quick Deploy (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/iseptianto/tumorotak.git
cd tumorotak

# 2. Login ke Google Cloud
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 3. Deploy langsung dari source
gcloud run deploy tumorotak \
  --source . \
  --region asia-southeast2 \
  --allow-unauthenticated \
  --memory 2Gi
```

Selesai! 🎉

## 📋 Prerequisites

- Google Cloud account dengan billing enabled
- gcloud CLI installed ([Install](https://cloud.google.com/sdk/docs/install))

## 🧪 Test Deployment

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe tumorotak --region asia-southeast2 --format 'value(status.url)')

# Test health
curl $SERVICE_URL/health

# Test prediction (ganti dengan path image Anda)
curl -X POST $SERVICE_URL/predict -F "file=@test_image.jpg"
```

## 🔧 Local Testing (Optional)

```bash
# Build image
docker build -t tumorotak .

# Run locally
docker run -p 8080:8080 -e PORT=8080 tumorotak

# Test
curl http://localhost:8080/health
```

## 📚 Detailed Guides

- **Cloud Run Deployment**: [DEPLOY_CLOUDRUN.md](DEPLOY_CLOUDRUN.md)
- **GitHub Actions CI/CD**: [GITHUB_SETUP.md](GITHUB_SETUP.md)
- **API Documentation**: Visit `/docs` endpoint after deployment

## 💰 Cost Estimate

- **Free Tier**: 2 million requests/month
- **Typical Cost**: $1-5/month for moderate usage
- **Auto-scaling**: Scales to zero when not in use

## 🆘 Need Help?

- 📧 Email: indraseptianto18@gmail.com
- 💬 WhatsApp: +628983776946
- 🐛 Issues: [GitHub Issues](https://github.com/iseptianto/tumorotak/issues)

## ✅ Validation

Run validation before deployment:
```bash
python validate_setup.py
```

## 🎯 What's Included

✅ FastAPI application with health checks
✅ TFLite model with lazy loading
✅ Optimized Dockerfile for Cloud Run
✅ GitHub Actions for CI/CD
✅ Comprehensive documentation
✅ Cost optimization settings
✅ Auto-scaling configuration

## 🔄 Update Deployment

```bash
# Make changes to code
git add .
git commit -m "Update feature"
git push

# Redeploy
gcloud run deploy tumorotak --source . --region asia-southeast2
```

Or use GitHub Actions for automatic deployment!
