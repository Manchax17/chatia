"""Factory para crear modelos de embeddings"""

from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.embeddings.base import Embeddings
from sentence_transformers import SentenceTransformer
from typing import List
import torch

from ..config import settings

class EmbeddingFactory:
    """Factory para crear embeddings"""
    
    @staticmethod
    def create_embeddings(
        provider: str = None, 
        model_name: str = None
    ) -> Embeddings:
        """
        Crea instancia de embeddings según proveedor
        
        Args:
            provider: 'openai', 'huggingface', 'sentence-transformers'
            model_name: Nombre del modelo específico
        """
        provider = provider or settings.embedding_provider
        
        print(f"🧠 Creando embeddings: {provider}")
        
        if provider == 'openai':
            return EmbeddingFactory._create_openai_embeddings(model_name)
        elif provider in ['huggingface', 'sentence-transformers']:
            return EmbeddingFactory._create_huggingface_embeddings(model_name)
        else:
            raise ValueError(f"Proveedor de embeddings no soportado: {provider}")
    
    @staticmethod
    def _create_openai_embeddings(model_name: str = None) -> OpenAIEmbeddings:
        """Crea embeddings de OpenAI"""
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY no configurada")
        
        return OpenAIEmbeddings(
            model=model_name or settings.openai_embedding_model,
            openai_api_key=settings.openai_api_key
        )
    
    @staticmethod
    def _create_huggingface_embeddings(model_name: str = None) -> HuggingFaceEmbeddings:
        """Crea embeddings de HuggingFace/Sentence-Transformers"""
        model_id = model_name or settings.embedding_model
        
        print(f"   Modelo: {model_id}")
        
        # Determinar dispositivo
        if settings.embedding_device == "auto":
            if torch.cuda.is_available():
                device = "cuda"
            elif torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"
        else:
            device = settings.embedding_device
        
        print(f"   Dispositivo: {device}")
        
        embeddings = HuggingFaceEmbeddings(
            model_name=model_id,
            model_kwargs={'device': device},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        print(f"✅ Embeddings cargados")
        
        return embeddings