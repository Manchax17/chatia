"""
Script para probar el backend completo sin frontend
Ejecutar: python tests/test_backend.py
"""

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name: str):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}TEST: {name}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

def print_success(message: str):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message: str):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message: str):
    print(f"{Colors.YELLOW}ℹ️  {message}{Colors.END}")

async def test_root():
    """Test del endpoint raíz"""
    print_test("Endpoint Raíz")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/")
            data = response.json()
            
            if response.status_code == 200:
                print_success("Endpoint raíz respondiendo")
                print_info(f"Versión: {data.get('version')}")
                print_info(f"LLM Provider: {data['features']['llm_provider']}")
                print_info(f"Wearable: {data['features']['wearable_connection']}")
            else:
                print_error(f"Status code: {response.status_code}")
                
        except Exception as e:
            print_error(f"Error: {e}")

async def test_health():
    """Test del health check"""
    print_test("Health Check")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            data = response.json()
            
            if response.status_code == 200:
                print_success("Health check OK")
                
                # Verificar componentes
                components = data.get('components', {})
                for name, info in components.items():
                    if isinstance(info, dict):
                        status = info.get('status') or ('disponible' if info.get('available') else 'no disponible')
                        print_info(f"{name}: {status}")
            else:
                print_error(f"Status code: {response.status_code}")
                
        except Exception as e:
            print_error(f"Error: {e}")

async def test_wearable_data():
    """Test de datos del wearable"""
    print_test("Datos del Wearable")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/api/v1/wearable/latest")
            data = response.json()
            
            if response.status_code == 200 and data.get('success'):
                print_success("Datos del wearable obtenidos")
                wearable = data['data']
                
                print_info(f"Pasos: {wearable.get('steps', 'N/A'):,}")
                print_info(f"Calorías: {wearable.get('calories', 'N/A'):,}")
                print_info(f"FC: {wearable.get('heart_rate', 'N/A')} bpm")
                print_info(f"Sueño: {wearable.get('sleep_hours', 'N/A')} hrs")
                print_info(f"Dispositivo: {wearable.get('device_model', 'N/A')}")
                
                if wearable.get('mock_data'):
                    print_info("⚠️  Usando datos MOCK (de prueba)")
            else:
                print_error(f"Error obteniendo datos: {data}")
                
        except Exception as e:
            print_error(f"Error: {e}")

async def test_models_list():
    """Test de lista de modelos"""
    print_test("Lista de Modelos Disponibles")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/api/v1/chat/models")
            data = response.json()
            
            if response.status_code == 200:
                print_success("Modelos listados")
                
                for provider_info in data:
                    status = "✅" if provider_info['available'] else "❌"
                    print_info(f"\n{status} {provider_info['provider'].upper()}")
                    print_info(f"  Modelo actual: {provider_info['current_model']}")
                    print_info(f"  Disponibles: {len(provider_info['models'])} modelos")
            else:
                print_error(f"Error: {response.status_code}")
                
        except Exception as e:
            print_error(f"Error: {e}")

async def test_chat_simple():
    """Test de chat simple"""
    print_test("Chat Simple (Sin Herramientas)")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            payload = {
                "message": "Hola, ¿cómo estás?",
                "chat_history": [],
                "include_wearable": True
            }
            
            response = await client.post(
                f"{BASE_URL}/api/v1/chat/",
                json=payload
            )
            data = response.json()
            
            if response.status_code == 200 and data.get('success'):
                print_success("Chat respondió correctamente")
                print_info(f"Respuesta: {data['response'][:150]}...")
                print_info(f"Modelo: {data['model_info']['provider']}")
                print_info(f"Tools usadas: {len(data['tools_used'])}")
            else:
                print_error(f"Error en chat: {data.get('error', 'Unknown')}")
                
        except Exception as e:
            print_error(f"Error: {e}")

async def test_chat_with_tools():
    """Test de chat usando herramientas"""
    print_test("Chat con Herramientas (IMC)")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            payload = {
                "message": "Calcula mi IMC. Peso 70 kg y mido 175 cm",
                "chat_history": [],
                "include_wearable": False
            }
            
            response = await client.post(
                f"{BASE_URL}/api/v1/chat/",
                json=payload
            )
            data = response.json()
            
            if response.status_code == 200 and data.get('success'):
                print_success("Chat con tools ejecutado")
                print_info(f"Respuesta: {data['response'][:200]}...")
                
                if data['tools_used']:
                    print_success(f"Tools usadas: {len(data['tools_used'])}")
                    for tool in data['tools_used']:
                        print_info(f"  - {tool['tool']}: {tool['input']}")
                else:
                    print_error("No se usaron herramientas")
            else:
                print_error(f"Error: {data.get('error', 'Unknown')}")
                
        except Exception as e:
            print_error(f"Error: {e}")

async def test_chat_with_wearable():
    """Test de chat usando datos del wearable"""
    print_test("Chat Analizando Datos del Wearable")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            payload = {
                "message": "¿Cómo voy con mis pasos hoy?",
                "chat_history": [],
                "include_wearable": True
            }
            
            response = await client.post(
                f"{BASE_URL}/api/v1/chat/",
                json=payload
            )
            data = response.json()
            
            if response.status_code == 200 and data.get('success'):
                print_success("Chat analizó datos del wearable")
                print_info(f"Respuesta: {data['response'][:250]}...")
                
                if data['wearable_data']:
                    print_success("Datos del wearable incluidos")
                    print_info(f"Pasos: {data['wearable_data']['steps']:,}")
                
                if data['tools_used']:
                    print_success("Tools usadas:")
                    for tool in data['tools_used']:
                        print_info(f"  - {tool['tool']}")
            else:
                print_error(f"Error: {data.get('error', 'Unknown')}")
                
        except Exception as e:
            print_error(f"Error: {e}")

async def test_conversation():
    """Test de conversación con historial"""
    print_test("Conversación con Historial")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Primer mensaje
            payload1 = {
                "message": "Tengo 25 años y peso 70kg",
                "chat_history": [],
                "include_wearable": False
            }
            
            response1 = await client.post(f"{BASE_URL}/api/v1/chat/", json=payload1)
            data1 = response1.json()
            
            if not data1.get('success'):
                print_error("Primer mensaje falló")
                return
            
            print_success("Primer mensaje OK")
            
            # Segundo mensaje con historial
            payload2 = {
                "message": "¿Cuál debería ser mi frecuencia cardíaca máxima?",
                "chat_history": [
                    {"role": "user", "content": payload1["message"]},
                    {"role": "assistant", "content": data1["response"]}
                ],
                "include_wearable": False
            }
            
            response2 = await client.post(f"{BASE_URL}/api/v1/chat/", json=payload2)
            data2 = response2.json()
            
            if data2.get('success'):
                print_success("Conversación con historial OK")
                print_info(f"Respuesta: {data2['response'][:200]}...")
                
                if data2['tools_used']:
                    print_success("Usó herramientas basándose en contexto previo")
            else:
                print_error("Segundo mensaje falló")
                
        except Exception as e:
            print_error(f"Error: {e}")

async def main():
    """Ejecuta todos los tests"""
    print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}🧪 CHATFIT AI - Test Suite{Colors.END}")
    print(f"{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.YELLOW}Servidor: {BASE_URL}{Colors.END}")
    print(f"{Colors.YELLOW}Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    print(f"{Colors.GREEN}{'='*60}{Colors.END}")
    
    tests = [
        ("Root Endpoint", test_root),
        ("Health Check", test_health),
        ("Wearable Data", test_wearable_data),
        ("Models List", test_models_list),
        ("Chat Simple", test_chat_simple),
        ("Chat with Tools", test_chat_with_tools),
        ("Chat with Wearable", test_chat_with_wearable),
        ("Conversation", test_conversation),
        ("RAG Reindex + Query", test_rag_reindex_and_query),
        ("Recall First Message", test_recall_first_message),
    ]

async def test_recall_first_message():
    """Test que verifica que se puede recordar el primer mensaje de una conversación"""
    print_test("Recall First Message")

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Crear chat
            create_resp = await client.post(f"{BASE_URL}/api/v1/chats/create", json={"title": "Test Recall"})
            create_data = create_resp.json()
            if not create_data.get('success'):
                print_error("No se pudo crear chat para el test")
                return
            chat_id = create_data['chat_id']

            # Enviar primer mensaje y asegurarse que se guarde
            payload1 = {"message": "Hola, ¿cómo estás?", "chat_history": [], "include_wearable": False}
            resp1 = await client.post(f"{BASE_URL}/api/v1/chat/?chat_id={chat_id}", json=payload1)
            data1 = resp1.json()
            if not data1.get('success'):
                print_error("Primer mensaje falló al guardarse")
                return

            # Preguntar por el primer mensaje
            payload2 = {"message": "¿Me puedes recordar mi primer mensaje?", "chat_history": [], "include_wearable": False}
            resp2 = await client.post(f"{BASE_URL}/api/v1/chat/?chat_id={chat_id}", json=payload2)
            data2 = resp2.json()

            if resp2.status_code == 200 and data2.get('success'):
                print_success("Respuesta de recuerdo recibida")
                if 'Hola' in data2.get('response', ''):
                    print_success("El primer mensaje fue recordado correctamente")
                else:
                    print_error("La respuesta no contenía el primer mensaje esperado")
            else:
                print_error(f"Error en la respuesta de recuerdo: {data2}")

            # ---------------------------
            # Ahora crear chats de ejemplo: uno de hace 7 días y otro de hace 1 día
            # ---------------------------
            resp_week = await client.post(f"{BASE_URL}/api/v1/chats/create_sample?days_ago=7&title=Chat+Hace+7+días")
            data_week = resp_week.json()
            if resp_week.status_code == 200 and data_week.get('success'):
                print_success("Chat de hace 7 días creado")
            else:
                print_error(f"No se pudo crear chat de hace 7 días: {data_week}")

            resp_yesterday = await client.post(f"{BASE_URL}/api/v1/chats/create_sample?days_ago=1&title=Chat+Ayer")
            data_y = resp_yesterday.json()
            if resp_yesterday.status_code == 200 and data_y.get('success'):
                print_success("Chat de ayer creado")
            else:
                print_error(f"No se pudo crear chat de ayer: {data_y}")

            # Crear chats adicionales: hace 7, 30 y 365 días con nuevo endpoint
            resp_samples = await client.post(f"{BASE_URL}/api/v1/chats/create_samples")
            samples_data = resp_samples.json()
            if resp_samples.status_code == 200 and samples_data.get('success'):
                print_success("Chats de ejemplo (7,30,365 días) creados")
            else:
                print_error(f"No se pudieron crear chats de ejemplo: {samples_data}")

            # Consultar listados y verificar que existe un chat en 'yesterday' y uno en 'this_week' y en 'this_month' y en 'older'
            # Enviamos zona horaria del cliente para reproducibilidad de la prueba
            list_resp = await client.get(f"{BASE_URL}/api/v1/chats?user_tz=UTC")
            list_data = list_resp.json()
            if list_resp.status_code == 200:
                y_count = len(list_data.get('yesterday', []))
                week_count = len(list_data.get('this_week', []))
                if y_count >= 1:
                    print_success("Se detectó al menos 1 chat en 'Ayer'")
                else:
                    print_error("No se detectaron chats en 'Ayer' cuando se esperaba al menos 1")
                if week_count >= 1:
                    print_success("Se detectó al menos 1 chat en 'Esta semana'")
                else:
                    print_error("No se detectaron chats en 'Esta semana' cuando se esperaba al menos 1")
            else:
                print_error("No se pudo listar chats para verificar agrupación")

        except Exception as e:
            print_error(f"Error: {e}")

async def test_rag_reindex_and_query():
    """Test de reindexado y recuperación RAG"""
    print_test("RAG Reindex + Query")
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # Reindexar toda la colección
            resp = await client.post(f"{BASE_URL}/api/v1/rag/reindex")
            data = resp.json()
            if resp.status_code == 200 and data.get('success'):
                print_success(f"Reindexado completado, docs añadidos: {data.get('added')}")
            else:
                print_error(f"Reindexado falló: {data}")
                return

            # Preguntar algo que debería estar en la base de conocimiento inicial
            payload = {"message": "¿Qué es el IMC?", "chat_history": [], "include_wearable": False}
            response = await client.post(f"{BASE_URL}/api/v1/chat/", json=payload)
            resdata = response.json()

            if response.status_code == 200 and resdata.get('success'):
                print_success("Chat respondió correctamente tras reindex")
                answer = resdata.get('response', '').lower()
                if 'imc' in answer or 'índice de masa corporal' in answer:
                    print_success("Respuesta contiene información relevante sobre IMC")
                else:
                    print_error("Respuesta no parece incluir información sobre IMC")
            else:
                print_error(f"Error en chat tras reindex: {resdata}")

        except Exception as e:
            print_error(f"Error: {e}")
    
    results = []
    
    for name, test_func in tests:
        try:
            await test_func()
            results.append((name, True))
        except Exception as e:
            print_error(f"Test '{name}' falló: {e}")
            results.append((name, False))
        
        await asyncio.sleep(1)  # Pausa entre tests
    
    # Resumen
    print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}📊 RESUMEN DE TESTS{Colors.END}")
    print(f"{Colors.GREEN}{'='*60}{Colors.END}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{Colors.GREEN}✅ PASS{Colors.END}" if result else f"{Colors.RED}❌ FAIL{Colors.END}"
        print(f"{status} - {name}")
    
    print(f"\n{Colors.YELLOW}Total: {passed}/{total} tests pasaron{Colors.END}")
    
    if passed == total:
        print(f"{Colors.GREEN}🎉 Todos los tests pasaron!{Colors.END}")
    else:
        print(f"{Colors.RED}⚠️  Algunos tests fallaron{Colors.END}")
    
    print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrumpidos por el usuario{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Error fatal: {e}{Colors.END}")