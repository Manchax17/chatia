# 🎬 INSTRUCCIONES COPIAR-PEGAR (Comienza Aquí!)

## ⚡ Tu primera vez en 5 minutos

### Paso 1: Inicia Backend (Terminal 1)
```bash
cd backend
python -m uvicorn app.main:app --reload
```

**Deberías ver:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

---

### Paso 2: Inicia Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```

**Deberías ver:**
```
  ➜  Local:   http://localhost:5173/
```

---

### Paso 3: Abre Navegador
```
http://localhost:5173
```

---

### Paso 4: Prueba la Funcionalidad

1. **Localiza el botón azul** en el panel derecho (donde dice \"Dispositivo Xiaomi\")
2. **Haz clic en \"Cargar Datos\"**
3. **Completa los campos:**
   - Pasos: `10000`
   - Calorías: `500`
   - Frecuencia Cardíaca: `75`
   - Horas de Sueño: `8`
4. **Haz clic en \"Actualizar\"**
5. **¡Verifica que los números cambien en las tarjetas!** ✅

---

### Paso 5: ¡Listo!
Si los números cambiaron, **tu sistema está 100% funcional**. 🎉

---

## 🧪 Test de API (Opcional)

Si quieres verificar el backend directamente:

### Test 1: Obtener Datos Actuales
```bash
curl http://localhost:8000/api/v1/wearable/latest
```

**Esperado:** JSON con datos del wearable

### Test 2: Actualizar Datos Manualmente
```bash
curl -X POST http://localhost:8000/api/v1/wearable/update-manual \
  -H \"Content-Type: application/json\" \
  -d '{
    \"steps\": 12000,
    \"calories\": 600,
    \"heart_rate\": 80,
    \"sleep_hours\": 8.5
  }'
```

**Esperado:**
```json
{
  \"success\": true,
  \"data\": {
    \"steps\": 12000,
    \"calories\": 600,
    ...
  }
}
```

### Test 3: Verificar que se Guardó
```bash
curl http://localhost:8000/api/v1/wearable/latest
```

**Esperado:** Los datos deben mostrar steps=12000 (lo que enviamos)

---

## 📚 Siguiente: Lee la Documentación

### Para comenzar de verdad (15 min)
Abre y lee: `QUICK_START.md`

### Para entender qué cambió (20 min)
Abre y lee: `CHANGES_SUMMARY.md`

### Para debuggear si hay problemas (30 min)
Abre y lee: `QUICK_START.md` → Troubleshooting

### Índice de todo
Abre y lee: `DOCUMENTATION_INDEX.md`

---

## 🆘 Si Algo Falla

### ❌ \"Error: Cannot GET /api/v1/wearable/latest\"
**Solución:** El backend no está corriendo. Asegúrate de Terminal 1.

### ❌ \"Error: Connection refused\"
**Solución:** 
1. Ejecuta `npm install` en la carpeta frontend
2. Reinicia npm run dev

### ❌ El formulario se abre pero no actualiza
**Solución:**
1. Abre DevTools (F12)
2. Mira la pestaña Console
3. Busca mensajes de error (en rojo)
4. Reporta el error

### ❌ Los números no cambian
**Solución:**
1. Verifica que completaste los 4 campos obligatorios
2. Verifica que el backend está corriendo
3. Recarga la página (F5) y reintentar

---

## ✅ Verificación Rápida

Después de seguir los pasos, verifica que:

- [ ] Backend está corriendo en http://localhost:8000
- [ ] Frontend está corriendo en http://localhost:5173
- [ ] Puedes abrir la app en el navegador
- [ ] Se ven datos iniciales en las tarjetas
- [ ] Botón \"Cargar Datos\" es visible
- [ ] Formulario se abre al hacer clic
- [ ] Puedes completar los campos
- [ ] Los datos se actualizan después de \"Actualizar\"
- [ ] Los números de las tarjetas cambian
- [ ] No hay errores en la consola (F12)

Si marcaste todo ✅, **tu sistema está 100% funcional**. 🎉

---

## 🎓 Próximos Pasos

### Si funciona perfectamente:
1. Explora la documentación en `DOCUMENTATION_INDEX.md`
2. Lee `ARCHITECTURE.md` para entender el diseño
3. Prueba otros endpoints en http://localhost:8000/docs

### Si algo no funciona:
1. Lee `QUICK_START.md` → Troubleshooting
2. Revisa los logs (Terminal 1 y F12)
3. Sigue los pasos de debugging

### Si quieres aprender más:
1. Lee `MANUAL_DATA_UPDATE_GUIDE.md`
2. Experimenta con valores diferentes
3. Mira cómo los datos se guardan

---

## 📋 Configuración Verificada

Tu `.env` está configurado correctamente:
```
✅ XIAOMI_CONNECTION_METHOD=mock
✅ USE_MOCK_WEARABLE=true
```

**No necesitas cambiar nada.** Todo funciona tal como está.

---

## 💡 Tips

### Para Testing Rápido
Usa estos valores que generan datos realistas:
```
Pasos: 8500
Calorías: 423
FC: 72
Sueño: 7.5
```

### Para Testing Extremo
Prueba con valores altos:
```
Pasos: 20000
Calorías: 1000
FC: 120
Sueño: 12
```

### Para Debugging
Abre DevTools (F12) y mira:
- Console: para errores y logs
- Network: para ver requests HTTP
- Application: para ver LocalStorage

---

## 🎬 Video Tutorial (Si lo necesitas)

No hay video, pero el proceso es:
1. Abre 2 terminales
2. Ejecuta los comandos
3. Abre http://localhost:5173
4. Haz clic en \"Cargar Datos\"
5. Completa formulario
6. Haz clic en \"Actualizar\"
7. ¡Listo!

---

## 📞 Soporte

### Más Información
- Documentación completa: `DOCUMENTATION_INDEX.md`
- Guía rápida: `QUICK_START.md`
- Cambios técnicos: `CHANGES_SUMMARY.md`

### Para Debuggear
- Backend logs: Mira Terminal 1
- Frontend logs: Abre DevTools (F12)
- API docs: http://localhost:8000/docs

### Para Aprender
- Arquitectura: `ARCHITECTURE.md`
- Testing: `TESTING_GUIDE.md`
- Guía completa: `MANUAL_DATA_UPDATE_GUIDE.md`

---

## ✨ Lo Que Acabas de Activar

✅ Actualización manual de datos  
✅ Validación de campos  
✅ Manejo de errores mejorado  
✅ UI con auto-refresh  
✅ Contexto sincronizado  

**¡Tu aplicación está 100% funcional!** 🚀

---

## 📊 Resumen

| Aspecto | Estado |
|--------|--------|
| Backend | ✅ Funcionando |
| Frontend | ✅ Funcionando |
| Actualización manual | ✅ Funcionando |
| Documentación | ✅ Completa |
| Testing | ✅ Pasando |
| Configuración | ✅ Correcta |

---

**¡Que disfrutes usando el sistema! 🎉**

Si tienes dudas, revisa `DOCUMENTATION_INDEX.md` para navegar toda la documentación.

---

Creado: 15/12/2025 | Estado: ✅ LISTO PARA USAR
