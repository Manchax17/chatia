import api from './api';

export const apiService = {
  /**
   * Health check
   */
  async healthCheck() {
    const response = await api.get('/health');
    return response.data;
  },

  /**
   * Obtiene configuración
   */
  async getConfig() {
    const response = await api.get('/config');
    return response.data;
  },

  /**
   * Obtiene info del root
   */
  async getRootInfo() {
    const response = await api.get('/');
    return response.data;
  },
};