import React, { useMemo, useState } from 'react';
import jsPDF from 'jspdf';

const categories = ['All', 'Content', 'Buttons', 'Images', 'Responsive', 'SEO', 'Accessibility', 'Performance', 'Security'];
const severities = ['all', 'high', 'medium', 'low'];

export default function ReportView({ results }) {
  const [category, setCategory] = useState('All');
  const [severity, setSeverity] = useState('all');

  const filtered = useMemo(() => {
    return results.map((result) => ({
      ...result,
      issues: (result.issues || []).filter((issue) => {
        const byCategory = category === 'All' || issue.category === category;
        const bySeverity = severity === 'all' || issue.severity === severity;
        return byCategory && bySeverity;
      }),
    }));
  }, [category, severity, results]);

  const downloadJson = () => {
    const blob = new Blob([JSON.stringify(filtered, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'qa-report.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadPdf = () => {
    const doc = new jsPDF();
    doc.text('Elementor QA Report', 10, 10);
    doc.text(JSON.stringify(filtered, null, 2).slice(0, 3000), 10, 20);
    doc.save('qa-report.pdf');
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2 items-center">
        <select className="border rounded p-2" value={category} onChange={(e) => setCategory(e.target.value)}>
          {categories.map((c) => <option key={c}>{c}</option>)}
        </select>
        <select className="border rounded p-2" value={severity} onChange={(e) => setSeverity(e.target.value)}>
          {severities.map((s) => <option key={s}>{s}</option>)}
        </select>
        <button className="bg-slate-700 text-white px-3 py-2 rounded" onClick={downloadJson}>Download JSON</button>
        <button className="bg-slate-900 text-white px-3 py-2 rounded" onClick={downloadPdf}>Download PDF</button>
      </div>

      {filtered.map((result) => (
        <div key={result.url + result.checked_at} className="bg-white rounded shadow p-4 space-y-3">
          <div className="flex justify-between gap-2">
            <h3 className="font-semibold break-all">{result.url}</h3>
            <span className="text-sm">{result.status}</span>
          </div>

          <div className="grid md:grid-cols-4 gap-3 text-sm">
            {Object.entries(result.screenshots || {}).map(([name, path]) => (
              <div key={name} className="border rounded p-2">
                <p className="font-medium">{name}</p>
                <p className="text-xs break-all text-gray-500">{path}</p>
              </div>
            ))}
          </div>

          <div className="overflow-auto">
            <table className="w-full text-sm border">
              <thead className="bg-gray-50">
                <tr>
                  <th className="p-2 border">Category</th>
                  <th className="p-2 border">Severity</th>
                  <th className="p-2 border">Message</th>
                </tr>
              </thead>
              <tbody>
                {result.issues?.map((issue, i) => (
                  <tr key={i}>
                    <td className="p-2 border">{issue.category}</td>
                    <td className="p-2 border">{issue.severity}</td>
                    <td className="p-2 border">{issue.message}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  );
}
