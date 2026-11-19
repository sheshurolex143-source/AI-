import React, { useState, useEffect } from 'react';
import {
  PieChart,
  Target,
  Plus,
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  Calendar,
  DollarSign,
  TrendingUp,
  Trash2,
  Loader2,
} from 'lucide-react';
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
  'Other',
];

export default function Budgets() {
  const { currencySymbol } = useAuth();

  const [budgets, setBudgets] = useState([]);
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);

  // Modals / Form toggles
  const [showAddBudget, setShowAddBudget] = useState(false);
  const [budgetCategory, setBudgetCategory] = useState(CATEGORIES[0]);
  const [budgetLimit, setBudgetLimit] = useState('');
  const [budgetMonth, setBudgetMonth] = useState(() => new Date().toISOString().slice(0, 7));

  const [showAddGoal, setShowAddGoal] = useState(false);
  const [goalName, setGoalName] = useState('');
  const [goalTarget, setGoalTarget] = useState('');
  const [goalCurrent, setGoalCurrent] = useState('');
  const [goalDeadline, setGoalDeadline] = useState('');

  const [actionLoading, setActionLoading] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [bRes, gRes] = await Promise.all([
        api.get('/api/budgets'),
        api.get('/api/goals'),
      ]);
      setBudgets(bRes.data);
      setGoals(gRes.data);
    } catch (err) {
      console.error('Failed to load budgets & goals', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Create Budget
  const handleCreateBudget = async (e) => {
    e.preventDefault();
    setActionLoading(true);
    try {
      await api.post('/api/budgets', {
        category: budgetCategory,
        monthly_limit: parseFloat(budgetLimit),
        month: budgetMonth,
      });
      setShowAddBudget(false);
      setBudgetLimit('');
      fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create budget.');
    } finally {
      setActionLoading(false);
    }
  };

  // Delete Budget
  const handleDeleteBudget = async (id) => {
    if (!window.confirm('Delete this budget?')) return;
    try {
      await api.delete(`/api/budgets/${id}`);
      fetchData();
    } catch (err) {
      alert('Failed to delete budget.');
    }
  };

  // Create Goal
  const handleCreateGoal = async (e) => {
    e.preventDefault();
    setActionLoading(true);
    try {
      await api.post('/api/goals', {
        name: goalName,
        target_amount: parseFloat(goalTarget),
        current_amount: goalCurrent ? parseFloat(goalCurrent) : 0,
        deadline: goalDeadline,
      });
      setShowAddGoal(false);
      setGoalName('');
      setGoalTarget('');
      setGoalCurrent('');
      setGoalDeadline('');
      fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create savings goal.');
    } finally {
      setActionLoading(false);
    }
  };

  // Delete Goal
  const handleDeleteGoal = async (id) => {
    if (!window.confirm('Delete this savings goal?')) return;
    try {
      await api.delete(`/api/goals/${id}`);
      fetchData();
    } catch (err) {
      alert('Failed to delete goal.');
    }
  };

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-64 bg-slate-200 dark:bg-slate-800 rounded-3xl" />
        <div className="h-64 bg-slate-200 dark:bg-slate-800 rounded-3xl" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* ── 1. Monthly Category Budgets ── */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400">
                <PieChart className="w-5 h-5" />
              </div>
              <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100">
                Monthly Category Budgets
              </h2>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Live tracking vs monthly expenditure limit with end-of-month run-rate projections
            </p>
          </div>

          <button
            onClick={() => setShowAddBudget(!showAddBudget)}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-xs shadow-md shadow-indigo-500/25 transition active:scale-95"
          >
            <Plus className="w-4 h-4" />
            <span>{showAddBudget ? 'Cancel' : 'Set Category Budget'}</span>
          </button>
        </div>

        {/* Add Budget Form Drawer */}
        {showAddBudget && (
          <form
            onSubmit={handleCreateBudget}
            className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-md space-y-4 animate-in fade-in duration-200"
          >
            <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200">
              New Monthly Spending Cap
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Category
                </label>
                <select
                  value={budgetCategory}
                  onChange={(e) => setBudgetCategory(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs"
                >
                  {CATEGORIES.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Monthly Limit ({currencySymbol})
                </label>
                <input
                  type="number"
                  required
                  placeholder="e.g. 8000"
                  value={budgetLimit}
                  onChange={(e) => setBudgetLimit(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Target Month (YYYY-MM)
                </label>
                <input
                  type="month"
                  required
                  value={budgetMonth}
                  onChange={(e) => setBudgetMonth(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setShowAddBudget(false)}
                className="px-3 py-1.5 text-xs text-slate-500 hover:text-slate-700"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={actionLoading}
                className="px-4 py-2 rounded-xl bg-indigo-600 text-white font-semibold text-xs shadow"
              >
                {actionLoading ? 'Saving...' : 'Save Budget'}
              </button>
            </div>
          </form>
        )}

        {/* Budgets Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {budgets.map((b) => {
            const isOver = b.is_over_budget;
            const isWarning = b.percentage >= 80 && !isOver;
            const willExceed = b.projected_end_of_month > b.monthly_limit;

            return (
              <div
                key={b.id}
                className={`p-5 rounded-2xl bg-white dark:bg-slate-900 border shadow-sm flex flex-col justify-between ${
                  isOver
                    ? 'border-rose-300 dark:border-rose-900/60 bg-rose-50/20'
                    : isWarning
                    ? 'border-amber-300 dark:border-amber-900/60 bg-amber-50/20'
                    : 'border-slate-200 dark:border-slate-800'
                }`}
              >
                <div>
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-bold text-slate-800 dark:text-slate-100 text-sm">{b.category}</h4>
                      <span className="text-[10px] text-slate-400 font-mono">Period: {b.month}</span>
                    </div>
                    <button
                      onClick={() => handleDeleteBudget(b.id)}
                      className="text-slate-300 hover:text-rose-500 p-1"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  <div className="mt-4 flex items-baseline justify-between text-xs">
                    <span className="text-slate-500">Spent so far:</span>
                    <span className="font-bold text-slate-800 dark:text-slate-100">
                      {currencySymbol}{b.spent.toLocaleString()} / {currencySymbol}{b.monthly_limit.toLocaleString()}
                    </span>
                  </div>

                  {/* Progress bar */}
                  <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2 mt-2 overflow-hidden">
                    <div
                      className={`h-2 rounded-full transition-all duration-500 ${
                        isOver ? 'bg-rose-500' : isWarning ? 'bg-amber-500' : 'bg-indigo-600'
                      }`}
                      style={{ width: `${Math.min(100, b.percentage)}%` }}
                    />
                  </div>

                  <div className="mt-2 flex items-center justify-between text-[11px]">
                    <span className={`font-semibold ${isOver ? 'text-rose-500' : 'text-slate-500'}`}>
                      {b.percentage}% utilized
                    </span>
                    <span className="text-slate-400">
                      {b.remaining >= 0 ? `${currencySymbol}${b.remaining.toLocaleString()} left` : `Over by ${currencySymbol}${Math.abs(b.remaining).toLocaleString()}`}
                    </span>
                  </div>
                </div>

                {/* Overspend warning / projection alert */}
                {willExceed && !isOver && (
                  <div className="mt-4 p-2 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900/40 flex items-center gap-1.5 text-[10px] text-amber-700 dark:text-amber-300">
                    <AlertTriangle className="w-3.5 h-3.5 shrink-0 text-amber-500" />
                    <span>
                      Projected end of month: <strong>{currencySymbol}{b.projected_end_of_month.toLocaleString()}</strong> (Likely overrun)
                    </span>
                  </div>
                )}

                {isOver && (
                  <div className="mt-4 p-2 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/40 flex items-center gap-1.5 text-[10px] text-rose-700 dark:text-rose-300">
                    <AlertCircle className="w-3.5 h-3.5 shrink-0 text-rose-500" />
                    <span>Budget cap exceeded for {b.category}!</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* ── 2. Savings Goals ── */}
      <div className="space-y-4 pt-6 border-t border-slate-200 dark:border-slate-800">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400">
                <Target className="w-5 h-5" />
              </div>
              <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100">
                Savings Goals & Deadlines
              </h2>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Target amount milestones with automated monthly savings pace calculations
            </p>
          </div>

          <button
            onClick={() => setShowAddGoal(!showAddGoal)}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-xs shadow-md shadow-emerald-500/25 transition active:scale-95"
          >
            <Plus className="w-4 h-4" />
            <span>{showAddGoal ? 'Cancel' : 'Create New Goal'}</span>
          </button>
        </div>

        {/* Add Goal Form Drawer */}
        {showAddGoal && (
          <form
            onSubmit={handleCreateGoal}
            className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-md space-y-4 animate-in fade-in duration-200"
          >
            <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200">
              New Savings Target Milestone
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Goal Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Emergency Fund"
                  value={goalName}
                  onChange={(e) => setGoalName(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Target Amount ({currencySymbol})
                </label>
                <input
                  type="number"
                  required
                  placeholder="e.g. 150000"
                  value={goalTarget}
                  onChange={(e) => setGoalTarget(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Current Saved ({currencySymbol})
                </label>
                <input
                  type="number"
                  placeholder="e.g. 25000"
                  value={goalCurrent}
                  onChange={(e) => setGoalCurrent(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Target Deadline
                </label>
                <input
                  type="date"
                  required
                  value={goalDeadline}
                  onChange={(e) => setGoalDeadline(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setShowAddGoal(false)}
                className="px-3 py-1.5 text-xs text-slate-500 hover:text-slate-700"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={actionLoading}
                className="px-4 py-2 rounded-xl bg-emerald-600 text-white font-semibold text-xs shadow"
              >
                {actionLoading ? 'Saving...' : 'Save Goal'}
              </button>
            </div>
          </form>
        )}

        {/* Goals Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {goals.map((g) => (
            <div
              key={g.id}
              className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between">
                  <h4 className="font-bold text-slate-800 dark:text-slate-100 text-base">{g.name}</h4>
                  <button
                    onClick={() => handleDeleteGoal(g.id)}
                    className="text-slate-300 hover:text-rose-500 p-1"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>

                <div className="mt-4 flex items-baseline justify-between text-xs">
                  <span className="text-slate-400">Current Progress</span>
                  <span className="font-extrabold text-slate-800 dark:text-slate-100">
                    {currencySymbol}{g.current_amount.toLocaleString()} / {currencySymbol}{g.target_amount.toLocaleString()}
                  </span>
                </div>

                {/* Progress bar */}
                <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2.5 mt-2 overflow-hidden">
                  <div
                    className="h-2.5 rounded-full bg-gradient-to-r from-emerald-500 to-teal-400 transition-all duration-500"
                    style={{ width: `${Math.min(100, g.progress_percentage)}%` }}
                  />
                </div>

                <div className="mt-2 flex items-center justify-between text-xs">
                  <span className="font-semibold text-emerald-600 dark:text-emerald-400">
                    {g.progress_percentage}% Completed
                  </span>
                  <button
                    onClick={async () => {
                      const amountStr = prompt(`Enter deposit amount for "${g.name}" (${currencySymbol}):`, '5000');
                      if (!amountStr) return;
                      const added = parseFloat(amountStr);
                      if (isNaN(added) || added <= 0) return alert('Invalid amount');
                      try {
                        await api.put(`/api/goals/${g.id}`, { current_amount: g.current_amount + added });
                        fetchData();
                      } catch (err) {
                        alert('Failed to update goal');
                      }
                    }}
                    className="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 hover:underline flex items-center gap-1"
                  >
                    <span>+ Add Funds</span>
                  </button>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between text-xs">
                <div>
                  <span className="text-slate-400 text-[10px] block">Required Monthly Saving</span>
                  <span className="font-bold text-slate-700 dark:text-slate-300">
                    {currencySymbol}{g.monthly_saving_needed.toLocaleString()} / mo
                  </span>
                </div>

                <div className="text-right">
                  <span className="text-slate-400 text-[10px] block">Deadline</span>
                  <span className="font-medium text-slate-600 dark:text-slate-400 font-mono">
                    {g.deadline}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

