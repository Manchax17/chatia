import React from 'react';
import { User, Bot, CheckCircle, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const MessageBubble = ({ message, isUser }) => {
  const { content, tools_used, error } = message;

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'} mb-4 animate-fade-in`}>
      {/* Avatar */}
      <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
        isUser 
          ? 'bg-gradient-to-br from-blue-500 to-blue-600' 
          : 'bg-gradient-to-br from-purple-500 to-purple-600'
      }`}>
        {isUser ? <User size={20} /> : <Bot size={20} />}
      </div>

      {/* Mensaje */}
      <div className={`flex-1 max-w-3xl ${isUser ? 'items-end' : 'items-start'}`}>
        <div className={`rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white'
            : error
            ? 'bg-red-900/30 border border-red-700 text-red-200'
            : 'glass text-gray-100'
        }`}>
          {error ? (
            <div className="flex items-start gap-2">
              <AlertCircle size={20} className="flex-shrink-0 mt-1" />
              <div>
                <p className="font-semibold mb-1">Error</p>
                <p className="text-sm">{content}</p>
              </div>
            </div>
          ) : (
            <div className="prose prose-invert max-w-none">
              <ReactMarkdown
                components={{
                  p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                  ul: ({ children }) => <ul className="list-disc ml-4 mb-2">{children}</ul>,
                  ol: ({ children }) => <ol className="list-decimal ml-4 mb-2">{children}</ol>,
                  li: ({ children }) => <li className="mb-1">{children}</li>,
                  strong: ({ children }) => <strong className="font-bold text-white">{children}</strong>,
                  em: ({ children }) => <em className="italic">{children}</em>,
                  code: ({ children }) => (
                    <code className="bg-black/30 px-1.5 py-0.5 rounded text-sm font-mono">
                      {children}
                    </code>
                  ),
                }}
              >
                {content}
              </ReactMarkdown>
            </div>
          )}

          {/* Tools usadas */}
          {tools_used && tools_used.length > 0 && (
            <div className="mt-3 pt-3 border-t border-white/10">
              <div className="flex items-center gap-2 text-xs text-gray-400">
                <CheckCircle size={14} className="text-green-400" />
                <span>Herramientas usadas:</span>
              </div>
              <div className="flex flex-wrap gap-1 mt-1">
                {tools_used.map((tool, idx) => (
                  <span
                    key={idx}
                    className="text-xs px-2 py-1 bg-white/5 rounded-full text-gray-300"
                  >
                    {tool.tool}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Timestamp */}
        <div className={`text-xs text-gray-500 mt-1 px-2 ${isUser ? 'text-right' : 'text-left'}`}>
          {new Date().toLocaleTimeString('es-ES', { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;