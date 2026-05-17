# Lab Manual: Deploying FastAPI to Azure Functions with CI/CD

## Objective

By the end of this lab, you will:

- Build a FastAPI app.
- Containerise it using the Azure Functions runtime image.
- Test it locally with Azure Functions Core Tools.
- Push the image to Azure Container Registry (ACR).
- Deploy to Azure Functions.
- Automate redeployment with a GitHub Actions CI/CD pipeline.

---

## Step 1: Create the FastAPI App

`main.py`

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello from FastAPI on Azure Functions!"}
```

Defines a simple `GET` endpoint at `/`.

---

## Step 2: Define Dependencies

`requirements.txt`

```
fastapi
uvicorn[standard]
azure-functions
```

Includes `azure-functions` so the runtime recognizes this as a Function app.

---

## Step 3: Write the Dockerfile

`Dockerfile`

```dockerfile
FROM mcr.microsoft.com/azure-functions/python:4-python3.10

# Azure Functions runtime expects this directory
ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

# Install dependencies
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

# Copy source code
COPY . /home/site/wwwroot
```

### Explanation

- Base image → Azure Functions runtime for Python 3.10.
- `AzureWebJobsScriptRoot` → tells Azure where to look for code.
- Code is copied into `/home/site/wwwroot`, the Functions root directory.

---

## Step 4: Test Locally with Azure Functions

Install **Azure Functions Core Tools**.

Run:

```bash
func start
```

Simulates Azure Functions locally. Visit: [http://localhost:7071](http://localhost:7071)

---

## Step 5: Push Image to Azure Container Registry (ACR)

Create ACR:

```bash
az acr create --resource-group myResourceGroup --name myacr --sku Basic
```

Login to ACR:

```bash
az acr login --name myacr
```

Build and Push:

```bash
docker build -t myacr.azurecr.io/fastapi-function:latest .
docker push myacr.azurecr.io/fastapi-function:latest
```

The image is now stored in ACR.

---

## Step 6: Deploy Azure Function App

```bash
az functionapp create \
  --resource-group myResourceGroup \
  --name fastapi-function-app \
  --storage-account mystorageaccount \
  --plan myAppServicePlan \
  --deployment-container-image-name myacr.azurecr.io/fastapi-function:latest
```

Function App now runs using the container image from ACR.

---

## Step 7: GitHub Actions CI/CD Pipeline

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Azure Functions

on:
  push:
    branches: ["main"]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Log in to Azure
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}

    - name: Log in to ACR
      run: az acr login --name myacr

    - name: Build and Push to ACR
      run: |
        docker build -t myacr.azurecr.io/fastapi-function:latest .
        docker push myacr.azurecr.io/fastapi-function:latest

    - name: Update Azure Function
      run: |
        az functionapp update \
          --resource-group myResourceGroup \
          --name fastapi-function-app \
          --set siteConfig.linuxFxVersion="DOCKER|myacr.azurecr.io/fastapi-function:latest"
```

---

## Step 8: Configure GitHub Secrets

In your repo → **Settings → Secrets and Variables → Actions**:

- `AZURE_CREDENTIALS` → JSON output of a service principal created with:

```bash
az ad sp create-for-rbac \
  --name fastapi-function-sp \
  --role contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/myResourceGroup \
  --sdk-auth
```

Copy the JSON output and store it in GitHub Secrets.

---

## Verification Checklist

- [ ] FastAPI app runs locally with `func start`.
- [ ] Image pushed to ACR.
- [ ] Function App created with `az functionapp create`.
- [ ] GitHub Actions pipeline runs on push.
- [ ] Function App updates automatically.

---

## Summary

In this lab, you:

- Built a FastAPI app.
- Containerised it with the Azure Functions runtime image.
- Ran it locally with Azure Functions Core Tools.
- Pushed the image to ACR.
- Deployed to Azure Functions.
- Automated redeployment with a GitHub Actions pipeline.

You now have a **serverless FastAPI API running on Azure Functions** with full CI/CD.
