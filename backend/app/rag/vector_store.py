"""Gestión de ChromaDB para RAG"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path
from typing import List, Optional, Dict
import os

from ..config import settings
from .embeddings import EmbeddingFactory

class VectorStore:
    """Gestión de ChromaDB para conocimiento verificado"""
    
    def __init__(self):
        self.persist_directory = Path(settings.chroma_persist_dir)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        print(f"📚 Inicializando ChromaDB: {self.persist_directory}")
        
        # Crear embeddings
        try:
            self.embeddings = EmbeddingFactory.create_embeddings()
        except Exception as e:
            print(f"⚠️ Error creando embeddings: {e}")
            print("   Usando embeddings por defecto...")
            self.embeddings = EmbeddingFactory.create_embeddings(
                provider='sentence-transformers'
            )
        
        # Inicializar ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Crear/obtener colección
        try:
            self.collection = self.client.get_collection(
                name=settings.chroma_collection_name
            )
            print(f"✅ Colección '{settings.chroma_collection_name}' cargada")
        except:
            self.collection = self.client.create_collection(
                name=settings.chroma_collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"✅ Colección '{settings.chroma_collection_name}' creada")
            self._populate_initial_knowledge()
        
        # Vector store de LangChain
        self.vector_store = Chroma(
            client=self.client,
            collection_name=settings.chroma_collection_name,
            embedding_function=self.embeddings
        )
    
    def _populate_initial_knowledge(self):
        """Popula la base de conocimiento inicial con información verificada"""
        print("📝 Poblando base de conocimiento inicial...")
        
        initial_documents = [
            {
                "content": """
                Índice de Masa Corporal (IMC): El IMC es una medida que relaciona el peso y la altura de una persona.
                Se calcula dividiendo el peso en kilogramos por el cuadrado de la altura en metros.
                Rangos según la OMS: Bajo peso (<18.5), Normal (18.5-24.9), Sobrepeso (25-29.9), Obesidad (≥30).
                Es una herramienta de screening, no un diagnóstico definitivo de salud.
                """,
                "metadata": {"category": "metrics", "source": "OMS", "topic": "IMC"}
            },
            {
                "content": """
                Actividad física recomendada: La OMS recomienda 150-300 minutos de actividad aeróbica moderada
                o 75-150 minutos de actividad vigorosa por semana para adultos. Esto equivale a aproximadamente
                10,000 pasos diarios. El mínimo para obtener beneficios de salud es 7,000 pasos al día.
                """,
                "metadata": {"category": "exercise", "source": "OMS", "topic": "pasos"}
            },
            {
                "content": """
                Frecuencia cardíaca: La frecuencia cardíaca en reposo normal para adultos es de 60-100 latidos
                por minuto. Los atletas pueden tener frecuencias más bajas (40-60 bpm). La frecuencia cardíaca
                máxima se estima con la fórmula 220 - edad. Las zonas de entrenamiento son: 50-60% calentamiento,
                60-70% quema de grasa, 70-80% cardio, 80-90% alta intensidad, 90-100% máximo esfuerzo.
                """,
                "metadata": {"category": "health", "source": "ACSM", "topic": "frecuencia_cardiaca"}
            },
            {
                "content": """
                Sueño: Los adultos necesitan 7-9 horas de sueño por noche para una salud óptima. El sueño se
                divide en fases: sueño ligero (55%), sueño profundo (25%), REM (20%). El sueño profundo es
                crucial para la recuperación física, mientras que el REM es importante para la memoria y
                el aprendizaje. La falta crónica de sueño se asocia con obesidad, diabetes y problemas cardiovasculares.
                """,
                "metadata": {"category": "health", "source": "National Sleep Foundation", "topic": "sueno"}
            },
            {
                "content": """
                Nutrición y calorías: El gasto calórico total (TDEE) se calcula con la fórmula de Mifflin-St Jeor:
                Hombres: (10 × peso kg) + (6.25 × altura cm) - (5 × edad) + 5
                Mujeres: (10 × peso kg) + (6.25 × altura cm) - (5 × edad) - 161
                Este resultado se multiplica por un factor de actividad (1.2-1.9). Para perder peso de forma
                saludable, se recomienda un déficit de 500 kcal/día (0.5 kg/semana). Nunca bajar de 1200-1500 kcal/día.
                """,
                "metadata": {"category": "nutrition", "source": "NIH", "topic": "calorias"}
            },
            {
                "content": """
                Hidratación: Se recomienda consumir 2-3 litros de agua al día para adultos. Durante el ejercicio,
                agregar 500ml por hora de actividad. La deshidratación afecta el rendimiento físico y cognitivo.
                Señales de buena hidratación: orina clara o amarillo pálido. La sed no es un indicador confiable
                en personas mayores o durante ejercicio intenso.
                """,
                "metadata": {"category": "nutrition", "source": "European Hydration Institute", "topic": "hidratacion"}
            },
            {
                "content": """
                Entrenamiento de fuerza: Se recomienda al menos 2 sesiones por semana trabajando todos los grupos
                musculares principales. Beneficios: aumenta masa muscular, mejora metabolismo, fortalece huesos,
                previene lesiones. Para hipertrofia: 8-12 repeticiones, 3-4 series. Para fuerza: 4-6 repeticiones,
                4-5 series. Descanso entre series: 1-3 minutos.
                """,
                "metadata": {"category": "exercise", "source": "ACSM", "topic": "fuerza"}
            }
        ]
        
        texts = [doc["content"] for doc in initial_documents]
        metadatas = [doc["metadata"] for doc in initial_documents]
        
        self.add_documents(texts, metadatas)
        print(f"✅ {len(initial_documents)} documentos iniciales agregados")
    
    def add_documents(self, texts: List[str], metadatas: Optional[List[dict]] = None):
        """
        Añade documentos al vector store
        
        Args:
            texts: Lista de textos
            metadatas: Metadatos opcionales para cada texto
        """
        # Dividir textos en chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        chunks = []
        chunk_metadatas = []
        
        for i, text in enumerate(texts):
            splits = text_splitter.split_text(text)
            chunks.extend(splits)
            
            # Añadir metadata
            base_metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
            chunk_metadatas.extend([
                {**base_metadata, "chunk_index": j} 
                for j in range(len(splits))
            ])
        
        # Añadir a ChromaDB
        try:
            self.vector_store.add_texts(
                texts=chunks,
                metadatas=chunk_metadatas
            )
            print(f"✅ {len(chunks)} chunks añadidos al vector store")
        except Exception as e:
            print(f"❌ Error añadiendo documentos: {e}")
    
    def similarity_search(
        self, 
        query: str, 
        k: int = 3,
        filter: Optional[dict] = None
    ) -> List[Dict]:
        """
        Búsqueda por similitud
        
        Args:
            query: Consulta
            k: Número de resultados
            filter: Filtros opcionales
            
        Returns:
            Lista de documentos relevantes
        """
        try:
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter
            )
            
            return [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score)
                }
                for doc, score in results
            ]
        except Exception as e:
            print(f"❌ Error en búsqueda: {e}")
            return []
    
    def get_retriever(self, k: int = 3):
        """Obtiene retriever de LangChain"""
        return self.vector_store.as_retriever(
            search_kwargs={"k": k}
        )
    
    def reset(self):
        """Limpia la colección"""
        try:
            self.client.delete_collection(settings.chroma_collection_name)
            self.collection = self.client.create_collection(
                name=settings.chroma_collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            self._populate_initial_knowledge()
            print("✅ Vector store reseteado")
        except Exception as e:
            print(f"❌ Error reseteando vector store: {e}")

# Instancia global
try:
    vector_store = VectorStore()
except Exception as e:
    print(f"⚠️ Error inicializando vector store: {e}")
    vector_store = None