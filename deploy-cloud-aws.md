# Lab Manual: Deploying FastAPI to AWS Lambda with ECR + GitHub Actions CI/CD

## Objective

By the end of this lab, you will:

- Build a FastAPI app compatible with AWS Lambda.
- Containerise it using AWS's Lambda base image.
- Test it locally with Docker.
- Push the image to Amazon ECR.
- Deploy it as an AWS Lambda function.
- Set up a CI/CD pipeline with GitHub Actions for automatic redeploys.

---

## Step 1: Build a Simple FastAPI App

Create `main.py`:

```python
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello from FastAPI on AWS Lambda!"}

# Adapter for Lambda
handler = Mangum(app)
```

Mangum adapts FastAPI → AWS Lambda + API Gateway.

---

## Step 2: Define Dependencies

Create `requirements.txt`:

```
fastapi
uvicorn[standard]
mangum
```

`mangum` is key for Lambda compatibility.

---

## Step 3: Write the Dockerfile

Create `Dockerfile`:

```dockerfile
FROM public.ecr.aws/lambda/python:3.10

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY main.py .

# Define Lambda entrypoint (filename.handler)
CMD ["main.handler"]
```

### Explanation

- Base image → `public.ecr.aws/lambda/python:3.10` (official AWS Lambda runtime).
- `CMD ["main.handler"]` → tells Lambda to start with `handler` inside `main.py`.

---

## Step 4: Build and Test Locally

```bash
# Build image
docker build -t fastapi-lambda .

# Run locally (map host:9000 → container:8080)
docker run -p 9000:8080 fastapi-lambda
```

Test locally (Lambda's event API):

```bash
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
```

You should see:

```json
{"message": "Hello from FastAPI on AWS Lambda!"}
```

---

## Step 5: Push Image to Amazon ECR

Create repository:

```bash
aws ecr create-repository --repository-name fastapi-lambda
```

Authenticate Docker with ECR:

```bash
aws ecr get-login-password --region us-east-1 \
| docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com
```

Tag and push image:

```bash
docker tag fastapi-lambda:latest <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/fastapi-lambda:latest
docker push <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/fastapi-lambda:latest
```

---

## Step 6: Deploy to AWS Lambda

```bash
aws lambda create-function \
  --function-name fastapi-lambda-func \
  --package-type Image \
  --code ImageUri=<AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/fastapi-lambda:latest \
  --role arn:aws:iam::<AWS_ACCOUNT_ID>:role/<LAMBDA_EXECUTION_ROLE>
```

Replace `<LAMBDA_EXECUTION_ROLE>` with the ARN of a role with **AWSLambdaBasicExecutionRole** policy.

---

## Step 7: Set Up GitHub Actions for CI/CD

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to AWS Lambda

on:
  push:
    branches: ["main"]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1

    - name: Log in to Amazon ECR
      run: |
        aws ecr get-login-password --region us-east-1 \
        | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

    - name: Build and push to ECR
      run: |
        docker build -t fastapi-lambda .
        docker tag fastapi-lambda:latest <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/fastapi-lambda:latest
        docker push <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/fastapi-lambda:latest

    - name: Update Lambda
      run: |
        aws lambda update-function-code \
          --function-name fastapi-lambda-func \
          --image-uri <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/fastapi-lambda:latest
```

---

## Step 8: Configure GitHub Secrets

In your repo → **Settings → Secrets and Variables → Actions**:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

These must belong to an IAM user with **ECR + Lambda permissions**.

---

## Verification Checklist

- [ ] FastAPI app works locally inside Docker.
- [ ] Image pushed successfully to ECR.
- [ ] Lambda function created and returns JSON.
- [ ] GitHub Actions pipeline runs on push.
- [ ] Lambda redeploys automatically when pushing new code.

---

## Summary

In this lab, you:

- Built a FastAPI app adapted for AWS Lambda with Mangum.
- Containerised it using AWS's Lambda Python base image.
- Tested locally via Docker.
- Pushed the image to Amazon ECR.
- Deployed a containerised Lambda function.
- Automated redeployment with a GitHub Actions CI/CD pipeline.

You now have a **serverless FastAPI API on AWS** with automated deployments.
