"""Main FastAPI application.

This module initializes the FastAPI application, configures middleware,
sets up logging, and includes all API routers.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .config import settings, get_settings
from .routers import threat_intel, iac_upload, swarm, archive, llm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Swarm TM API",
    description="Multi-agent threat modeling system using swarm intelligence",
    version="0.1.0"
)


@app.on_event("startup")
async def startup_validation():
    """
    Validate LLM configuration on application startup.

    Checks if the configured LLM provider (Bedrock, Anthropic, or Ollama)
    is properly configured with credentials and models. Logs warnings if
    configuration is incomplete or unreachable.
    """
    settings = get_settings()

    logger.info("=" * 60)
    logger.info("Swarm TM API Starting Up")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("=" * 60)

    # Debug: Environment loading
    logger.info(f"Current working directory: {os.getcwd()}")
    env_file_path = os.path.join(os.getcwd(), "..", ".env")
    logger.info(f"Looking for .env at: {os.path.abspath(env_file_path)}")
    logger.info(f".env exists: {os.path.exists(env_file_path)}")

    logger.info(f"LLM Provider: {settings.LLM_PROVIDER}")
    logger.info(f"Ollama Base URL: {settings.OLLAMA_BASE_URL}")
    logger.info(f"Ollama Model: {settings.OLLAMA_MODEL}")

    if settings.LLM_PROVIDER == "bedrock":
        if not settings.AWS_BEARER_TOKEN_BEDROCK:
            logger.error(
                "AWS_BEARER_TOKEN_BEDROCK not set. Set it in .env to use Bedrock. "
                "Example: AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key"
            )
        else:
            logger.info(
                f"AWS Bedrock configured with model: {settings.BEDROCK_MODEL} "
                f"in region: {settings.AWS_REGION}"
            )

    elif settings.LLM_PROVIDER == "anthropic":
        if not settings.ANTHROPIC_API_KEY:
            logger.error(
                "ANTHROPIC_API_KEY not set. Set it in .env to use Anthropic API. "
                "Example: ANTHROPIC_API_KEY=sk-ant-..."
            )
        else:
            logger.info(f"Anthropic API configured with model: {settings.ANTHROPIC_MODEL}")

    elif settings.LLM_PROVIDER == "ollama":
        logger.info(
            f"Ollama configured with model: {settings.OLLAMA_MODEL} "
            f"at {settings.OLLAMA_BASE_URL}"
        )

        # Check if Ollama server is reachable
        try:
            response = requests.get(
                f"{settings.OLLAMA_BASE_URL}/api/tags",
                timeout=5,
            )
            response.raise_for_status()
            ollama_data = response.json()

            # Check if configured model is available
            available_models = [model.get("name") for model in ollama_data.get("models", [])]

            if settings.OLLAMA_MODEL in available_models:
                logger.info(f"Ollama model '{settings.OLLAMA_MODEL}' is available")
            else:
                logger.warning(
                    f"Model '{settings.OLLAMA_MODEL}' not found in Ollama. "
                    f"Available models: {', '.join(available_models) if available_models else 'none'}. "
                    f"Pull it with: ollama pull {settings.OLLAMA_MODEL}"
                )

        except requests.exceptions.RequestException as e:
            logger.warning(
                f"Ollama not reachable at {settings.OLLAMA_BASE_URL}. "
                f"Make sure Ollama is running: ollama serve. Error: {e}"
            )

    else:
        logger.error(
            f"Invalid LLM_PROVIDER: {settings.LLM_PROVIDER}. "
            f"Must be 'bedrock', 'anthropic', or 'ollama'."
        )

    if not settings.is_llm_configured():
        logger.warning("LLM is not properly configured. Exploration endpoints will fail.")

    logger.info("=" * 60)

# Configure CORS
# Allow origins from environment variable for production, fallback to localhost for development
allowed_origins = settings.CORS_ORIGINS.split(",") if hasattr(settings, "CORS_ORIGINS") and settings.CORS_ORIGINS else ["http://localhost:5173", "http://localhost:3000"]

logger.info(f"CORS allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(threat_intel.router)
app.include_router(iac_upload.router)
app.include_router(swarm.router)
app.include_router(archive.router)
app.include_router(llm.router)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}


@app.get("/api/llm-status")
async def llm_status():
    """
    Get LLM configuration status.

    Returns information about the configured LLM provider and whether
    it's properly configured with credentials.
    """
    settings = get_settings()

    # Debug logging
    logger.info(f"[llm-status] LLM_PROVIDER: {settings.LLM_PROVIDER}")
    logger.info(f"[llm-status] OLLAMA_BASE_URL: {settings.OLLAMA_BASE_URL}")
    logger.info(f"[llm-status] OLLAMA_MODEL: {settings.OLLAMA_MODEL}")

    llm_config = settings.get_llm_config()

    response = {
        "provider": llm_config["provider"],
        "model": llm_config["model"],
        "configured": settings.is_llm_configured(),
    }

    # For Ollama, add additional status information
    if settings.LLM_PROVIDER == "ollama":
        response["base_url"] = settings.OLLAMA_BASE_URL

        # Check if Ollama server is reachable and model is available
        model_available = False
        try:
            ollama_response = requests.get(
                f"{settings.OLLAMA_BASE_URL}/api/tags",
                timeout=3,
            )
            ollama_response.raise_for_status()
            ollama_data = ollama_response.json()

            available_models = [model.get("name") for model in ollama_data.get("models", [])]
            model_available = settings.OLLAMA_MODEL in available_models

        except requests.exceptions.RequestException:
            pass

        response["model_available"] = model_available

    return response


# ============================================================================
# Frontend serving (must be LAST to avoid catching API routes)
# ============================================================================

# Mount static files for frontend (production deployment)
FRONTEND_BUILD_DIR = Path(__file__).parent.parent / "static"

# Log static directory status for debugging Zeabur deployment
logger.info(f"Checking frontend static directory at: {FRONTEND_BUILD_DIR}")
logger.info(f"Static directory exists: {FRONTEND_BUILD_DIR.exists()}")

if FRONTEND_BUILD_DIR.exists():
    logger.info(f"Mounting frontend static files from: {FRONTEND_BUILD_DIR}")
    try:
        static_contents = list(FRONTEND_BUILD_DIR.iterdir())
        logger.info(f"Static directory contents ({len(static_contents)} items): {[f.name for f in static_contents[:10]]}")
    except Exception as e:
        logger.error(f"Error listing static directory contents: {e}")

    # Mount assets directory for static files (CSS, JS, images)
    if (FRONTEND_BUILD_DIR / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(FRONTEND_BUILD_DIR / "assets")), name="static-assets")

    # Catch-all route for frontend SPA (must be last)
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve frontend SPA for all non-API routes."""
        # Serve index.html for all paths that don't start with 'api'
        if not full_path.startswith("api"):
            index_file = FRONTEND_BUILD_DIR / "index.html"
            if index_file.exists():
                return FileResponse(index_file)

        # If API route not found, return 404
        return {"detail": "Not found"}
else:
    logger.warning(f"Frontend build directory not found at {FRONTEND_BUILD_DIR}. Frontend will not be served.")
