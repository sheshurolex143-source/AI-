import React, { useState, useEffect } from 'react';
import { useOutletContext, Link } from 'react-router-dom';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  PiggyBank,
  Sparkles,
  AlertTriangle,
  ArrowUpRight,
  ArrowDownRight,
  ShieldCheck,
  ChevronRight,
  PieChart as PieIcon,
  RefreshCw,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
  CartesianGrid,
} from 'recharts';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';

const COLORS = [
  '#6366f1', '#ec4899', '#f59e0b', '#10b981', '#3b82f6',
  '#8b5cf6', '#14b8a6', '#f97316', '#06b6d4', '#84cc16'
];

export default function Dashboard() {
  const { currencySymbol } = useAuth();
  const { openAddModal } = useOutletContext();

  const [summary, setSummary] = useState(null);
  const [monthlyData, setMonthlyData] = useState([]);
  const [categoryData, setCategoryData] = useState([]);
  const [healthScore, setHealthScore] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [
        sumRes,
        monthlyRes,
        catRes,
        healthRes,
        recsRes,
        anomRes,
      ] = await Promise.all([
        api.get('/api/analytics/summary?months=6'),
        api.get('/api/analytics/monthly'),
        api.get('/api/analytics/categories'),
        api.get('/api/insights/health-score'),
        api.get('/api/insights/recommendations'),
        api.get('/api/analytics/anomalies'),
      ]);

      setSummary(sumRes.data);
      setMonthlyData(monthlyRes.data);
      setCategoryData(catRes.data);
      setHealthScore(healthRes.data);
      setRecommendations(recsRes.data);
      setAnomalies(anomRes.data);
    } catch (err) {
      console.error('Failed to load dashboard metrics', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
    const handleTxnAdded = () => loadDashboardData();
    window.addEventListener('transaction_added', handleTxnAdded);
    return () => window.removeEventListener('transaction_added', handleTxnAdded);
  }, []);

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-32 bg-slate-200 dark:bg-slate-800 rounded-2xl" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="h-80 lg:col-span-2 bg-slate-200 dark:bg-slate-800 rounded-2xl" />
          <div className="h-80 bg-slate-200 dark:bg-slate-800 rounded-2xl" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Anomaly Alert Banner (if any) */}
      {anomalies.length > 0 && (
        <div className="p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900/60 flex items-start justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-xl bg-amber-100 dark:bg-amber-900/50 text-amber-600 dark:text-amber-400 shrink-0">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-amber-900 dark:text-amber-200">
                {anomalies.length} Unusual Spending Anomalies Detected
              </h4>
              <p className="text-xs text-amber-700 dark:text-amber-300/90 mt-0.5">
                AI flagged unusual transactions, e.g. "{anomalies[0].reason}". Review them in Insights.
              </p>
            </div>
          </div>
          <Link
            to="/insights"
            className="px-3.5 py-1.5 rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-medium text-xs whitespace-nowrap transition"
          >
            Review Anomalies
          </Link>
        </div>
      )}

      {/* 4 Summary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Income Card */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400">
            <span className="text-xs font-semibold">Total Income</span>
            <div className="p-2 rounded-xl bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-800 dark:text-slate-100">
              {currencySymbol}{summary?.total_income.toLocaleString()}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">Across 6-month historical window</p>
        </div>

        {/* Expenses Card */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400">
            <span className="text-xs font-semibold">Total Expenses</span>
            <div className="p-2 rounded-xl bg-rose-50 dark:bg-rose-950/50 text-rose-600 dark:text-rose-400">
              <TrendingDown className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-800 dark:text-slate-100">
              {currencySymbol}{summary?.total_expenses.toLocaleString()}
            </span>
            {summary?.month_over_month_change !== 0 && (
              <span className={`text-xs font-semibold flex items-center ${
                summary?.month_over_month_change > 0 ? 'text-rose-500' : 'text-emerald-500'
              }`}>
                {summary?.month_over_month_change > 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                {Math.abs(summary?.month_over_month_change || 0)}% MoM
              </span>
            )}
          </div>
          <p className="text-xs text-slate-400 mt-1">Avg {currencySymbol}{summary?.avg_daily_expense}/day</p>
        </div>

        {/* Savings Card */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400">
            <span className="text-xs font-semibold">Net Savings</span>
            <div className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400">
              <PiggyBank className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-800 dark:text-slate-100">
              {currencySymbol}{summary?.total_savings.toLocaleString()}
            </span>
          </div>
          <p className="text-xs text-indigo-600 dark:text-indigo-400 font-semibold mt-1">
            Savings Rate: {summary?.savings_rate}%
          </p>
        </div>

        {/* Top Category Card */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400">
            <span className="text-xs font-semibold">Primary Outflow</span>
            <div className="p-2 rounded-xl bg-violet-50 dark:bg-violet-950/50 text-violet-600 dark:text-violet-400">
              <PieIcon className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2">
            <span className="text-xl font-bold text-slate-800 dark:text-slate-100 truncate block">
              {summary?.top_category}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">{summary?.transaction_count} recorded transactions</p>
        </div>
      </div>

      {/* Main Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Income vs Expenses Bar Chart */}
        <div className="lg:col-span-2 p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-slate-800 dark:text-slate-100 text-base">
                Income vs Expense Trends
              </h3>
              <p className="text-xs text-slate-400">Monthly cash flow and cumulative net surplus</p>
            </div>
          </div>
          <div className="h-72 w-full mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={monthlyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip
                  formatter={(val) => [`${currencySymbol}${val.toLocaleString()}`]}
                  contentStyle={{
                    borderRadius: '12px',
                    backgroundColor: '#1e293b',
                    border: 'none',
                    color: '#f8fafc',
                    fontSize: '12px',
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                <Bar dataKey="income" name="Income" fill="#10b981" radius={[4, 4, 0, 0]} />
                <Bar dataKey="expenses" name="Expenses" fill="#f43f5e" radius={[4, 4, 0, 0]} />
                <Bar dataKey="savings" name="Savings" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Financial Health Score Gauge Card */}
        <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-slate-800 dark:text-slate-100 text-base">
                Financial Health
              </h3>
              <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 border border-indigo-200/50">
                Grade: {healthScore?.grade}
              </span>
            </div>

            {/* Score Ring / Radial */}
            <div className="my-4 flex flex-col items-center justify-center">
              <div className="relative w-36 h-36 flex items-center justify-center">
                <svg className="w-full h-full transform -rotate-90">
                  <circle
                    cx="72"
                    cy="72"
                    r="58"
                    stroke="currentColor"
                    strokeWidth="10"
                    className="text-slate-100 dark:text-slate-800"
                    fill="transparent"
                  />
                  <circle
                    cx="72"
                    cy="72"
                    r="58"
                    stroke="currentColor"
                    strokeWidth="10"
                    strokeDasharray={364}
                    strokeDashoffset={364 - (364 * (healthScore?.score || 0)) / 100}
                    strokeLinecap="round"
                    className="text-indigo-600 dark:text-indigo-500 transition-all duration-1000"
                    fill="transparent"
                  />
                </svg>
                <div className="absolute text-center">
                  <span className="text-3xl font-extrabold text-slate-800 dark:text-slate-100">
                    {healthScore?.score}
                  </span>
                  <span className="text-xs text-slate-400 block font-medium">/ 100</span>
                </div>
              </div>
            </div>

            {/* Metric Bars */}
            <div className="space-y-2 mt-2">
              <div className="flex justify-between text-xs">
                <span className="text-slate-500">Savings Rate</span>
                <span className="font-semibold text-slate-700 dark:text-slate-300">
                  {healthScore?.breakdown?.savings_rate} / 25
                </span>
              </div>
              <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-1.5">
                <div
                  className="bg-emerald-500 h-1.5 rounded-full"
                  style={{ width: `${((healthScore?.breakdown?.savings_rate || 0) / 25) * 100}%` }}
                />
              </div>

              <div className="flex justify-between text-xs pt-1">
                <span className="text-slate-500">Budget Adherence</span>
                <span className="font-semibold text-slate-700 dark:text-slate-300">
                  {healthScore?.breakdown?.budget_adherence} / 25
                </span>
              </div>
              <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-1.5">
                <div
                  className="bg-indigo-500 h-1.5 rounded-full"
                  style={{ width: `${((healthScore?.breakdown?.budget_adherence || 0) / 25) * 100}%` }}
                />
              </div>

              <div className="flex justify-between text-xs pt-1">
                <span className="text-slate-500">Debt & EMI Ratio</span>
                <span className="font-semibold text-slate-700 dark:text-slate-300">
                  {healthScore?.breakdown?.debt_ratio} / 20
                </span>
              </div>
              <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-1.5">
                <div
                  className="bg-amber-500 h-1.5 rounded-full"
                  style={{ width: `${((healthScore?.breakdown?.debt_ratio || 0) / 20) * 100}%` }}
                />
              </div>
            </div>
          </div>

          <p className="text-[11px] text-slate-400 mt-4 italic">
            {healthScore?.tips?.[0] || 'Good financial hygiene maintained.'}
          </p>
        </div>
      </div>

      {/* Bottom Section: Category Donut & AI Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Category Expense Donut Chart */}
        <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-bold text-slate-800 dark:text-slate-100 text-base">
              Category Distribution
            </h3>
            <span className="text-xs text-slate-400">All Expenses</span>
          </div>

          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={categoryData.slice(0, 6)}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={4}
                  dataKey="amount"
                >
                  {categoryData.slice(0, 6).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(val) => [`${currencySymbol}${val.toLocaleString()}`]}
                  contentStyle={{
                    borderRadius: '12px',
                    backgroundColor: '#1e293b',
                    border: 'none',
                    color: '#f8fafc',
                    fontSize: '12px',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-1.5 mt-2">
            {categoryData.slice(0, 4).map((cat, idx) => (
              <div key={cat.category} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <div
                    className="w-2.5 h-2.5 rounded-full"
                    style={{ backgroundColor: COLORS[idx % COLORS.length] }}
                  />
                  <span className="text-slate-600 dark:text-slate-400 truncate max-w-[140px]">
                    {cat.category}
                  </span>
                </div>
                <span className="font-semibold text-slate-700 dark:text-slate-300">
                  {cat.percentage}% ({currencySymbol}{cat.amount.toLocaleString()})
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Top 3 Prioritized AI Recommendations */}
        <div className="lg:col-span-2 p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400">
                  <Sparkles className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-bold text-slate-800 dark:text-slate-100 text-base">
                    Smart AI Recommendations
                  </h3>
                  <p className="text-xs text-slate-400">Data-driven actions to optimize your cash flow</p>
                </div>
              </div>
              <Link
                to="/insights"
                className="text-xs text-indigo-600 dark:text-indigo-400 font-semibold hover:underline flex items-center gap-1"
              >
                <span>View Simulator</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="space-y-3">
              {recommendations.slice(0, 3).map((rec, i) => (
                <div
                  key={i}
                  className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60 flex items-start justify-between gap-4"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                        rec.priority === 'high'
                          ? 'bg-rose-100 text-rose-700 dark:bg-rose-950/60 dark:text-rose-400'
                          : 'bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-400'
                      }`}>
                        {rec.priority} Priority
                      </span>
                      <h4 className="text-sm font-semibold text-slate-800 dark:text-slate-100">
                        {rec.title}
                      </h4>
                    </div>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      {rec.evidence}
                    </p>
                  </div>

                  {rec.estimated_saving > 0 && (
                    <div className="text-right shrink-0">
                      <span className="text-xs text-emerald-600 dark:text-emerald-400 font-bold block">
                        +{currencySymbol}{rec.estimated_saving.toLocaleString()}/mo
                      </span>
                      <span className="text-[10px] text-slate-400">Potential Saving</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="pt-4 mt-2 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-400">
            <span>Powered by FinSight Rule & ML Inference Engine</span>
            <button
              onClick={openAddModal}
              className="text-indigo-600 dark:text-indigo-400 font-semibold hover:underline"
            >
              + Quick Add Transaction
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

