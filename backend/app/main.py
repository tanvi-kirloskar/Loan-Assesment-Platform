from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.applications import router as applications_router
from app.routes.auth import router as auth_router
from app.routes.documents import router as documents_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(applications_router)
app.include_router(auth_router)
app.include_router(documents_router)