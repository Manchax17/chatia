// Servicio para manejar la configuración del usuario
const SETTINGS_KEY = 'chatfit_settings';

export const getSettings = () => {
  try {
    const settings = localStorage.getItem(SETTINGS_KEY);
    return settings ? JSON.parse(settings) : {
      llmProvider: 'ollama',
      modelName: 'gemma3:1b'
    };
  } catch (error) {
    console.warn('Error loading settings from localStorage:', error);
    return {
      llmProvider: 'ollama',
      modelName: 'gemma3:1b'
    };
  }
};

export const updateSettings = (newSettings) => {
  try {
    const currentSettings = getSettings();
    const updatedSettings = { ...currentSettings, ...newSettings };
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(updatedSettings));
    return updatedSettings;
  } catch (error) {
    console.warn('Error saving settings to localStorage:', error);
    return newSettings;
  }
};