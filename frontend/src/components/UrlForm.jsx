import React, { useState } from 'react';

export default function UrlForm({ onSingle, onBulk, loading }) {
  const [single, setSingle] = useState('');
  const [bulk, setBulk] = useState('');

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <div className="bg-white shadow rounded p-4">
        <h2 className="font-semibold mb-2">Single URL</h2>
        <input
          className="w-full border rounded p-2 mb-3"
          value={single}
          onChange={(e) => setSingle(e.target.value)}
          placeholder="https://example.com"
        />
        <button
          disabled={loading || !single}
          className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-60"
          onClick={() => onSingle(single)}
        >
          Run QA
        </button>
      </div>

      <div className="bg-white shadow rounded p-4">
        <h2 className="font-semibold mb-2">Bulk URLs</h2>
        <textarea
          className="w-full border rounded p-2 h-32 mb-3"
          value={bulk}
          onChange={(e) => setBulk(e.target.value)}
          placeholder={'https://site1.com\nhttps://site2.com'}
        />
        <button
          disabled={loading || !bulk.trim()}
          className="bg-indigo-600 text-white px-4 py-2 rounded disabled:opacity-60"
          onClick={() => onBulk(bulk.split('\n').map((u) => u.trim()).filter(Boolean))}
        >
          Queue Bulk QA
        </button>
      </div>
    </div>
  );
}
