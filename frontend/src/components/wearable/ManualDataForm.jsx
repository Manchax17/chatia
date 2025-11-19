import React, { useState } from 'react';
import { Upload, Check, X, Loader } from 'lucide-react';
import { wearableService } from '../../services/wearableService';
import { useWearable } from '../../WearableContext';

const ManualDataForm = ({ onClose }) => {
  const [formData, setFormData] = useState({
    steps: 0,
    calories: 0,
    heart_rate: 0,
    sleep_hours: 0,
    distance_km: 0,
    active_minutes: 0,
    floors_climbed: 0,
    resting_heart_rate: 0,
    max_heart_rate: 0,
    sleep_quality: 'good',
    stress_level: 50,
    battery_level: 100,
    device_model: 'Xiaomi Mi Band'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const { setWearableData } = useWearable(); // Usar el contexto

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'sleep_quality' ? value : parseFloat(value) || 0
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Asegurarse de que todos los campos requeridos sean números válidos
      const dataToSend = {
        steps: parseInt(formData.steps) || 0,
        calories: parseInt(formData.calories) || 0,
        heart_rate: parseInt(formData.heart_rate) || 0,
        sleep_hours: parseFloat(formData.sleep_hours) || 0,
        distance_km: parseFloat(formData.distance_km) || 0,
        active_minutes: parseInt(formData.active_minutes) || 0,
        floors_climbed: parseInt(formData.floors_climbed) || 0,
        resting_heart_rate: parseInt(formData.resting_heart_rate) || 0,
        max_heart_rate: parseInt(formData.max_heart_rate) || 0,
        sleep_quality: formData.sleep_quality || 'good',
        stress_level: parseInt(formData.stress_level) || 50,
        battery_level: parseInt(formData.battery_level) || 100,
        device_model: formData.device_model || 'Xiaomi Mi Band'
      };

      const response = await wearableService.updateManualData(dataToSend);
      
      if (response.success) {
        alert('✅ Datos actualizados correctamente');
        
        // Actualizar el estado global
        setWearableData(response.data);
        
        if (onClose) onClose();
      }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Error desconocido';
      setError(errorMsg);
      console.error('Error updating data:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div className="w-full max-w-2xl max-h-[90vh] bg-gray-900 rounded-2xl shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-800 bg-gray-900/50">
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            <Upload size={24} className="text-blue-500" />
            Actualizar Datos Manualmente
          </h3>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="mx-6 mt-4 px-4 py-3 bg-red-900/30 border border-red-700 rounded-lg text-red-200 text-sm">
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto px-6 py-4 scrollbar-thin">
          <div className="grid grid-cols-2 gap-4">
            {/* Pasos */}
            <div>
              <label className="text-sm text-gray-400 block mb-1">👟 Pasos *</label>
              <input
                type="number"
                name="steps"
                value={formData.steps}
                onChange={handleChange}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                required
                min="0"
              />
            </div>

            {/* Calorías */}
            <div>
              <label className="text-sm text-gray-400 block mb-1">🔥 Calorías (kcal) *</label>
              <input
                type="number"
                name="calories"
                value={formData.calories}
                onChange={handleChange}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                required
                min="0"
              />
            </div>

            {/* Frecuencia Cardíaca */}
            <div>
              <label className="text-sm text-gray-400 block mb-1">❤️ Frecuencia Cardíaca (bpm) *</label>
              <input
                type="number"
                name="heart_rate"
                value={formData.heart_rate}
                onChange={handleChange}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                required
                min="0"
                max="220"
              />
            </div>

            {/* Horas de Sueño */}
            <div>
              <label className="text-sm text-gray-400 block mb-1">😴 Horas de Sueño *</label>
              <input
                type="number"
                step="0.1"
                name="sleep_hours"
                value={formData.sleep_hours}
                onChange={handleChange}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                required
                min="0"
                max="24"
              />
            </div>

            {/* Distancia */}
            <div>
              <label className="text-sm text-gray-400 block mb-1">📏 Distancia (km)</label>
              <input
                type="number"
                step="0.1"
                name="distance_km"
                value={formData.distance_km}
                onChange={handleChange}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                min="0"
              />
            </div>

            {/* Minutos Activos */}
            <div>
              <label className="text-sm text-gray-400 block mb-1">⏱️ Minutos Activos</label>
              <input
                type="number"
                name="active_minutes"
                value={formData.active_minutes}
                onChange={handleChange}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                min="0"
              />
            </div>

            {/* Pisos Subidos */}
            <div>
              <label className="text-sm text-gray-400 block mb-1">🏢 Pisos Subidos</label>
              <input
                type="number"
                name="floors_climbed"
                value={formData.floors_climbed}
                onChange={handleChange}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                min="0"
              />
            </div>

            {/* FC en Reposo */}
            <div>
              <label className="text-sm text-gray-400 block mb-1">💤 FC en Reposo (bpm)</label>
              <input
                type="number"
                name="resting_heart_rate"
                value={formData.resting_heart_rate}
                onChange={handleChange}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                min="0"
              />
            </div>

            {/* FC Máxima */}
            <div>
              <label className="text-sm text-gray-400 block mb-1">📈 FC Máxima (bpm)</label>
              <input
                type="number"
                name="max_heart_rate"
                value={formData.max_heart_rate}
                onChange={handleChange}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                min="0"
              />
            </div>

            {/* Nivel de Estrés */}
            <div>
              <label className="text-sm text-gray-400 block mb-1">😰 Nivel de Estrés (0-100)</label>
              <input
                type="number"
                name="stress_level"
                value={formData.stress_level}
                onChange={handleChange}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                min="0"
                max="100"
              />
            </div>

            {/* Batería */}
            <div>
              <label className="text-sm text-gray-400 block mb-1">🔋 Batería (%)</label>
              <input
                type="number"
                name="battery_level"
                value={formData.battery_level}
                onChange={handleChange}
                min="0"
                max="100"
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Calidad del Sueño */}
            <div className="col-span-2">
              <label className="text-sm text-gray-400 block mb-1">🌙 Calidad del Sueño</label>
              <select
                name="sleep_quality"
                value={formData.sleep_quality}
                onChange={handleChange}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
              >
                <option value="excellent">Excelente</option>
                <option value="good">Bueno</option>
                <option value="fair">Regular</option>
                <option value="poor">Malo</option>
              </select>
            </div>
          </div>

          {/* Info */}
          <div className="mt-4 p-3 bg-blue-900/20 border border-blue-700/50 rounded-lg text-xs text-blue-200">
            <strong>💡 Tip:</strong> Abre la app <strong>Mi Fitness</strong> en tu teléfono y copia los valores que aparecen ahí.
            Los campos marcados con * son obligatorios.
          </div>
        </form>

        {/* Footer */}
        <div className="flex gap-3 px-6 py-4 border-t border-gray-800 bg-gray-900/50">
          <button
            type="button"
            onClick={onClose}
            disabled={loading}
            className="flex-1 px-4 py-2 glass rounded-lg hover:bg-white/10 transition-colors disabled:opacity-50"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={loading}
            className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader size={16} className="animate-spin" />
                Actualizando...
              </>
            ) : (
              <>
                <Check size={16} />
                Actualizar
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ManualDataForm;