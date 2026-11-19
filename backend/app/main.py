"""Main FastAPI application entry point for FinSight AI."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import (
    auth,
    transactions,
    ml,
    analytics,
    budgets,
    goals,
    insights,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan event handler to initialize database schema."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="FinSight AI API",
    description="AI-Powered Personal Finance Management System API",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(ml.router)
app.include_router(analytics.router)
app.include_router(budgets.router)
app.include_router(goals.router)
app.include_router(insights.router)

# Mount frontend production build if available
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))

if os.path.exists(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        # Ignore API routes
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            return None
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    @app.get("/", tags=["Health"])
    def root():
        """Root endpoint verifying API availability."""
        return {
            "name": "FinSight AI API",
            "status": "online",
            "documentation": "/docs",
            "version": "1.0.0",
        }
