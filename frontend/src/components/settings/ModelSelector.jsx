import React, { useState, useEffect } from 'react';
import { Cpu, Check, AlertCircle, Loader } from 'lucide-react';
import { chatService } from '../../services/chatService';

// ✅ Añadido: Servicio para manejar la configuración
const SETTINGS_KEY = 'chatfit_settings';

const getSettings = () => {
  try {
    const settings = localStorage.getItem(SETTINGS_KEY);
    return settings ? JSON.parse(settings) : {
      llmProvider: 'ollama',
      modelName: 'gemma3:1b'
    };
  } catch (error) {
    console.warn('Error loading settings from localStorage:', error);
    return {
      llmProvider: 'ollama',
      modelName: 'gemma3:1b'
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

const ModelSelector = ({ onModelChange, currentSettings }) => {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  // ✅ Usar la configuración actual como estado inicial
  const [selectedProvider, setSelectedProvider] = useState(currentSettings?.llmProvider || 'ollama');
  const [selectedModel, setSelectedModel] = useState(currentSettings?.modelName || 'gemma3:1b');

  useEffect(() => {
    fetchModels();
  }, []);

  // ✅ Actualizar selección cuando cambie la configuración actual
  useEffect(() => {
    if (currentSettings) {
      setSelectedProvider(currentSettings.llmProvider);
      setSelectedModel(currentSettings.modelName);
    }
  }, [currentSettings]);

  const fetchModels = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('🔍 Fetching models...');
      
      const data = await chatService.getAvailableModels();
      console.log('✅ Models received:', data);
      
      setModels(data);

      // ✅ Si no hay configuración actual, usar la del backend
      if (!currentSettings) {
        const currentProvider = data.find(p => p.available);
        if (currentProvider) {
          setSelectedProvider(currentProvider.provider);
          setSelectedModel(currentProvider.current_model);
        }
      }
    } catch (err) {
      console.error('❌ Error fetching models:', err);
      setError(err.message || 'Error al cargar modelos');
    } finally {
      setLoading(false);
    }
  };

  const handleProviderChange = (provider) => {
    const providerData = models.find(m => m.provider === provider);
    if (providerData && providerData.available) {
      setSelectedProvider(provider);
      // ✅ Usar el modelo actual del proveedor si no hay uno seleccionado
      const modelToSelect = providerData.current_model || providerData.models[0];
      setSelectedModel(modelToSelect);
      
      // ✅ Actualizar configuración y notificar
      const newSettings = { llmProvider: provider, modelName: modelToSelect };
      updateSettings(newSettings);
      if (onModelChange) {
        onModelChange(provider, modelToSelect);
      }
    }
  };

  const handleModelChange = (model) => {
    setSelectedModel(model);
    
    // ✅ Actualizar configuración y notificar
    const newSettings = { llmProvider: selectedProvider, modelName: model };
    updateSettings(newSettings);
    if (onModelChange) {
      onModelChange(selectedProvider, model);
    }
  };

  if (loading) {
    return (
      <div className="glass rounded-xl p-6">
        <div className="flex items-center justify-center py-8">
          <Loader size={24} className="animate-spin text-blue-500" />
          <span className="ml-3 text-gray-400">Cargando modelos...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass rounded-xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <AlertCircle size={24} className="text-red-500" />
          <div>
            <h3 className="text-lg font-bold text-white">Error</h3>
            <p className="text-sm text-gray-400">{error}</p>
          </div>
        </div>
        <button
          onClick={fetchModels}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white text-sm"
        >
          Reintentar
        </button>
      </div>
    );
  }

  if (models.length === 0) {
    return (
      <div className="glass rounded-xl p-6">
        <div className="flex items-center gap-3">
          <AlertCircle size={24} className="text-yellow-500" />
          <div>
            <h3 className="text-lg font-bold text-white">Sin modelos</h3>
            <p className="text-sm text-gray-400">No se encontraron modelos disponibles</p>
          </div>
        </div>
      </div>
    );
  }

  const currentProviderData = models.find(m => m.provider === selectedProvider);

  return (
    <div className="glass rounded-xl p-6">
      <div className="flex items-center gap-3 mb-6">
        <Cpu size={24} className="text-blue-500" />
        <div>
          <h3 className="text-lg font-bold text-white">Modelo LLM</h3>
          <p className="text-sm text-gray-400">Selecciona el proveedor y modelo a usar</p>
        </div>
      </div>

      {/* Provider Selector */}
      <div className="mb-6">
        <label className="text-sm text-gray-400 mb-2 block">Proveedor</label>
        <div className="grid grid-cols-3 gap-2">
          {models.map((provider) => (
            <button
              key={provider.provider}
              onClick={() => handleProviderChange(provider.provider)}
              disabled={!provider.available}
              className={`px-4 py-3 rounded-lg border-2 transition-all ${
                selectedProvider === provider.provider
                  ? 'border-blue-500 bg-blue-500/10 text-white'
                  : provider.available
                  ? 'border-gray-700 bg-gray-800/50 text-gray-300 hover:border-gray-600'
                  : 'border-gray-800 bg-gray-900/50 text-gray-600 cursor-not-allowed'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold capitalize">{provider.provider}</span>
                {selectedProvider === provider.provider && (
                  <Check size={16} className="text-blue-500" />
                )}
                {!provider.available && (
                  <AlertCircle size={16} className="text-gray-600" />
                )}
              </div>
              <div className="text-xs mt-1 opacity-75">
                {provider.available ? 'Disponible' : 'No disponible'}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Model Selector */}
      {currentProviderData && currentProviderData.models.length > 0 && (
        <div>
          <label className="text-sm text-gray-400 mb-2 block">
            Modelo ({currentProviderData.models.length} disponibles)
          </label>
          <div className="space-y-2 max-h-64 overflow-y-auto scrollbar-thin">
            {currentProviderData.models.map((model) => (
              <button
                key={model}
                onClick={() => handleModelChange(model)}
                className={`w-full px-4 py-3 rounded-lg border transition-all text-left ${
                  selectedModel === model
                    ? 'border-blue-500 bg-blue-500/10 text-white'
                    : 'border-gray-700 bg-gray-800/50 text-gray-300 hover:border-gray-600'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-sm">{model}</span>
                  {selectedModel === model && (
                    <Check size={16} className="text-blue-500" />
                  )}
                </div>
                {model === currentProviderData.current_model && (
                  <div className="text-xs text-blue-400 mt-1">Modelo actual</div>
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Info */}
      <div className="mt-4 px-3 py-2 bg-blue-900/20 border border-blue-700/50 rounded-lg text-xs text-blue-200">
        <strong>Nota:</strong> Cambiar el modelo afectará la siguiente conversación. Los cambios se aplican por sesión.
      </div>
    </div>
  );
};

export default ModelSelector;