// src/context/WearableContext.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';

const WearableContext = createContext();

export const WearableProvider = ({ children }) => {
  const [wearableData, setWearableData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Función para actualizar los datos del wearable
  const updateWearableData = (newData) => {
    setWearableData(newData);
  };

  // Función para recargar los datos desde el backend
  const refreshWearableData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Aquí deberías llamar a tu servicio para obtener los datos más recientes
      // Por ahora, solo actualizamos el estado con los datos que recibimos
      // En una implementación real, esto debería hacer una llamada a la API
      // const response = await wearableService.getLatestData();
      // if (response.success) {
      //   setWearableData(response.data);
      // }
    } catch (err) {
      console.error('Error refreshing wearable data:', err);
      setError('Error al obtener datos del wearable');
    } finally {
      setLoading(false);
    }
  };

  return (
    <WearableContext.Provider value={{
      wearableData,
      setWearableData: updateWearableData,
      refreshWearableData,
      loading,
      error
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