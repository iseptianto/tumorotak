# 🔐 GitHub Actions Setup untuk Auto-Deploy

Panduan setup GitHub Actions untuk auto-deploy ke Google Cloud Run setiap kali push ke repository.

## Prerequisites

1. Google Cloud Project dengan billing enabled
2. Repository GitHub (https://github.com/iseptianto/tumorotak)
3. gcloud CLI terinstall

## Step 1: Create Service Account

```bash
# Set project ID
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions Deploy"

# Get service account email
export SA_EMAIL="github-actions@${PROJECT_ID}.iam.gserviceaccount.com"
```

## Step 2: Grant Permissions

```bash
# Grant Cloud Run Admin role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.admin"

# Grant Storage Admin role (for Container Registry)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.admin"

# Grant Service Account User role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser"
```

## Step 3: Create Service Account Key

```bash
# Create and download key
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=${SA_EMAIL}

# Display key content (copy this for GitHub)
cat github-actions-key.json
```

⚠️ **IMPORTANT**: Simpan file ini dengan aman dan jangan commit ke Git!

## Step 4: Add GitHub Secrets

1. Buka repository: https://github.com/iseptianto/tumorotak
2. Go to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

### Add these secrets:

#### Secret 1: GCP_PROJECT_ID
- Name: `GCP_PROJECT_ID`
- Value: Your Google Cloud Project ID (e.g., `my-project-123`)

#### Secret 2: GCP_SA_KEY
- Name: `GCP_SA_KEY`
- Value: Entire content of `github-actions-key.json` file

## Step 5: Enable Required APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

## Step 6: Test Workflow

### Option 1: Push to main branch
```bash
git add .
git commit -m "Setup Cloud Run deployment"
git push origin main
```

### Option 2: Manual trigger
1. Go to **Actions** tab in GitHub
2. Select **Deploy to Cloud Run** workflow
3. Click **Run workflow**

## Verify Deployment

1. Check GitHub Actions tab untuk melihat progress
2. Setelah selesai, cek service URL di logs
3. Test dengan:
```bash
curl https://tumorotak-xxxxx-xx.a.run.app/health
```

## Workflow Features

✅ **Auto-deploy** on push to main/master branch
✅ **Manual trigger** via GitHub Actions UI
✅ **Docker build** and push to GCR
✅ **Cloud Run deployment** with optimal settings
✅ **Health check** after deployment
✅ **Service URL** displayed in logs

## Troubleshooting

### Error: Permission denied

**Solution**: Pastikan service account punya semua roles yang diperlukan:
```bash
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:${SA_EMAIL}"
```

### Error: API not enabled

**Solution**: Enable required APIs:
```bash
gcloud services enable run.googleapis.com containerregistry.googleapis.com
```

### Error: Invalid credentials

**Solution**: 
1. Regenerate service account key
2. Update `GCP_SA_KEY` secret di GitHub
3. Pastikan JSON format valid (no extra spaces/newlines)

## Security Best Practices

1. ✅ **Never commit** service account keys to Git
2. ✅ **Rotate keys** regularly (every 90 days)
3. ✅ **Use least privilege** - only grant necessary permissions
4. ✅ **Monitor usage** via Cloud Console
5. ✅ **Delete old keys** after rotation

## Cleanup Service Account Key

After adding to GitHub:
```bash
# Delete local key file
rm github-actions-key.json

# List keys
gcloud iam service-accounts keys list --iam-account=${SA_EMAIL}

# Delete old keys if needed
gcloud iam service-accounts keys delete KEY_ID --iam-account=${SA_EMAIL}
```

## Cost Monitoring

Setup budget alerts:
```bash
# Create budget alert
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="Cloud Run Budget" \
  --budget-amount=50USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

## Next Steps

1. ✅ Setup branch protection rules
2. ✅ Add staging environment
3. ✅ Implement rollback strategy
4. ✅ Add integration tests
5. ✅ Setup monitoring alerts

## Support

Jika ada masalah:
- 📧 Email: indraseptianto18@gmail.com
- 💬 WhatsApp: +628983776946
- 🐛 GitHub Issues: https://github.com/iseptianto/tumorotak/issues
