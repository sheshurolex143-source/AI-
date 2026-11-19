import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  TrendingUp,
  AlertTriangle,
  Calendar,
  Sliders,
  DollarSign,
  ArrowRight,
  ShieldAlert,
  Repeat,
  CheckCircle,
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from 'recharts';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';

export default function Insights() {
  const { currencySymbol } = useAuth();

  const [recommendations, setRecommendations] = useState([]);
  const [forecast, setForecast] = useState(null);
  const [recurring, setRecurring] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);

  // What-If Simulator State
  const [adjustments, setAdjustments] = useState({
    'Food & Dining': 15,
    Shopping: 20,
    'Entertainment & Subscriptions': 10,
  });
  const [simResult, setSimResult] = useState(null);
  const [simLoading, setSimLoading] = useState(false);

  useEffect(() => {
    const fetchInsights = async () => {
      setLoading(true);
      try {
        const [recsRes, fcRes, recsPayRes, anomRes] = await Promise.all([
          api.get('/api/insights/recommendations'),
          api.get('/api/analytics/forecast'),
          api.get('/api/analytics/recurring'),
          api.get('/api/analytics/anomalies'),
        ]);

        setRecommendations(recsRes.data);
        setForecast(fcRes.data);
        setRecurring(recsPayRes.data);
        setAnomalies(anomRes.data);
      } catch (err) {
        console.error('Failed to load insights', err);
      } finally {
        setLoading(false);
      }
    };
    fetchInsights();
  }, []);

  // Run What-If simulation
  useEffect(() => {
    const runSimulation = async () => {
      setSimLoading(true);
      try {
        const res = await api.post('/api/insights/what-if', { adjustments });
        setSimResult(res.data);
      } catch (err) {
        console.error('What-if error', err);
      } finally {
        setSimLoading(false);
      }
    };
    runSimulation();
  }, [adjustments]);

  const handleSliderChange = (cat, val) => {
    setAdjustments((prev) => ({
      ...prev,
      [cat]: parseInt(val, 10),
    }));
  };

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-64 bg-slate-200 dark:bg-slate-800 rounded-3xl" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="h-80 bg-slate-200 dark:bg-slate-800 rounded-3xl" />
          <div className="h-80 bg-slate-200 dark:bg-slate-800 rounded-3xl" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* 1. What-If Scenario Simulator Card */}
      <div className="p-6 sm:p-8 rounded-3xl bg-gradient-to-br from-indigo-900 via-indigo-950 to-slate-950 text-white shadow-xl border border-indigo-800/40 relative overflow-hidden">
        <div className="absolute top-0 right-0 p-8 opacity-10 pointer-events-none">
          <Sliders className="w-64 h-64 text-indigo-400" />
        </div>

        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-2">
            <span className="p-1.5 rounded-lg bg-indigo-500/20 text-indigo-300 border border-indigo-400/20">
              <Sliders className="w-4 h-4" />
            </span>
            <span className="text-xs font-bold uppercase tracking-wider text-indigo-300">
              Interactive Financial Simulation
            </span>
          </div>
          <h2 className="text-2xl font-black">AI What-If Budget Simulator</h2>
          <p className="text-xs sm:text-sm text-indigo-200/80 max-w-2xl mt-1">
            Adjust discretionary spending cuts below to see instantaneous projections on monthly surplus, annualized savings, and financial health score improvement.
          </p>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-6">
            {/* Sliders Column */}
            <div className="lg:col-span-2 space-y-4">
              {['Food & Dining', 'Shopping', 'Entertainment & Subscriptions', 'Travel'].map((cat) => (
                <div key={cat} className="space-y-1.5 bg-white/5 p-4 rounded-2xl border border-white/10">
                  <div className="flex justify-between items-center text-xs font-semibold">
                    <span className="text-indigo-100">{cat}</span>
                    <span className="text-indigo-300 font-mono">
                      -{adjustments[cat] || 0}% cut
                    </span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="50"
                    step="5"
                    value={adjustments[cat] || 0}
                    onChange={(e) => handleSliderChange(cat, e.target.value)}
                    className="w-full accent-indigo-400 cursor-pointer h-1.5 bg-slate-700 rounded-lg appearance-none"
                  />
                  <div className="flex justify-between text-[10px] text-slate-400">
                    <span>0% (As-is)</span>
                    <span>25% Moderate</span>
                    <span>50% Aggressive</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Projection Outcome Panel */}
            <div className="bg-white/10 backdrop-blur-md p-6 rounded-2xl border border-white/20 flex flex-col justify-between">
              <div>
                <span className="text-xs font-semibold text-indigo-200">Simulation Projections</span>
                <div className="mt-4 space-y-3">
                  <div>
                    <span className="text-[11px] text-indigo-300 block">Monthly Savings Boost</span>
                    <span className="text-2xl font-bold text-emerald-400">
                      +{currencySymbol}{simResult?.monthly_savings.toLocaleString()} / mo
                    </span>
                  </div>
                  <div>
                    <span className="text-[11px] text-indigo-300 block">Yearly Compounded Surplus</span>
                    <span className="text-xl font-bold text-emerald-300">
                      +{currencySymbol}{simResult?.yearly_savings.toLocaleString()} / yr
                    </span>
                  </div>
                  <div className="pt-2 border-t border-white/10">
                    <span className="text-[11px] text-indigo-300 block">Projected Health Score</span>
                    <div className="flex items-baseline gap-2 mt-0.5">
                      <span className="text-3xl font-extrabold text-white">
                        {simResult?.new_health_score}
                      </span>
                      <span className="text-xs text-indigo-300 font-semibold">/ 100</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-white/10 text-[10px] text-indigo-200/70">
                Calculated across weighted historical categorical distributions.
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 2. Spending Forecast Chart with Confidence Band */}
      <div className="p-6 sm:p-8 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400">
                <TrendingUp className="w-4 h-4" />
              </div>
              <h3 className="font-bold text-slate-800 dark:text-slate-100 text-lg">
                Next-Month Spending Forecast
              </h3>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Linear trend regression + weighted moving average with 90% confidence bands
            </p>
          </div>

          <div className="text-right">
            <span className="text-xs text-slate-400 block font-medium">Total Predicted Next Month</span>
            <span className="text-2xl font-extrabold text-indigo-600 dark:text-indigo-400">
              {currencySymbol}{forecast?.total_predicted.toLocaleString()}
            </span>
            <span className="text-[11px] text-slate-400 block">
              Confidence Range: {currencySymbol}{forecast?.total_confidence_low.toLocaleString()} – {currencySymbol}{forecast?.total_confidence_high.toLocaleString()}
            </span>
          </div>
        </div>

        {/* Forecast Bar/Category comparison */}
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={forecast?.forecasts.slice(0, 7) || []}
              margin={{ top: 10, right: 10, left: -20, bottom: 25 }}
            >
              <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
              <XAxis dataKey="category" tick={{ fontSize: 10 }} interval={0} angle={-15} textAnchor="end" />
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
              <Legend wrapperStyle={{ fontSize: '12px' }} />
              <Bar dataKey="current_month_avg" name="Recent Average" fill="#94a3b8" radius={[4, 4, 0, 0]} />
              <Bar dataKey="predicted_next_month" name="AI Predicted Next Month" fill="#6366f1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 3. Smart Recommendations Full List */}
      <div className="p-6 sm:p-8 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        <div className="flex items-center gap-2 mb-2">
          <div className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-bold text-slate-800 dark:text-slate-100 text-lg">
              Personalized Recommendations Engine
            </h3>
            <p className="text-xs text-slate-400">
              Targeted savings suggestions synthesized from your spending habits
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {recommendations.map((rec, i) => (
            <div
              key={i}
              className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/80 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className={`text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full ${
                    rec.priority === 'high'
                      ? 'bg-rose-100 text-rose-700 dark:bg-rose-950/60 dark:text-rose-400'
                      : 'bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-400'
                  }`}>
                    {rec.priority} Priority
                  </span>
                  <span className="text-xs text-slate-400 font-medium">{rec.category}</span>
                </div>
                <h4 className="font-bold text-slate-800 dark:text-slate-100 text-sm">{rec.title}</h4>
                <p className="text-xs text-slate-600 dark:text-slate-300 mt-1">{rec.reason}</p>
                <p className="text-xs text-slate-400 dark:text-slate-400 mt-2 bg-white dark:bg-slate-900 p-2.5 rounded-xl border border-slate-200/60 dark:border-slate-800 font-mono">
                  {rec.evidence}
                </p>
              </div>

              {rec.estimated_saving > 0 && (
                <div className="mt-4 pt-3 border-t border-slate-200/60 dark:border-slate-700/60 flex items-center justify-between text-xs">
                  <span className="text-slate-500">Target Monthly Reduction:</span>
                  <span className="font-bold text-emerald-600 dark:text-emerald-400 text-sm">
                    +{currencySymbol}{rec.estimated_saving.toLocaleString()}
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* 4. Recurring Subscriptions & Anomaly Explorer */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recurring Payments Table */}
        <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="p-2 rounded-xl bg-purple-50 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400">
                <Repeat className="w-4 h-4" />
              </div>
              <div>
                <h3 className="font-bold text-slate-800 dark:text-slate-100 text-base">
                  Detected Subscriptions & Recurring Debits
                </h3>
                <p className="text-xs text-slate-400">Regular debits clustered at ~monthly intervals</p>
              </div>
            </div>

            <div className="divide-y divide-slate-100 dark:divide-slate-800 text-xs">
              {recurring.length === 0 ? (
                <p className="py-6 text-center text-slate-400">No recurring payments identified yet.</p>
              ) : (
                recurring.map((item, idx) => (
                  <div key={idx} className="py-3 flex items-center justify-between">
                    <div>
                      <span className="font-semibold text-slate-800 dark:text-slate-200 block">
                        {item.merchant}
                      </span>
                      <span className="text-[11px] text-slate-400">
                        {item.category} • {item.transaction_count} charges recorded
                      </span>
                    </div>
                    <div className="text-right">
                      <span className="font-bold text-slate-800 dark:text-slate-100 block">
                        {currencySymbol}{item.monthly_cost.toLocaleString()} / mo
                      </span>
                      <span className="text-[10px] text-slate-400">
                        ({currencySymbol}{item.yearly_cost.toLocaleString()} / yr)
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Anomaly Detection List */}
        <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="p-2 rounded-xl bg-rose-50 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400">
                <ShieldAlert className="w-4 h-4" />
              </div>
              <div>
                <h3 className="font-bold text-slate-800 dark:text-slate-100 text-base">
                  IsolationForest Anomaly Watch
                </h3>
                <p className="text-xs text-slate-400">Ensemble z-score + multivariate outlier flags</p>
              </div>
            </div>

            <div className="space-y-3">
              {anomalies.length === 0 ? (
                <p className="py-6 text-center text-slate-400">No active spending anomalies.</p>
              ) : (
                anomalies.map((item, idx) => (
                  <div
                    key={idx}
                    className="p-3.5 rounded-2xl bg-rose-50/60 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900/50 flex items-start justify-between gap-3 text-xs"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-rose-800 dark:text-rose-200">
                          {item.transaction.description}
                        </span>
                        <span className="text-[10px] text-slate-400">{item.transaction.date}</span>
                      </div>
                      <p className="text-[11px] text-rose-700 dark:text-rose-300 mt-1">
                        Reason: {item.reason}
                      </p>
                    </div>
                    <div className="text-right shrink-0">
                      <span className="font-bold text-rose-600 dark:text-rose-400 block">
                        {currencySymbol}{item.transaction.amount.toLocaleString()}
                      </span>
                      <span className="text-[10px] text-slate-400">{item.transaction.category}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

