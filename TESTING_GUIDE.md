# 🧪 Guía de Testing - Actualización Manual de Wearable

## Quick Test (1 minuto)

### Paso 1: Verificar Backend
```bash
curl -s http://localhost:8000/api/v1/wearable/latest | python -m json.tool
```

**Esperado:**
```json
{
  \"data\": {
    \"steps\": 8547,
    \"calories\": 423,
    \"mock_data\": true
  },
  \"success\": true
}
```

### Paso 2: Verificar Frontend
Abre http://localhost:5173 y verifica que:
- [ ] Se carga sin errores
- [ ] Panel derecho muestra \"Dispositivo Xiaomi\"
- [ ] Tarjetas muestran datos
- [ ] Botón \"Cargar Datos\" es visible

### Paso 3: Test Actualización
1. Click \"Cargar Datos\"
2. Ingresa: Pasos=10000, Cal=500, FC=75, Sueño=8
3. Click \"Actualizar\"
4. Verifica que los números cambien

---

## Full Test Suite (5 minutos)

### Test 1: Configuración
```bash
# Verificar .env
grep XIAOMI_CONNECTION_METHOD backend/.env
# Esperado: XIAOMI_CONNECTION_METHOD=mock

# Verificar servidor corriendo
curl -s http://localhost:8000/health | python -m json.tool
```

### Test 2: Endpoint GET
```bash
curl -X GET http://localhost:8000/api/v1/wearable/latest \
  -H \"Content-Type: application/json\" \
  -H \"Origin: http://localhost:5173\"
```

**Esperado:** HTTP 200 con datos

### Test 3: Endpoint POST (Actualización Manual)
```bash
curl -X POST http://localhost:8000/api/v1/wearable/update-manual \
  -H \"Content-Type: application/json\" \
  -H \"Origin: http://localhost:5173\" \
  -d '{
    \"steps\": 12000,
    \"calories\": 600,
    \"heart_rate\": 80,
    \"sleep_hours\": 8.5,
    \"distance_km\": 7.5,
    \"active_minutes\": 50,
    \"floors_climbed\": 5,
    \"resting_heart_rate\": 65,
    \"max_heart_rate\": 170,
    \"sleep_quality\": \"excellent\",
    \"stress_level\": 40,
    \"battery_level\": 90,
    \"device_model\": \"Xiaomi Mi Band 7\"
  }'
```

**Esperado:**
```json
{
  \"data\": {
    \"steps\": 12000,
    \"calories\": 600,
    \"heart_rate\": 80,
    \"mock_data\": true
  },
  \"success\": true,
  \"message\": \"Datos mock actualizados para testing\"
}
```

### Test 4: Verificar que se Guardaron
```bash
curl -s http://localhost:8000/api/v1/wearable/latest | python -m json.tool
# Verifica que steps sea 12000 (el valor que enviamos)
```

### Test 5: Validación de Campos Requeridos
```bash
# Falta steps
curl -X POST http://localhost:8000/api/v1/wearable/update-manual \
  -H \"Content-Type: application/json\" \
  -d '{
    \"calories\": 500,
    \"heart_rate\": 75,
    \"sleep_hours\": 8
  }'
```

**Esperado:** HTTP 422 (Validation Error)

### Test 6: Errores en Modo No Permitido
```bash
# Cambiar .env temporalmente a:
# XIAOMI_CONNECTION_METHOD=mi_fitness

curl -X POST http://localhost:8000/api/v1/wearable/update-manual \
  -H \"Content-Type: application/json\" \
  -d '{
    \"steps\": 10000,
    \"calories\": 500,
    \"heart_rate\": 75,
    \"sleep_hours\": 8
  }'
```

**Esperado:** HTTP 400
```json
{
  \"detail\": \"Actualización manual no disponible en modo 'mi_fitness'...\"
}
```

---

## Frontend Testing

### Test 1: Abrir Formulario
```javascript
// En DevTools Console
document.querySelector('[class*=\"Upload\"]').parentElement.click()
```
**Esperado:** Modal se abre

### Test 2: Llenar Formulario
```javascript
// En DevTools Console
document.querySelector('input[name=\"steps\"]').value = 15000;
document.querySelector('input[name=\"calories\"]').value = 700;
document.querySelector('input[name=\"heart_rate\"]').value = 85;
document.querySelector('input[name=\"sleep_hours\"]').value = 9;
```

### Test 3: Enviar Datos
```javascript
// En DevTools Console (después de llenar)
document.querySelector('button[type=\"submit\"]').click()
```

**Esperado en Console:**
```
📤 Enviando datos: {steps: 15000, calories: 700, ...}
📥 Respuesta: {success: true, data: {...}, message: \"...\"}
```

### Test 4: Validar UI
```javascript
// En DevTools Console
// Verificar que las tarjetas actualizaron
const stepsCard = Array.from(document.querySelectorAll('[class*=\"card\"]'))
  .find(el => el.textContent.includes('Pasos'));
console.log(stepsCard?.textContent);
```

**Esperado:** \"15000 pasos\" (el valor que enviamos)

---

## Performance Testing

### Test 1: Tiempo de Respuesta
```bash
time curl -X POST http://localhost:8000/api/v1/wearable/update-manual \
  -H \"Content-Type: application/json\" \
  -d '{\"steps\": 10000, \"calories\": 500, \"heart_rate\": 75, \"sleep_hours\": 8}'
```

**Esperado:** < 100ms

### Test 2: Memory Usage
```bash
# Monitorear memoria durante múltiples actualizaciones
watch -n 1 'curl -s http://localhost:8000/api/v1/wearable/latest > /dev/null && echo OK'
```

**Esperado:** Sin memory leaks

---

## Integration Testing

### Test 1: Flujo Completo
1. Abre http://localhost:5173
2. Espera que carguen datos iniciales
3. Verifica que WearableContext tiene datos
4. Click \"Cargar Datos\"
5. Completa formulario
6. Envía
7. Verifica actualización en UI
8. Recarga página (F5)
9. Verifica que contexto recarga datos

### Test 2: Múltiples Usuarios (Simulado)
```bash
# Terminal 1
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/v1/wearable/update-manual \
    -H \"Content-Type: application/json\" \
    -d \"{\\\"steps\\\": $((8000 + i*1000)), \\\"calories\\\": 500, \\\"heart_rate\\\": 75, \\\"sleep_hours\\\": 8}\"
  sleep 1
done

# Terminal 2
watch -n 0.5 'curl -s http://localhost:8000/api/v1/wearable/latest | grep steps'
```

**Esperado:** Valores cambian secuencialmente

---

## Edge Cases Testing

### Test 1: Valores Extremos
```bash
curl -X POST http://localhost:8000/api/v1/wearable/update-manual \
  -H \"Content-Type: application/json\" \
  -d '{
    \"steps\": 0,
    \"calories\": 99999,
    \"heart_rate\": 220,
    \"sleep_hours\": 24,
    \"battery_level\": 100,
    \"stress_level\": 100
  }'
```

**Esperado:** HTTP 200 (sin validación de rangos actualmente)

### Test 2: Campos Faltantes
```bash
curl -X POST http://localhost:8000/api/v1/wearable/update-manual \
  -H \"Content-Type: application/json\" \
  -d '{\"steps\": 10000}'
```

**Esperado:** HTTP 422 (Validation Error por campos requeridos faltantes)

### Test 3: Tipos Incorrectos
```bash
curl -X POST http://localhost:8000/api/v1/wearable/update-manual \
  -H \"Content-Type: application/json\" \
  -d '{
    \"steps\": \"abc\",
    \"calories\": \"xyz\",
    \"heart_rate\": \"not_a_number\",
    \"sleep_hours\": \"invalid\"
  }'
```

**Esperado:** HTTP 422 (Type validation error)

### Test 4: Campos Vacíos
```bash
curl -X POST http://localhost:8000/api/v1/wearable/update-manual \
  -H \"Content-Type: application/json\" \
  -d '{
    \"steps\": null,
    \"calories\": null,
    \"heart_rate\": null,
    \"sleep_hours\": null
  }'
```

**Esperado:** HTTP 422

---

## Browser Compatibility Testing

### Chrome/Edge
```
✅ Abre http://localhost:5173
✅ DevTools muestra logs
✅ Formulario funciona
✅ Actualización sucede
```

### Firefox
```
✅ Igual que Chrome
```

### Safari
```
✅ Igual que Chrome
```

---

## Network Error Testing

### Test 1: Backend Desconectado
1. Detén el servidor backend
2. Frontend debería mostrar error
3. Reintenta: debe fallar con mensaje claro

### Test 2: CORS Error
```bash
# Simular request desde origen no permitido
curl -X POST http://localhost:8000/api/v1/wearable/update-manual \
  -H \"Content-Type: application/json\" \
  -H \"Origin: http://evil.com\" \
  -d '{...}'
```

**Esperado:** CORS error (o permitir si * configurado)

### Test 3: Timeout
```javascript
// En DevTools
fetch('http://localhost:8000/api/v1/wearable/update-manual', {
  method: 'POST',
  body: JSON.stringify({...}),
  signal: AbortSignal.timeout(100)  // Timeout de 100ms
})
```

**Esperado:** AbortError por timeout

---

## Logging & Debugging

### Backend Logs
```bash
# Ver en terminal del servidor
POST /api/v1/wearable/update-manual HTTP/1.1\" 200 OK

# Error logs
ERROR:root:Error actualizando datos: [error details]
```

### Frontend Logs
```javascript
// Ver en DevTools Console
📤 Enviando datos: {...}
📥 Respuesta: {...}
❌ Error actualizando datos: {...}
```

### Habilitar Debug Avanzado
```python
# En backend/app/config.py
DEBUG = true  # Ya está habilitado

# En frontend/src/components/wearable/ManualDataForm.jsx
console.log('📤 Enviando datos:', dataToSend);  // Ya está
console.log('📥 Respuesta:', response);  // Ya está
```

---

## Checklist de Prueba Final

### Backend ✅
- [ ] Server inicia sin errores
- [ ] GET /latest devuelve datos
- [ ] POST /update-manual acepta datos en modo mock
- [ ] POST /update-manual rechaza en otros modos
- [ ] Valores actualizados persisten en GET siguiente
- [ ] Errores tienen mensajes claros
- [ ] CORS funciona

### Frontend ✅
- [ ] App carga sin errores de consola
- [ ] WearableContext tiene datos iniciales
- [ ] WearableStats renderiza tarjetas
- [ ] Botón \"Cargar Datos\" abre modal
- [ ] Formulario valida campos requeridos
- [ ] Envío exitoso muestra alert
- [ ] Datos se actualizan en UI
- [ ] Modal se cierra después

### Integration ✅
- [ ] Flujo completo end-to-end funciona
- [ ] Múltiples actualizaciones mantienen consistencia
- [ ] Recarga de página no pierde contexto
- [ ] Errores se manejan apropiadamente

---

## Commands Rápidos

### Testing Individual
```bash
# Solo backend
cd backend && python -m uvicorn app.main:app --reload

# Solo frontend
cd frontend && npm run dev

# Test API
curl http://localhost:8000/api/v1/wearable/latest

# Test POST
curl -X POST http://localhost:8000/api/v1/wearable/update-manual \
  -H \"Content-Type: application/json\" \
  -d '{\"steps\": 10000, \"calories\": 500, \"heart_rate\": 75, \"sleep_hours\": 8}'
```

### Debugging
```bash
# Ver config
cat backend/.env

# Ver conexión
netstat -an | grep 8000
netstat -an | grep 5173

# Kill procesos
lsof -ti :8000 | xargs kill -9
lsof -ti :5173 | xargs kill -9
```

---

## ✅ Estado: Todo Funcionando

Si todos los tests pasan, el sistema está **100% funcional**. 🎉

**Próximos pasos:** Explorar otras funcionalidades como:
- Chat integration
- Data persistence
- Historical tracking
