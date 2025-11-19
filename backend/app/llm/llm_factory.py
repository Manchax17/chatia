"""Factory para crear instancias de LLM según proveedor"""

from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from langchain_community.llms import HuggingFacePipeline
from langchain.llms.base import LLM
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from typing import Literal, Optional, Any, List
import httpx
from groq import Groq

from ..config import settings


class GroqChat(BaseChatModel):
    """Wrapper para Groq compatible con LangChain"""
    
    # Definir campos de Pydantic correctamente
    model: str = "llama-3.3-70b-versatile"
    temperature: float = 0.3
    groq_api_key: str = ""
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, model: str, temperature: float = 0.3, groq_api_key: str = "", **kwargs):
        """Inicializa el modelo Groq"""
        super().__init__(
            model=model,
            temperature=temperature,
            groq_api_key=groq_api_key,
            **kwargs
        )
        # Cliente Groq (no es un campo de Pydantic)
        object.__setattr__(self, '_client', Groq(api_key=groq_api_key))
    
    @property
    def client(self):
        """Acceso al cliente Groq"""
        return self._client
    
    def _generate(self, messages: List[Any], stop: Optional[List[str]] = None, **kwargs) -> ChatResult:
        """Genera respuesta usando Groq"""
        groq_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                groq_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                groq_messages.append({"role": "assistant", "content": msg.content})
            elif isinstance(msg, SystemMessage):
                groq_messages.append({"role": "system", "content": msg.content})
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=groq_messages,
                temperature=self.temperature,
                max_tokens=kwargs.get('max_tokens', 2048),
                top_p=1.0
            )
            
            message = AIMessage(content=completion.choices[0].message.content)
            generation = ChatGeneration(message=message)
            
            return ChatResult(generations=[generation])
            
        except Exception as e:
            print(f"❌ Error en Groq: {e}")
            raise
    
    @property
    def _llm_type(self) -> str:
        return "groq-chat"


class LLMFactory:
    """Factory para crear LLMs"""
    
    @staticmethod
    def get_ollama_models() -> list:
        """Obtiene modelos reales disponibles en Ollama"""
        try:
            response = httpx.get(f"{settings.ollama_base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            return []
        except Exception as e:
            print(f"⚠️ Error obteniendo modelos de Ollama: {e}")
            return []
    
    @staticmethod
    def create_llm(
        provider: Optional[Literal['openai', 'ollama', 'huggingface', 'groq']] = None,
        model_name: Optional[str] = None,
        **kwargs
    ) -> LLM:
        """
        Crea instancia de LLM según proveedor
        
        Args:
            provider: 'openai', 'ollama', 'huggingface', 'groq'
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
        elif provider == 'groq':
            return LLMFactory._create_groq(model_name, **kwargs)
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
    def _create_groq(model_name: Optional[str] = None, **kwargs) -> GroqChat:
        """Crea LLM de Groq"""
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY no configurada en .env")
        
        model = model_name or settings.groq_model
        print(f"✅ Inicializando Groq con modelo: {model}")
        
        return GroqChat(
            model=model,
            temperature=kwargs.get('temperature', settings.groq_temperature),
            groq_api_key=settings.groq_api_key
        )
    
    @staticmethod
    def _create_ollama(model_name: Optional[str] = None, **kwargs) -> Ollama:
        """Crea LLM de Ollama"""
        try:
            response = httpx.get(f"{settings.ollama_base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                raise Exception("Ollama no responde")
        except Exception as e:
            raise ValueError(f"Ollama no está disponible en {settings.ollama_base_url}. Inicia Ollama primero. Error: {e}")
        
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
        
        model_kwargs = {"trust_remote_code": True}
        
        if device == "cuda" and settings.huggingface_load_in_8bit:
            model_kwargs["load_in_8bit"] = True
            model_kwargs["device_map"] = "auto"
        
        tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            token=settings.huggingface_token if settings.huggingface_token else None
        )
        
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            token=settings.huggingface_token if settings.huggingface_token else None,
            **model_kwargs
        )
        
        if not settings.huggingface_load_in_8bit:
            model = model.to(device)
        
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
        models = {
            "ollama": settings.available_ollama_models,
            "huggingface": settings.available_huggingface_models,
            "openai": settings.available_openai_models,
            "groq": settings.available_groq_models
        }
        
        ollama_models = LLMFactory.get_ollama_models()
        if ollama_models:
            models["ollama"] = ollama_models
            print(f"✅ Modelos de Ollama detectados: {len(ollama_models)}")
        
        return models
    
    @staticmethod
    def validate_provider(provider: str) -> bool:
        """Valida si el proveedor está disponible"""
        if provider == "ollama":
            try:
                response = httpx.get(f"{settings.ollama_base_url}/api/tags", timeout=5)
                return response.status_code == 200
            except:
                return False
        elif provider == "huggingface":
            return True
        elif provider == "openai":
            return bool(settings.openai_api_key)
        elif provider == "groq":
            return bool(settings.groq_api_key)
        return False