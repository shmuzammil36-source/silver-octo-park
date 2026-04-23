import React from 'react';

export default function ProgressBar({ value }) {
  return (
    <div className="w-full bg-gray-200 rounded h-3 overflow-hidden">
      <div className="bg-green-500 h-full transition-all" style={{ width: `${value || 0}%` }} />
    </div>
  );
}
