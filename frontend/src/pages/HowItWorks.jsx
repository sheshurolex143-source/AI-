import React, { useState, useEffect } from 'react';
import {
  BrainCircuit,
  Sparkles,
  BarChart3,
  ShieldCheck,
  CheckCircle,
  HelpCircle,
  Layers,
  ArrowRight,
  Database,
  Cpu,
  RefreshCw,
  Search,
} from 'lucide-react';
import api from '../api/client';

export default function HowItWorks() {
  const [metrics, setMetrics] = useState(null);
  const [loadingMetrics, setLoadingMetrics] = useState(true);

  // Live Playground Sandbox state
  const [testText, setTestText] = useState('UPI/SWIGGY*ORDER 8842 BLR');
  const [prediction, setPrediction] = useState(null);
  const [predicting, setPredicting] = useState(false);

  const sampleQueries = [
    'UPI/SWIGGY*ORDER 8842 BLR',
    'POS 4421 BIGBASKET RETAIL',
    'NACH DEBIT HDFC HOME LOAN EMI',
    'NEFT MONTHLY SALARY CREDIT INFOSYS',
    'NETFLIX ENTERTAINMENT SUBSCRIPTION',
    'MAKEMYTRIP FLIGHT TICKETS INDIGO',
    'BESCOM ELECTRICITY ONLINE BILL',
    'ZERODHA BROKING EQUITY DEPOSIT',
    'APOLLO PHARMACY BLR TXN 8891',
  ];

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await api.get('/api/ml/metrics');
        setMetrics(res.data);
      } catch (err) {
        console.error('Failed to load ML metrics', err);
      } finally {
        setLoadingMetrics(false);
      }
    };
    fetchMetrics();
    handlePredict('UPI/SWIGGY*ORDER 8842 BLR');
  }, []);

  const handlePredict = async (text) => {
    if (!text.trim()) return;
    setPredicting(true);
    try {
      const res = await api.post('/api/ml/categorize', { description: text });
      setPrediction(res.data);
    } catch (err) {
      console.error('Prediction failed', err);
    } finally {
      setPredicting(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400">
            <BrainCircuit className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-2xl font-black text-slate-800 dark:text-slate-100">
              Machine Learning Architecture & Viva Lab
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Transparent review of text categorization, anomaly isolation, forecasting, and evaluation matrices
            </p>
          </div>
        </div>
      </div>

      {/* ── 1. Interactive AI Classification Sandbox ── */}
      <div className="p-6 sm:p-8 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
            <h3 className="font-bold text-slate-800 dark:text-slate-100 text-base">
              Live Categorization Inference Sandbox
            </h3>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 border border-emerald-200/50">
            LinearSVC + CalibratedClassifierCV
          </span>
        </div>

        <p className="text-xs text-slate-500 dark:text-slate-400">
          Type or select any noisy bank statement description to see real-time TF-IDF n-gram tokenization, top predicted category, calibrated Bayesian confidence probability, and top alternative classes:
        </p>

        {/* Input box */}
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
            <input
              type="text"
              value={testText}
              onChange={(e) => setTestText(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handlePredict(testText)}
              placeholder="Enter noisy bank description e.g. POS 8812 DMART BLR"
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            />
          </div>
          <button
            onClick={() => handlePredict(testText)}
            disabled={predicting}
            className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs shadow-md shadow-indigo-500/25 transition active:scale-95 whitespace-nowrap"
          >
            {predicting ? 'Evaluating...' : 'Run Inference'}
          </button>
        </div>

        {/* Preset pill buttons */}
        <div className="flex items-center gap-2 flex-wrap text-xs">
          <span className="text-slate-400 font-semibold text-[11px]">Quick Samples:</span>
          {sampleQueries.map((sample, idx) => (
            <button
              key={idx}
              onClick={() => {
                setTestText(sample);
                handlePredict(sample);
              }}
              className="px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 text-slate-600 dark:text-slate-300 text-[11px] font-mono border border-slate-200/60 dark:border-slate-700 transition"
            >
              {sample}
            </button>
          ))}
        </div>

        {/* Prediction Results Card */}
        {prediction && (
          <div className="p-5 rounded-2xl bg-indigo-50/50 dark:bg-indigo-950/30 border border-indigo-200/80 dark:border-indigo-900/60 grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
            <div>
              <span className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider block">
                Primary Model Output
              </span>
              <div className="mt-1 flex items-baseline gap-3">
                <span className="text-2xl font-black text-slate-800 dark:text-slate-100">
                  {prediction.category}
                </span>
                <span className="text-sm font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-100 dark:bg-indigo-900/60 px-2.5 py-0.5 rounded-full">
                  {Math.round(prediction.confidence * 100)}% Confidence
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-2">
                Status:{' '}
                {prediction.needs_review ? (
                  <span className="text-amber-600 font-semibold">
                    Flagged for Human Review (&lt;60% confidence threshold)
                  </span>
                ) : (
                  <span className="text-emerald-600 font-semibold">
                    High Confidence Auto-Classification Passed
                  </span>
                )}
              </p>
            </div>

            {/* Top 3 Alternatives */}
            <div className="space-y-2 border-t md:border-t-0 md:border-l border-indigo-100 dark:border-indigo-900/60 md:pl-6 pt-4 md:pt-0">
              <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 block">
                Top Alternative Probabilities:
              </span>
              {prediction.alternatives.map((alt, i) => (
                <div key={i} className="flex items-center justify-between text-xs">
                  <span className="text-slate-700 dark:text-slate-300 font-medium">
                    {i + 1}. {alt.category}
                  </span>
                  <div className="flex items-center gap-2">
                    <div className="w-24 bg-slate-200 dark:bg-slate-700 rounded-full h-1.5 overflow-hidden">
                      <div
                        className="bg-indigo-500 h-1.5 rounded-full"
                        style={{ width: `${alt.confidence * 100}%` }}
                      />
                    </div>
                    <span className="text-slate-400 font-mono w-10 text-right">
                      {Math.round(alt.confidence * 100)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* ── 2. Model Metrics & Evaluation Report ── */}
      {metrics && (
        <div className="space-y-6">
          {/* Key Metrics Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
              <span className="text-xs text-slate-400 font-semibold">Test Accuracy</span>
              <p className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-400 mt-1">
                {(metrics.accuracy * 100).toFixed(1)}%
              </p>
              <p className="text-[11px] text-slate-400 mt-1">Held-out 20% stratified test set</p>
            </div>

            <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
              <span className="text-xs text-slate-400 font-semibold">Training Corpus</span>
              <p className="text-3xl font-extrabold text-indigo-600 dark:text-indigo-400 mt-1">
                {metrics.training_samples.toLocaleString()}
              </p>
              <p className="text-[11px] text-slate-400 mt-1">Synthetic + feedback samples</p>
            </div>

            <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
              <span className="text-xs text-slate-400 font-semibold">Feature Dimension</span>
              <p className="text-3xl font-extrabold text-violet-600 dark:text-violet-400 mt-1">
                {metrics.feature_count.toLocaleString()}
              </p>
              <p className="text-[11px] text-slate-400 mt-1">Word (1-2) & Char (2-4) n-grams</p>
            </div>

            <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
              <span className="text-xs text-slate-400 font-semibold">Classes Supported</span>
              <p className="text-3xl font-extrabold text-slate-800 dark:text-slate-100 mt-1">
                {metrics.categories.length}
              </p>
              <p className="text-[11px] text-slate-400 mt-1">Full categorical taxonomy</p>
            </div>
          </div>

          {/* Per-Class Precision / Recall / F1 Table */}
          <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
            <h3 className="font-bold text-slate-800 dark:text-slate-100 text-base mb-4">
              Per-Class Classification Report
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800 text-slate-500 uppercase tracking-wider font-semibold">
                  <tr>
                    <th className="py-2.5 px-4">Category</th>
                    <th className="py-2.5 px-4">Precision</th>
                    <th className="py-2.5 px-4">Recall</th>
                    <th className="py-2.5 px-4">F1-Score</th>
                    <th className="py-2.5 px-4">Support</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800 text-slate-700 dark:text-slate-300">
                  {Object.entries(metrics.per_class_metrics || {}).map(([cat, m]) => (
                    <tr key={cat} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30">
                      <td className="py-2 px-4 font-semibold">{cat}</td>
                      <td className="py-2 px-4 font-mono text-emerald-600 dark:text-emerald-400">
                        {(m.precision * 100).toFixed(1)}%
                      </td>
                      <td className="py-2 px-4 font-mono text-indigo-600 dark:text-indigo-400">
                        {(m.recall * 100).toFixed(1)}%
                      </td>
                      <td className="py-2 px-4 font-mono font-bold text-slate-800 dark:text-slate-100">
                        {(m.f1_score * 100).toFixed(1)}%
                      </td>
                      <td className="py-2 px-4 font-mono text-slate-400">{m.support}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Confusion Matrix Heatmap */}
          {metrics.confusion_matrix && metrics.confusion_matrix.length > 0 && (
            <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-bold text-slate-800 dark:text-slate-100 text-base">
                    Empirical Confusion Matrix Heatmap (13 × 13)
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Rows represent True Actual Classes; Columns represent Model Predictions on held-out test data
                  </p>
                </div>
                <span className="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/50 px-2.5 py-1 rounded-full border border-emerald-200/50">
                  Strong Diagonal Concentration = High Precision
                </span>
              </div>

              <div className="overflow-x-auto pb-2">
                <div className="inline-block min-w-full">
                  <table className="text-center text-[10px] border-collapse">
                    <thead>
                      <tr>
                        <th className="p-1.5 text-left text-slate-400 font-semibold min-w-[120px]">
                          True \ Pred
                        </th>
                        {metrics.categories.map((cat, i) => (
                          <th key={i} className="p-1 text-slate-500 dark:text-slate-400 font-mono text-[9px] w-9 truncate" title={cat}>
                            {cat.slice(0, 3)}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {metrics.confusion_matrix.map((row, i) => (
                        <tr key={i} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/20">
                          <td className="p-1.5 text-left font-semibold text-slate-700 dark:text-slate-300 truncate max-w-[120px]" title={metrics.categories[i]}>
                            {metrics.categories[i]}
                          </td>
                          {row.map((val, j) => {
                            const isDiagonal = i === j;
                            const isNonZero = val > 0;
                            return (
                              <td
                                key={j}
                                className={`p-1 font-mono font-semibold rounded transition cursor-help ${
                                  isDiagonal
                                    ? 'bg-indigo-600 text-white shadow-sm'
                                    : isNonZero
                                    ? 'bg-rose-500/80 text-white'
                                    : 'text-slate-300 dark:text-slate-700'
                                }`}
                                title={`True: ${metrics.categories[i]} | Predicted: ${metrics.categories[j]} | Count: ${val}`}
                              >
                                {val}
                              </td>
                            );
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── 3. Four Core AI Algorithms Architecture ── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Module 1 */}
        <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400">
              <Cpu className="w-4 h-4" />
            </span>
            <h4 className="font-bold text-slate-800 dark:text-slate-100 text-sm">
              1. TF-IDF + Calibrated LinearSVC Classifier
            </h4>
          </div>
          <p className="text-xs text-slate-600 dark:text-slate-300">
            Combines word (1-2) n-grams and character-level (2-4) n-grams to gracefully handle abbreviations, typo noise, and cryptic banking prefixes (UPI, POS, NEFT, NACH). Linear Support Vector Classification provides maximal margin separation, while CalibratedClassifierCV fits isotonic/sigmoid calibration for true posterior probability confidence scores.
          </p>
        </div>

        {/* Module 2 */}
        <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-xl bg-rose-50 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400">
              <ShieldCheck className="w-4 h-4" />
            </span>
            <h4 className="font-bold text-slate-800 dark:text-slate-100 text-sm">
              2. IsolationForest + Z-Score Ensemble Anomaly Detector
            </h4>
          </div>
          <p className="text-xs text-slate-600 dark:text-slate-300">
            Engineers logarithmic amount scaling, merchant transaction frequency, day-of-week, and weekend indicators into Isolation Trees to isolate multi-dimensional outliers. Coupled with robust per-category standard score (z &gt; 2.5) to generate plain-English explanations (e.g. "4.2x higher than usual Shopping spend").
          </p>
        </div>

        {/* Module 3 */}
        <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-xl bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400">
              <BarChart3 className="w-4 h-4" />
            </span>
            <h4 className="font-bold text-slate-800 dark:text-slate-100 text-sm">
              3. Weighted MA + Linear Trend Spending Forecaster
            </h4>
          </div>
          <p className="text-xs text-slate-600 dark:text-slate-300">
            Fuses an exponentially weighted moving average (prioritizing recent months) with first-order linear trend regression to forecast next month's outflow per category. Produces parametric 90% confidence bands derived from residual standard deviation to reflect spending volatility.
          </p>
        </div>

        {/* Module 4 */}
        <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400">
              <Layers className="w-4 h-4" />
            </span>
            <h4 className="font-bold text-slate-800 dark:text-slate-100 text-sm">
              4. Evidence-Based Recommendation & Health Score Engine
            </h4>
          </div>
          <p className="text-xs text-slate-600 dark:text-slate-300">
            Evaluates financial health across 5 core pillars: savings rate (25 pts), budget adherence (25 pts), debt/EMI ratio (20 pts), cash flow stability (15 pts), and emergency fund coverage (15 pts). Computes what-if sensitivity simulations when discretionary categories are reduced.
          </p>
        </div>
      </div>
    </div>
  );
}

