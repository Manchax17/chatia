from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Literal, List

class Settings(BaseSettings):
    """Configuración centralizada de la aplicación"""
    
    # ============================================
    # API CONFIG
    # ============================================
    api_title: str = "CHATFIT AI API"
    api_version: str = "2.0.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    # ============================================
    # LLM PROVIDER
    # ============================================
    llm_provider: Literal['openai', 'ollama', 'huggingface', 'groq'] = 'ollama'
    
    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo-preview"
    openai_temperature: float = 0.3
    
    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    ollama_temperature: float = 0.3
    ollama_num_ctx: int = 4096
    
    # HuggingFace
    huggingface_model: str = "meta-llama/Llama-2-7b-chat-hf"
    huggingface_token: str = ""
    huggingface_device: str = "auto"
    huggingface_load_in_8bit: bool = True
    huggingface_temperature: float = 0.3
    huggingface_max_length: int = 2048
    
    # Groq
    groq_api_key: str = ""
    groq_model: str = "llama3-70b-8192"
    groq_temperature: float = 0.3

    # ============================================
    # EMBEDDINGS
    # ============================================
    embedding_provider: Literal['openai', 'huggingface', 'sentence-transformers'] = 'sentence-transformers'
    openai_embedding_model: str = "text-embedding-3-small"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_device: str = "auto"
    
    # ============================================
    # CHROMADB
    # ============================================
    chroma_persist_dir: str = "./data/chroma"
    chroma_collection_name: str = "fitness_knowledge"
    
    # ============================================
    # XIAOMI WEARABLE
    # ============================================
    xiaomi_connection_method: Literal['mi_fitness', 'bluetooth', 'mock'] = 'mock'
    
    # Mi Fitness (Xiaomi Health)
    mi_fitness_email: str = ""
    mi_fitness_password: str = ""
    mi_fitness_region: str = "us"
    mi_fitness_device_id: str = ""
    
    # Bluetooth
    xiaomi_mac_address: str = ""
    bluetooth_enabled: bool = False
    
    # Mock (desarrollo)
    use_mock_wearable: bool = True
    mock_user_profile: dict = {
        "age": 25,
        "weight_kg": 70,
        "height_cm": 175,
        "gender": "male",
        "activity_level": "moderado"
    }
    
    # Cache
    wearable_cache_ttl: int = 300  # 5 minutos
    
    # ============================================
    # MODELOS DISPONIBLES
    # ============================================
    available_ollama_models: List[str] = []  # ← Déjalo vacío para obtener dinámicamente desde Ollama
    
    available_huggingface_models: List[str] = []
    
    available_openai_models: List[str] = [
        "gpt-4-turbo-preview",
        "gpt-4",
        "gpt-3.5-turbo"
    ]

    available_groq_models: List[str] = [
    "llama3-8b-8192",
    "llama3-70b-8192",
    "mixtral-8x7b-32768",
    "gemma-7b-it",
    "llama-3.3-70b-versatile"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()