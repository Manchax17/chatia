// src/context/WearableContext.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { wearableService } from './services/wearableService';

const WearableContext = createContext();

export const WearableProvider = ({ children }) => {
  const [wearableData, setWearableData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Función para actualizar los datos del wearable
  const updateWearableData = (newData) => {
    setWearableData(newData);
    setError(null);
  };

  // Función para recargar los datos desde el backend
  const refreshWearableData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await wearableService.getLatestData();
      if (response && response.success) {
        setWearableData(response.data);
        setError(null);
      } else {
        setError('No se pudieron cargar los datos del wearable');
      }
    } catch (err) {
      console.error('Error refreshing wearable data:', err);
      setError('Error al obtener datos del wearable');
    } finally {
      setLoading(false);
    }
  };

  // Cargar datos al montar el componente
  useEffect(() => {
    refreshWearableData();
  }, []);

  return (
    <WearableContext.Provider value={{
      wearableData,
      setWearableData: updateWearableData,
      refreshWearableData,
      loading,
      error,
      setError
    }}>
      {children}
    </WearableContext.Provider>
  );
};

export const useWearable = () => {
  const context = useContext(WearableContext);
  if (!context) {
    throw new Error('useWearable must be used within a WearableProvider');
  }
  return context;
};