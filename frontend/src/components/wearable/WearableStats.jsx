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
  Smartphone
} from 'lucide-react';
import StatsCard from './StatsCard';
import { wearableService } from '../../services/wearableService';

const WearableStats = ({ onDataUpdate }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [syncing, setSyncing] = useState(false);
  const [connectionInfo, setConnectionInfo] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await wearableService.getLatestData();
      
      if (response.success) {
        setData(response.data);
        if (onDataUpdate) {
          onDataUpdate(response.data);
        }
      }
    } catch (err) {
      console.error('Error fetching wearable data:', err);
      setError('Error al obtener datos del wearable');
    } finally {
      setLoading(false);
    }
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
      await fetchData();
    } catch (err) {
      console.error('Error syncing:', err);
      setError('Error al sincronizar');
    } finally {
      setSyncing(false);
    }
  };

  useEffect(() => {
    fetchData();
    fetchConnectionInfo();

    // Auto-refresh cada 5 minutos
    const interval = setInterval(fetchData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !data) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <RefreshCw size={40} className="animate-spin text-blue-500 mx-auto mb-3" />
          <p className="text-gray-400">Cargando datos del wearable...</p>
        </div>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertCircle size={40} className="text-red-500 mx-auto mb-3" />
          <p className="text-gray-300 mb-4">{error}</p>
          <button
            onClick={fetchData}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  const stepsProgress = data?.steps ? (data.steps / 10000) * 100 : 0;

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
              {data?.device_model || 'Xiaomi Band'}
            </p>
          </div>

          <button
            onClick={handleSync}
            disabled={syncing}
            className="px-3 py-2 glass glass-hover rounded-lg text-gray-300 hover:text-white transition-all disabled:opacity-50"
          >
            <RefreshCw size={16} className={`inline mr-1 ${syncing ? 'animate-spin' : ''}`} />
            Sincronizar
          </button>
        </div>

        {/* Connection info */}
        <div className="flex items-center gap-2 text-xs">
          <div className={`w-2 h-2 rounded-full ${
            data?.mock_data ? 'bg-yellow-500' : 'bg-green-500'
          }`}></div>
          <span className="text-gray-400">
            {data?.mock_data ? 'Datos de prueba' : 'Conectado'} • 
            {connectionInfo?.method === 'mock' ? ' Modo simulado' : 
             connectionInfo?.method === 'mi_fitness' ? ' Mi Fitness' : 
             connectionInfo?.method === 'bluetooth' ? ' Bluetooth' : 
             ' Desconocido'}
          </span>
        </div>

        {/* Warning si es mock */}
        {data?.mock_data && (
          <div className="mt-3 px-3 py-2 bg-yellow-900/30 border border-yellow-700 rounded-lg flex items-center gap-2 text-yellow-200 text-xs">
            <AlertCircle size={14} />
            <span>Usando datos simulados. Configura tu dispositivo Xiaomi en el backend.</span>
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
            value={data?.steps || 0}
            unit="pasos"
            color="green"
            progress={stepsProgress}
            subtext={`Objetivo: 10,000 pasos`}
          />

          {/* Calorías */}
          <StatsCard
            icon={Flame}
            label="Calorías"
            value={data?.calories || 0}
            unit="kcal"
            color="orange"
            subtext="Quemadas hoy"
          />

          {/* Frecuencia cardíaca */}
          <StatsCard
            icon={Heart}
            label="Frecuencia Cardíaca"
            value={data?.heart_rate || 0}
            unit="bpm"
            color="red"
            subtext="Promedio actual"
          />

          {/* Sueño */}
          <StatsCard
            icon={Moon}
            label="Sueño"
            value={data?.sleep_hours || 0}
            unit="horas"
            color="purple"
            subtext="Última noche"
          />

          {/* Distancia */}
          <StatsCard
            icon={TrendingUp}
            label="Distancia"
            value={data?.distance_km?.toFixed(2) || 0}
            unit="km"
            color="blue"
            subtext="Recorrida hoy"
          />

          {/* Batería */}
          {data?.battery_level && (
            <StatsCard
              icon={Battery}
              label="Batería"
              value={data.battery_level}
              unit="%"
              color={data.battery_level > 50 ? 'green' : data.battery_level > 20 ? 'orange' : 'red'}
              progress={data.battery_level}
            />
          )}
        </div>

        {/* Última sincronización */}
        <div className="mt-6 text-center text-xs text-gray-500">
          Última sincronización: {data?.last_sync ? new Date(data.last_sync).toLocaleString('es-ES') : 'Nunca'}
        </div>
      </div>
    </div>
  );
};

export default WearableStats;