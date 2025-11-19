# ⚙️ Configuration Guide

Complete configuration reference for the Brain Tumor Detection System.

## Environment Variables

### Backend (FastAPI)

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `PORT` | `8080` | Server port (set by Cloud Run) | No |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins | No |
| `HF_REPO_ID` | `palawakampa/tumorotak` | Hugging Face model repository | No |
| `HF_FILENAME` | `brain_tumor.tflite` | Model filename | No |
| `HF_TOKEN` | - | Hugging Face API token (for private repos) | No |
| `MODEL_GCS_PATH` | - | GCS path to model (e.g., `gs://bucket/model.tflite`) | No |

### Frontend (Streamlit)

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `PORT` | `8080` | Server port (set by Cloud Run) | No |
| `API_URL` | - | Backend API URL | **Yes** |
| `DEBUG` | `false` | Enable debug mode | No |

## GitHub Secrets

Required secrets for CI/CD:

| Secret | Description | How to Get |
|--------|-------------|------------|
| `GCP_PROJECT` | GCP project ID | `gcloud config get-value project` |
| `GCP_SA_KEY` | Service account JSON key | See [Setup Guide](#service-account-setup) |
| `GCP_REGION` | Deployment region | Default: `us-west1` |
| `ARTIFACT_REPO` | Artifact Registry repo name | Default: `tumorotak` |
| `GCP_SERVICE_ACCOUNT` | Service account email (optional) | `SA_NAME@PROJECT.iam.gserviceaccount.com` |

## Service Account Setup

### Create Service Account

```bash
export PROJECT_ID="your-project-id"
export SA_NAME="github-actions"

gcloud iam service-accounts create $SA_NAME \
  --display-name="GitHub Actions Deployer" \
  --project=$PROJECT_ID
```

### Grant Required Roles

```bash
export SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Cloud Run Admin - Deploy services
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.admin"

# Storage Admin - Push to Artifact Registry
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.admin"

# Service Account User - Act as service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser"

# (Optional) Storage Object Viewer - Read from GCS
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.objectViewer"
```

### Create Key

```bash
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=$SA_EMAIL

# Display key content (copy this to GitHub secret)
cat github-actions-key.json
```

⚠️ **Security**: Never commit this key to Git! Add to `.gitignore`.

## Cloud Run Configuration

### Backend Service

```yaml
Service: tumorotak-backend
Region: us-west1
Memory: 2Gi
CPU: 2
Timeout: 300s
Max Instances: 10
Min Instances: 0
Port: 8080
Concurrency: 80
```

### Frontend Service

```yaml
Service: tumorotak-frontend
Region: us-west1
Memory: 1Gi
CPU: 1
Timeout: 300s
Max Instances: 5
Min Instances: 0
Port: 8080
Concurrency: 80
```

## CORS Configuration

### Development (Allow All)

```bash
--set-env-vars "CORS_ORIGINS=*"
```

### Production (Specific Origins)

```bash
--set-env-vars "CORS_ORIGINS=https://frontend-url.run.app,https://yourdomain.com"
```

## Model Configuration

### Using Hugging Face (Default)

```bash
--set-env-vars "HF_REPO_ID=palawakampa/tumorotak,HF_FILENAME=brain_tumor.tflite"
```

### Using Private Hugging Face Repo

```bash
--set-env-vars "HF_REPO_ID=your-org/private-repo,HF_TOKEN=hf_xxxxx"
```

### Using Google Cloud Storage

```bash
--set-env-vars "MODEL_GCS_PATH=gs://your-bucket/models/brain_tumor.tflite"
```

**Note**: Service account needs `roles/storage.objectViewer` on the bucket.

## Artifact Registry Setup

### Create Repository

```bash
gcloud artifacts repositories create tumorotak \
  --repository-format=docker \
  --location=us-west1 \
  --description="Brain tumor detection containers" \
  --project=$PROJECT_ID
```

### Configure Docker Authentication

```bash
gcloud auth configure-docker us-west1-docker.pkg.dev
```

### List Images

```bash
gcloud artifacts docker images list \
  us-west1-docker.pkg.dev/$PROJECT_ID/tumorotak
```

## Monitoring & Logging

### View Logs

```bash
# Backend logs
gcloud run services logs read tumorotak-backend \
  --region us-west1 \
  --limit 100

# Frontend logs
gcloud run services logs read tumorotak-frontend \
  --region us-west1 \
  --limit 100
```

### Stream Logs

```bash
gcloud run services logs tail tumorotak-backend --region us-west1
```

### View Metrics

```bash
# Service details
gcloud run services describe tumorotak-backend --region us-west1

# Revisions
gcloud run revisions list --service tumorotak-backend --region us-west1
```

## Cost Optimization

### Auto-scaling to Zero

```bash
--min-instances 0
```

Services scale to zero when idle = $0 cost when not in use.

### Reduce Resources

```bash
# Backend
--memory 1Gi --cpu 1

# Frontend
--memory 512Mi --cpu 1
```

### Set Request Limits

```bash
--max-instances 5  # Prevent runaway costs
--concurrency 80   # Requests per instance
```

### Budget Alerts

```bash
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="Cloud Run Budget" \
  --budget-amount=50USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90
```

## Security Best Practices

### 1. Use Non-Root Containers

Already implemented in Dockerfiles:
```dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

### 2. Restrict CORS Origins

Production:
```bash
--set-env-vars "CORS_ORIGINS=https://yourdomain.com"
```

### 3. Enable Binary Authorization (Optional)

```bash
gcloud run services update tumorotak-backend \
  --binary-authorization=default \
  --region us-west1
```

### 4. Use Secret Manager for Sensitive Data

```bash
# Create secret
echo -n "your-secret-value" | gcloud secrets create hf-token --data-file=-

# Grant access to service account
gcloud secrets add-iam-policy-binding hf-token \
  --member="serviceAccount:SA_EMAIL" \
  --role="roles/secretmanager.secretAccessor"

# Use in Cloud Run
--set-secrets="HF_TOKEN=hf-token:latest"
```

### 5. Rotate Service Account Keys

```bash
# List keys
gcloud iam service-accounts keys list --iam-account=$SA_EMAIL

# Delete old key
gcloud iam service-accounts keys delete KEY_ID --iam-account=$SA_EMAIL

# Create new key
gcloud iam service-accounts keys create new-key.json --iam-account=$SA_EMAIL
```

## Troubleshooting

### Container Failed to Start

**Check logs:**
```bash
gcloud run services logs read tumorotak-backend --region us-west1 --limit 50
```

**Common causes:**
- Port not bound to `$PORT` environment variable
- Missing dependencies in requirements.txt
- Model download timeout

### Model Loading Timeout

**Increase timeout:**
```bash
gcloud run services update tumorotak-backend \
  --timeout 600 \
  --region us-west1
```

**Increase memory:**
```bash
gcloud run services update tumorotak-backend \
  --memory 4Gi \
  --region us-west1
```

### CORS Errors

**Check CORS configuration:**
```bash
gcloud run services describe tumorotak-backend \
  --region us-west1 \
  --format="value(spec.template.spec.containers[0].env)"
```

**Update CORS:**
```bash
gcloud run services update tumorotak-backend \
  --set-env-vars "CORS_ORIGINS=*" \
  --region us-west1
```

### Permission Denied

**Check service account roles:**
```bash
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:$SA_EMAIL"
```

## Support

- 📧 Email: indraseptianto18@gmail.com
- 💬 WhatsApp: +628983776946
- 🐛 GitHub Issues: https://github.com/iseptianto/tumorotak/issues
