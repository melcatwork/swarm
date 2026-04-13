"""LLM model management endpoints.

This module provides REST API endpoints for:
- Listing available LLM models
- Checking model availability
- Getting current LLM configuration
"""

import logging
import requests
from typing import Dict, List, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/llm", tags=["LLM"])


class ModelInfo(BaseModel):
    """Information about an available model."""

    name: str
    provider: str
    available: bool
    is_default: bool
    display_name: str
    description: str | None = None


class AvailableModelsResponse(BaseModel):
    """Response with available models."""

    current_provider: str
    current_model: str
    models: List[ModelInfo]


@router.get("/models", response_model=AvailableModelsResponse)
async def get_available_models():
    """
    Get all available LLM models from .env configuration.

    Returns models grouped by provider (ollama, bedrock, anthropic).
    Includes availability status by checking if the model is actually accessible.

    Returns:
        AvailableModelsResponse with list of available models
    """
    settings = get_settings()

    # Get models from .env file
    models_by_provider = settings.get_available_models()

    # Flatten to list with display names
    all_models = []

    # Process Ollama models
    if settings.LLM_PROVIDER == "ollama":
        # Check which Ollama models are actually available
        available_ollama_models = []
        try:
            response = requests.get(
                f"{settings.OLLAMA_BASE_URL}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                ollama_data = response.json()
                available_ollama_models = [
                    model.get("name") for model in ollama_data.get("models", [])
                ]
                logger.info(f"Found {len(available_ollama_models)} Ollama models")
        except Exception as e:
            logger.warning(f"Could not fetch Ollama models: {e}")

        for model in models_by_provider.get("ollama", []):
            # Check if model is actually pulled in Ollama
            is_available = model["name"] in available_ollama_models

            all_models.append(ModelInfo(
                name=model["name"],
                provider="ollama",
                available=is_available,
                is_default=model["is_default"],
                display_name=f"{model['name']} (Ollama)",
                description="Local Ollama model" if is_available else "Not pulled - run: ollama pull " + model["name"]
            ))

    # Process Bedrock models
    for model in models_by_provider.get("bedrock", []):
        all_models.append(ModelInfo(
            name=model["name"],
            provider="bedrock",
            available=model["available"],
            is_default=model["is_default"],
            display_name=f"{model['name'].split('/')[-1]} (AWS Bedrock)",
            description="AWS Bedrock model" if model["available"] else "Credentials not configured"
        ))

    # Process Anthropic models
    for model in models_by_provider.get("anthropic", []):
        all_models.append(ModelInfo(
            name=model["name"],
            provider="anthropic",
            available=model["available"],
            is_default=model["is_default"],
            display_name=f"{model['name']} (Anthropic)",
            description="Anthropic API model" if model["available"] else "API key not configured"
        ))

    # Sort: available first, then by provider, then by name
    all_models.sort(key=lambda m: (not m.available, m.provider, m.name))

    return AvailableModelsResponse(
        current_provider=settings.LLM_PROVIDER,
        current_model=settings.OLLAMA_MODEL if settings.LLM_PROVIDER == "ollama"
                      else settings.BEDROCK_MODEL if settings.LLM_PROVIDER == "bedrock"
                      else settings.ANTHROPIC_MODEL,
        models=all_models
    )


@router.get("/status")
async def get_llm_status():
    """
    Get current LLM configuration and status.

    Returns:
        Current LLM provider, model, and availability status
    """
    settings = get_settings()

    status = {
        "provider": settings.LLM_PROVIDER,
        "configured": settings.is_llm_configured(),
        "temperature": settings.LLM_TEMPERATURE,
        "max_tokens": settings.LLM_MAX_TOKENS,
    }

    if settings.LLM_PROVIDER == "ollama":
        status["model"] = settings.OLLAMA_MODEL
        status["base_url"] = settings.OLLAMA_BASE_URL

        # Check Ollama availability
        try:
            response = requests.get(
                f"{settings.OLLAMA_BASE_URL}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                ollama_data = response.json()
                available_models = [model.get("name") for model in ollama_data.get("models", [])]
                status["ollama_reachable"] = True
                status["model_available"] = settings.OLLAMA_MODEL in available_models
                status["available_models_count"] = len(available_models)
            else:
                status["ollama_reachable"] = False
                status["model_available"] = False
        except Exception as e:
            status["ollama_reachable"] = False
            status["model_available"] = False
            status["error"] = str(e)

    elif settings.LLM_PROVIDER == "bedrock":
        status["model"] = settings.BEDROCK_MODEL
        status["region"] = settings.AWS_REGION_NAME

    elif settings.LLM_PROVIDER == "anthropic":
        status["model"] = settings.ANTHROPIC_MODEL

    return status
