import React, { createContext, useContext, useState, useEffect } from 'react';
import { chatsService } from './services/chatsService';
import { chatService } from './services/chatService';

const ChatsContext = createContext();

export const ChatsProvider = ({ children }) => {
  const [currentChatId, setCurrentChatId] = useState(null);
  const [chats, setChats] = useState({
    today: [],
    yesterday: [],
    this_week: [],
    this_month: [],
    older: []
  });
  const [currentChat, setCurrentChat] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showTitleModal, setShowTitleModal] = useState(false);
  const [pendingFirstMessage, setPendingFirstMessage] = useState(null);
  const [isCreatingChat, setIsCreatingChat] = useState(false);

  // Cargar lista de chats
  const loadChats = async () => {
    try {
      setLoading(true);
      setError(null);
      // Detectar timezone del navegador para agrupar correctamente (IANA + offset en minutos)
      let tz = null;
      let tzOffset = null;
      try {
        tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
      } catch (e) {
        tz = null;
      }
      try {
        tzOffset = new Date().getTimezoneOffset();
      } catch (e) {
        tzOffset = null;
      }
      const grouped = await chatsService.listChatsGrouped(tz, tzOffset);
      setChats(grouped);
    } catch (err) {
      console.error('Error cargando chats:', err);
      setError('Error cargando chats');
    } finally {
      setLoading(false);
    }
  };

  // Crear nuevo chat
  const createNewChat = async (title, wearableData) => {
    try {
      const response = await chatsService.createChat(title, wearableData);
      if (response.success) {
        setCurrentChatId(response.chat_id);
        setCurrentChat({
          chat_id: response.chat_id,
          title: response.title,
          messages: [],
          created_at: response.created_at,
          updated_at: response.created_at
        });
        await loadChats();
        return response.chat_id;
      }
    } catch (err) {
      console.error('Error creando chat:', err);
      setError('Error creando chat');
    }
  };

  // Cargar chat específico
  const loadChat = async (chatId) => {
    try {
      setLoading(true);
      setError(null);
      const chat = await chatsService.getChat(chatId);
      setCurrentChat(chat);
      setCurrentChatId(chatId);
    } catch (err) {
      console.error('Error cargando chat:', err);
      setError('Error cargando chat');
    } finally {
      setLoading(false);
    }
  };

  // Añadir mensaje al chat actual (server + local)
  const addMessage = async (role, content, modelUsed = null, toolsUsed = []) => {
    if (!currentChatId) return false;

    try {
      await chatsService.addMessage(currentChatId, role, content, modelUsed, toolsUsed);
      
      // Actualizar contexto local
      setCurrentChat(prev => ({
        ...prev,
        messages: [...prev.messages, {
          role,
          content,
          timestamp: new Date().toISOString(),
          model_used: modelUsed,
          tools_used: toolsUsed
        }],
        updated_at: new Date().toISOString()
      }));
      
      return true;
    } catch (err) {
      console.error('Error añadiendo mensaje:', err);
      return false;
    }
  };

  // Añade un mensaje SOLO localmente (no hace llamada al servidor)
  const addLocalMessage = (role, content, modelUsed = null, toolsUsed = []) => {
    if (!currentChatId) return false;

    setCurrentChat(prev => ({
      ...prev,
      messages: [
        ...(prev.messages || []),
        {
          role,
          content,
          timestamp: new Date().toISOString(),
          model_used: modelUsed,
          tools_used: toolsUsed
        }
      ],
      updated_at: new Date().toISOString()
    }));

    return true;
  };

  // Actualizar título del chat
  const updateChatTitle = async (chatId, newTitle) => {
    try {
      await chatsService.updateChatTitle(chatId, newTitle);
      if (currentChatId === chatId) {
        setCurrentChat(prev => ({ ...prev, title: newTitle }));
      }
      await loadChats();
      return true;
    } catch (err) {
      console.error('Error actualizando título:', err);
      return false;
    }
  };

  // Actualizar resumen del chat
  const updateChatSummary = async (chatId, summary) => {
    try {
      await chatsService.updateChatSummary(chatId, summary);
      if (currentChatId === chatId) {
        setCurrentChat(prev => ({ ...prev, summary }));
      }
      return true;
    } catch (err) {
      console.error('Error actualizando resumen:', err);
      return false;
    }
  };

  // Eliminar chat
  const deleteChat = async (chatId) => {
    try {
      await chatsService.deleteChat(chatId);
      if (currentChatId === chatId) {
        setCurrentChatId(null);
        setCurrentChat(null);
      }
      await loadChats();
      return true;
    } catch (err) {
      console.error('Error eliminando chat:', err);
      return false;
    }
  };

  // ✅ NUEVO: Preparar primer mensaje (mostrar modal de título)
  const preparePendingChat = (firstMessage) => {
    setPendingFirstMessage(firstMessage);
    setShowTitleModal(true);
  };

  // ✅ NUEVO: Crear chat con título y primer mensaje
  const createChatWithTitle = async (title) => {
    if (!title.trim() || !pendingFirstMessage) {
      console.error('Título o mensaje pendiente no válido');
      setError('Título o mensaje no válido');
      return;
    }

    try {
      setIsCreatingChat(true);
      setError(null);
      
      // 1. Crear chat con título
      console.log('📝 Creando chat con título:', title.trim());
      const response = await chatsService.createChat(title.trim());
      
      console.log('📝 Respuesta del servidor:', response);
      
      const chatId = response.chat_id;
      if (!chatId) {
        throw new Error(`No se pudo crear el chat. Respuesta: ${JSON.stringify(response)}`);
      }

      setCurrentChatId(chatId);
      
      // 2. Enviar el primer mensaje al endpoint de chat (backend guardará user + assistant)
      console.log('💬 Enviando primer mensaje al chat...');
      try {
        await chatService.sendMessage(pendingFirstMessage, [], { includeWearable: true, chat_id: chatId });
      } catch (sendErr) {
        console.warn('⚠️ Error enviando primer mensaje, se guardará localmente:', sendErr);
        // Guardar solo el mensaje del usuario en caso de fallo de envío
        await chatsService.addMessage(chatId, 'user', pendingFirstMessage);
      }

      // 3. Recargar lista de chats y cargar el chat creado
      console.log('📋 Recargando lista de chats...');
      await loadChats();
      console.log('📖 Cargando chat creado...');
      const chat = await chatsService.getChat(chatId);
      setCurrentChat(chat);

      // 5. Limpiar estado
      setShowTitleModal(false);
      setPendingFirstMessage(null);

      console.log('✅ Chat creado exitosamente:', chatId);
      return chatId;
    } catch (err) {
      console.error('❌ Error creando chat con título:', err);
      setError(`Error: ${err.message}`);
    } finally {
      setIsCreatingChat(false);
    }
  };

  // ✅ NUEVO: Cerrar modal sin crear chat
  const closeTitleModal = () => {
    setShowTitleModal(false);
    setPendingFirstMessage(null);
  };

  // Cargar chats al montar
  useEffect(() => {
    loadChats();
  }, []);

  return (
    <ChatsContext.Provider value={{
      currentChatId,
      setCurrentChatId,
      chats,
      currentChat,
      loading,
      error,
      showTitleModal,
      pendingFirstMessage,
      isCreatingChat,
      loadChats,
      createNewChat,
      loadChat,
      addMessage,
      addLocalMessage,
      updateChatTitle,
      updateChatSummary,
      deleteChat,
      preparePendingChat,
      createChatWithTitle,
      closeTitleModal
    }}>
      {children}
    </ChatsContext.Provider>
  );
};

export const useChats = () => {
  const context = useContext(ChatsContext);
  if (!context) {
    throw new Error('useChats must be used within a ChatsProvider');
  }
  return context;
};
