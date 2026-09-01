from fastapi import FastAPI

from app.routes.applications import router as applications_router


app = FastAPI()


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(applications_router)