import React, { useState, useEffect } from 'react';
import { Settings, Github, Heart } from 'lucide-react';
import ChatInterface from './components/chat/ChatInterface';
import WearableStats from './components/wearable/WearableStats';
import SettingsPanel from './components/settings/SettingsPanel';
import { WearableProvider } from './WearableContext';

// ✅ Añadido: Servicio para manejar la configuración
const SETTINGS_KEY = 'chatfit_settings';

// Si se usa OLLAMA.
const getSettings = () => {
  try {
    const settings = localStorage.getItem(SETTINGS_KEY);
    return settings ? JSON.parse(settings) : {
      llmProvider: 'ollama',
      modelName: 'gemma3:1b'  // ← Cambiado a tu modelo Ollama por defecto
    };
  } catch (error) {
    console.warn('Error loading settings from localStorage:', error);
    return {
      llmProvider: 'ollama',
      modelName: 'gemma3:1b'
    };
  }
};

function App() {
  const [wearableData, setWearableData] = useState(null);
  const [showSettings, setShowSettings] = useState(false);
  
  // ✅ CAMBIO IMPORTANTE: Estado centralizado para la configuración
  const [appSettings, setAppSettings] = useState(getSettings);

  // ✅ Cargar configuración al iniciar
  useEffect(() => {
    const loadSettings = () => {
      const settings = getSettings();
      setAppSettings(settings);
    };
    
    loadSettings();
    
    // ✅ Escuchar cambios en localStorage desde otras pestañas
    const handleStorageChange = (e) => {
      if (e.key === SETTINGS_KEY) {
        try {
          const newSettings = JSON.parse(e.newValue);
          setAppSettings(newSettings);
        } catch (error) {
          console.warn('Error parsing settings from storage:', error);
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  // ✅ Función para actualizar configuración
  const handleSettingsChange = (newSettings) => {
    try {
      // Actualizar localStorage
      localStorage.setItem(SETTINGS_KEY, JSON.stringify(newSettings));
      // Actualizar estado
      setAppSettings(newSettings);
      console.log('✅ Configuración actualizada:', newSettings);
    } catch (error) {
      console.error('❌ Error actualizando configuración:', error);
    }
  };

  const handleWearableDataUpdate = (data) => {
    setWearableData(data);
  };

  return (
    <WearableProvider>
      <div className="h-screen w-screen overflow-hidden bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950">
        
        {/* Header */}
        <header className="fixed top-0 left-0 right-0 z-40 bg-gray-900/80 backdrop-blur-xl border-b border-gray-800">
          <div className="px-6 py-4 flex items-center justify-between">
            
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                <Heart size={24} className="text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">CHATFIT AI</h1>
                <p className="text-xs text-gray-400">
                  {appSettings.modelName} ({appSettings.llmProvider})
                </p>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-3">

              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 glass glass-hover rounded-lg transition-all"
                title="GitHub"
              >
                <Github size={20} className="text-gray-400 hover:text-white transition-colors" />
              </a>

              <button
                onClick={() => setShowSettings(true)}
                className="px-4 py-2 glass glass-hover rounded-lg flex items-center gap-2 transition-all"
              >
                <Settings size={18} />
                <span className="text-sm font-medium">Configuración</span>
              </button>

            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="pt-[73px] h-full">
          <div className="h-full flex">
            
            {/* Wearable Sidebar */}
            <aside className="w-80 border-r border-gray-800 bg-gray-900/50 backdrop-blur-xl overflow-hidden flex-shrink-0">
              <WearableStats />
            </aside>

            {/* Chat Area */}
            <section className="flex-1 overflow-hidden">
              <ChatInterface 
                currentSettings={appSettings}
                onSettingsChange={handleSettingsChange}
              />
            </section>

          </div>
        </main>

        {/* Settings Panel */}
        <SettingsPanel
          isOpen={showSettings}
          onClose={() => setShowSettings(false)}
          onModelChange={handleSettingsChange}  // ✅ Pasar la función actualizada
        />

        {/* Background Effects */}
        <div className="fixed inset-0 pointer-events-none overflow-hidden -z-10">
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"></div>
          <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl"></div>
        </div>
      </div>
    </WearableProvider>
  );
}

export default App;