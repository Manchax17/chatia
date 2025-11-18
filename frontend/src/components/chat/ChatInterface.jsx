import React, { useState, useRef, useEffect } from 'react';
import { AlertCircle, RefreshCw, Bot } from 'lucide-react';import MessageBubble from './MessageBubble';
import MessageInput from './MessageInput';
import TypingIndicator from './TypingIndicator';
import { chatService } from '../../services/chatService';

const ChatInterface = ({ wearableData }) => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSendMessage = async (messageText) => {
    if (!messageText.trim()) return;

    // Agregar mensaje del usuario
    const userMessage = {
      role: 'user',
      content: messageText,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      // Preparar historial
      const chatHistory = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      // Enviar mensaje
      const response = await chatService.sendMessage(
        messageText,
        chatHistory,
        { includeWearable: true }
      );

      // Agregar respuesta del asistente
      const assistantMessage = {
        role: 'assistant',
        content: response.response,
        tools_used: response.tools_used,
        model_info: response.model_info,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);

    } catch (err) {
      console.error('Error sending message:', err);
      setError(err.response?.data?.detail || 'Error al enviar el mensaje');
      
      // Agregar mensaje de error
      const errorMessage = {
        role: 'assistant',
        content: 'Lo siento, hubo un error al procesar tu mensaje. Por favor intenta de nuevo.',
        error: true,
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, errorMessage]);
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

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex-shrink-0 px-6 py-4 border-b border-gray-800 bg-gray-900/50 backdrop-blur-xl">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white">Chat con CHATFIT AI</h2>
            <p className="text-sm text-gray-400">
              Pregunta sobre fitness, salud o tus datos del wearable
            </p>
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

        {/* Error banner */}
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
    </div>
  );
};

export default ChatInterface;