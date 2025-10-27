import os
from openai import OpenAI
from mistralai import Mistral
from google import genai
import anthropic
from xai_sdk import Client
import json

STARTING_MODELS_OPENAI = [
    "gpt-5",
    "gpt-5-mini",
    "gpt-5-nano",
    "gpt-pro",
    "gpt-4.1",
    "grok-4",
    "deepseek-chat",
    "Llama-4-Maverick-17B-128E-Instruct-FP8",
    "Llama-4-Scout-17B-16E-Instruct-FP8",
]
STARTING_MODELS_GEMINI = ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite"]
STARTING_MODELS_XAI = [
    "grok-code-fast-1",
    "grok-4-fast-reasoning",
    "grok-4-fast-non-reasoning",
    "grok-4-0709",
    "grok-3-mini",
    "grok-3",
    "grok-2-image-1212",
]
STARTING_MODELS_ANTHROPIC = [
    "claude-opus-4-1-20250805",
    "claude-opus-4-1",
    "claude-opus-4-20250514",
    "claude-opus-4-0",
    "claude-sonnet-4-5-20250929",
    "claude-sonnet-4-5",
    "claude-sonnet-4-20250514",
    "claude-sonnet-4-0",
    "claude-haiku-4-5-20251001",
    "claude-haiku-4-5",
    "claude-3-7-sonnet-20250219",
    "claude-3-7-sonnet-latest",
    "claude-3-5-haiku-20241022",
    "claude-3-5-haiku-latest",
    "claude-3-5-sonnet-latest",
    "claude-3-opus-latest",
    "claude-3-haiku-20240307",
]
STARTING_MODELS_META = [
    "Llama-4-Maverick-17B-128E-Instruct-FP8",
    "Llama-4-Scout-17B-16E-Instruct-FP8",
    "Llama-3.3-70B-Instruct",
    "Llama-3.3-8B-Instruct",
]
STARTING_MODELS_MISTRALAI = ["mistral-medium-2508", "magistral-medium-2509"]


def list_models():
    client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    openai_models = [
        model.id
        for model in client_openai.models.list()
        if model.id not in STARTING_MODELS_OPENAI
    ] + STARTING_MODELS_OPENAI
    client_google = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    gemini_models = [
        model.name
        for model in client_google.models.list()
        if model.name not in STARTING_MODELS_GEMINI
    ] + STARTING_MODELS_GEMINI
    mistral_client = Mistral(api_key=os.getenv("MISTRALAI_API_KEY"))
    mistral_models = [
        model.id
        for model in dict(mistral_client.models.list())["data"]
        if model.id not in STARTING_MODELS_MISTRALAI
    ] + STARTING_MODELS_MISTRALAI
    anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    anthropic_models = [
        model.id
        for model in dict(anthropic_client.models.list())["data"]
        if model.id not in STARTING_MODELS_ANTHROPIC
    ] + STARTING_MODELS_ANTHROPIC
    xai_client = Client(api_key=os.getenv("XAI_API_KEY"))
    xai_models = [ # adding language models
        model.id
        for model in dict(xai_client.models.list_language_models())["data"]
        if model.id not in STARTING_MODELS_XAI
    ] + STARTING_MODELS_XAI
    xai_models = [ # adding embedded models
        model.id
        for model in dict(xai_client.models.list_embedding_models())["data"]
        if model.id not in STARTING_MODELS_XAI
    ] + STARTING_MODELS_XAI
    xai_models = [ # adding image generation models
        model.id
        for model in dict(xai_client.models.list_image_generation_models())["data"]
        if model.id not in STARTING_MODELS_XAI
    ] + STARTING_MODELS_XAI

    # Creiamo il dizionario modello → provider
    model_provider_dict = create_model_provider_dict(
        openai_models, gemini_models, mistral_models, anthropic_models, xai_models
    )

    save_model_provider_dict(model_provider_dict)
    return model_provider_dict

def create_model_provider_dict(openai_models, gemini_models, mistral_models, anthropic_models, xai_models):
    """
    Crea un dizionario dove le chiavi sono i nomi dei modelli e i valori sono i produttori corrispondenti.
    """
    model_to_provider = {}

    for model in openai_models:
        model_to_provider[model] = "openai"
    for model in gemini_models:
        model_to_provider[model] = "gemini"
    for model in mistral_models:
        model_to_provider[model] = "mistral"
    for model in anthropic_models:
        model_to_provider[model] = "anthropic"
    for model in xai_models:
        model_to_provider[model] = "xai"

    return model_to_provider

def save_model_provider_dict(model_provider_dict, filename="model_provider_dict.json"):

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(model_provider_dict, f, indent=4, ensure_ascii=False)
        print(f"Dizionario salvato correttamente in '{filename}'")
    except Exception as e:
        print(f"Errore durante il salvataggio del file JSON: {e}")

if __name__ == "__main__":
    list_models()
