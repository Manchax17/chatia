import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader, Sparkles } from 'lucide-react';

const MessageInput = ({ onSend, isLoading, disabled }) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [message]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !isLoading && !disabled) {
      onSend(message);
      setMessage('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Sugerencias rápidas
  const suggestions = [
    '¿Cómo voy con mis pasos hoy?',
    'Calcula mi IMC',
    '¿Cuál es mi zona de frecuencia cardíaca?',
    'Dame consejos para mejorar mi sueño',
  ];

  const handleSuggestionClick = (suggestion) => {
    if (!isLoading && !disabled) {
      onSend(suggestion);
    }
  };

  return (
    <div className="border-t border-gray-800 bg-gray-900/50 backdrop-blur-xl">
      {/* Sugerencias */}
      {message === '' && (
        <div className="px-4 py-3 flex gap-2 overflow-x-auto scrollbar-thin">
          {suggestions.map((suggestion, idx) => (
            <button
              key={idx}
              onClick={() => handleSuggestionClick(suggestion)}
              disabled={isLoading || disabled}
              className="flex-shrink-0 text-xs px-3 py-1.5 glass glass-hover rounded-full text-gray-300 hover:text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Sparkles size={12} className="inline mr-1" />
              {suggestion}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit} className="px-4 py-4">
        <div className="flex gap-3 items-end">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Pregunta sobre fitness, salud o tus datos del wearable..."
              disabled={isLoading || disabled}
              rows={1}
              className="w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-2xl text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none max-h-32 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            />
          </div>

          <button
            type="submit"
            disabled={!message.trim() || isLoading || disabled}
            className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 disabled:from-gray-700 disabled:to-gray-800 text-white rounded-2xl flex items-center justify-center transition-all disabled:cursor-not-allowed disabled:opacity-50 shadow-lg hover:shadow-blue-500/50"
          >
            {isLoading ? (
              <Loader size={20} className="animate-spin" />
            ) : (
              <Send size={20} />
            )}
          </button>
        </div>

        {/* Contador de caracteres */}
        {message.length > 0 && (
          <div className="text-xs text-gray-500 mt-2 text-right">
            {message.length} caracteres
          </div>
        )}
      </form>
    </div>
  );
};

export default MessageInput;