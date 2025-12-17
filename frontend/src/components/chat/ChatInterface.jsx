import React, { useState, useRef, useEffect } from 'react';
import { AlertCircle, RefreshCw, Bot, Cpu, Zap, Brain, Cog } from 'lucide-react';
import MessageBubble from './MessageBubble';
import MessageInput from './MessageInput';
import TypingIndicator from './TypingIndicator';
import ChatTitleModal from './ChatTitleModal';
import { chatService } from '../../services/chatService';
import { useChats } from '../../ChatsContext';

const ChatInterface = ({ wearableData, currentSettings, onSettingsChange }) => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showModelSelector, setShowModelSelector] = useState(false);
  const messagesEndRef = useRef(null);

  // ✅ Usar contexto de chats
  const { 
    currentChatId, 
    currentChat, 
    addMessage,
    addLocalMessage,
    preparePendingChat,
    createChatWithTitle,
    closeTitleModal,
    showTitleModal,
    pendingFirstMessage,
    isCreatingChat
  } = useChats();

  // ✅ Usar settings desde props
  const settings = currentSettings || {
    llmProvider: 'ollama',
    modelName: 'gemma3:1b'  // ← Actualizado al modelo por defecto
  };

  // ✅ Sincronizar mensajes desde el chat actual
  useEffect(() => {
    if (currentChat && currentChat.messages) {
      setMessages(currentChat.messages);
    } else {
      setMessages([]);
    }
  }, [currentChat]);

  // ✅ Definir modelos disponibles
  const availableModels = {
    ollama: [
      { value: 'gemma3:1b', label: 'Gemma3 1B' },
      { value: 'llama3.1:8b', label: 'Llama3.1 8B' },
      { value: 'mistral:7b', label: 'Mistral 7B' },
      { value: 'phi3:3.8b', label: 'Phi3 3.8B' }
    ],
    groq: [
      { value: 'llama3-70b-8192', label: 'Llama3 70B' },
      { value: 'llama3-8b-8192', label: 'Llama3 8B' },
      { value: 'llama-3.3-70b-versatile', label: 'Llama 3.3 70B Versatile' },
      { value: 'mixtral-8x7b-32768', label: 'Mixtral 8x7B' },
      { value: 'gemma-7b-it', label: 'Gemma 7B' }
    ],
    openai: [
      { value: 'gpt-4-turbo-preview', label: 'GPT-4 Turbo' },
      { value: 'gpt-4', label: 'GPT-4' },
      { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' }
    ],
    huggingface: [
      { value: 'meta-llama/Llama-2-7b-chat-hf', label: 'Llama 2 7B' },
      { value: 'microsoft/DialoGPT-medium', label: 'DialoGPT Medium' }
    ]
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSendMessage = async (messageText) => {
    if (!messageText.trim()) return;

    // ✅ NUEVO: Si no hay chat, mostrar modal para crear uno
    if (!currentChatId) {
      preparePendingChat(messageText);
      return;
    }

    // Añadir mensaje del usuario localmente (no hace POST adicional)
    addLocalMessage('user', messageText);

    setIsLoading(true);
    setError(null);

    try {
      // Construir historial incluyendo el mensaje que acabamos de añadir localmente
      const chatHistory = [
        ...messages.map(msg => ({ role: msg.role, content: msg.content })),
        { role: 'user', content: messageText }
      ];

      console.log('🚀 Enviando mensaje con configuración:', {
        provider: settings.llmProvider,
        model: settings.modelName
      });

      // ✅ Usar la configuración actual del padre (App)
      const response = await chatService.sendMessage(
        messageText,
        chatHistory,
        { 
          includeWearable: true,
          llmProvider: settings.llmProvider,
          modelName: settings.modelName,
          chat_id: currentChatId  // ← Pasar chat_id para persistencia
        }
      );

      // Añadir la respuesta del asistente SOLO localmente (el backend ya la guarda)
      addLocalMessage('assistant', response.response, settings.modelName, response.tools_used);

    } catch (err) {
      console.error('Error sending message:', err);
      setError(err.response?.data?.detail || 'Error al enviar el mensaje');
      
      const errorMessage = {
        role: 'assistant',
        content: 'Lo siento, hubo un error al procesar tu mensaje. Por favor intenta de nuevo.',
        error: true,
        timestamp: new Date(),
      };
      
      addLocalMessage('assistant', errorMessage.content, null, []);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    if (window.confirm('¿Estás seguro de que quieres limpiar el chat?')) {
      setMessages([]);
      setError(null);
    }
  };

  const handleModelChange = (provider, model) => {
    const newSettings = {
      llmProvider: provider,
      modelName: model
    };
    onSettingsChange(newSettings);
    setShowModelSelector(false);
  };

  const getProviderIcon = (provider) => {
    switch (provider) {
      case 'ollama': return <Cpu size={14} />;
      case 'groq': return <Zap size={14} />;
      case 'openai': return <Brain size={14} />;
      case 'huggingface': return <Cog size={14} />;
      default: return <Cpu size={14} />;
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex-shrink-0 px-6 py-4 border-b border-gray-800 bg-gray-900/50 backdrop-blur-xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-bold text-white">Chat con CHATFIT AI</h2>
            <button
              onClick={() => setShowModelSelector(!showModelSelector)}
              className="px-3 py-1 text-xs glass glass-hover rounded-lg flex items-center gap-2 transition-all hover:bg-gray-800/50"
            >
              {getProviderIcon(settings.llmProvider)}
              <span className="text-gray-300">{settings.modelName}</span>
              <span className="text-gray-500 text-xs">({settings.llmProvider})</span>
            </button>
          </div>
          
          {messages.length > 0 && (
            <button
              onClick={handleClearChat}
              className="px-3 py-2 text-sm glass glass-hover rounded-lg text-gray-300 hover:text-white transition-all"
            >
              <RefreshCw size={16} className="inline mr-1" />
              Limpiar
            </button>
          )}
        </div>

        {/* Selector de modelo */}
        {showModelSelector && (
          <div className="mt-3 p-3 bg-gray-800/50 rounded-lg border border-gray-700">
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(availableModels).map(([provider, models]) => (
                <div key={provider} className="space-y-1">
                  <div className="text-xs text-gray-400 font-semibold flex items-center gap-1">
                    {getProviderIcon(provider)}
                    {provider.toUpperCase()}
                  </div>
                  {models.map((model) => (
                    <button
                      key={model.value}
                      onClick={() => handleModelChange(provider, model.value)}
                      className={`w-full text-xs px-2 py-1 rounded text-left transition-all ${
                        settings.llmProvider === provider && settings.modelName === model.value
                          ? 'bg-blue-600 text-white'
                          : 'text-gray-300 hover:bg-gray-700'
                      }`}
                    >
                      {model.label}
                    </button>
                  ))}
                </div>
              ))}
            </div>
          </div>
        )}

        {error && (
          <div className="mt-3 px-4 py-2 bg-red-900/30 border border-red-700 rounded-lg flex items-center gap-2 text-red-200">
            <AlertCircle size={16} />
            <span className="text-sm">{error}</span>
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6 scrollbar-thin">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center max-w-md">
              <div className="w-20 h-20 mx-auto mb-4 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center">
                <Bot size={40} className="text-white" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-2">
                ¡Hola! Soy CHATFIT AI
              </h3>
              <p className="text-gray-400 mb-6">
                Tu asistente personal de fitness y salud. Puedo ayudarte con:
              </p>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="glass rounded-lg p-3 text-left">
                  <div className="text-2xl mb-1">📊</div>
                  <div className="text-white font-semibold">Análisis de datos</div>
                  <div className="text-gray-400 text-xs">De tu wearable Xiaomi</div>
                </div>
                <div className="glass rounded-lg p-3 text-left">
                  <div className="text-2xl mb-1">🎯</div>
                  <div className="text-white font-semibold">Consejos personalizados</div>
                  <div className="text-gray-400 text-xs">Basados en ciencia</div>
                </div>
                <div className="glass rounded-lg p-3 text-left">
                  <div className="text-2xl mb-1">💪</div>
                  <div className="text-white font-semibold">Planes de ejercicio</div>
                  <div className="text-gray-400 text-xs">Adaptados a ti</div>
                </div>
                <div className="glass rounded-lg p-3 text-left">
                  <div className="text-2xl mb-1">🧮</div>
                  <div className="text-white font-semibold">Cálculos de salud</div>
                  <div className="text-gray-400 text-xs">IMC, calorías, más</div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <MessageBubble
                key={index}
                message={message}
                isUser={message.role === 'user'}
              />
            ))}
            {isLoading && <TypingIndicator />}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="flex-shrink-0">
        <MessageInput
          onSend={handleSendMessage}
          isLoading={isLoading}
          disabled={false}
        />
      </div>

      {/* ✅ NUEVO: Modal para título del primer chat */}
      <ChatTitleModal
        isOpen={showTitleModal}
        onClose={closeTitleModal}
        onConfirm={createChatWithTitle}
        defaultTitle={pendingFirstMessage ? pendingFirstMessage.substring(0, 50) : ''}
      />
    </div>
  );
};

export default ChatInterface;