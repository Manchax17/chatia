import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Heart, 
  Flame, 
  Moon, 
  TrendingUp,
  Battery,
  RefreshCw,
  AlertCircle,
  Smartphone,
  Upload
} from 'lucide-react';
import StatsCard from './StatsCard';
import ManualDataForm from './ManualDataForm';
import { wearableService } from '../../services/wearableService';
import { useWearable } from '../../WearableContext'; // Asegúrate de importar el contexto

const WearableStats = () => {
  // Obtener estados y funciones del contexto
  const { wearableData, setWearableData, refreshWearableData, loading, error } = useWearable();

  const [syncing, setSyncing] = useState(false);
  const [connectionInfo, setConnectionInfo] = useState(null);
  const [showManualForm, setShowManualForm] = useState(false);

  // La función fetchData ahora no maneja setLoading ni setError localmente
  const fetchData = async () => {
    // Si el contexto maneja loading/error, aquí solo haces la petición
    // y actualizas el estado global de datos si es necesario.
    // Si setLoading y setError se manejan dentro de refreshWearableData o setWearableData,
    // no debes usarlos aquí directamente en este componente.
    try {
      // Opcional: Si el contexto no maneja loading/error internamente,
      // podrías necesitar un `setGlobalLoading(true)` aquí si tu contexto lo provee.
      // Pero basado en tu código, parece que el contexto lo maneja.
      // Ejemplo hipotético si tu contexto tuviera esta función:
      // setGlobalLoading(true); // <-- Esto vendría del contexto si existiera

      const response = await wearableService.getLatestData();
      
      if (response.success) {
        setWearableData(response.data); // Actualizar el estado global vía el contexto
        // El contexto probablemente ya hizo setError(null) y setLoading(false) aquí
      } else {
         // Si la respuesta no es exitosa, el contexto debería manejar el error
         // según como esté implementado refreshWearableData/setWearableData
      }
    } catch (err) {
      console.error('Error fetching wearable data:', err);
      // Manejo de error: Si el contexto no maneja errores aquí,
      // necesitarías setError(err.message) aquí, pero como lo obtienes del contexto,
      // lo más probable es que el manejo esté integrado en setWearableData o refreshWearableData.
      // Si estás seguro de que el contexto no lo maneja, tendrías que usar una función
      // del contexto para setear el error global, p.ej. setGlobalError.
      // Ejemplo hipotético:
      // setGlobalError('Error al obtener datos del wearable'); // <-- Del contexto
    }
    // finally {
    //   // No usar setLoading(false) aquí porque viene del contexto
    //   setGlobalLoading(false); // <-- Del contexto si aplica
    // }
  };

  const fetchConnectionInfo = async () => {
    try {
      const info = await wearableService.getConnectionInfo();
      setConnectionInfo(info);
    } catch (err) {
      console.error('Error fetching connection info:', err);
    }
  };

  const handleSync = async () => {
    try {
      setSyncing(true);
      await wearableService.sync();
      await fetchData(); // Recarga datos usando la función corregida
    } catch (err) {
      console.error('Error syncing:', err);
      // Manejo de error de sincronización, si es distinto del error de datos generales
      // Puedes usar setError aquí si handleSync no está integrado en el contexto
      // o una función específica para errores de sync si la tienes.
      // Por ahora, asumimos que el error general del contexto es suficiente
      // o que lo manejas de otra manera específica para sync.
    } finally {
      setSyncing(false);
    }
  };

  // Función para actualizar los datos después de una actualización manual
  const handleManualUpdate = async () => {
    await fetchData(); // Recargar los datos
    setShowManualForm(false); // Cerrar el formulario
  };

  useEffect(() => {
    fetchData();
    fetchConnectionInfo();

    // Auto-refresh cada 5 minutos
    const interval = setInterval(fetchData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []); // Agrega dependencias si refreshWearableData cambia

  // Renderizado condicional basado en `loading` y `error` del contexto
  if (loading && !wearableData) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <RefreshCw size={40} className="animate-spin text-blue-500 mx-auto mb-3" />
          <p className="text-gray-400">Cargando datos del wearable...</p>
        </div>
      </div>
    );
  }

  if (error && !wearableData) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertCircle size={40} className="text-red-500 mx-auto mb-3" />
          <p className="text-gray-300 mb-4">{error}</p>
          <button
            onClick={fetchData} // Reintenta usando la función corregida
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  const stepsProgress = wearableData?.steps ? (wearableData.steps / 10000) * 100 : 0;

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex-shrink-0 px-6 py-4 border-b border-gray-800 bg-gray-900/50 backdrop-blur-xl">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Smartphone size={24} />
              Dispositivo Xiaomi
            </h2>
            <p className="text-sm text-gray-400">
              {wearableData?.device_model || 'Xiaomi Band'}
            </p>
          </div>

          {/* Botones de acción */}
          <div className="flex items-center gap-2">
            <button
              onClick={handleSync}
              disabled={syncing}
              className="px-3 py-2 glass glass-hover rounded-lg text-gray-300 hover:text-white transition-all disabled:opacity-50 text-sm"
            >
              <RefreshCw size={16} className={`inline mr-1 ${syncing ? 'animate-spin' : ''}`} />
              Sincronizar
            </button>

            <button
              onClick={() => setShowManualForm(true)}
              className="px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white transition-all text-sm flex items-center gap-1"
            >
              <Upload size={16} />
              Cargar Datos
            </button>
          </div>
        </div>

        {/* Connection info */}
        <div className="flex items-center gap-2 text-xs">
          <div className={`w-2 h-2 rounded-full ${
            wearableData?.mock_data ? 'bg-yellow-500' : 'bg-green-500'
          }`}></div>
          <span className="text-gray-400">
            {wearableData?.mock_data ? 'Datos de prueba' : 'Conectado'} • 
            {connectionInfo?.method === 'mock' ? ' Modo simulado' : 
             connectionInfo?.method === 'manual' ? ' Modo manual' :
             connectionInfo?.method === 'mi_fitness' ? ' Mi Fitness' : 
             connectionInfo?.method === 'bluetooth' ? ' Bluetooth' : 
             ' Desconocido'}
          </span>
        </div>

        {/* Warning si es mock */}
        {wearableData?.mock_data && (
          <div className="mt-3 px-3 py-2 bg-yellow-900/30 border border-yellow-700 rounded-lg flex items-center gap-2 text-yellow-200 text-xs">
            <AlertCircle size={14} />
            <span>Usando datos simulados. Haz clic en "Cargar Datos" para usar información real de Mi Fitness.</span>
          </div>
        )}

        {/* Info si es modo manual y no hay datos */}
        {connectionInfo?.method === 'manual' && (!wearableData || wearableData.steps === 0) && (
          <div className="mt-3 px-3 py-2 bg-blue-900/30 border border-blue-700 rounded-lg flex items-center gap-2 text-blue-200 text-xs">
            <AlertCircle size={14} />
            <span>Modo manual activo. Haz clic en "Cargar Datos" para actualizar con tu información de Mi Fitness.</span>
          </div>
        )}
      </div>

      {/* Stats */}
      <div className="flex-1 overflow-y-auto px-6 py-6 scrollbar-thin">
        <div className="grid grid-cols-1 gap-4">
          {/* Pasos */}
          <StatsCard
            icon={Activity}
            label="Pasos"
            value={wearableData?.steps || 0}
            unit="pasos"
            color="green"
            progress={stepsProgress}
            subtext={`Objetivo: 10,000 pasos`}
          />

          {/* Calorías */}
          <StatsCard
            icon={Flame}
            label="Calorías"
            value={wearableData?.calories || 0}
            unit="kcal"
            color="orange"
            subtext="Quemadas hoy"
          />

          {/* Frecuencia cardíaca */}
          <StatsCard
            icon={Heart}
            label="Frecuencia Cardíaca"
            value={wearableData?.heart_rate || 0}
            unit="bpm"
            color="red"
            subtext="Promedio actual"
          />

          {/* Sueño */}
          <StatsCard
            icon={Moon}
            label="Sueño"
            value={wearableData?.sleep_hours || 0}
            unit="horas"
            color="purple"
            subtext="Última noche"
          />

          {/* Distancia */}
          <StatsCard
            icon={TrendingUp}
            label="Distancia"
            value={wearableData?.distance_km?.toFixed(2) || 0}
            unit="km"
            color="blue"
            subtext="Recorrida hoy"
          />

          {/* Batería */}
          {wearableData?.battery_level && (
            <StatsCard
              icon={Battery}
              label="Batería"
              value={wearableData.battery_level}
              unit="%"
              color={wearableData.battery_level > 50 ? 'green' : wearableData.battery_level > 20 ? 'orange' : 'red'}
              progress={wearableData.battery_level}
            />
          )}
        </div>

        {/* Última sincronización */}
        <div className="mt-6 text-center text-xs text-gray-500">
          Última sincronización: {wearableData?.last_sync ? new Date(wearableData.last_sync).toLocaleString('es-ES') : 'Nunca'}
        </div>
      </div>

      {/* Modal de carga manual */}
      {showManualForm && (
        <ManualDataForm
          onClose={() => setShowManualForm(false)}
        />
      )}
    </div>
  );
};

export default WearableStats;