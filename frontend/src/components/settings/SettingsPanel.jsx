import React, { useState, useEffect } from 'react';
import { Settings, X, Info, Server, Activity } from 'lucide-react';
import ModelSelector from './ModelSelector';
import { apiService } from '../../services/apiService';

const SettingsPanel = ({ isOpen, onClose, onModelChange }) => {
  const [apiInfo, setApiInfo] = useState(null);
  const [healthStatus, setHealthStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isOpen) {
      fetchData();
    }
  }, [isOpen]);

  const fetchData = async () => {
    setLoading(true);
    await Promise.all([
      fetchApiInfo(),
      fetchHealth()
    ]);
    setLoading(false);
  };

  const fetchApiInfo = async () => {
    try {
      console.log('🔍 Fetching API info...');
      const data = await apiService.getRootInfo();
      console.log('✅ API info received:', data);
      setApiInfo(data);
    } catch (err) {
      console.error('❌ Error fetching API info:', err);
    }
  };

  const fetchHealth = async () => {
    try {
      console.log('🔍 Fetching health status...');
      const data = await apiService.healthCheck();
      console.log('✅ Health status received:', data);
      setHealthStatus(data);
    } catch (err) {
      console.error('❌ Error fetching health:', err);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="w-full max-w-2xl max-h-[90vh] bg-gray-900 rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-800 flex items-center justify-between bg-gray-900/50 backdrop-blur-xl">
          <div className="flex items-center gap-3">
            <Settings size={24} className="text-blue-500" />
            <div>
              <h2 className="text-xl font-bold text-white">Configuración</h2>
              <p className="text-sm text-gray-400">Ajusta modelos y preferencias</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-80px)] scrollbar-thin">
          <div className="space-y-6">
            {/* Model Selector */}
            <ModelSelector onModelChange={onModelChange} />

            {/* API Status */}
            <div className="glass rounded-xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <Server size={24} className="text-green-500" />
                <div>
                  <h3 className="text-lg font-bold text-white">Estado del Backend</h3>
                  <p className="text-sm text-gray-400">Información de la API</p>
                </div>
              </div>

              {loading ? (
                <div className="text-center py-4 text-gray-400">
                  Cargando información...
                </div>
              ) : apiInfo ? (
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Versión:</span>
                    <span className="text-white font-mono">{apiInfo.version}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Estado:</span>
                    <span className="text-green-400 font-semibold">{apiInfo.status}</span>
                  </div>
                  {apiInfo.features && (
                    <>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">LLM Provider:</span>
                        <span className="text-white capitalize">{apiInfo.features.llm_provider}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">Embeddings:</span>
                        <span className="text-white capitalize">{apiInfo.features.embedding_provider}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">Wearable:</span>
                        <span className="text-white capitalize">{apiInfo.features.wearable_connection}</span>
                      </div>
                    </>
                  )}
                </div>
              ) : (
                <div className="text-center py-4 text-red-400">
                  Error al cargar información de la API
                </div>
              )}
            </div>

            {/* Health Status */}
            {healthStatus && healthStatus.components && (
              <div className="glass rounded-xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <Activity size={24} className="text-blue-500" />
                  <div>
                    <h3 className="text-lg font-bold text-white">Estado de Componentes</h3>
                    <p className="text-sm text-gray-400">Verificación de salud</p>
                  </div>
                </div>

                <div className="space-y-2">
                  {Object.entries(healthStatus.components).map(([key, value]) => {
                    const isHealthy = typeof value === 'object' 
                      ? value.available || value.status === 'ok'
                      : value === 'ok';

                    return (
                      <div
                        key={key}
                        className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0"
                      >
                        <span className="text-gray-300 capitalize">{key.replace('_', ' ')}</span>
                        <span className={`text-sm font-semibold ${
                          isHealthy ? 'text-green-400' : 'text-red-400'
                        }`}>
                          {isHealthy ? '✓ OK' : '✗ No disponible'}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Info */}
            <div className="glass rounded-xl p-6">
              <div className="flex items-start gap-3">
                <Info size={20} className="text-blue-500 flex-shrink-0 mt-0.5" />
                <div className="text-sm text-gray-300 space-y-2">
                  <p>
                    <strong className="text-white">CHATFIT AI</strong> es un asistente inteligente de fitness que combina:
                  </p>
                  <ul className="list-disc list-inside space-y-1 text-gray-400">
                    <li>Modelos LLM locales (Ollama, HuggingFace) y OpenAI</li>
                    <li>Integración con dispositivos Xiaomi wearables</li>
                    <li>Base de conocimiento verificada (RAG)</li>
                    <li>Herramientas de cálculo de salud</li>
                  </ul>
                  <p className="text-xs text-gray-500 mt-3">
                    Versión {apiInfo?.version || '2.0.0'} • Desarrollado con React + FastAPI
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPanel;