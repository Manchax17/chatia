import api from './api';

export const chatsService = {
  /**
   * Crea un nuevo chat
   */
  async createChat(title, wearableData) {
    const response = await api.post('/api/v1/chats/create', {
      title,
      wearable_data: wearableData
    });
    return response.data;
  },

  /**
   * Obtiene lista de chats agrupados por período
   */
  async listChatsGrouped(userTz = null, userTzOffset = null) {
    const params = {};
    if (userTz) params.user_tz = userTz;
    if (userTzOffset !== null && userTzOffset !== undefined) params.user_tz_offset = userTzOffset;
    const response = await api.get('/api/v1/chats', { params });
    return response.data;
  },

  /**
   * Obtiene detalle completo de un chat
   */
  async getChat(chatId) {
    const response = await api.get(`/api/v1/chats/${chatId}`);
    return response.data;
  },

  /**
   * Obtiene historial de mensajes de un chat
   */
  async getChatHistory(chatId) {
    const response = await api.get(`/api/v1/chats/${chatId}/history`);
    return response.data;
  },

  /**
   * Añade un mensaje a un chat
   */
  async addMessage(chatId, role, content, modelUsed = null, toolsUsed = []) {
    const response = await api.post(`/api/v1/chats/${chatId}/message`, {
      role,
      content,
      model_used: modelUsed,
      tools_used: toolsUsed
    });
    return response.data;
  },

  /**
   * Actualiza el título de un chat
   */
  async updateChatTitle(chatId, title) {
    const response = await api.put(`/api/v1/chats/${chatId}/title`, {
      title
    });
    return response.data;
  },

  /**
   * Actualiza el resumen de un chat
   */
  async updateChatSummary(chatId, summary) {
    const response = await api.put(`/api/v1/chats/${chatId}/summary`, {
      summary
    });
    return response.data;
  },

  /**
   * Elimina un chat
   */
  async deleteChat(chatId) {
    const response = await api.delete(`/api/v1/chats/${chatId}`);
    return response.data;
  },

  /**
   * Guarda valor en memoria global
   */
  async saveGlobalMemory(key, value) {
    const response = await api.post(`/api/v1/memory/global/${key}`, value);
    return response.data;
  },

  /**
   * Obtiene valor de memoria global
   */
  async getGlobalMemory(key, defaultValue) {
    const response = await api.get(`/api/v1/memory/global/${key}`, {
      params: { default: defaultValue }
    });
    return response.data;
  },

  /**
   * Guarda valor en memoria de sesión
   */
  async saveSessionMemory(sessionId, key, value) {
    const response = await api.post(`/api/v1/memory/session/${sessionId}/${key}`, value);
    return response.data;
  },

  /**
   * Obtiene valor de memoria de sesión
   */
  async getSessionMemory(sessionId, key, defaultValue) {
    const response = await api.get(`/api/v1/memory/session/${sessionId}/${key}`, {
      params: { default: defaultValue }
    });
    return response.data;
  },

  /**
   * Obtiene toda la memoria de una sesión
   */
  async getAllSessionMemory(sessionId) {
    const response = await api.get(`/api/v1/memory/session/${sessionId}`);
    return response.data;
  }
};
