# ✅ Deployment Checklist

Checklist lengkap untuk memastikan deployment sukses ke Google Cloud Run.

## Pre-Deployment

### 1. Google Cloud Setup
- [ ] Google Cloud account created
- [ ] Billing enabled
- [ ] Project created
- [ ] gcloud CLI installed
- [ ] Authenticated: `gcloud auth login`
- [ ] Project set: `gcloud config set project PROJECT_ID`

### 2. Enable APIs
```bash
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 3. Local Validation
- [ ] Run: `python validate_setup.py`
- [ ] All checks passed

### 4. Docker Test (Optional)
- [ ] Build: `docker build -t tumorotak .`
- [ ] Run: `docker run -p 8080:8080 -e PORT=8080 tumorotak`
- [ ] Test: `curl http://localhost:8080/health`

## Deployment Options

### Option A: Direct Deploy (Easiest)
```bash
gcloud run deploy tumorotak \
  --source . \
  --region asia-southeast2 \
  --allow-unauthenticated \
  --memory 2Gi
```

### Option B: Using Script
```bash
chmod +x deploy-cloudrun.sh
./deploy-cloudrun.sh YOUR_PROJECT_ID asia-southeast2
```

### Option C: Using Cloud Build
```bash
gcloud builds submit --config cloudbuild.yaml
```

## Post-Deployment

### 1. Get Service URL
```bash
gcloud run services describe tumorotak \
  --region asia-southeast2 \
  --format 'value(status.url)'
```

### 2. Test Endpoints
- [ ] Health: `curl https://SERVICE_URL/health`
- [ ] Root: `curl https://SERVICE_URL/`
- [ ] Docs: Open `https://SERVICE_URL/docs` in browser
- [ ] Model Meta: `curl https://SERVICE_URL/debug/model_meta`

### 3. Test Prediction
```bash
curl -X POST https://SERVICE_URL/predict \
  -F "file=@test_image.jpg"
```

### 4. Monitor Logs
```bash
gcloud run services logs read tumorotak --region asia-southeast2
```

### 5. Check Metrics
- [ ] Open Cloud Console
- [ ] Navigate to Cloud Run
- [ ] Check service metrics
- [ ] Verify no errors

## GitHub Actions Setup (Optional)

### 1. Create Service Account
```bash
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions Deploy"
```

### 2. Grant Permissions
```bash
export PROJECT_ID="your-project-id"
export SA_EMAIL="github-actions@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser"
```

### 3. Create Key
```bash
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=${SA_EMAIL}
```

### 4. Add GitHub Secrets
- [ ] Go to GitHub repo settings
- [ ] Add secret: `GCP_PROJECT_ID`
- [ ] Add secret: `GCP_SA_KEY` (content of github-actions-key.json)

### 5. Test Workflow
- [ ] Push to main branch
- [ ] Check GitHub Actions tab
- [ ] Verify deployment success

## Troubleshooting

### Container failed to start
- [ ] Check logs: `gcloud run services logs read tumorotak`
- [ ] Verify PORT binding in Dockerfile
- [ ] Check memory limits

### Model loading timeout
- [ ] Increase timeout: `--timeout 600`
- [ ] Increase memory: `--memory 4Gi`
- [ ] Check model download

### Permission denied
- [ ] Verify service account permissions
- [ ] Check IAM policies
- [ ] Ensure APIs are enabled

### Out of memory
- [ ] Increase memory allocation
- [ ] Optimize model loading
- [ ] Check for memory leaks

## Cost Optimization

- [ ] Set min-instances to 0 for auto-scaling
- [ ] Set appropriate max-instances
- [ ] Monitor usage in billing console
- [ ] Set up budget alerts
- [ ] Review and optimize resource allocation

## Security

- [ ] Review IAM permissions
- [ ] Enable Cloud Armor (if needed)
- [ ] Set up VPC connector (if needed)
- [ ] Configure secrets management
- [ ] Enable audit logging

## Monitoring

- [ ] Set up uptime checks
- [ ] Configure alerting policies
- [ ] Enable Cloud Monitoring
- [ ] Set up error reporting
- [ ] Configure log-based metrics

## Documentation

- [ ] Update README with service URL
- [ ] Document API endpoints
- [ ] Add usage examples
- [ ] Update architecture diagrams
- [ ] Document troubleshooting steps

## Final Verification

- [ ] Service is accessible
- [ ] Health check passes
- [ ] Predictions work correctly
- [ ] Performance is acceptable
- [ ] Costs are within budget
- [ ] Monitoring is active
- [ ] Documentation is complete

## Rollback Plan

If deployment fails:
```bash
# List revisions
gcloud run revisions list --service tumorotak --region asia-southeast2

# Rollback to previous revision
gcloud run services update-traffic tumorotak \
  --to-revisions REVISION_NAME=100 \
  --region asia-southeast2
```

## Support

Need help? Contact:
- 📧 Email: indraseptianto18@gmail.com
- 💬 WhatsApp: +628983776946
- 🐛 GitHub: https://github.com/iseptianto/tumorotak/issues

---

**Last Updated**: 2024
**Version**: 1.0.0
