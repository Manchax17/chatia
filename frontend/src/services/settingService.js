import api from './api';

export const chatService = {
  /**
   * Envía mensaje al chat
   */
  async sendMessage(message, chatHistory = [], options = {}) {
    const { includeWearable = true, llmProvider, modelName } = options;
    
    console.log('🚀 Enviando mensaje con configuración:', {
      llmProvider,
      modelName,
      includeWearable
    });

    const response = await api.post('/api/v1/chat/', {
      message,
      chat_history: chatHistory,
      include_wearable: includeWearable,
      llm_provider: llmProvider,
      model_name: modelName,
    });
    return response.data;
  },

  /**
   * Obtiene modelos disponibles
   */
  async getAvailableModels() {
    const response = await api.get('/api/v1/chat/models');
    return response.data;
  },

  /**
   * Limpia cache del wearable
   */
  async clearCache() {
    const response = await api.post('/api/v1/chat/clear-cache');
    return response.data;
  },
};