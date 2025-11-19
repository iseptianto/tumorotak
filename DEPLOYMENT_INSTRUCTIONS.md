# 🚀 Deployment Instructions for Repository Owner

## 📋 Summary

I've successfully implemented a production-ready Cloud Run deployment solution with automated CI/CD. All code changes have been pushed to branch `fix/cloudrun-integration`.

## ✅ What's Been Done

### Code Changes
- ✅ FastAPI backend optimized for Cloud Run (lazy loading, PORT binding, health checks)
- ✅ Streamlit frontend with configurable API_URL
- ✅ Dockerfiles for both backend and frontend
- ✅ GitHub Actions CI/CD workflow
- ✅ Comprehensive documentation

### Branch & Commit
- **Branch**: `fix/cloudrun-integration`
- **Status**: Pushed to GitHub
- **PR URL**: https://github.com/iseptianto/tumorotak/pull/new/fix/cloudrun-integration

## 🎯 What You Need to Do

### Step 1: Configure GitHub Secrets (REQUIRED)

Go to: https://github.com/iseptianto/tumorotak/settings/secrets/actions

Click "New repository secret" and add these:

#### 1. GCP_PROJECT
```
Name: GCP_PROJECT
Value: your-gcp-project-id
```

#### 2. GCP_SA_KEY
First, create the service account and key:

```bash
# Set your project ID
export PROJECT_ID="your-project-id"

# Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions Deployer"

# Get email
export SA_EMAIL="github-actions@${PROJECT_ID}.iam.gserviceaccount.com"

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser"

# Create key
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=$SA_EMAIL

# Display key
cat github-actions-key.json
```

Then add to GitHub:
```
Name: GCP_SA_KEY
Value: <paste entire JSON content from github-actions-key.json>
```

#### 3. GCP_REGION (Optional)
```
Name: GCP_REGION
Value: us-west1
```

#### 4. ARTIFACT_REPO (Optional)
```
Name: ARTIFACT_REPO
Value: tumorotak
```

### Step 2: Setup GCP Infrastructure (REQUIRED)

```bash
# Enable APIs
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Create Artifact Registry
gcloud artifacts repositories create tumorotak \
  --repository-format=docker \
  --location=us-west1 \
  --description="Brain tumor detection containers"
```

### Step 3: Create Pull Request

1. Go to: https://github.com/iseptianto/tumorotak/pull/new/fix/cloudrun-integration
2. Review the changes
3. Copy content from `PR_DESCRIPTION.md` as the PR description
4. Create the pull request

### Step 4: Merge and Deploy

Once the PR is created:
1. Review the changes
2. Click "Merge pull request"
3. GitHub Actions will automatically:
   - Build Docker images
   - Push to Artifact Registry
   - Deploy to Cloud Run
   - Post deployment URLs in PR comment

### Step 5: Access Your Application

After deployment completes (5-10 minutes), you'll see a comment on the PR with:
- Backend URL: `https://tumorotak-backend-xxxxx-uc.a.run.app`
- Frontend URL: `https://tumorotak-frontend-xxxxx-uc.a.run.app`

## 🧪 Testing

### Test Backend
```bash
# Health check
curl https://backend-url/health

# Prediction
curl -X POST https://backend-url/predict -F "file=@test_image.jpg"

# API docs
open https://backend-url/docs
```

### Test Frontend
1. Open frontend URL in browser
2. Upload brain scan image
3. Click "Analyze Image"
4. View results

## 📊 Expected Costs

- **Free Tier**: 2 million requests/month
- **Typical Usage**: $1-5/month (1000-10000 requests/day)
- **Auto-scaling**: $0 when idle (scales to zero)

## 🔧 Configuration Options

### Change Region
Edit `.github/workflows/deploy-cloudrun.yml`:
```yaml
env:
  GCP_REGION: asia-southeast2  # Change this
```

### Adjust Resources
Edit workflow file:
```yaml
--memory 4Gi  # Increase memory
--cpu 4       # Increase CPU
```

### Configure CORS
Edit workflow file:
```yaml
--set-env-vars "CORS_ORIGINS=https://yourdomain.com"
```

## 🚨 Troubleshooting

### Workflow Fails

**Check logs**: Go to Actions tab → Click failed workflow → View logs

**Common issues**:
1. Missing GitHub secrets → Add them in Settings
2. APIs not enabled → Run `gcloud services enable ...`
3. Service account permissions → Re-run IAM binding commands

### Container Failed to Start

```bash
# View logs
gcloud run services logs read tumorotak-backend --region us-west1 --limit 50
```

### Model Loading Timeout

Increase timeout in workflow:
```yaml
--timeout 600  # 10 minutes
--memory 4Gi   # More memory
```

## 📞 Support

If you encounter any issues:

1. **Check Documentation**:
   - README.md - Setup guide
   - CONFIGURATION.md - Detailed config
   - PR_DESCRIPTION.md - Complete checklist

2. **View Logs**:
   - GitHub Actions logs
   - Cloud Run logs

3. **Contact**:
   - 📧 indraseptianto18@gmail.com
   - 💬 +628983776946

## ✅ Checklist

Before merging:
- [ ] GitHub secrets configured (GCP_PROJECT, GCP_SA_KEY)
- [ ] GCP APIs enabled
- [ ] Artifact Registry created
- [ ] Service account created with permissions
- [ ] PR created and reviewed

After merging:
- [ ] GitHub Actions workflow completed successfully
- [ ] Backend health check passes
- [ ] Frontend loads and connects to backend
- [ ] Prediction works end-to-end

## 🎉 Success Criteria

Deployment is successful when:
1. ✅ GitHub Actions workflow shows green checkmark
2. ✅ Backend `/health` returns `{"status":"ok"}`
3. ✅ Frontend loads without errors
4. ✅ Image upload and prediction works
5. ✅ PR comment shows deployment URLs

---

**Next Step**: Configure GitHub secrets and create the PR!

The PR URL will be: https://github.com/iseptianto/tumorotak/pull/new/fix/cloudrun-integration
