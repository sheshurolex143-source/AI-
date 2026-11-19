import React, { useState } from 'react';
import {
  Settings as SettingsIcon,
  RefreshCw,
  RotateCcw,
  DollarSign,
  User,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  Loader2,
} from 'lucide-react';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';

const CURRENCIES = [
  { symbol: '₹', code: 'INR', name: 'Indian Rupee' },
  { symbol: '$', code: 'USD', name: 'US Dollar' },
  { symbol: '€', code: 'EUR', name: 'Euro' },
  { symbol: '£', code: 'GBP', name: 'British Pound' },
];

export default function Settings() {
  const { user, currencySymbol, updateCurrency } = useAuth();

  const [retrainLoading, setRetrainLoading] = useState(false);
  const [retrainResult, setRetrainResult] = useState(null);
  const [retrainError, setRetrainError] = useState('');

  const [resetLoading, setResetLoading] = useState(false);
  const [resetSuccess, setResetSuccess] = useState('');
  const [resetError, setResetError] = useState('');

  const handleResetDemoData = async () => {
    if (!window.confirm('Reset all demo data? This will restore clean 6 months of transactions, budgets, and savings goals.')) return;
    setResetLoading(true);
    setResetSuccess('');
    setResetError('');
    try {
      const res = await api.post('/api/auth/reset-demo');
      setResetSuccess(res.data.message);
      window.dispatchEvent(new CustomEvent('transaction_added'));
    } catch (err) {
      setResetError(err.response?.data?.detail || 'Failed to reset demo data.');
    } finally {
      setResetLoading(false);
    }
  };

  // Trigger Model Retraining with feedback loop
  const handleRetrain = async () => {
    setRetrainLoading(true);
    setRetrainError('');
    setRetrainResult(null);
    try {
      const res = await api.post('/api/ml/retrain');
      setRetrainResult(res.data);
    } catch (err) {
      setRetrainError(err.response?.data?.detail || 'Failed to retrain model.');
    } finally {
      setRetrainLoading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-4xl">
      <div>
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400">
            <SettingsIcon className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-2xl font-black text-slate-800 dark:text-slate-100">
              System Settings & AI Ops
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Currency localization, interactive ML model retraining loop, and demo state
            </p>
          </div>
        </div>
      </div>

      {/* ── 1. Currency Configuration ── */}
      <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        <div>
          <h3 className="font-bold text-slate-800 dark:text-slate-100 text-base">
            Default Currency Localization
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Configure the currency symbol utilized across dashboards, summaries, and charts.
          </p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
          {CURRENCIES.map((curr) => {
            const isSelected = currencySymbol === curr.symbol;
            return (
              <button
                key={curr.code}
                onClick={() => updateCurrency(curr.symbol)}
                className={`p-4 rounded-2xl border text-left transition flex flex-col justify-between ${
                  isSelected
                    ? 'border-indigo-600 bg-indigo-50/50 dark:bg-indigo-950/30 text-indigo-900 dark:text-indigo-100 shadow-sm'
                    : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:border-slate-300'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold font-mono">{curr.symbol}</span>
                  {isSelected && (
                    <CheckCircle2 className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                  )}
                </div>
                <div className="mt-2">
                  <span className="text-xs font-bold block">{curr.code}</span>
                  <span className="text-[10px] text-slate-400">{curr.name}</span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* ── 2. AI Model Retraining Feedback Loop ── */}
      <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-bold text-slate-800 dark:text-slate-100 text-base">
              Continuous Learning & Model Retraining
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Incorporate all your manual category corrections back into the training corpus to improve classifier accuracy.
            </p>
          </div>
          <button
            onClick={handleRetrain}
            disabled={retrainLoading}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs shadow-md shadow-indigo-500/25 disabled:opacity-50 transition active:scale-95 whitespace-nowrap"
          >
            {retrainLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <RefreshCw className="w-4 h-4" />
            )}
            <span>{retrainLoading ? 'Retraining...' : 'Trigger Model Retrain'}</span>
          </button>
        </div>

        {retrainResult && (
          <div className="p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-900/50 space-y-2 text-xs">
            <div className="flex items-center gap-2 text-emerald-800 dark:text-emerald-200 font-bold">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              <span>{retrainResult.message}</span>
            </div>
            <div className="flex items-center gap-6 text-slate-600 dark:text-slate-300 pt-1">
              {retrainResult.old_accuracy && (
                <div>
                  <span className="text-slate-400 block text-[10px]">Previous Accuracy:</span>
                  <span className="font-mono font-bold">
                    {(retrainResult.old_accuracy * 100).toFixed(2)}%
                  </span>
                </div>
              )}
              <div>
                <span className="text-slate-400 block text-[10px]">New Accuracy:</span>
                <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400">
                  {(retrainResult.new_accuracy * 100).toFixed(2)}%
                </span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px]">Samples Retrained On:</span>
                <span className="font-mono font-bold">{retrainResult.samples_used.toLocaleString()}</span>
              </div>
            </div>
          </div>
        )}

        {retrainError && (
          <div className="p-4 rounded-2xl bg-red-50 dark:bg-red-950/40 text-red-600 dark:text-red-400 text-xs flex items-center gap-2 border border-red-200">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{retrainError}</span>
          </div>
        )}
      </div>

      {/* ── 3. Reset Demo Data ── */}
      <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-bold text-slate-800 dark:text-slate-100 text-base">
              Reset Demo Environment
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Restore the account state to a pristine 6-month transaction ledger with planted anomalies and active goals.
            </p>
          </div>
          <button
            onClick={handleResetDemoData}
            disabled={resetLoading}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl border border-rose-300 dark:border-rose-900/60 bg-rose-50/50 dark:bg-rose-950/20 text-rose-600 dark:text-rose-400 hover:bg-rose-100 dark:hover:bg-rose-950/40 font-semibold text-xs transition active:scale-95 disabled:opacity-50 whitespace-nowrap"
          >
            {resetLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <RotateCcw className="w-4 h-4" />}
            <span>{resetLoading ? 'Resetting...' : 'Reset Demo Data'}</span>
          </button>
        </div>

        {resetSuccess && (
          <div className="p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-900/50 text-emerald-700 dark:text-emerald-300 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-500" />
            <span>{resetSuccess}</span>
          </div>
        )}

        {resetError && (
          <div className="p-4 rounded-2xl bg-red-50 dark:bg-red-950/40 text-red-600 dark:text-red-400 text-xs flex items-center gap-2 border border-red-200">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{resetError}</span>
          </div>
        )}
      </div>

      {/* ── 4. User Profile Card ── */}
      <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        <div>
          <h3 className="font-bold text-slate-800 dark:text-slate-100 text-base">
            Authenticated Profile
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Active session authenticated via cryptographic JWT Bearer tokens
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60">
            <span className="text-slate-400 block">Full Name</span>
            <span className="font-semibold text-slate-800 dark:text-slate-100 text-sm mt-0.5 block">
              {user?.full_name || 'Alex Morgan'}
            </span>
          </div>
          <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60">
            <span className="text-slate-400 block">Email Address</span>
            <span className="font-semibold text-slate-800 dark:text-slate-100 text-sm mt-0.5 block font-mono">
              {user?.email || 'demo@finsight.ai'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

