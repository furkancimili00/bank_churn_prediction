from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from api import ml_model
from api.limiter import limiter
from api.routers import predict_router, system_router
from core.config import get_settings
from core.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Eski test ve entegrasyon sozlesmeleri icin geriye uyumlu alanlar.
API_KEY = settings.api_key
model = ml_model.model
scaler = ml_model.scaler
expected_features = ml_model.expected_features

app = FastAPI(
    title="Banka Churn Tahmin API",
    description="Müşterilerin bankayı terk etme (churn) riskini hesaplayan XAI destekli kurumsal API",
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(system_router.router)
app.include_router(predict_router.router)
