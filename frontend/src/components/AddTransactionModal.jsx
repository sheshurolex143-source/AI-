import React, { useState, useEffect } from 'react';
import { X, Sparkles, AlertCircle, Loader2 } from 'lucide-react';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';

const CATEGORIES = [
  'Food & Dining',
  'Groceries',
  'Transport',
  'Shopping',
  'Bills & Utilities',
  'Rent & Housing',
  'Entertainment & Subscriptions',
  'Health',
  'Education',
  'Travel',
  'Investments & Savings',
  'Income',
  'Other',
];

export default function AddTransactionModal({ isOpen, onClose, onSuccess }) {
  const { currencySymbol } = useAuth();
  const [date, setDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [description, setDescription] = useState('');
  const [amount, setAmount] = useState('');
  const [type, setType] = useState('expense');
  const [category, setCategory] = useState('');
  const [aiSuggestion, setAiSuggestion] = useState(null);
  const [isAiPredicting, setIsAiPredicting] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Live AI categorization on debounce description change
  useEffect(() => {
    if (description.trim().length < 3) {
      setAiSuggestion(null);
      return;
    }

    const timer = setTimeout(async () => {
      setIsAiPredicting(true);
      try {
        const res = await api.post('/api/ml/categorize', { description });
        setAiSuggestion(res.data);
        if (!category) {
          setCategory(res.data.category);
        }
      } catch (err) {
        // Silent fail for inline suggestions
      } finally {
        setIsAiPredicting(false);
      }
    }, 450);

    return () => clearTimeout(timer);
  }, [description]);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!description.trim()) {
      setError('Description is required.');
      return;
    }
    const parsedAmount = parseFloat(amount);
    if (isNaN(parsedAmount) || parsedAmount <= 0) {
      setError('Please enter a valid positive amount.');
      return;
    }

    setLoading(true);
    try {
      await api.post('/api/transactions', {
        date,
        description: description.trim(),
        amount: parsedAmount,
        type,
        category: category || undefined,
      });
      onSuccess();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create transaction.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-md w-full shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400">
              <Sparkles className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-slate-800 dark:text-slate-100 text-lg">Add New Transaction</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-3 rounded-xl bg-red-50 dark:bg-red-950/40 text-red-600 dark:text-red-400 text-xs flex items-center gap-2 border border-red-200 dark:border-red-900/50">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Type Toggle */}
          <div className="grid grid-cols-2 gap-2 p-1 bg-slate-100 dark:bg-slate-800 rounded-xl">
            <button
              type="button"
              onClick={() => setType('expense')}
              className={`py-2 rounded-lg text-xs font-semibold transition ${
                type === 'expense'
                  ? 'bg-white dark:bg-slate-900 text-rose-600 dark:text-rose-400 shadow-sm'
                  : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              💸 Expense
            </button>
            <button
              type="button"
              onClick={() => setType('income')}
              className={`py-2 rounded-lg text-xs font-semibold transition ${
                type === 'income'
                  ? 'bg-white dark:bg-slate-900 text-emerald-600 dark:text-emerald-400 shadow-sm'
                  : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              💰 Income
            </button>
          </div>

          {/* Description with AI preview */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
              Description / Merchant
            </label>
            <div className="relative">
              <input
                type="text"
                required
                placeholder="e.g. Swiggy Order 8912 or Rent to Landlord"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              />
              {isAiPredicting && (
                <Loader2 className="w-4 h-4 text-indigo-500 animate-spin absolute right-3 top-3" />
              )}
            </div>

            {/* AI Suggestion pill */}
            {aiSuggestion && (
              <div className="mt-2 flex items-center justify-between text-xs p-2 rounded-lg bg-indigo-50/80 dark:bg-indigo-950/40 border border-indigo-100 dark:border-indigo-900/60">
                <div className="flex items-center gap-1.5 text-indigo-700 dark:text-indigo-300 font-medium">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>AI Predicted:</span>
                  <span className="font-bold underline">{aiSuggestion.category}</span>
                  <span className="text-[10px] text-indigo-500 bg-indigo-100 dark:bg-indigo-900/60 px-1.5 py-0.5 rounded-full">
                    {Math.round(aiSuggestion.confidence * 100)}%
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => setCategory(aiSuggestion.category)}
                  className="text-indigo-600 dark:text-indigo-400 hover:underline font-semibold text-[11px]"
                >
                  Apply
                </button>
              </div>
            )}
          </div>

          {/* Amount & Date in 2 columns */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Amount ({currencySymbol})
              </label>
              <div className="relative">
                <span className="absolute left-3 top-2.5 text-slate-400 font-medium text-sm">{currencySymbol}</span>
                <input
                  type="number"
                  step="0.01"
                  required
                  placeholder="0.00"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="w-full pl-8 pr-3 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Date
              </label>
              <input
                type="date"
                required
                value={date}
                onChange={(e) => setDate(e.target.value)}
                className="w-full px-3 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              />
            </div>
          </div>

          {/* Category Dropdown */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
              Category
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            >
              <option value="">Auto-Assign with AI</option>
              {CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          {/* Action buttons */}
          <div className="pt-2 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2.5 rounded-xl text-xs font-semibold text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs shadow-md shadow-indigo-500/25 disabled:opacity-50 transition active:scale-95"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              <span>Save Transaction</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

