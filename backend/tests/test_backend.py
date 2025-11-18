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
    ]
    
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