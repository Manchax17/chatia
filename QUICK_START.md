# 🚀 Guía Rápida - Comenzar Ahora

## ⏱️ 5 Minutos para que Funcione

### Paso 1: Verificar que el servidor está corriendo (1 min)

```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn app.main:app --reload
```

**Deberías ver:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Paso 2: Iniciar frontend (1 min)

```bash
# Terminal 2 - Frontend
cd frontend
npm run dev
```

**Deberías ver:**
```
  ➜  Local:   http://localhost:5173/
```

### Paso 3: Abrir navegador (30 seg)

1. Abre http://localhost:5173
2. Deberías ver la interfaz CHATFIT AI
3. A la derecha verás "Dispositivo Xiaomi" con un botón azul "Cargar Datos"

### Paso 4: Probar actualización manual (2 min)

1. **Click en "Cargar Datos"** (botón azul en panel derecho)
2. **Completa el formulario:**
   - Pasos: `10000`
   - Calorías: `500`
   - Frecuencia Cardíaca: `75`
   - Horas de Sueño: `8`
3. **Click en "Actualizar"**
4. **Verifica que se actualicen** las tarjetas en el panel derecho

### ✅ ¡Listo!

Si ves que los números cambian en las tarjetas, entonces **funciona correctamente**. 🎉

---

## 🔧 Si Algo No Funciona

### ❌ "Error: Cannot GET /api/v1/wearable/latest"
**Solución:** Asegúrate de que el backend está corriendo en Terminal 1

### ❌ "Error: Conexión rechazada"
**Solución:** Ejecuta `npm install` en la carpeta `frontend`

### ❌ El formulario no se abre
**Solución:** Abre la consola del navegador (F12) y verifica los errores

### ❌ Los datos no se actualizan
**Solución:** 
1. Verifica que completaste los 4 campos obligatorios
2. Busca mensajes de error en rojo en el formulario

---

## 📝 Configuración Actual

Tu `.env` está configurado así:
```dotenv
XIAOMI_CONNECTION_METHOD=mock  ✅ Perfecto
USE_MOCK_WEARABLE=true         ✅ Perfecto
```

**No necesitas cambiar nada** - funciona tal como está.

---

## 🎯 Casos de Uso

### Para Testing (Actual)
✅ Tu configuración es perfecta
- Datos simulados
- Actualización manual funciona
- No requiere dispositivo físico

### Para Datos Reales (Opcional)
Si quieres usar datos reales de Mi Fitness:
```dotenv
XIAOMI_CONNECTION_METHOD=manual
```
Luego carga datos manualmente desde tu app Mi Fitness

### Para Dispositivo Real (Avanzado)
```dotenv
XIAOMI_CONNECTION_METHOD=mi_fitness
MI_FITNESS_EMAIL=tu_email@gmail.com
MI_FITNESS_PASSWORD=tu_contraseña
```

---

## 📊 Datos Recomendados para Prueba

Copia estos valores al formulario:

```
👟 Pasos: 8500
🔥 Calorías: 423
❤️ FC: 72
😴 Sueño: 7.5 horas
📏 Distancia: 5.2 km
⏱️ Minutos activos: 45
🏢 Pisos: 3
💤 FC en reposo: 65
📈 FC máxima: 168
🌙 Calidad sueño: good
😰 Estrés: 45
🔋 Batería: 85%
```

---

## 🧪 Verificación Final

Después de actualizar, verifica que:

- [ ] Las tarjetas muestran los nuevos valores
- [ ] No hay errores en la consola (F12)
- [ ] El mensaje dice "Datos actualizados correctamente"
- [ ] Las tarjetas dicen "Datos de prueba" (naranja)

---

## 📞 Soporte

### Ver Logs del Backend
En la Terminal 1 verás líneas como:
```
INFO:     "POST /api/v1/wearable/update-manual HTTP/1.1" 200 OK
```

### Ver Logs del Frontend
En la consola del navegador (F12) verás:
```
📤 Enviando datos: {steps: 10000, calories: 500, ...}
📥 Respuesta: {success: true, data: {...}}
```

### Archivos de Referencia
- **Guía completa:** `MANUAL_DATA_UPDATE_GUIDE.md`
- **Cambios técnicos:** `CHANGES_SUMMARY.md`
- **Verificación:** `TECHNICAL_VERIFICATION.md`

---

## ✨ Características Que Funcionan Ahora

✅ Ver datos del wearable en tiempo real
✅ Actualizar datos manualmente sin cambiar .env
✅ Validación de campos requeridos
✅ Mensajes de error claros
✅ Actualización automática de UI
✅ Contexto global funcional

---

## 🎓 Próximo Paso Opcional

Después de que funcione:
1. Lee `MANUAL_DATA_UPDATE_GUIDE.md` para más funciones
2. Explora otros endpoints en http://localhost:8000/docs
3. Prueba la integración del chat con datos del wearable

---

**¡Todo está listo! Comienza en el Paso 1.** 🚀
