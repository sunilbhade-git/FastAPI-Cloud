# Lab Manual: Deploying FastAPI to Google Cloud Run with GitHub Actions CI/CD

## Objective

By the end of this lab, you will:

- Build a minimal FastAPI app.
- Containerise it using Docker.
- Deploy it to Google Cloud Run.
- Automate redeployment with a GitHub Actions CI/CD pipeline.

---

## Step 1: Create a Minimal FastAPI App

Create `main.py`:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI on Cloud Run!"}
```

This defines a root endpoint that returns JSON.

---

## Step 2: Define Dependencies

Create `requirements.txt`:

```
fastapi
uvicorn[standard]
```

This ensures a consistent environment inside Docker.

---

## Step 3: Write the Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Explanation

- Uses a lightweight Python base image.
- Installs FastAPI + Uvicorn.
- Runs app on `0.0.0.0:8080` (required by Cloud Run).

---

## Step 4: Build and Run Locally

```bash
# Build image
docker build -t fastapi-cloudrun .

# Run container locally
docker run -p 8080:8080 fastapi-cloudrun
```

Open in browser: [http://localhost:8080](http://localhost:8080)

You should see:

```json
{"message": "Hello from FastAPI on Cloud Run!"}
```

---

## Step 5: Deploy to Google Cloud Run

Authenticate & set project:

```bash
gcloud auth login
gcloud config set project PROJECT_ID
```

Deploy the service:

```bash
gcloud run deploy fastapi-service \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

Once complete, GCP gives you a public HTTPS URL.

---

## Step 6: Create GitHub Actions Workflow

Inside your repo, create folder:

```
.github/workflows/deploy.yml
```

**`deploy.yml`**

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: ["main"]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout repository
      uses: actions/checkout@v3

    - name: Set up gcloud
      uses: google-github-actions/setup-gcloud@v1
      with:
        project_id: ${{ secrets.GCP_PROJECT_ID }}
        service_account_key: ${{ secrets.GCP_SA_KEY }}
        export_default_credentials: true

    - name: Deploy to Cloud Run
      run: |
        gcloud run deploy fastapi-service \
          --source . \
          --platform managed \
          --region us-central1 \
          --allow-unauthenticated
```

---

## Step 7: Configure GitHub Secrets

In your GitHub repo → **Settings → Secrets and Variables → Actions**:

- `GCP_PROJECT_ID` → your GCP project ID
- `GCP_SA_KEY` → JSON key of a service account with **Cloud Run Admin** + **Storage Admin** roles

---

## Step 8: Test CI/CD Pipeline

Commit and push code:

```bash
git add .
git commit -m "Deploy FastAPI to Cloud Run"
git push origin main
```

GitHub Actions runs automatically:

- Checks out code
- Authenticates with GCP
- Deploys to Cloud Run

Each new push to `main` redeploys the app automatically.

---

## Verification Checklist

- [ ] FastAPI app runs locally on port 8080.
- [ ] Service deployed successfully to Cloud Run.
- [ ] GitHub Actions workflow triggers on push.
- [ ] CI/CD redeploys app automatically.

---

## Summary

In this lab, you:

- Built a FastAPI app.
- Containerized it with Docker.
- Deployed it to Cloud Run with `gcloud run deploy`.
- Automated redeployment via GitHub Actions CI/CD.

This workflow is now fully cloud-native: **write code → push to GitHub → app redeploys automatically.**
