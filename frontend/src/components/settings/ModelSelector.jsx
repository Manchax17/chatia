import React, { useState, useEffect } from 'react';
import { Cpu, Check, AlertCircle, Loader } from 'lucide-react';
import { chatService } from '../../services/chatService';

const ModelSelector = ({ onModelChange }) => {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedProvider, setSelectedProvider] = useState('ollama');
  const [selectedModel, setSelectedModel] = useState(null);

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('🔍 Fetching models...');
      
      const data = await chatService.getAvailableModels();
      console.log('✅ Models received:', data);
      
      setModels(data);

      // Seleccionar provider y modelo actual
      const currentProvider = data.find(p => p.available);
      if (currentProvider) {
        setSelectedProvider(currentProvider.provider);
        setSelectedModel(currentProvider.current_model);
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
      setSelectedModel(providerData.current_model);
      if (onModelChange) {
        onModelChange(provider, providerData.current_model);
      }
    }
  };

  const handleModelChange = (model) => {
    setSelectedModel(model);
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