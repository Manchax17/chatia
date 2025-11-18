# 🏋️ CHATFIT AI

Asistente personal de fitness con inteligencia artificial que integra dispositivos wearables Xiaomi para proporcionar recomendaciones personalizadas de salud y fitness.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![React](https://img.shields.io/badge/React-18.2-61dafb)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Características

- 🤖 **Múltiples modelos LLM**: OpenAI, Ollama (local), HuggingFace
- 📱 **Integración Xiaomi**: Mi Fitness API, Bluetooth, datos simulados
- 🧠 **RAG con ChromaDB**: Base de conocimiento verificada
- 🛠️ **Herramientas especializadas**: Cálculos de IMC, calorías, zonas cardíacas
- 💬 **Chat inteligente**: Conversación natural con contexto
- 📊 **Dashboard en tiempo real**: Visualización de métricas del wearable

## 🏗️ Arquitectura
```
chatfit-ai/
├── backend/          # FastAPI + Python
│   ├── app/
│   │   ├── llm/     # Sistema LLM con LangChain
│   │   ├── rag/     # Embeddings + ChromaDB
│   │   ├── iot/     # Clientes Xiaomi
│   │   └── api/     # Endpoints REST
│   └── requirements.txt
│
└── frontend/         # React + Tailwind CSS
    ├── src/
    │   ├── components/
    │   │   ├── chat/      # Interfaz de chat
    │   │   ├── wearable/  # Stats del dispositivo
    │   │   └── settings/  # Configuración
    │   └── services/      # API clients
    └── package.json
```

## 🚀 Instalación

### Requisitos Previos

- Python 3.9 - 3.11
- Node.js 18+
- (Opcional) Ollama instalado
- (Opcional) GPU para modelos HuggingFace

### Backend
```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install --upgrade pip
pip install torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Iniciar servidor
python -m uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env

# Iniciar servidor de desarrollo
npm run dev
```

## ⚙️ Configuración

### Backend (.env)
```env
# LLM Provider
LLM_PROVIDER=ollama  # ollama, huggingface, openai

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# OpenAI (opcional)
OPENAI_API_KEY=your-api-key

# Xiaomi Wearable
XIAOMI_CONNECTION_METHOD=mock  # mock, mi_fitness, bluetooth
USE_MOCK_WEARABLE=true
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

## 📖 Uso

1. **Iniciar Backend** (puerto 8000):
```bash
   cd backend
   source venv/bin/activate
   python -m uvicorn app.main:app --reload
```

2. **Iniciar Frontend** (puerto 5173):
```bash
   cd frontend
   npm run dev
```

3. **Abrir en navegador**: http://localhost:5173

4. **Ver documentación API**: http://localhost:8000/docs

## 🛠️ Tecnologías

### Backend
- **FastAPI** - Framework web
- **LangChain** - Orquestación LLM
- **ChromaDB** - Vector store
- **Sentence Transformers** - Embeddings
- **Ollama** - LLMs locales
- **PyTorch** - Deep learning

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Estilos
- **Axios** - HTTP client
- **Lucide React** - Iconos

## 📊 Modelos LLM Soportados

### Ollama (Local)
- llama3.1:8b
- mistral:7b
- phi3:latest
- gemma2:9b

### HuggingFace (Local)
- meta-llama/Llama-2-7b-chat-hf
- mistralai/Mistral-7B-Instruct-v0.2
- microsoft/phi-2

### OpenAI (API)
- gpt-4-turbo-preview
- gpt-4
- gpt-3.5-turbo

## 🔌 Integración Xiaomi

### Métodos Soportados

1. **Mock Data** (Desarrollo)
   - Datos simulados realistas
   - No requiere dispositivo físico

2. **Mi Fitness API**
   - Conexión con app Xiaomi Health
   - Requiere credenciales

3. **Bluetooth BLE** (Linux/RPi)
   - Conexión directa al dispositivo
   - Limitado a algunos datos

## 🧪 Testing
```bash
# Backend
cd backend
python tests/test_backend.py

# Frontend
cd frontend
npm run test
```

## 📝 Estructura de Datos

### Datos del Wearable
```json
{
  "steps": 8000,
  "calories": 1820,
  "heart_rate": 72,
  "sleep_hours": 7.5,
  "distance_km": 6.2,
  "active_minutes": 45,
  "battery_level": 85
}
```

### Respuesta del Chat
```json
{
  "response": "Has dado 8,000 pasos...",
  "tools_used": [
    {"tool": "analyze_steps", "input": "8000"}
  ],
  "model_info": {
    "provider": "ollama",
    "model": "llama3.1:8b"
  }
}
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## 📄 Licencia

MIT License - ver archivo [LICENSE](LICENSE) para detalles

## 👥 Autores

- **Tu Nombre** - *Trabajo inicial* - [TuUsuario](https://github.com/tuusuario)

## 🙏 Agradecimientos

- OpenAI por GPT
- Meta por Llama
- Anthropic por Claude
- Comunidad de LangChain
- Comunidad de FastAPI y React

## 📞 Contacto

- Email: tu@email.com
- GitHub: [@tuusuario](https://github.com/tuusuario)
- LinkedIn: [Tu Perfil](https://linkedin.com/in/tuperfil)

---

⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub
```

---

## 📝 PASO 5: Crear LICENSE (Opcional)

**`chatfit-ai/LICENSE`** (MIT License):
```
MIT License

Copyright (c) 2024 [Tu Nombre]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.