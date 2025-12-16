import api from './api';

export const chatService = {
  /**
   * Envía mensaje al chat
   */
  async sendMessage(message, chatHistory = [], options = {}) {
    const { includeWearable = true, llmProvider, modelName, chat_id } = options;
    
    console.log('🚀 Enviando mensaje con configuración:', {
      llmProvider,
      modelName,
      includeWearable,
      chat_id
    });

    const params = new URLSearchParams();
    if (chat_id) {
      params.append('chat_id', chat_id);
    }

    const response = await api.post(`/api/v1/chat/?${params.toString()}`, {
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