"""Agente conversacional con herramientas"""

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from typing import Optional, List, Dict
import traceback
from datetime import datetime

from .tools import get_tools
from .llm_factory import LLMFactory
from ..config import settings

class ChatFitAgent:
    """Agente conversacional para CHATFIT AI"""
    
    def __init__(
        self, 
        wearable_data: Optional[dict] = None,
        llm_provider: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        self.wearable_data = wearable_data
        self.llm_provider = llm_provider or settings.llm_provider
        self.model_name = model_name
        
        print(f"🤖 Inicializando ChatFit Agent")
        print(f"   Proveedor: {self.llm_provider}")
        if self.model_name:
            print(f"   Modelo: {self.model_name}")
        
        try:
            self.llm = LLMFactory.create_llm(
                provider=self.llm_provider,
                model_name=self.model_name
            )
            print(f"✅ LLM creado exitosamente")
            
            # Crear herramientas de forma segura
            try:
                self.tools = get_tools()
                print(f"✅ {len(self.tools)} herramientas creadas")
            except Exception as e:
                print(f"⚠️ Error creando herramientas: {e}")
                self.tools = []
            
            # Crear agente de forma segura
            try:
                self.agent_executor = self._create_agent()
                print(f"✅ Agente inicializado correctamente")
            except Exception as e:
                print(f"⚠️ Error creando agente: {e}")
                print(f"   Usando LLM directo como fallback")
                self.agent_executor = None
                
        except Exception as e:
            print(f"❌ Error inicializando agente: {e}")
            traceback.print_exc()
            self.llm = None
            self.tools = []
            self.agent_executor = None
    
    def _create_agent(self) -> AgentExecutor:
        """Crea el agente ReAct con herramientas"""
        
        # Template ReAct (compatible con todos los LLMs)
        template = """Responde las siguientes preguntas lo mejor que puedas. Tienes acceso a las siguientes herramientas:

{tools}

Usa el siguiente formato:

Question: la pregunta de entrada que debes responder
Thought: siempre debes pensar qué hacer
Action: la acción a tomar, debe ser una de [{tool_names}]
Action Input: la entrada a la acción
Observation: el resultado de la acción
... (este Thought/Action/Action Input/Observation puede repetirse N veces)
Thought: Ahora sé la respuesta final
Final Answer: la respuesta final a la pregunta de entrada original

CONTEXTO DEL USUARIO:
{full_context}

IMPORTANTE:
- USA las herramientas cuando sea apropiado
- Cita fuentes de información
- Sé empático y motivador
- Mantén respuestas concisas pero completas
- Personaliza con los datos del wearable cuando sea relevante

Question: {input}
{agent_scratchpad}"""

        wearable_context = self._format_wearable_context()
        user_profile_context = self._get_user_profile_context()
        full_context = f"{wearable_context}\n\n{user_profile_context}"
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["input", "agent_scratchpad"],
            partial_variables={
                "tools": "\n".join([
                    f"- {tool.name}: {tool.description}" 
                    for tool in self.tools
                ]) if self.tools else "No tools available",
                "tool_names": ", ".join([tool.name for tool in self.tools]) if self.tools else "",
                "full_context": full_context
            }
        )
        
        # Crear agente ReAct
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Executor con configuración segura
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=settings.debug,
            max_iterations=5,
            max_execution_time=60,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )
        
        return agent_executor
    
    def _format_wearable_context(self) -> str:
        """Formatea datos del wearable para el prompt"""
        if not self.wearable_data:
            return "⚠️ Datos del dispositivo wearable no disponibles"
        
        mock_note = " (DATOS DE PRUEBA)" if self.wearable_data.get("mock_data") else ""
        
        return f"""
📱 DISPOSITIVO XIAOMI{mock_note}:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👟 Pasos: {self.wearable_data.get('steps', 'N/A'):,}
❤️ FC: {self.wearable_data.get('heart_rate', 'N/A')} bpm
🔥 Calorías: {self.wearable_data.get('calories', 'N/A'):,} kcal
😴 Sueño: {self.wearable_data.get('sleep_hours', 'N/A')} hrs
📏 Distancia: {self.wearable_data.get('distance_km', 'N/A')} km
⏱️ Activo: {self.wearable_data.get('active_minutes', 'N/A')} min
🔋 Batería: {self.wearable_data.get('battery_level', 'N/A')}%
📱 Modelo: {self.wearable_data.get('device_model', 'Xiaomi Band')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    def _get_user_profile_context(self) -> str:
        """Formatea el perfil del usuario para el prompt"""
        from ..config import settings
        profile = settings.mock_user_profile
        
        return f"""
👤 PERFIL DEL USUARIO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎂 Edad: {profile.get('age', 'N/A')} años
⚖️ Peso: {profile.get('weight_kg', 'N/A')} kg  
📏 Altura: {profile.get('height_cm', 'N/A')} cm
🚻 Género: {profile.get('gender', 'N/A')}
🏃‍♂️ Nivel de actividad: {profile.get('activity_level', 'N/A')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    def chat(self, message: str, chat_history: Optional[List[dict]] = None) -> dict:
        """
        Procesa mensaje del usuario
        
        Args:
            message: Mensaje del usuario
            chat_history: Historial de conversación previo
            
        Returns:
            dict con respuesta, tools usadas y metadata
        """
        try:
            # ✅ AGREGAR: Información detallada del modelo
            model_info = {
                "provider": self.llm_provider,
                "model": self.model_name or getattr(settings, f"{self.llm_provider}_model", "unknown"),
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"🔧 Modelo activo: {model_info}")
            
            # Verificar si tenemos LLM disponible
            if not self.llm:
                return {
                    "response": "Lo siento, el sistema de IA no está disponible en este momento. Por favor verifica la configuración.",
                    "error": "LLM no disponible",
                    "success": False,
                    "model_info": model_info
                }
            
            # Construir input con historial si existe
            full_input = message
            if chat_history and len(chat_history) > 0:
                history_text = "\n".join([
                    f"{'Usuario' if msg['role'] == 'user' else 'Asistente'}: {msg['content']}"
                    for msg in chat_history[-6:]
                ])
                full_input = f"HISTORIAL RECIENTE:\n{history_text}\n\nPREGUNTA ACTUAL: {message}"
            
            # Si tenemos agente_executor, usarlo
            if self.agent_executor:
                print(f"💬 Procesando con agente: {message[:50]}...")
                response = self.agent_executor.invoke({"input": full_input})
                
                # Extraer tools usadas
                tools_used = []
                if response.get("intermediate_steps"):
                    for step in response["intermediate_steps"]:
                        try:
                            tool_action = step[0]
                            tools_used.append({
                                "tool": tool_action.tool,
                                "input": str(tool_action.tool_input)
                            })
                        except Exception as e:
                            print(f"⚠️ Error extrayendo tool info: {e}")
                
                return {
                    "response": response["output"],
                    "tools_used": tools_used,
                    "model_info": model_info,
                    "wearable_data_used": bool(self.wearable_data),
                    "success": True
                }
            else:
                # Fallback: usar LLM directamente sin agente
                print(f"💬 Procesando con LLM directo: {message[:50]}...")
                
                # Si hay datos del wearable, incluirlos en el mensaje
                context = self._format_wearable_context()
                full_input_with_context = f"{context}\n\nUsuario: {full_input}\nAsistente:"
                
                # Para LLM directo, usar el método invoke o generate
                try:
                    # Intentar con invoke
                    result = self.llm.invoke(full_input_with_context)
                    # Extraer el contenido del mensaje (puede ser AIMessage u otro tipo)
                    if hasattr(result, 'content'):
                        response_text = result.content
                    else:
                        response_text = str(result)
                except Exception as e:
                    print(f"⚠️ Error con invoke, intentando con generate: {e}")
                    try:
                        # Intentar con generate
                        result = self.llm.generate([full_input_with_context])
                        response_text = result.generations[0][0].text if result.generations else "No se pudo generar respuesta"
                    except Exception as e2:
                        print(f"❌ Error con generate: {e2}")
                        response_text = "Lo siento, no pude procesar tu mensaje en este momento."
                
                return {
                    "response": response_text,
                    "tools_used": [],
                    "model_info": model_info,
                    "wearable_data_used": bool(self.wearable_data),
                    "success": True
                }
                
        except Exception as e:
            print(f"❌ Error en agente: {e}")
            traceback.print_exc()
            
            return {
                "response": "Lo siento, hubo un error al procesar tu mensaje. Por favor intenta de nuevo o reformula tu pregunta.",
                "error": str(e),
                "success": False,
                "model_info": model_info
            }
    
    def update_wearable_data(self, new_data: dict):
        """Actualiza datos del wearable y recrea el agente"""
        self.wearable_data = new_data
        print("✅ Datos del wearable actualizados")