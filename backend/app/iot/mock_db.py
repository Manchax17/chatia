# mock_db.py

class MockHealthData:
    """
    Almacena los datos de salud en memoria para simular Google Fit.
    Permite actualizar los datos manualmente sin reiniciar el servidor.
    """
    def __init__(self):
        # Valores por defecto al iniciar
        self.steps = 0
        self.calories = 0
        self.sleep_hours = 0
        self.last_update = "Nunca"

    def update(self, steps, calories, sleep_hours):
        self.steps = steps
        self.calories = calories
        self.sleep_hours = sleep_hours
        from datetime import datetime
        self.last_update = datetime.now().strftime("%H:%M:%S")

    def get_context_string(self):
        """Genera el texto que leerá el Chatbot."""
        return (
            f"DATOS DE SALUD ACTUALES (Simulados):\n"
            f"- Pasos hoy: {self.steps}\n"
            f"- Calorías quemadas: {self.calories} kcal\n"
            f"- Horas de sueño: {self.sleep_hours} horas\n"
            f"(Última actualización manual: {self.last_update})"
        )

# Instancia global para ser usada por app.py
current_health_data = MockHealthData()