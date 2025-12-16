import React, { useState } from 'react';
import { MessageCircle, Trash2, Edit2, Plus, ChevronDown, ChevronUp } from 'lucide-react';
import { useChats } from '../../ChatsContext';

const ChatHistory = () => {
  const { chats, currentChatId, createNewChat, loadChat, deleteChat, updateChatTitle } = useChats();
  const [expandedSections, setExpandedSections] = useState({
    today: true,
    this_week: true,
    this_month: false,
    older: false
  });
  const [editingId, setEditingId] = useState(null);
  const [editingTitle, setEditingTitle] = useState('');

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const handleNewChat = () => {
    createNewChat(`Chat ${new Date().toLocaleTimeString()}`);
  };

  const handleDeleteChat = (e, chatId) => {
    e.stopPropagation();
    if (confirm('¿Estás seguro de que deseas eliminar este chat?')) {
      deleteChat(chatId);
    }
  };

  const handleEditTitle = (e, chatId, currentTitle) => {
    e.stopPropagation();
    setEditingId(chatId);
    setEditingTitle(currentTitle);
  };

  const handleSaveTitle = async (chatId) => {
    if (editingTitle.trim()) {
      await updateChatTitle(chatId, editingTitle);
    }
    setEditingId(null);
  };

  const renderChatGroup = (title, sectionKey, chatList) => {
    if (chatList.length === 0) return null;

    const isExpanded = expandedSections[sectionKey];

    return (
      <div key={sectionKey} className="mb-4">
        {/* Encabezado de sección */}
        <button
          onClick={() => toggleSection(sectionKey)}
          className="w-full flex items-center justify-between px-3 py-2 hover:bg-gray-800 rounded-lg transition-colors"
        >
          <span className="flex items-center gap-2 text-sm font-semibold text-gray-300">
            {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            {title}
            <span className="text-xs bg-gray-700 px-2 py-0.5 rounded-full">
              {chatList.length}
            </span>
          </span>
        </button>

        {/* Lista de chats */}
        {isExpanded && (
          <div className="space-y-1 mt-2">
            {chatList.map((chat) => (
              <div
                key={chat.chat_id}
                onClick={() => loadChat(chat.chat_id)}
                className={`group px-3 py-2 rounded-lg cursor-pointer transition-colors ${
                  currentChatId === chat.chat_id
                    ? 'bg-blue-600 text-white'
                    : 'hover:bg-gray-800 text-gray-300'
                }`}
              >
                {/* Chat item */}
                <div className="flex items-center gap-2 justify-between">
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <MessageCircle size={14} className="flex-shrink-0" />
                    
                    {editingId === chat.chat_id ? (
                      <input
                        autoFocus
                        value={editingTitle}
                        onChange={(e) => setEditingTitle(e.target.value)}
                        onClick={(e) => e.stopPropagation()}
                        onBlur={() => handleSaveTitle(chat.chat_id)}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            handleSaveTitle(chat.chat_id);
                          }
                        }}
                        className="flex-1 bg-transparent outline-none text-sm"
                      />
                    ) : (
                      <div className="flex-1 min-w-0">
                        <p className="text-sm truncate font-medium">{chat.title}</p>
                        <p className="text-xs opacity-70 truncate">{chat.preview}</p>
                      </div>
                    )}
                  </div>

                  {/* Botones de acciones */}
                  <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0">
                    <button
                      onClick={(e) => handleEditTitle(e, chat.chat_id, chat.title)}
                      className="p-1 hover:bg-black/30 rounded transition-colors"
                      title="Editar título"
                    >
                      <Edit2 size={12} />
                    </button>
                    <button
                      onClick={(e) => handleDeleteChat(e, chat.chat_id)}
                      className="p-1 hover:bg-red-600/50 rounded transition-colors"
                      title="Eliminar chat"
                    >
                      <Trash2 size={12} />
                    </button>
                  </div>
                </div>

                {/* Información adicional */}
                <div className="text-xs opacity-60 ml-6 mt-1">
                  {chat.message_count} mensajes
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="w-full h-full flex flex-col bg-gray-900 rounded-lg overflow-hidden">
      {/* Encabezado */}
      <div className="px-4 py-3 border-b border-gray-800 flex items-center justify-between">
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <MessageCircle size={20} className="text-blue-500" />
          Historial de Chats
        </h3>
        <button
          onClick={handleNewChat}
          className="p-2 hover:bg-blue-600 rounded-lg transition-colors bg-blue-600/50"
          title="Nuevo chat"
        >
          <Plus size={18} />
        </button>
      </div>

      {/* Lista de chats */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {chats.today.length === 0 &&
        chats.this_week.length === 0 &&
        chats.this_month.length === 0 &&
        chats.older.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <MessageCircle size={32} className="opacity-50 mb-2" />
            <p className="text-sm">No hay chats aún</p>
            <p className="text-xs opacity-70 mt-1">Crea uno nuevo para comenzar</p>
          </div>
        ) : (
          <>
            {renderChatGroup('🕐 Hoy', 'today', chats.today)}
            {renderChatGroup('📅 Esta semana', 'this_week', chats.this_week)}
            {renderChatGroup('📆 Este mes', 'this_month', chats.this_month)}
            {renderChatGroup('📊 Anterior', 'older', chats.older)}
          </>
        )}
      </div>

      {/* Footer */}
      <div className="px-3 py-2 border-t border-gray-800 text-xs text-gray-500 text-center">
        {chats.today.length + chats.this_week.length + chats.this_month.length + chats.older.length} chats totales
      </div>
    </div>
  );
};

export default ChatHistory;
