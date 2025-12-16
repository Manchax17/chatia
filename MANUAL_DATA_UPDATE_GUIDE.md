# Guía de Actualización Manual de Datos del Wearable

## Descripción General
Este proyecto CHATFIT AI permite actualizar datos del wearable Xiaomi de dos formas:
1. **Modo Simulado (Mock)**: Datos de prueba con actualización manual para testing
2. **Modo Manual**: Carga de datos reales desde Mi Fitness manualmente

---

## Configuración en `.env`

Tu archivo `.env` debe tener una de estas configuraciones:

### Opción 1: Modo Mock (Recomendado para Testing)
```dotenv
XIAOMI_CONNECTION_METHOD=mock
USE_MOCK_WEARABLE=true
```
**Ventajas:**
- Los datos se simulan automáticamente
- Puedes actualizar los datos manualmente desde la interfaz
- Perfecto para testing y desarrollo
- No requiere credenciales

### Opción 2: Modo Manual (para Datos Reales)
```dotenv
XIAOMI_CONNECTION_METHOD=manual
USE_MOCK_WEARABLE=false
```
**Ventajas:**
- Puedes ingresar datos reales de Mi Fitness
- Control total sobre qué datos se muestran
- No requiere conexión a dispositivo físico

### Opción 3: Modo Mi Fitness (Conexión Real)
```dotenv
XIAOMI_CONNECTION_METHOD=mi_fitness
MI_FITNESS_EMAIL=tu_email@gmail.com
MI_FITNESS_PASSWORD=tu_contraseña
MI_FITNESS_REGION=us
MI_FITNESS_DEVICE_ID=tu_device_id
```
**Ventajas:**
- Obtiene datos directamente del dispositivo
- Sincronización automática
- Datos en tiempo real

---

## Cómo Actualizar Datos Manualmente

### Paso 1: Verificar la Configuración
Asegúrate de que en tu `.env` tienes configurado:
- `XIAOMI_CONNECTION_METHOD=mock` **O** `XIAOMI_CONNECTION_METHOD=manual`
- El servidor está corriendo

### Paso 2: Abrir la Interfaz
1. Abre la aplicación CHATFIT AI en tu navegador (http://localhost:5173)
2. En la sección derecha "Dispositivo Xiaomi"
3. Haz clic en el botón **"Cargar Datos"** (azul con icono de upload)

### Paso 3: Completar el Formulario
Completa los campos (los marcados con * son obligatorios):
- **👟 Pasos** *: Número de pasos del día (ej: 8500)
- **🔥 Calorías** *: Calorías quemadas (ej: 423)
- **❤️ Frecuencia Cardíaca** *: En bpm (ej: 72)
- **😴 Horas de Sueño** *: Horas dormidas (ej: 7.5)

Campos opcionales:
- 📏 Distancia (km)
- ⏱️ Minutos Activos
- 🏢 Pisos Subidos
- 💤 FC en Reposo
- 📈 FC Máxima
- 🌙 Calidad del Sueño
- 😰 Nivel de Estrés (0-100)
- 🔋 Batería (%)

### Paso 4: Enviar
1. Verifica que todos los campos requeridos tengan valores
2. Haz clic en el botón **"Actualizar"**
3. Verás un mensaje de confirmación

### Paso 5: Ver Datos Actualizados
Los datos se mostrarán inmediatamente en:
- Tarjetas de estadísticas en el panel derecho
- Historial de sincronización actualizado

---

## Flujo Backend

```
Frontend (Formulario Manual)
        ↓
    POST /api/v1/wearable/update-manual
        ↓
    backend/app/api/v1/wearable.py
        ↓
    Si XIAOMI_CONNECTION_METHOD = "mock":
        → Actualiza xiaomi_client.mock_data
    Si XIAOMI_CONNECTION_METHOD = "manual":
        → Actualiza xiaomi_client.manual_data
        ↓
    GET /api/v1/wearable/latest
        ↓
    Devuelve datos actualizados
        ↓
    Frontend actualiza UI
```

---

## Archivos Modificados

### Backend
- `backend/app/api/v1/wearable.py`: Endpoint `/update-manual` ahora funciona en modo `mock` y `manual`
- `backend/app/api/v1/models.py`: Se añadió campo `message` a `WearableDataResponse`

### Frontend
- `frontend/src/components/wearable/ManualDataForm.jsx`: Mejorado manejo de errores y validación
- `frontend/src/components/wearable/WearableStats.jsx`: Mejor integración con contexto
- `frontend/src/WearableContext.jsx`: Contexto mejorado con carga real de datos

---

## Troubleshooting

### Problema: "Error 400: Este endpoint solo funciona en modo 'manual'"
**Solución**: Verifica que en tu `.env` tengas:
```dotenv
XIAOMI_CONNECTION_METHOD=mock
```
O reinicia el servidor después de cambiar la configuración.

### Problema: El formulario no se abre
**Solución**: 
1. Verifica que el servidor backend está corriendo (`http://localhost:8000/docs`)
2. Revisa la consola del navegador (F12) para errores de red

### Problema: Los datos no se guardan
**Solución**:
1. Asegúrate de completar los 4 campos requeridos (*)
2. Verifica que los valores sean números válidos
3. Revisa la consola del navegador para mensajes de error

### Problema: "Error de conexión al servidor"
**Solución**:
1. Backend debe estar corriendo: `python -m uvicorn app.main:app --reload`
2. Verificar CORS en `backend/app/main.py`
3. Frontend conecta a `http://localhost:8000` por defecto

---

## Desarrollo y Testing

Para testing rápido:
1. Usa modo `mock` (por defecto)
2. Haz clic en "Cargar Datos"
3. Ingresa valores de prueba
4. Verifica que se actualicen las tarjetas de estadísticas

Para usar datos reales:
1. Cambia `XIAOMI_CONNECTION_METHOD=manual`
2. Carga datos de tu app Mi Fitness
3. El sistema los guardará en memoria (reinicio borra datos)

---

## API Endpoints

### GET /api/v1/wearable/latest
Obtiene los datos más recientes del wearable

**Response:**
```json
{
  "data": {
    "steps": 8500,
    "calories": 423,
    "heart_rate": 72,
    "sleep_hours": 7.5,
    "mock_data": true,
    "connection_method": "mock",
    ...
  },
  "success": true
}
```

### POST /api/v1/wearable/update-manual
Actualiza datos manualmente

**Request:**
```json
{
  "steps": 8500,
  "calories": 423,
  "heart_rate": 72,
  "sleep_hours": 7.5,
  "distance_km": 5.2,
  "active_minutes": 45,
  "floors_climbed": 3,
  "resting_heart_rate": 65,
  "max_heart_rate": 168,
  "sleep_quality": "good",
  "stress_level": 45,
  "battery_level": 85,
  "device_model": "Xiaomi Mi Band 7"
}
```

**Response:**
```json
{
  "data": {...datos actualizados...},
  "success": true,
  "message": "Datos mock actualizados para testing"
}
```

---

## Próximos Pasos

1. **Persistencia**: Implementar guardado en base de datos
2. **Histórico**: Guardar histórico de actualizaciones
3. **Validación**: Validación avanzada de rangos de valores
4. **Exportación**: Exportar datos a CSV/JSON

---

**Última Actualización:** 15 de Diciembre, 2025
**Versión:** 1.0
