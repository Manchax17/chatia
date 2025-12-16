# 📚 Sistema de Historial de Chats y Memoria - Documentación

## 🎯 Descripción General

Se ha implementado un sistema completo de:
- **Registro persistente de chats** con almacenamiento en archivos JSON
- **Memoria conversacional** (global y por sesión)
- **Historial organizado** (Hoy, Esta semana, Este mes, Anterior)
- **Componente de interfaz** para visualizar y gestionar chats

## 🏗️ Arquitectura

### Backend

#### Base de Datos (`backend/app/database/chat_db.py`)

**Clases:**
- `Message`: Representa un mensaje individual
- `Chat`: Representa un chat completo con historial
- `ChatMemoryDB`: Gestor de persistencia de chats y memoria

**Características:**
- Almacenamiento en `backend/data/chats/` (archivos JSON)
- Métodos CRUD para chats
- Almacenamiento de memoria global y por sesión
- Snapshots de datos wearable al crear chat

**Archivos de almacenamiento:**
```
backend/data/chats/
├── chats.json       # Todos los chats con mensajes
└── memory.json      # Memoria global y por sesión
```

#### Endpoints (`backend/app/api/v1/chats.py`)

**Chats:**
```
POST   /chats/create              - Crear nuevo chat
GET    /chats                     - Listar chats agrupados por período
GET    /chats/{chat_id}           - Obtener chat completo
GET    /chats/{chat_id}/history   - Obtener historial de mensajes
POST   /chats/{chat_id}/message   - Añadir mensaje a chat
PUT    /chats/{chat_id}/title     - Actualizar título
PUT    /chats/{chat_id}/summary   - Actualizar resumen
DELETE /chats/{chat_id}           - Eliminar chat
```

**Memoria:**
```
POST   /memory/global/{key}            - Guardar en memoria global
GET    /memory/global/{key}            - Obtener de memoria global
POST   /memory/session/{session_id}/{key}    - Guardar en sesión
GET    /memory/session/{session_id}/{key}    - Obtener de sesión
GET    /memory/session/{session_id}          - Obtener toda sesión
```

#### Integración en Endpoint de Chat

El endpoint `POST /chat/` ahora acepta parámetro:
```
chat_id (query) - ID del chat donde guardar mensajes
```

Si se proporciona `chat_id`:
- Guarda automáticamente el mensaje del usuario
- Guarda la respuesta del asistente con metadatos
  - Modelo utilizado
  - Herramientas usadas
  - Timestamp

### Frontend

#### Contexto (`frontend/src/ChatsContext.jsx`)

Proporciona:
```javascript
const {
  currentChatId,              // ID del chat actual
  setCurrentChatId,           // Establecer chat actual
  chats,                      // {today, this_week, this_month, older}
  currentChat,                // Chat completo con mensajes
  loading,                    // Estado de carga
  error,                      // Errores
  loadChats,                  // Recargar lista
  createNewChat,              // Crear nuevo chat
  loadChat,                   // Cargar chat específico
  addMessage,                 // Añadir mensaje
  updateChatTitle,            // Cambiar título
  updateChatSummary,          // Cambiar resumen
  deleteChat                  // Eliminar chat
} = useChats();
```

#### Servicio (`frontend/src/services/chatsService.js`)

Proporciona métodos para:
- CRUD de chats
- Gestión de memoria global y por sesión
- Consultas de historial

#### Componente (`frontend/src/components/chat/ChatHistory.jsx`)

**Características:**
- Historial con secciones expandibles/colapsables
- Muestra: "Hoy", "Esta semana", "Este mes", "Anterior"
- Solo muestra secciones si hay chats
- Contador de mensajes por chat
- Botones para:
  - Crear nuevo chat (+)
  - Editar título (lápiz)
  - Eliminar chat (papelera)
- Preview de primer mensaje
- Selección visual de chat actual

## 📋 Uso

### Crear Nuevo Chat

```javascript
import { useChats } from './ChatsContext';

function MyComponent() {
  const { createNewChat } = useChats();
  
  const handleNewChat = async () => {
    const chatId = await createNewChat(
      "Mi primer chat",
      wearableData  // opcional
    );
  };
}
```

### Enviar Mensaje y Guardarlo

```javascript
async function sendMessage(userMessage) {
  const { currentChatId, addMessage } = useChats();
  
  // 1. Obtener respuesta del chat
  const response = await chatService.chat({
    message: userMessage,
    chat_id: currentChatId  // ← Esto lo guardará automáticamente
  });
  
  // O manualmente:
  await addMessage('user', userMessage);
  await addMessage('assistant', response.response, 'llama-3.3-70b-versatile', []);
}
```

### Usar Memoria Global

```javascript
import { chatsService } from './services/chatsService';

// Guardar preferencia
await chatsService.saveGlobalMemory('user_preferences', {
  theme: 'dark',
  notifications: true
});

// Obtener preferencia
const prefs = await chatsService.getGlobalMemory('user_preferences');
```

### Usar Memoria de Sesión

```javascript
const sessionId = 'user-123';

// Guardar dato de sesión
await chatsService.saveSessionMemory(sessionId, 'current_goal', {
  steps: 10000,
  date: '2025-12-15'
});

// Obtener dato
const goal = await chatsService.getSessionMemory(sessionId, 'current_goal');
```

## 📊 Estructura de Datos

### Chat JSON
```json
{
  "chat_id": "a1b2c3d4",
  "title": "Mi conversación sobre fitness",
  "created_at": "2025-12-15T10:30:00.000Z",
  "updated_at": "2025-12-15T11:45:00.000Z",
  "messages": [
    {
      "role": "user",
      "content": "¿Cuántos pasos debo dar?",
      "timestamp": "2025-12-15T10:30:10.000Z",
      "model_used": null,
      "tools_used": []
    },
    {
      "role": "assistant",
      "content": "Se recomienda 10000 pasos diarios...",
      "timestamp": "2025-12-15T10:30:20.000Z",
      "model_used": "llama-3.3-70b-versatile",
      "tools_used": []
    }
  ],
  "wearable_data_snapshot": {
    "steps": 8500,
    "calories": 423
  },
  "summary": null
}
```

### Memoria JSON
```json
{
  "global": {
    "user_preferences": {
      "theme": "dark",
      "language": "es"
    },
    "learned_habits": [
      "Ejercicio matutino",
      "Bebe agua"
    ]
  },
  "sessions": {
    "session-123": {
      "current_chat": "a1b2c3d4",
      "goals": {"steps": 10000},
      "last_sync": "2025-12-15T11:00:00Z"
    }
  }
}
```

## 🔄 Integración en Chat

Para integrar en la interfaz de chat:

```jsx
import { ChatsProvider, useChats } from './ChatsContext';
import ChatHistory from './components/chat/ChatHistory';

export default function App() {
  return (
    <ChatsProvider>
      <div className="flex gap-4">
        {/* Sidebar con historial */}
        <div className="w-64 h-screen">
          <ChatHistory />
        </div>
        
        {/* Chat principal */}
        <div className="flex-1">
          <ChatInterface />
        </div>
      </div>
    </ChatsProvider>
  );
}
```

## 🧠 Sistema de Memoria

### Memoria Global
- Datos compartidos entre todas las sesiones
- Ej: preferencias de usuario, hábitos aprendidos
- Persiste entre reinicios

### Memoria de Sesión
- Datos específicos de cada sesión de usuario
- Ej: chat actual, objetivos de hoy, estado temporal
- Se limpia con `clearSessionMemory()`

### Contexto del Chat
- El LLM usa memoria de sesión para recordar conversación
- Cada mensaje incluye: `chat_history` (últimos 6 mensajes)
- Snapshots de wearable al crear chat

## ⚙️ Configuración Recomendada

En tu `App.jsx`:

```jsx
import { ChatsProvider } from './ChatsContext';
import { WearableProvider } from './WearableContext';

export default function App() {
  return (
    <ChatsProvider>
      <WearableProvider>
        <div className="flex">
          {/* Historial */}
          <ChatHistory />
          {/* Chat */}
          <ChatInterface />
          {/* Wearable Stats */}
          <WearableStats />
        </div>
      </WearableProvider>
    </ChatsProvider>
  );
}
```

## 🚀 Próximas Mejoras Opcionales

1. **Búsqueda de chats** - Búsqueda por título/contenido
2. **Exportar chats** - Descargar como JSON/PDF
3. **Compartir chats** - Generar links para compartir
4. **Archivos en chats** - Guardar imágenes/archivos
5. **Sincronización cloud** - Backup en la nube
6. **Etiquetas/Categorías** - Organizar chats por temas
7. **Análisis de conversación** - Estadísticas de chat
8. **IA que genera títulos** - Resumen automático del primer mensaje

---

**Versión:** 1.0  
**Fecha:** 15 Diciembre 2025  
**Estado:** ✅ Implementado
