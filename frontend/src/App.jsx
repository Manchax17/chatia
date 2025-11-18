import React, { useState } from 'react';
import { Settings, Github, Heart } from 'lucide-react';
import ChatInterface from './components/chat/ChatInterface';
import WearableStats from './components/wearable/WearableStats';
import SettingsPanel from './components/settings/SettingsPanel';

function App() {
  const [wearableData, setWearableData] = useState(null);
  const [showSettings, setShowSettings] = useState(false);
  const [modelConfig, setModelConfig] = useState(null);

  const handleWearableDataUpdate = (data) => {
    setWearableData(data);
  };

  const handleModelChange = (provider, model) => {
    setModelConfig({ provider, model });
    console.log('Model changed:', provider, model);
  };

  return (
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
              <p className="text-xs text-gray-400">Tu asistente personal de fitness</p>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-3">

            {/* FIX: Venía roto este <a> */}
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
            <WearableStats onDataUpdate={handleWearableDataUpdate} />
          </aside>

          {/* Chat Area */}
          <section className="flex-1 overflow-hidden">
            <ChatInterface wearableData={wearableData} modelConfig={modelConfig} />
          </section>

        </div>
      </main>

      {/* Settings Panel */}
      <SettingsPanel
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        onModelChange={handleModelChange}
      />

      {/* Background Effects */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden -z-10">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl"></div>
      </div>
    </div>
  );
}

export default App;
