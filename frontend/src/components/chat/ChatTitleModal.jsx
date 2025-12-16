import React, { useState, useEffect } from 'react';
import { X, Check } from 'lucide-react';

/**
 * Modal para asignar título al primer chat
 * Aparece automáticamente después del primer mensaje
 */
export default function ChatTitleModal({ isOpen, onClose, onConfirm, defaultTitle = '' }) {
  const [title, setTitle] = useState(defaultTitle);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setTitle(defaultTitle);
    }
  }, [isOpen, defaultTitle]);

  const handleSubmit = async () => {
    if (!title.trim()) {
      alert('Por favor ingresa un título para el chat');
      return;
    }

    setIsSubmitting(true);
    try {
      console.log('📝 Guardando título:', title.trim());
      await onConfirm(title.trim());
      console.log('✅ Título guardado');
    } catch (err) {
      console.error('❌ Error guardando título:', err);
      alert(`Error: ${err.message || 'No se pudo guardar el chat'}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !isSubmitting) {
      handleSubmit();
    }
    if (e.key === 'Escape') {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-gray-900 border border-gray-700 rounded-xl shadow-2xl w-96 p-6 animate-in fade-in zoom-in-95 duration-200">
        
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-white">Nombra tu chat</h3>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-800 rounded-lg transition-colors"
          >
            <X size={20} className="text-gray-400 hover:text-white" />
          </button>
        </div>

        {/* Descripción */}
        <p className="text-sm text-gray-400 mb-4">
          Dale un nombre descriptivo a este chat para identificarlo fácilmente en tu historial.
        </p>

        {/* Input */}
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ej: Mi rutina de ejercicio, Planes de fitness..."
          className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 mb-4"
          autoFocus
          disabled={isSubmitting}
        />

        {/* Botones */}
        <div className="flex gap-3 justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 glass glass-hover rounded-lg text-gray-300 hover:text-white transition-colors disabled:opacity-50"
            disabled={isSubmitting}
          >
            Cancelar
          </button>
          <button
            onClick={handleSubmit}
            disabled={isSubmitting}
            className="px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 rounded-lg text-white font-medium flex items-center gap-2 transition-all disabled:opacity-50"
          >
            {isSubmitting ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                Guardando...
              </>
            ) : (
              <>
                <Check size={18} />
                Guardar
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
