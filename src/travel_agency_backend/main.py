from fastapi import FastAPI

app = FastAPI(
    title="Travel Agency Backend",
    version="1.0.0",
    description="Backend API for managing travel agency operations.",
)


@app.get("/health")
def health_check():
    return {"status": "OK"}
