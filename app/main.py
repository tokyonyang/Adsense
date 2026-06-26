from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.routers import (
    dashboard,
    profile,
    keywords,
    issues,
    evidence,
    sns_trends,
    economic_events,
    content,
    publish,
    logs,
    support,
)

settings = get_settings()

app = FastAPI(
    title="AdSense SEO Dashboard API",
    version="0.1.0",
    description="AdSense SEO 자동화 대시보드 API",
)

origins = ["*"] if settings.cors_origins == "*" else [
    origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"ok": True, "service": "adsense-dashboard-api"}


app.include_router(dashboard.router)
app.include_router(profile.router)
app.include_router(keywords.router)
app.include_router(issues.router)
app.include_router(evidence.router)
app.include_router(sns_trends.router)
app.include_router(economic_events.router)
app.include_router(content.router)
app.include_router(publish.router)
app.include_router(logs.router)
app.include_router(support.router)
