"""Herramientas (Tools) para el agente LLM"""

from langchain.tools import tool
from typing import Optional

# Base de conocimiento verificada
HEALTH_KNOWLEDGE = {
    "imc": {
        "info": "Índice de Masa Corporal = peso(kg) / altura(m)²",
        "rangos": {
            "Bajo peso": "<18.5",
            "Normal": "18.5-24.9",
            "Sobrepeso": "25-29.9",
            "Obesidad": "≥30"
        },
        "fuente": "OMS (Organización Mundial de la Salud, 2023)"
    },
    "pasos": {
        "info": "Se recomienda 10,000 pasos diarios para salud cardiovascular óptima",
        "minimo": "7,000 pasos para beneficios básicos de salud",
        "fuente": "American Heart Association, 2021"
    },
    "frecuencia_cardiaca": {
        "reposo_normal": "60-100 bpm",
        "formula_maxima": "220 - edad",
        "zona_cardio": "50-85% de FC máxima",
        "fuente": "American College of Sports Medicine (ACSM)"
    },
    "calorias": {
        "deficit": "Déficit de 500 kcal/día = ~0.5kg pérdida semanal",
        "minimo_mujer": "1200 kcal/día mínimo",
        "minimo_hombre": "1500 kcal/día mínimo",
        "fuente": "National Institutes of Health (NIH)"
    },
    "sueno": {
        "adultos": "7-9 horas por noche",
        "adolescentes": "8-10 horas",
        "beneficios": "Recuperación muscular, regulación hormonal, salud mental",
        "fuente": "National Sleep Foundation, 2023"
    },
    "hidratacion": {
        "general": "2-3 litros de agua al día",
        "ejercicio": "+500ml por hora de ejercicio",
        "fuente": "European Hydration Institute"
    }
}

@tool
def get_health_info(topic: str) -> str:
    """
    Consulta información de salud verificada y basada en evidencia científica.
    
    Temas disponibles: imc, pasos, frecuencia_cardiaca, calorias, sueno, hidratacion
    
    Args:
        topic: El tema de salud a consultar
        
    Returns:
        Información detallada con fuente científica
    """
    topic = topic.lower().replace(" ", "_")
    
    if topic not in HEALTH_KNOWLEDGE:
        return f"❌ Tema no encontrado. Disponibles: {', '.join(HEALTH_KNOWLEDGE.keys())}"
    
    info = HEALTH_KNOWLEDGE[topic]
    response = f"📚 **Información sobre {topic.upper().replace('_', ' ')}**\n\n"
    
    for key, value in info.items():
        if key == "fuente":
            response += f"\n🔬 Fuente: {value}"
        elif isinstance(value, dict):
            response += f"\n**{key.title()}:**\n"
            for k, v in value.items():
                response += f"  • {k}: {v}\n"
        else:
            response += f"{value}\n"
    
    return response

@tool
def calculate_bmi(weight_kg: float, height_cm: float) -> str:
    """
    Calcula el Índice de Masa Corporal (IMC).
    
    Args:
        weight_kg: Peso en kilogramos
        height_cm: Altura en centímetros
        
    Returns:
        IMC calculado con interpretación y recomendaciones
    """
    if weight_kg <= 0 or height_cm <= 0:
        return "❌ Error: Peso y altura deben ser valores positivos"
    
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    
    if bmi < 18.5:
        category = "Bajo peso"
        advice = "Considera consultar un nutricionista para un plan de aumento saludable de peso."
        color = "🟡"
    elif bmi < 25:
        category = "Peso normal"
        advice = "¡Excelente! Mantén tus hábitos saludables actuales con ejercicio regular y nutrición balanceada."
        color = "🟢"
    elif bmi < 30:
        category = "Sobrepeso"
        advice = "Pequeños cambios en dieta y ejercicio pueden ayudar. Considera actividad física regular y reducción moderada de calorías."
        color = "🟠"
    else:
        category = "Obesidad"
        advice = "Recomendado consultar profesional de salud para plan personalizado y seguro."
        color = "🔴"
    
    return f"""
{color} **CÁLCULO DE IMC**

📊 **Datos ingresados:**
  • Peso: {weight_kg} kg
  • Altura: {height_cm} cm ({height_m:.2f} m)

📈 **Resultado:**
  • IMC: **{bmi:.1f}**
  • Categoría: **{category}**

💡 **Recomendación:**
{advice}

📋 **Rangos de referencia (OMS):**
  • Bajo peso: < 18.5
  • Normal: 18.5 - 24.9
  • Sobrepeso: 25 - 29.9
  • Obesidad: ≥ 30

🔬 Fuente: Organización Mundial de la Salud (OMS)
"""

@tool
def analyze_steps(steps: int, goal: int = 10000) -> str:
    """
    Analiza el conteo de pasos diario comparado con objetivos de salud.
    
    Args:
        steps: Número de pasos dados hoy
        goal: Objetivo de pasos (default: 10,000)
        
    Returns:
        Análisis detallado del progreso
    """
    if steps < 0:
        return "❌ Error: Los pasos no pueden ser negativos"
    
    percentage = (steps / goal) * 100
    remaining = max(0, goal - steps)
    
    if percentage >= 100:
        message = "🎉 ¡Objetivo cumplido! Excelente trabajo."
        advice = "Mantén este ritmo. Si es sostenible, considera aumentar tu meta gradualmente (+1000 pasos/semana)."
        emoji = "🌟"
    elif percentage >= 75:
        message = "💪 ¡Casi lo logras! Vas muy bien."
        advice = f"Solo faltan {remaining:,} pasos (~{remaining//130} minutos de caminata). ¡Un último empujón!"
        emoji = "👏"
    elif percentage >= 50:
        message = "👍 Buen progreso, pero hay margen de mejora."
        advice = f"Faltan {remaining:,} pasos. Intenta caminar durante llamadas o tomar escaleras."
        emoji = "💪"
    elif percentage >= 25:
        message = "⚠️ Actividad moderada-baja hoy."
        advice = "Intenta incorporar caminatas cortas cada hora. Pequeños movimientos suman."
        emoji = "🚶"
    else:
        message = "🔴 Actividad muy baja hoy."
        advice = "Tu salud lo agradecerá si te mueves más. Empieza con 10 minutos de caminata."
        emoji = "⏰"
    
    # Calcular equivalencias
    calories_burned = steps * 0.04  # Aproximación: ~0.04 kcal por paso
    distance_km = steps * 0.00075  # Aproximación: ~0.75m por paso
    time_walking = steps // 130  # ~130 pasos por minuto
    
    return f"""
{emoji} **ANÁLISIS DE PASOS**

📊 **Resumen:**
  • Pasos hoy: **{steps:,}**
  • Objetivo: {goal:,}
  • Progreso: **{percentage:.0f}%**
  • Restantes: {remaining:,}

📏 **Equivalencias:**
  • Distancia: ~{distance_km:.2f} km
  • Tiempo caminando: ~{time_walking} minutos
  • Calorías quemadas: ~{calories_burned:.0f} kcal

{message}

💡 **Recomendación:**
{advice}

📚 **Datos científicos:**
  • Mínimo saludable: 7,000 pasos/día (reducción riesgo cardiovascular)
  • Objetivo recomendado: 10,000 pasos/día (salud óptima)
  • Elite: 12,000-15,000 pasos/día

🔬 Fuente: American Heart Association, British Journal of Sports Medicine (2021)
"""

@tool
def calculate_target_heart_rate(age: int, resting_hr: Optional[int] = None) -> str:
    """
    Calcula zonas de frecuencia cardíaca objetivo para ejercicio.
    
    Args:
        age: Edad del usuario
        resting_hr: Frecuencia cardíaca en reposo (opcional)
        
    Returns:
        Zonas cardíacas para diferentes intensidades
    """
    if age <= 0 or age > 120:
        return "❌ Error: Edad debe estar entre 1 y 120 años"
    
    max_hr = 220 - age
    
    zones = {
        "Calentamiento (50-60%)": (max_hr * 0.5, max_hr * 0.6),
        "Quema grasa (60-70%)": (max_hr * 0.6, max_hr * 0.7),
        "Cardio moderado (70-80%)": (max_hr * 0.7, max_hr * 0.8),
        "Alta intensidad (80-90%)": (max_hr * 0.8, max_hr * 0.9),
        "Máximo esfuerzo (90-100%)": (max_hr * 0.9, max_hr)
    }
    
    result = f"""
❤️ **ZONAS DE FRECUENCIA CARDÍACA**

📊 **Datos base:**
  • Edad: {age} años
  • FC Máxima estimada: **{max_hr} bpm**
"""
    
    if resting_hr:
        result += f"  • FC en reposo: {resting_hr} bpm"
        if resting_hr < 60:
            result += " (🌟 Excelente - indica buena condición cardiovascular)\n"
        elif resting_hr <= 80:
            result += " (✅ Normal)\n"
        elif resting_hr <= 100:
            result += " (⚠️ Ligeramente elevada)\n"
        else:
            result += " (🔴 Elevada - consulta médico si es constante)\n"
    
    result += "\n🎯 **Zonas de Entrenamiento:**\n"
    for zone_name, (min_hr, max_hr_zone) in zones.items():
        result += f"  • {zone_name}: **{min_hr:.0f}-{max_hr_zone:.0f} bpm**\n"
    
    result += """
💡 **Guía de uso:**
  • Calentamiento: Inicio de actividad, recuperación activa
  • Quema grasa: Ejercicio aeróbico prolongado, pérdida de peso
  • Cardio: Mejora resistencia cardiovascular
  • Alta intensidad: HIIT, mejora rendimiento deportivo
  • Máximo: Sprints cortos, solo atletas entrenados

⚠️ **Precauciones:**
  • Consulta médico antes de ejercicio intenso si no estás activo
  • Aumenta intensidad gradualmente
  • Escucha a tu cuerpo, detente si hay molestias

🔬 Fuente: American College of Sports Medicine (ACSM)
"""
    
    return result

@tool
def calculate_daily_calories(
    weight_kg: float, 
    height_cm: float, 
    age: int,
    gender: str, 
    activity_level: str
) -> str:
    """
    Calcula el gasto calórico diario total (TDEE).
    
    Args:
        weight_kg: Peso en kilogramos
        height_cm: Altura en centímetros
        age: Edad en años
        gender: 'hombre' o 'mujer'
        activity_level: 'sedentario', 'ligero', 'moderado', 'activo', 'muy_activo'
        
    Returns:
        Calorías de mantenimiento y objetivos
    """
    if weight_kg <= 0 or height_cm <= 0 or age <= 0:
        return "❌ Error: Todos los valores deben ser positivos"
    
    # Fórmula Mifflin-St Jeor (más precisa que Harris-Benedict)
    if gender.lower() in ['hombre', 'male', 'm', 'masculino']:
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        min_cal = 1500
    else:
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
        min_cal = 1200
    
    # Factores de actividad
    activity_factors = {
        'sedentario': (1.2, "Poco o ningún ejercicio"),
        'ligero': (1.375, "Ejercicio ligero 1-3 días/semana"),
        'moderado': (1.55, "Ejercicio moderado 3-5 días/semana"),
        'activo': (1.725, "Ejercicio intenso 6-7 días/semana"),
        'muy_activo': (1.9, "Ejercicio muy intenso, trabajo físico")
    }
    
    factor_data = activity_factors.get(activity_level.lower(), (1.2, "Nivel no especificado"))
    factor, activity_desc = factor_data
    tdee = bmr * factor
    
    # Objetivos
    deficit = tdee - 500  # Pérdida de peso saludable
    surplus = tdee + 300  # Ganancia muscular
    
    return f"""
🍽️ **ANÁLISIS CALÓRICO DIARIO**

📊 **Datos ingresados:**
  • Peso: {weight_kg} kg
  • Altura: {height_cm} cm
  • Edad: {age} años
  • Género: {gender}
  • Actividad: {activity_level} ({activity_desc})

🔥 **Resultados:**
  • **Metabolismo basal (BMR):** {bmr:.0f} kcal/día
    (Calorías que quema tu cuerpo en reposo)
  
  • **Gasto total (TDEE):** **{tdee:.0f} kcal/día**
    (Incluye actividad diaria)

🎯 **Objetivos sugeridos:**

🔵 **Mantenimiento:** {tdee:.0f} kcal/día
   → Mantener peso actual

🟢 **Pérdida de peso:** {deficit:.0f} kcal/día
   → Pérdida sostenible de ~0.5 kg/semana
   → Déficit de 500 kcal/día

🟡 **Ganancia muscular:** {surplus:.0f} kcal/día
   → Ganancia de ~0.25 kg/semana
   → Superávit de 300 kcal/día
   → Requiere entrenamiento de fuerza

⚠️ **Límites saludables:**
  • Mínimo recomendado: {min_cal} kcal/día
  • No bajar más sin supervisión médica
  • Déficits extremos (>1000 kcal) son contraproducentes

💡 **Recomendaciones:**
  • Ajusta gradualmente (+/- 200 kcal cada 2 semanas)
  • Monitorea peso semanalmente
  • Prioriza alimentos nutritivos sobre "calorías vacías"
  • Combina dieta con ejercicio para mejores resultados

🔬 Fuente: Journal of the American Dietetic Association - Fórmula Mifflin-St Jeor
"""

@tool
def analyze_heart_rate(current_hr: int, age: int, context: str = "reposo") -> str:
    """
    Analiza frecuencia cardíaca según contexto.
    
    Args:
        current_hr: Frecuencia cardíaca actual (bpm)
        age: Edad del usuario
        context: 'reposo', 'ejercicio', 'post_ejercicio'
        
    Returns:
        Análisis de la frecuencia cardíaca
    """
    if current_hr <= 0 or age <= 0:
        return "❌ Error: Valores deben ser positivos"
    
    max_hr = 220 - age
    percentage_max = (current_hr / max_hr) * 100
    
    if context == "reposo":
        if current_hr < 60:
            status = "🟢 Excelente"
            msg = "FC en reposo baja indica buena condición cardiovascular (común en atletas)."
        elif current_hr <= 80:
            status = "✅ Normal"
            msg = "FC en reposo dentro del rango saludable."
        elif current_hr <= 100:
            status = "⚠️ Elevada"
            msg = "FC algo elevada. Puede mejorar con ejercicio regular."
        else:
            status = "🔴 Alta"
            msg = "FC en reposo alta. Consulta médico si es persistente."
            
    elif context == "ejercicio":
        if percentage_max < 50:
            status = "🔵 Muy ligero"
            msg = "Intensidad muy baja. Considera aumentar esfuerzo."
        elif percentage_max < 70:
            status = "🟢 Moderado"
            msg = "Zona de quema de grasa y salud cardiovascular."
        elif percentage_max < 85:
            status = "🟡 Intenso"
            msg = "Zona de mejora de rendimiento cardiorrespiratorio."
        elif percentage_max < 95:
            status = "🟠 Muy intenso"
            msg = "Alta intensidad. Mantener solo por períodos cortos."
        else:
            status = "🔴 Máximo"
            msg = "Esfuerzo máximo. Solo para intervalos muy cortos."
    
    else:  # post_ejercicio
        status = "📊 Post-ejercicio"
        msg = f"Observa qué tan rápido baja tu FC. Buena recuperación: -20 bpm en 1 minuto."
    
    return f"""
❤️ **ANÁLISIS DE FRECUENCIA CARDÍACA**

📊 **Datos:**
  • FC actual: **{current_hr} bpm**
  • Edad: {age} años
  • FC máxima: {max_hr} bpm
  • Contexto: {context}
  • % de FC máxima: {percentage_max:.0f}%

{status}

💡 **Interpretación:**
{msg}

📚 **Referencias:**
  • FC reposo normal: 60-100 bpm
  • FC reposo atleta: 40-60 bpm
  • FC máxima: 220 - edad

🔬 Fuente: American Heart Association
"""

def get_tools():
    """Retorna lista de todas las herramientas disponibles"""
    return [
        get_health_info,
        calculate_bmi,
        analyze_steps,
        calculate_target_heart_rate,
        calculate_daily_calories,
        analyze_heart_rate
    ]