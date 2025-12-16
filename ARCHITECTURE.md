# 🏗️ Arquitectura de Componentes - Sistema de Actualización Manual

## Diagrama de Arquitectura General

```
┌─────────────────────────────────────────────────────────────────┐
│                       FRONTEND (React)                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ App.jsx (WearableProvider)                              │  │
│  │ ├─ Envuelve toda la app con contexto                    │  │
│  │ └─ Proporciona estado global de wearable                │  │
│  └──────────────────┬───────────────────────────────────────┘  │
│                     │                                           │
│  ┌──────────────────▼───────────────────────────────────────┐  │
│  │ WearableContext.jsx                                     │  │
│  │ ├─ [wearableData, loading, error]                       │  │
│  │ ├─ setWearableData()                                    │  │
│  │ ├─ refreshWearableData() ← Carga datos del backend     │  │
│  │ └─ useWearable() hook                                   │  │
│  └──────────────────┬───────────────────────────────────────┘  │
│                     │                                           │
│  ┌──────────────────▼───────────────────────────────────────┐  │
│  │ WearableStats.jsx (Lado Derecho)                        │  │
│  │ ├─ Lee del contexto con useWearable()                   │  │
│  │ ├─ Renderiza StatsCard componentes                      │  │
│  │ ├─ Botón "Cargar Datos" → abre formulario              │  │
│  │ └─ Botón "Sincronizar"                                  │  │
│  └──────────────────┬───────────────────────────────────────┘  │
│                     │                                           │
│  ┌──────────────────▼───────────────────────────────────────┐  │
│  │ ManualDataForm.jsx (Modal)                              │  │
│  │ ├─ FormData (steps, calories, heart_rate, sleep_hours) │  │
│  │ ├─ Validación de campos requeridos                      │  │
│  │ ├─ handleSubmit()                                       │  │
│  │ │  └─ POST /api/v1/wearable/update-manual              │  │
│  │ ├─ Manejo de errores mejorado                           │  │
│  │ └─ Actualiza contexto al éxito                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ wearableService.js                                      │  │
│  │ ├─ getLatestData()                                      │  │
│  │ ├─ updateManualData(data)  ← Llama endpoint            │  │
│  │ ├─ sync()                                               │  │
│  │ └─ getConnectionInfo()                                  │  │
│  └──────────────────┬───────────────────────────────────────┘  │
└─────────────────────┼───────────────────────────────────────────┘
                      │
                      │ HTTP Requests
                      │ (CORS habilitado)
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                    BACKEND (FastAPI)                            │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ backend/app/main.py                                     │  │
│  │ ├─ FastAPI app                                          │  │
│  │ ├─ CORS middleware                                      │  │
│  │ └─ Incluye router de v1                                 │  │
│  └──────────────────┬───────────────────────────────────────┘  │
│                     │                                           │
│  ┌──────────────────▼───────────────────────────────────────┐  │
│  │ backend/app/api/v1/wearable.py                          │  │
│  │ ├─ GET /latest → get_latest_wearable_data()            │  │
│  │ ├─ POST /sync → sync_wearable()                         │  │
│  │ ├─ POST /update-manual → update_manual_data() ✏️       │  │
│  │ │  └─ NUEVO: Soporta mock + manual                     │  │
│  │ └─ GET /connection-info → get_connection_info()        │  │
│  └──────────────────┬───────────────────────────────────────┘  │
│                     │                                           │
│  ┌──────────────────▼───────────────────────────────────────┐  │
│  │ backend/app/api/v1/models.py                            │  │
│  │ ├─ WearableUpdateRequest                               │  │
│  │ ├─ WearableDataResponse ✏️ (message field)             │  │
│  │ ├─ SyncResponse                                         │  │
│  │ └─ ConnectionInfoResponse                              │  │
│  └──────────────────┬───────────────────────────────────────┘  │
│                     │                                           │
│  ┌──────────────────▼───────────────────────────────────────┐  │
│  │ backend/app/iot/xiaomi_client.py                        │  │
│  │ ├─ __init__()                                           │  │
│  │ │  ├─ Lee XIAOMI_CONNECTION_METHOD de .env             │  │
│  │ │  └─ Inicializa mock_data o manual_data               │  │
│  │ ├─ get_daily_summary()                                 │  │
│  │ │  ├─ Si mock: return mock_data                        │  │
│  │ │  └─ Si manual: return manual_data                    │  │
│  │ └─ update_data(data)                                    │  │
│  │    └─ Solo funciona en manual                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ backend/app/config.py                                   │  │
│  │ ├─ Settings (pydantic)                                  │  │
│  │ ├─ XIAOMI_CONNECTION_METHOD = 'mock' ← DE .env         │  │
│  │ ├─ USE_MOCK_WEARABLE = true                            │  │
│  │ └─ mock_user_profile                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Flujo de Actualización Manual Detallado

```
USER INTERACTION LAYER
═══════════════════════════════════════════════════════════════════

1. Usuario abre app
   ↓
   WearableContext.useEffect() → refreshWearableData()
   ├─ GET /api/v1/wearable/latest
   └─ setWearableData(data)
   
2. WearableStats renderiza con datos
   ├─ Tarjetas muestran pasos, calorías, FC, sueño
   └─ Botón "Cargar Datos" visible


INTERACTION FLOW
═══════════════════════════════════════════════════════════════════

3. Usuario click "Cargar Datos"
   ↓
   <ManualDataForm showModal={true}>
   ├─ FormData state inicializado
   ├─ inputs para 13 campos
   └─ 4 campos requeridos (*)

4. Usuario completa:
   ├─ steps: 10000 *
   ├─ calories: 500 *
   ├─ heart_rate: 75 *
   └─ sleep_hours: 8 *

5. Usuario click "Actualizar"
   ↓
   handleSubmit(e)
   ├─ e.preventDefault()
   ├─ Validación: if (!steps || !calories || ...) return error
   ├─ Conversión de tipos:
   │  ├─ steps: parseInt()
   │  ├─ calories: parseInt()
   │  ├─ heart_rate: parseInt()
   │  ├─ sleep_hours: parseFloat()
   │  └─ etc...
   ├─ console.log("📤 Enviando datos:", dataToSend)
   └─ await wearableService.updateManualData(dataToSend)


NETWORK REQUEST
═══════════════════════════════════════════════════════════════════

6. Frontend → Backend
   ├─ URL: POST http://localhost:8000/api/v1/wearable/update-manual
   ├─ Headers:
   │  ├─ Content-Type: application/json
   │  └─ (CORS: origin localhost:5173)
   └─ Body: {steps, calories, heart_rate, sleep_hours, ...}


BACKEND PROCESSING
═══════════════════════════════════════════════════════════════════

7. update_manual_data(data: WearableUpdateRequest)
   ├─ try:
   │  ├─ if xiaomi_client.connection_method == "manual":
   │  │  └─ xiaomi_client.update_data(data.dict())  ← Usa manual_data
   │  │
   │  ├─ elif xiaomi_client.connection_method == "mock":
   │  │  ├─ data_dict = data.dict()
   │  │  ├─ data_dict['timestamp'] = datetime.now()
   │  │  ├─ data_dict['mock_data'] = True
   │  │  ├─ xiaomi_client.mock_data.update(data_dict)  ← ✏️ NUEVO
   │  │  └─ retorna datos actualizados
   │  │
   │  └─ else:
   │     └─ raise HTTPException(400, "No disponible en mi_fitness/bluetooth")
   │
   └─ except:
      └─ retorna error con mensaje


8. xiaomi_client.mock_data.update()
   ├─ self.mock_data['steps'] = 10000
   ├─ self.mock_data['calories'] = 500
   ├─ self.mock_data['heart_rate'] = 75
   ├─ self.mock_data['sleep_hours'] = 8
   └─ self.mock_data['timestamp'] = datetime.now()

9. await xiaomi_client.get_daily_summary()
   ├─ if connection_method == "mock":
   │  └─ return self._get_mock_summary()
   └─ return {**self.mock_data, mock_data: True, ...}


RESPONSE GENERATION
═══════════════════════════════════════════════════════════════════

10. return WearableDataResponse(
    ├─ data={steps: 10000, calories: 500, ...},  ← Nuevos valores
    ├─ success=True,
    ├─ error=None,
    └─ message="Datos mock actualizados para testing"  ← ✏️ NUEVO
)

11. HTTP 200 Response Body:
    {
      "data": {
        "steps": 10000,
        "calories": 500,
        "heart_rate": 75,
        "sleep_hours": 8,
        "timestamp": "2025-12-15T...",
        "mock_data": true,
        "connection_method": "mock"
      },
      "success": true,
      "message": "Datos mock actualizados para testing"
    }


FRONTEND RESPONSE HANDLING
═══════════════════════════════════════════════════════════════════

12. Frontend recibe response
    ├─ console.log("📥 Respuesta:", response)
    └─ if (response.success):
       ├─ setError(null)  ← Limpia errores previos
       ├─ setWearableData(response.data)  ← Actualiza contexto
       ├─ alert("✅ Datos actualizados correctamente")
       ├─ if (onClose) onClose()  ← Cierra modal
       └─ ManualDataForm desaparece

13. Context update triggers re-render
    ├─ WearableStats recibe nuevos datos
    ├─ Las tarjetas se actualizan:
    │  ├─ Pasos: 8500 → 10000
    │  ├─ Calorías: 423 → 500
    │  ├─ FC: 72 → 75
    │  └─ Sueño: 7.5 → 8
    └─ Auto-refresh interval sigue corriendo (5 min)


ERROR HANDLING
═══════════════════════════════════════════════════════════════════

14. Si hay error:
    ├─ catch (err)
    ├─ Extrae mensaje de:
    │  ├─ err.response?.data?.detail
    │  ├─ err.response?.data?.error
    │  ├─ err.message
    │  └─ 'Error desconocido'
    ├─ setError("❌ " + errorMsg)
    └─ Muestra en UI roja con icono X


FINAL STATE
═══════════════════════════════════════════════════════════════════

15. UI Final:
    ├─ Modal cerrado
    ├─ Tarjetas actualizadas con nuevos valores
    ├─ Contexto global sincronizado
    ├─ Último timestamp actualizado
    └─ Usuario puede:
       ├─ Actualizar nuevamente
       ├─ Sincronizar
       ├─ Ver en el chat
       └─ Hacer cualquier otra cosa
```

---

## Componentes y Responsabilidades

### WearableContext
```javascript
Responsabilidad: Estado global
├─ wearableData: null | {steps, calories, ...}
├─ loading: boolean
├─ error: null | string
├─ setWearableData(data): void
├─ refreshWearableData(): Promise<void>
└─ setError(error): void
```

### ManualDataForm
```javascript
Responsabilidad: Capturar y validar entrada del usuario
├─ formData: {steps, calories, heart_rate, ...}
├─ loading: boolean
├─ error: null | string
├─ handleChange(e): void
├─ handleSubmit(e): Promise<void>
└─ Renderiza: Modal con 13 input fields
```

### WearableStats
```javascript
Responsabilidad: Mostrar datos y gestionar acciones
├─ wearableData: {steps, calories, ...}
├─ syncing: boolean
├─ connectionInfo: {method, using_mock, ...}
├─ showManualForm: boolean
├─ fetchData(): Promise<void>
├─ handleSync(): Promise<void>
└─ Renderiza: StatsCard × 6 + botones
```

### xiaomi_client (Backend)
```python
Responsabilidad: Gestionar datos del wearable
├─ connection_method: 'mock' | 'manual' | 'mi_fitness' | 'bluetooth'
├─ mock_data: dict
├─ manual_data: WearableData
├─ get_daily_summary(): Dict
├─ update_data(data: Dict): None
└─ get_connection_info(): Dict
```

---

## Estados y Transiciones

```
STARTUP
═════════════════════════════════════════════════════════════════

App Mount
├─ WearableContext.useEffect()
├─ loading = true
├─ refreshWearableData()
├─ GET /api/v1/wearable/latest
├─ setWearableData(data)
├─ loading = false
└─ WearableStats renderiza


WAITING FOR USER ACTION
═════════════════════════════════════════════════════════════════

showManualForm = false
├─ Usuario puede:
│  ├─ Click "Cargar Datos" → showManualForm = true
│  ├─ Click "Sincronizar" → sync API call
│  └─ Ver datos en chat
└─ Auto-refresh cada 5 min


MODAL OPEN
═════════════════════════════════════════════════════════════════

showManualForm = true
├─ Renderiza ManualDataForm
├─ Usuario completa campos
└─ Estados:
   ├─ error = null (no hay errores)
   ├─ loading = false (no enviando)


SUBMITTING
═════════════════════════════════════════════════════════════════

handleSubmit() llamado
├─ Validar campos → error si falta algo
├─ loading = true
├─ POST /api/v1/wearable/update-manual
├─ Esperando respuesta...
└─ Estados:
   ├─ error = null (limpiado)
   ├─ loading = true


RESPONSE RECEIVED - SUCCESS
═════════════════════════════════════════════════════════════════

response.success = true
├─ setWearableData(response.data)
├─ showManualForm = false (cierra)
├─ alert("✅ Éxito")
└─ VUELVE A: WAITING FOR USER ACTION


RESPONSE RECEIVED - ERROR
═════════════════════════════════════════════════════════════════

response.success = false
├─ error = "❌ " + error_msg
├─ loading = false
├─ showManualForm = true (permanece abierto)
└─ Usuario puede:
   ├─ Corregir y reintentar
   └─ Click X para cerrar
```

---

## Mapeo de Archivos a Responsabilidades

```
CAPAS DE LA APLICACIÓN
═══════════════════════════════════════════════════════════════════

┌─ PRESENTACIÓN (UI)
│  ├─ frontend/src/App.jsx
│  ├─ frontend/src/components/wearable/WearableStats.jsx
│  ├─ frontend/src/components/wearable/ManualDataForm.jsx
│  └─ frontend/src/components/wearable/StatsCard.jsx
│
├─ ESTADO GLOBAL
│  └─ frontend/src/WearableContext.jsx
│
├─ SERVICIOS (API Client)
│  └─ frontend/src/services/wearableService.js
│
├─ ENRUTAMIENTO (Router)
│  └─ backend/app/api/v1/wearable.py
│
├─ MODELOS (Data)
│  ├─ backend/app/api/v1/models.py
│  └─ backend/app/iot/xiaomi_client.py
│
└─ CONFIGURACIÓN
   ├─ backend/app/config.py (settings de .env)
   └─ backend/.env
```

---

## Puntos de Integración Clave

```
FRONTEND ↔ BACKEND
═══════════════════════════════════════════════════════════════════

1. wearableService.updateManualData()
   └─ POST http://localhost:8000/api/v1/wearable/update-manual
      ├─ Headers: Content-Type: application/json
      ├─ Body: {steps, calories, heart_rate, sleep_hours, ...}
      └─ Response: {data, success, error, message}

2. CORS Configuration
   ├─ backend/app/main.py
   ├─ allow_origins=["*"]  ← Permite localhost:5173
   └─ Habilitado para POST requests

3. Estado Compartido
   ├─ WearableContext proporciona wearableData
   ├─ ManualDataForm actualiza mediante setWearableData()
   └─ WearableStats consume y renderiza
```

---

## ✅ Resumen de Arquitectura

**Patrón:** Context API + Hooks + Fetch API
**Comunicación:** HTTP REST con JSON
**Estado:** Centralizado en WearableContext
**Actualización:** Bidireccional (GET inicial, POST en actualización)
**Errores:** Manejo en múltiples niveles (frontend y backend)

¡La arquitectura ahora está completamente funcional! 🎉
