import React, { useState, useEffect } from 'react';
import { Settings, X, Info, Server, Activity, CheckCircle } from 'lucide-react';
import ModelSelector from './ModelSelector';
import { apiService } from '../../services/apiService';

// ✅ Añadido: Servicio para manejar la configuración
const SETTINGS_KEY = 'chatfit_settings';

const getSettings = () => {
  try {
    const settings = localStorage.getItem(SETTINGS_KEY);
    return settings ? JSON.parse(settings) : {
      llmProvider: 'ollama',
      modelName: 'llama2'
    };
  } catch (error) {
    console.warn('Error loading settings from localStorage:', error);
    return {
      llmProvider: 'ollama',
      modelName: 'llama2'
    };
  }
};

const updateSettings = (newSettings) => {
  try {
    const currentSettings = getSettings();
    const updatedSettings = { ...currentSettings, ...newSettings };
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(updatedSettings));
    return updatedSettings;
  } catch (error) {
    console.warn('Error saving settings to localStorage:', error);
    return newSettings;
  }
};

const SettingsPanel = ({ isOpen, onClose, onModelChange }) => {
  const [apiInfo, setApiInfo] = useState(null);
  const [healthStatus, setHealthStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentSettings, setCurrentSettings] = useState(getSettings);
  const [pendingSettings, setPendingSettings] = useState(getSettings); // ✅ Nuevo estado para cambios pendientes
  const [saveStatus, setSaveStatus] = useState(null); // ✅ Estado para mostrar resultado

  useEffect(() => {
    if (isOpen) {
      fetchData();
      setCurrentSettings(getSettings());
      setPendingSettings(getSettings()); // ✅ Inicializar con configuración actual
      setSaveStatus(null); // ✅ Resetear estado al abrir
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

  // ✅ Nueva función para manejar cambios pendientes (sin aplicar todavía)
  const handlePendingModelChange = (provider, model) => {
    const newPendingSettings = { llmProvider: provider, modelName: model };
    setPendingSettings(newPendingSettings);
    setSaveStatus(null); // Resetear estado al hacer nuevos cambios
  };

  // ✅ NUEVA FUNCIÓN: Aplicar cambios y guardar
  const handleApplyChanges = async () => {
    try {
      setSaveStatus('saving');
      
      // Actualizar configuración en localStorage
      const updatedSettings = updateSettings(pendingSettings);
      setCurrentSettings(updatedSettings);
      
      // Notificar al componente padre
      if (onModelChange) {
        onModelChange(pendingSettings);
      }

      // ✅ Forzar una actualización enviando un mensaje de prueba al backend
      // Esto asegura que el backend reciba la nueva configuración
      try {
        await fetch('http://localhost:8000/api/v1/chat/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: "ping", // Mensaje de prueba
            chat_history: [],
            include_wearable: false,
            llm_provider: pendingSettings.llmProvider,
            model_name: pendingSettings.modelName
          })
        });
      } catch (testError) {
        console.log('⚠️ Test message failed, but settings are saved');
      }

      setSaveStatus('success');
      
      // Auto-cerrar el mensaje de éxito después de 2 segundos
      setTimeout(() => {
        setSaveStatus(null);
      }, 2000);

    } catch (error) {
      console.error('❌ Error applying settings:', error);
      setSaveStatus('error');
    }
  };

  // ✅ Verificar si hay cambios pendientes
  const hasPendingChanges = 
    pendingSettings.llmProvider !== currentSettings.llmProvider ||
    pendingSettings.modelName !== currentSettings.modelName;

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
            <ModelSelector 
              onModelChange={handlePendingModelChange} // ✅ Usar la función de cambios pendientes
              currentSettings={pendingSettings} // ✅ Usar configuración pendiente
            />

            {/* Current vs Pending Settings Display */}
            <div className="glass rounded-xl p-4 border border-gray-700">
              <div className="flex justify-between items-start mb-3">
                <h3 className="text-sm font-semibold text-gray-300">Configuración:</h3>
                {hasPendingChanges && (
                  <span className="text-xs px-2 py-1 bg-yellow-500/20 rounded-full text-yellow-300 border border-yellow-500/30">
                    Cambios pendientes
                  </span>
                )}
              </div>
              
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-gray-400 mb-1">Actual:</div>
                  <div className="flex flex-wrap gap-1">
                    <span className="text-xs px-2 py-1 bg-blue-500/20 rounded-full text-blue-300 border border-blue-500/30">
                      {currentSettings.modelName}
                    </span>
                    <span className="text-xs px-2 py-1 bg-gray-500/20 rounded-full text-gray-300 border border-gray-500/30">
                      {currentSettings.llmProvider}
                    </span>
                  </div>
                </div>
                
                <div>
                  <div className="text-gray-400 mb-1">Seleccionado:</div>
                  <div className="flex flex-wrap gap-1">
                    <span className="text-xs px-2 py-1 bg-green-500/20 rounded-full text-green-300 border border-green-500/30">
                      {pendingSettings.modelName}
                    </span>
                    <span className="text-xs px-2 py-1 bg-gray-500/20 rounded-full text-gray-300 border border-gray-500/30">
                      {pendingSettings.llmProvider}
                    </span>
                  </div>
                </div>
              </div>

              {/* ✅ Botón Aplicar Cambios */}
              {hasPendingChanges && (
                <div className="mt-4 pt-3 border-t border-gray-600">
                  <button
                    onClick={handleApplyChanges}
                    disabled={saveStatus === 'saving'}
                    className={`w-full py-2 px-4 rounded-lg font-semibold transition-all ${
                      saveStatus === 'saving' 
                        ? 'bg-gray-600 cursor-not-allowed' 
                        : 'bg-green-600 hover:bg-green-700'
                    } text-white flex items-center justify-center gap-2`}
                  >
                    {saveStatus === 'saving' ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        Aplicando...
                      </>
                    ) : saveStatus === 'success' ? (
                      <>
                        <CheckCircle size={16} />
                        ¡Aplicado!
                      </>
                    ) : (
                      '✅ Aplicar Cambios'
                    )}
                  </button>
                  
                  {saveStatus === 'error' && (
                    <div className="mt-2 text-xs text-red-400 text-center">
                      Error al aplicar cambios. Intenta nuevamente.
                    </div>
                  )}
                </div>
              )}

              {!hasPendingChanges && saveStatus === 'success' && (
                <div className="mt-3 text-xs text-green-400 text-center">
                  <CheckCircle size={14} className="inline mr-1" />
                  Configuración aplicada correctamente
                </div>
              )}
            </div>

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