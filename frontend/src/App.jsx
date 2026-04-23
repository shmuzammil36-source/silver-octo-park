import React, { useEffect, useState } from 'react';
import ProgressBar from './components/ProgressBar';
import ReportView from './components/ReportView';
import UrlForm from './components/UrlForm';
import { checkBulk, checkSingleUrl, getCsvUrl, getJob } from './lib/api';

export default function App() {
  const [loading, setLoading] = useState(false);
  const [jobId, setJobId] = useState(null);
  const [job, setJob] = useState(null);
  const [results, setResults] = useState([]);

  useEffect(() => {
    if (!jobId) return;
    const timer = setInterval(async () => {
      const next = await getJob(jobId);
      setJob(next);
      if (next.status === 'completed') {
        setResults(next.results || []);
        setLoading(false);
        clearInterval(timer);
      }
    }, 2000);

    return () => clearInterval(timer);
  }, [jobId]);

  const handleSingle = async (url) => {
    setLoading(true);
    try {
      const result = await checkSingleUrl(url);
      setResults([result]);
      setJobId(null);
      setJob(null);
    } finally {
      setLoading(false);
    }
  };

  const handleBulk = async (urls) => {
    setLoading(true);
    const queued = await checkBulk(urls);
    setResults([]);
    setJobId(queued.job_id);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        <h1 className="text-3xl font-bold">WordPress Elementor QA Dashboard</h1>
        <UrlForm onSingle={handleSingle} onBulk={handleBulk} loading={loading} />

        {job && (
          <div className="bg-white rounded shadow p-4 space-y-2">
            <div className="flex justify-between">
              <p className="font-medium">Bulk Job: {job.job_id}</p>
              <p>{job.completed}/{job.total}</p>
            </div>
            <ProgressBar value={job.progress} />
            <div>
              <a className="text-blue-600 underline" href={getCsvUrl(job.job_id)}>
                Export Summary CSV
              </a>
            </div>
          </div>
        )}

        {!!results.length && <ReportView results={results} />}
      </div>
    </div>
  );
}
