from fastapi import FastAPI

app = FastAPI(title="Domain Copilot")


@app.get("/health")
def health():
    return {"status": "ok"}