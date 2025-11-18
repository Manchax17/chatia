import React from 'react';

const StatsCard = ({ icon: Icon, label, value, unit, color, subtext, progress }) => {
  const colorClasses = {
    green: 'from-green-500 to-emerald-600',
    orange: 'from-orange-500 to-amber-600',
    red: 'from-red-500 to-rose-600',
    purple: 'from-purple-500 to-violet-600',
    blue: 'from-blue-500 to-cyan-600',
  };

  return (
    <div className="glass rounded-xl p-4 hover:bg-white/10 transition-all group">
      <div className="flex items-start justify-between mb-3">
        <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${colorClasses[color]} flex items-center justify-center group-hover:scale-110 transition-transform`}>
          <Icon size={24} className="text-white" />
        </div>
        
        {progress !== undefined && (
          <div className="text-right">
            <div className="text-2xl font-bold text-white">{progress}%</div>
            <div className="text-xs text-gray-400">Progreso</div>
          </div>
        )}
      </div>

      <div className="space-y-1">
        <div className="text-sm text-gray-400">{label}</div>
        <div className="flex items-baseline gap-1">
          <div className="text-3xl font-bold text-white">
            {typeof value === 'number' ? value.toLocaleString() : value}
          </div>
          {unit && <div className="text-lg text-gray-400">{unit}</div>}
        </div>
        {subtext && (
          <div className="text-xs text-gray-500 mt-1">{subtext}</div>
        )}
      </div>

      {/* Progress bar */}
      {progress !== undefined && (
        <div className="mt-3 h-2 bg-gray-800 rounded-full overflow-hidden">
          <div
            className={`h-full bg-gradient-to-r ${colorClasses[color]} transition-all duration-500`}
            style={{ width: `${Math.min(progress, 100)}%` }}
          />
        </div>
      )}
    </div>
  );
};

export default StatsCard;