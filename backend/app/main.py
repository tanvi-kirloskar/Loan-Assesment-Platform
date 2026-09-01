from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.applications import router as applications_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(applications_router)