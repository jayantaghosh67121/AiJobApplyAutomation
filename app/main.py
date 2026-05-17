"""FastAPI application factory and main entry point"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db, close_db
from app.api.users import router as users_router

# Import routers here (will be created in Phase 1)
# from app.api import jobs, applications, profiles


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    await init_db()
    yield
    # Shutdown
    print("Shutting down...")
    await close_db()


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title=settings.app_name,
        description="AI-powered job application automation system",
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add routes
    @app.get("/healthz", tags=["Health"])
    async def health_check():
        """Health check endpoint"""
        return JSONResponse(
            status_code=200,
            content={"status": "ok", "service": settings.app_name},
        )

    @app.get("/", tags=["Info"])
    async def root():
        """Root endpoint with API information"""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "openapi_schema": "/openapi.json",
        }

    # Include routers (Phase 1)
    app.include_router(users_router)
    # More routers to be added in Phase 2+
    # app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
    # app.include_router(applications.router, prefix="/api/applications", tags=["Applications"])

    return app


# Create app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        log_level=settings.log_level.lower(),
    )
