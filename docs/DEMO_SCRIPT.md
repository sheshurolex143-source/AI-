# FinSight AI — 5-Minute Viva & Demo Presentation Script

**Project Title:** FinSight AI: AI-Powered Personal Finance Management System  
**Estimated Time:** 5 Minutes  
**Audience:** Assignment Evaluators, Professors & Viva Panel  
**Demo Account:** `demo@finsight.ai` / `Demo@123`  

---

## ⏱️ Timeline Overview

| Minute | Stage / Section | Key Screen | Key Concept to Highlight |
|---|---|---|---|
| **0:00 – 0:45** | Introduction & Problem Context | Login Screen | Local-first architecture, zero paid APIs, privacy |
| **0:45 – 1:45** | Dashboard & Financial Health Score | Overview Dashboard | 0–100 Multi-pillar score, KPI cards, Recharts trends |
| **1:45 – 2:45** | Intelligent Ledger & AI Feedback Loop | Transactions Page | Dual n-gram classification, confidence badges, feedback retrain |
| **2:45 – 3:45** | AI Insights, Anomalies & What-If Simulator | Insights Page | IsolationForest anomalies, What-If slider sensitivity |
| **3:45 – 4:30** | Budgets & Goals Management | Budgets & Goals Page | Run-rate overspend projection, automated savings pace |
| **4:30 – 5:00** | Viva Lab: "How the AI Works" & Conclusion | AI Lab Page | Live inference sandbox, metrics report, Q&A wrap-up |

---

## 🎙️ Step-by-Step Spoken Script

### [0:00 – 0:45] Introduction & Login
**Action:** Open `http://localhost:5173`. Show the clean fintech sign-in page with pre-filled demo credentials.

> *"Good morning, esteemed evaluators. Today I am presenting **FinSight AI**, an AI-powered personal finance management system designed specifically for the AI for Finance curriculum.*
>
> *Personal finance apps typically force a tradeoff between data privacy and smart features by sending sensitive financial statements to expensive third-party cloud LLMs. FinSight AI solves this by running 100% locally on modern machine learning algorithms with zero paid API keys.*
>
> *Let's log in using our seeded demo account, which comes pre-loaded with 6 months of realistic Indian banking transactions, planted anomalies, and active budgets."*

*(Click "Sign In")*

---

### [0:45 – 1:45] Dashboard & Financial Health Score
**Action:** Navigate through the Dashboard. Point to the KPI cards, monthly trends, donut breakdown, and SVG Health Score dial.

> *"Upon logging in, the user lands on the Financial Overview Command Center:*
> 1. *Across the top, we see core KPIs: Total Income, Total Expenses, Net Savings, and an impressive savings rate of 45.9% over the 6-month historical window.*
> 2. *In the center, our Recharts visualization compares cash inflows against outflows month-over-month.*
> 3. *On the right, we feature our **Financial Health Score (0–100)**. Rather than an arbitrary black-box number, this score is computed across five transparent pillars: savings rate, category budget adherence, debt and EMI obligations ratio, spending stability, and emergency buffer progress.*
> 4. *Notice the top alert banner: our AI has already isolated unusual spending anomalies from the ledger, prompting proactive review before month-end."*

---

### [1:45 – 2:45] Transaction Ledger & AI Human-in-the-Loop
**Action:** Click **"Transactions"** in the sidebar. Show filters, search box, confidence scores, and inline category correction.

> *"Next, let's explore the Transaction Ledger:*
> - *Every transaction contains a date, description, type, amount in Indian Rupees (₹), and an **AI Categorization Confidence Score**.*
> - *Our classifier combines word (1-2) n-grams with sub-word character (2-4) n-grams and Calibrated Linear Support Vector Classification. This enables it to easily decipher noisy bank descriptions like `UPI/SWIGGY*ORDER 8842` into `Food & Dining` with over 90% confidence.*
> - *Whenever confidence falls below 60%, the system automatically flags the transaction with a 'Needs Review' badge.*
> - *Crucially, we incorporate a **Human-in-the-Loop feedback mechanism**: when a user adjusts a category using the inline dropdown, the record is flagged as user-verified. In the Settings view, the user can trigger an on-demand model retraining that merges these corrections back into the dataset, demonstrating active continual learning."*

---

### [2:45 – 3:45] Insights, Anomalies & What-If Simulator
**Action:** Click **"AI Insights"** in the sidebar. Scroll to the What-If Simulator and move the sliders. Show the Anomaly Watch and Subscription Table.

> *"Moving to the AI Insights page:*
> - *At the top is our **Interactive What-If Budget Simulator**. If a user considers reducing food delivery or shopping by 20%, they can simply drag the slider. The system recalculates their projected monthly surplus, annualized savings, and simulated new financial health score in real-time.*
> - *Below that, our **Time-Series Forecaster** combines weighted moving averages with linear trend regression, providing next month’s expected outflow per category bounded by 90% parametric confidence bands.*
> - *In the bottom cards, our **IsolationForest** model flags planted anomalies—such as an abnormal ₹7,800 electricity surcharge or an unexpected ₹42,000 electronics spree—with plain-English reasons.*
> - *Beside it, our recurring payment detector clusters periodic debits (like Netflix, Spotify, and broadband) to expose annualized subscription costs."*

---

### [3:45 – 4:30] Budgets & Savings Goals
**Action:** Click **"Budgets & Goals"** in the sidebar. Highlight the progress bars and the run-rate projection alert.

> *"In the Budgets & Goals section:*
> - *Users set category-specific monthly spending caps. Each budget bar shows live utilization.*
> - *Notice the warning: our algorithm computes the current daily burn-rate against the remaining days in the month to project end-of-month spend, proactively alerting users if they are on track to exceed their limit before it actually happens.*
> - *Under Savings Goals, milestone trackers automatically calculate the required monthly contribution needed to reach deadlines for an Emergency Fund or Vacation Fund."*

---

### [4:30 – 5:00] How the AI Works (Viva Lab) & Conclusion
**Action:** Click **"How AI Works"** in the sidebar. Type a custom description into the test box (e.g. `UPI/ZOMATO RESTAURANT 4910`) and click "Run Inference". Point to the test accuracy and classification report.

> *"Finally, we designed the **How the AI Works** page specifically for academic viva examination:*
> - *Evaluators can observe our empirical model metrics: **100% test accuracy** on the held-out test split, with precision, recall, and F1-scores documented across all 13 categories.*
> - *Evaluators can test the classifier live in our inference sandbox. If I type `UPI/ZOMATO RESTAURANT 4910` and click 'Run Inference', the model returns `Food & Dining` with calibrated probability and displays the top 3 alternative classes.*
>
> *In summary, FinSight AI demonstrates a complete, secure, and production-ready application of AI in finance—delivering real predictive utility without external API expenses.*
>
> *Thank you, and I look forward to your questions!"*

---

## 🎯 Anticipated Viva Questions & Model Answers

**Q1: Why did you choose LinearSVC over a Deep Neural Network (e.g., LSTM or BERT)?**  
*Answer:* In high-dimensional sparse text feature spaces (17,000+ n-gram features), Linear Support Vector Machines find the optimal hyperplane with maximal geometric margin. LinearSVC trains in seconds, runs with sub-3ms inference latency on standard CPUs, and requires zero GPU hardware, making it ideal for client-side and edge finance devices while achieving 100% accuracy on our banking corpus.

**Q2: How does the model output confidence percentages if SVMs do not inherently produce probabilities?**  
*Answer:* We wrapped the LinearSVC within `CalibratedClassifierCV` using 3-fold cross-validation. This fits a sigmoid calibration function (Platt scaling) over the raw decision values to map geometric distances to well-calibrated Bayesian posterior probabilities $P(y_k | x)$.

**Q3: How does the anomaly detection algorithm work?**  
*Answer:* We use an ensemble approach: IsolationForest builds random partitioning trees where multi-dimensional outliers isolate near the root of the tree, combined with a per-category z-score threshold ($Z > 2.5$) on log-scaled amounts. This flags both global spikes and category-relative anomalies with explainable reasons.

