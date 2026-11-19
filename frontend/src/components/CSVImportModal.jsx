import React, { useState } from 'react';
import { X, UploadCloud, AlertCircle, CheckCircle2, FileText, Loader2 } from 'lucide-react';
import api from '../api/client';

export default function CSVImportModal({ isOpen, onClose, onSuccess }) {
  const [file, setFile] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.name.endsWith('.csv')) {
        setFile(droppedFile);
        setError('');
      } else {
        setError('Please drop a valid .csv file.');
      }
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a CSV file to upload.');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await api.post('/api/transactions/import', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResult(res.data);
      if (res.data.successful > 0) {
        onSuccess();
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'CSV upload failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-lg w-full shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400">
              <UploadCloud className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-slate-800 dark:text-slate-100 text-lg">Import Bank Statement CSV</h3>
              <p className="text-xs text-slate-400">Transactions are auto-categorized by FinSight AI</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-4">
          {error && (
            <div className="p-3 rounded-xl bg-red-50 dark:bg-red-950/40 text-red-600 dark:text-red-400 text-xs flex items-center gap-2 border border-red-200 dark:border-red-900/50">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Drag & Drop Zone */}
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition ${
              dragOver
                ? 'border-indigo-500 bg-indigo-50/50 dark:bg-indigo-950/20'
                : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'
            }`}
            onClick={() => document.getElementById('csv-file-input').click()}
          >
            <input
              id="csv-file-input"
              type="file"
              accept=".csv"
              className="hidden"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  setFile(e.target.files[0]);
                  setError('');
                }
              }}
            />

            <UploadCloud className="w-10 h-10 mx-auto text-indigo-500 mb-2" />
            {file ? (
              <div className="flex items-center justify-center gap-2 text-sm font-semibold text-slate-800 dark:text-slate-200">
                <FileText className="w-4 h-4 text-indigo-500" />
                <span>{file.name}</span>
                <span className="text-xs text-slate-400 font-normal">
                  ({(file.size / 1024).toFixed(1)} KB)
                </span>
              </div>
            ) : (
              <>
                <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                  Click or drag and drop your CSV file here
                </p>
                <p className="text-xs text-slate-400 mt-1">
                  Required columns: <code className="text-indigo-600 dark:text-indigo-400 font-mono">date, description, amount, type</code>
                </p>
              </>
            )}
          </div>

          {/* Import Results Report */}
          {result && (
            <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200/80 dark:border-slate-700 space-y-2">
              <div className="flex items-center justify-between text-xs font-semibold">
                <span className="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Successfully Ingested: {result.successful}</span>
                </span>
                {result.failed > 0 && (
                  <span className="text-rose-500">Failed Rows: {result.failed}</span>
                )}
              </div>

              {result.errors.length > 0 && (
                <div className="mt-2 text-[11px] text-slate-600 dark:text-slate-400 max-h-32 overflow-y-auto space-y-1">
                  <span className="font-semibold text-slate-700 dark:text-slate-300 block">
                    Row-level errors:
                  </span>
                  {result.errors.map((err, i) => (
                    <div key={i} className="text-rose-600 dark:text-rose-400">
                      Row {err.row}: {err.errors.join(', ')}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Actions */}
          <div className="pt-2 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2.5 rounded-xl text-xs font-semibold text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
            >
              {result ? 'Done' : 'Cancel'}
            </button>
            <button
              type="button"
              onClick={handleUpload}
              disabled={loading || !file}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs shadow-md shadow-indigo-500/25 disabled:opacity-50 transition active:scale-95"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <UploadCloud className="w-4 h-4" />}
              <span>{loading ? 'Processing...' : 'Upload & Categorize'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

