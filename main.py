from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {
        "Message": "Hello from fastAPI on Cloud Run!",
        "Author": "GitHub Actions Workflow",
        "Version": "1.0.0"
    }