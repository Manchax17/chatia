import api from './api';

export const wearableService = {
  /**
   * Obtiene datos más recientes del wearable
   */
  async getLatestData() {
    const response = await api.get('/api/v1/wearable/latest');
    return response.data;
  },

  /**
   * Obtiene frecuencia cardíaca en tiempo real
   */
  async getHeartRate() {
    const response = await api.get('/api/v1/wearable/heart-rate');
    return response.data;
  },

  /**
   * Obtiene datos de sueño
   */
  async getSleepData() {
    const response = await api.get('/api/v1/wearable/sleep');
    return response.data;
  },

  /**
   * Obtiene actividades
   */
  async getActivities() {
    const response = await api.get('/api/v1/wearable/activities');
    return response.data;
  },

  /**
   * Fuerza sincronización
   */
  async sync() {
    const response = await api.post('/api/v1/wearable/sync');
    return response.data;
  },

  /**
   * Obtiene info de conexión
   */
  async getConnectionInfo() {
    const response = await api.get('/api/v1/wearable/connection-info');
    return response.data;
  },
   async updateManualData(data) {
    const response = await api.post('/api/v1/wearable/update-manual', data);
    return response.data;
  },
};