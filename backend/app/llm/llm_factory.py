"""Factory para crear instancias de LLM según proveedor"""

from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from langchain_community.llms import HuggingFacePipeline
from langchain.llms.base import LLM
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from typing import Literal, Optional
import httpx

from ..config import settings

class LLMFactory:
    """Factory para crear LLMs"""
    
    @staticmethod
    def create_llm(
        provider: Optional[Literal['openai', 'ollama', 'huggingface']] = None,
        model_name: Optional[str] = None,
        **kwargs
    ) -> LLM:
        """
        Crea instancia de LLM según proveedor
        
        Args:
            provider: 'openai', 'ollama', 'huggingface'
            model_name: Nombre del modelo específico
            **kwargs: Parámetros adicionales
        """
        provider = provider or settings.llm_provider
        
        print(f"🤖 Creando LLM: {provider}")
        
        if provider == 'openai':
            return LLMFactory._create_openai(model_name, **kwargs)
        elif provider == 'ollama':
            return LLMFactory._create_ollama(model_name, **kwargs)
        elif provider == 'huggingface':
            return LLMFactory._create_huggingface(model_name, **kwargs)
        else:
            raise ValueError(f"Proveedor no soportado: {provider}")
    
    @staticmethod
    def _create_openai(model_name: Optional[str] = None, **kwargs) -> ChatOpenAI:
        """Crea LLM de OpenAI"""
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY no configurada")
        
        return ChatOpenAI(
            model=model_name or settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=kwargs.get('temperature', settings.openai_temperature),
            streaming=True
        )
    
    @staticmethod
    def _create_ollama(model_name: Optional[str] = None, **kwargs) -> Ollama:
        """Crea LLM de Ollama"""
        # Verificar que Ollama esté corriendo
        try:
            response = httpx.get(f"{settings.ollama_base_url}/api/tags", timeout=2)
            if response.status_code != 200:
                raise Exception("Ollama no responde")
        except Exception as e:
            raise ValueError(f"Ollama no está disponible en {settings.ollama_base_url}. Error: {e}")
        
        return Ollama(
            model=model_name or settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=kwargs.get('temperature', settings.ollama_temperature),
            num_ctx=settings.ollama_num_ctx
        )
    
    @staticmethod
    def _create_huggingface(model_name: Optional[str] = None, **kwargs) -> HuggingFacePipeline:
        """Crea LLM de HuggingFace local"""
        model_id = model_name or settings.huggingface_model
        
        print(f"🔄 Cargando modelo HuggingFace: {model_id}")
        print(f"   Dispositivo: {settings.huggingface_device}")
        
        # Determinar dispositivo
        if settings.huggingface_device == "auto":
            if torch.cuda.is_available():
                device = "cuda"
            elif torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"
        else:
            device = settings.huggingface_device
        
        print(f"   Usando: {device}")
        
        # Configuración de carga
        model_kwargs = {"trust_remote_code": True}
        
        if device == "cuda" and settings.huggingface_load_in_8bit:
            model_kwargs["load_in_8bit"] = True
            model_kwargs["device_map"] = "auto"
        
        # Cargar tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            token=settings.huggingface_token if settings.huggingface_token else None
        )
        
        # Cargar modelo
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            token=settings.huggingface_token if settings.huggingface_token else None,
            **model_kwargs
        )
        
        if not settings.huggingface_load_in_8bit:
            model = model.to(device)
        
        # Crear pipeline
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_length=settings.huggingface_max_length,
            temperature=kwargs.get('temperature', settings.huggingface_temperature),
            top_p=0.95,
            repetition_penalty=1.15
        )
        
        print(f"✅ Modelo cargado")
        
        return HuggingFacePipeline(pipeline=pipe)
    
    @staticmethod
    def get_available_models() -> dict:
        """Retorna modelos disponibles por proveedor"""
        return {
            "ollama": settings.available_ollama_models,
            "huggingface": settings.available_huggingface_models,
            "openai": settings.available_openai_models
        }
    
    @staticmethod
    def validate_provider(provider: str) -> bool:
        """Valida si el proveedor está disponible"""
        if provider == "ollama":
            try:
                response = httpx.get(f"{settings.ollama_base_url}/api/tags", timeout=2)
                return response.status_code == 200
            except:
                return False
        elif provider == "huggingface":
            return True  # Siempre disponible si hay espacio en disco
        elif provider == "openai":
            return bool(settings.openai_api_key)
        return False