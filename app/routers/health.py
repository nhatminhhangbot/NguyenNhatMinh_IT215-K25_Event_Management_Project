from fastapi import APIRouter, Request
from datetime import datetime, timezone

router = APIRouter(tags=["Health Check"])


@router.get("/health")
def health_check(request: Request):
    return {
        "message": "API Quản lý Sự kiện đang chạy."
    }


@router.get("/")
def home():
    return {
        "status": "ok"
    }
