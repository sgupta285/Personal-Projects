# Srijan Gupta | Project Portfolio

<p align="left">
  <img src="https://img.shields.io/badge/Focus-AI%2FML-blue" alt="AI/ML Badge" />
  <img src="https://img.shields.io/badge/Focus-Backend%20Systems-green" alt="Backend Badge" />
  <img src="https://img.shields.io/badge/Focus-Cloud%20%26%20Infra-orange" alt="Infra Badge" />
  <img src="https://img.shields.io/badge/Focus-Quant%20Research-purple" alt="Quant Badge" />
  <img src="https://img.shields.io/badge/Projects-28-black" alt="Projects Count" />
</p>

I build production-minded systems across AI/LLM engineering, backend platforms, distributed infrastructure, quantitative finance, applied machine learning, and data science.

This repository is designed to act as a **portfolio of my work**, not just a dump of code. The goal is to show how I think about systems end to end: architecture, performance, experimentation, observability, reproducibility, and business impact.

## What this repository covers

- **Multiple projects** across AI systems, full-stack engineering, cloud infrastructure, trading systems, forecasting, econometrics, and analytics
- **Production-focused builds** with attention to latency, scale, reliability, deployment, and monitoring
- **Research and experimentation workflows** covering model evaluation, causal inference, forecasting, optimization, and backtesting
- **Broad technical range** across Python, C++, FastAPI, React, Kubernetes, Docker, PostgreSQL, Redis, AWS, Terraform, Spark, ML tooling, and observability stacks

## Featured projects

### 1) ClearClause
**Production Legal RAG System with Hybrid Search and Reranking**

Built a legal retrieval and grounded Q&A platform for contracts using hybrid retrieval, reranking, Redis semantic caching, and Kubernetes-based deployment. Focused on precision, latency reduction, observability, and safety guardrails such as PII redaction and structured validation.

**Highlights**
- Achieved **0.87 precision@10**
- Reduced **p95 latency by 93%** from **4.3s to 300ms**
- Deployed with **Kubernetes HPA** to support **200+ QPS**

**Stack:** Python, FastAPI, pgvector, Redis, BM25, embeddings, reranking, Docker, Kubernetes, OpenTelemetry, Prometheus, Grafana

---

### 2) BuckyConnect
**Real-Time Collaboration Platform using WebSockets and GraphQL**

Built a real-time collaboration system with WebSockets for live updates, GraphQL for structured reads, and Redis Pub/Sub for event fanout across instances. Designed for concurrency, responsiveness, and cloud-native deployment.

**Highlights**
- Supported **280+ concurrent users**
- Sustained **1,000+ events/sec**
- Maintained **sub-500ms latency targets** under real-time load

**Stack:** React, Node.js, TypeScript, WebSockets, GraphQL, Redis Pub/Sub, AWS ECS, CloudFront, DynamoDB

---

### 3) Spotify Music Popularity Pipeline
**ML Training and Serverless Inference System**

Built a reproducible ML pipeline to predict track popularity using ensemble models, Optuna optimization, MLflow tracking, and AWS Lambda inference. Focused on training reproducibility, deployment, and low-latency prediction.

**Highlights**
- Improved model accuracy by **45%**
- Achieved **MAE near 10.0** on a 0 to 100 popularity scale
- Processed **1M+ records** end to end

**Stack:** Python, XGBoost, LightGBM, scikit-learn, Optuna, MLflow, AWS Lambda, Redis

---

### 4) LLM Evaluation & Inference Stack
**Benchmarking and High-Throughput Serving for Transformer Models**

Built a scalable evaluation and inference stack for LLMs to compare latency, throughput, retrieval quality, and answer relevance across prompts, checkpoints, and serving strategies. Designed for reproducibility and structured experiment tracking.

**Highlights**
- Integrated **vLLM**, async FastAPI, and dynamic batching
- Added **MLflow-based run tracking** for reproducible comparison
- Improved observability for inference and evaluation workflows

**Stack:** Python, Hugging Face Transformers, vLLM, FastAPI, MLflow, Docker

---

### 5) Ads Integrity & Content Moderation Platform
**Fraud Detection and Policy Enforcement System**

Built a backend system that screens ad creatives and metadata before serving using moderation services, risk scoring, a rules engine, and analytics workflows. Designed to reflect real-world ad integrity and trust & safety problems.

**Highlights**
- Flagged spam, scams, and policy-violating content using ML plus rules
- Used **Kafka** for event streaming and **Redis** for real-time scoring
- Added a dashboard to surface fraud trends and moderation decisions

**Stack:** Python, FastAPI, Kafka, Redis, PostgreSQL, scikit-learn, React, Docker

---

### 6) Algorithmic Trading Strategy Backtest
**Research-Grade Momentum Backtesting Engine**

Built a backtesting engine in C++ with Python analysis tooling and PostgreSQL-backed data workflows for systematic momentum research. Emphasized walk-forward validation, execution realism, and speed.

**Highlights**
- Achieved **18.2% annualized return** and **1.47 Sharpe**
- Outperformed **SPY by 820 bps**
- Improved simulation throughput **3x** for **100K+ simulations**

**Stack:** C++, Python, PostgreSQL, OpenMP, SIMD, quantitative research tooling

## Full project index

## AI, ML, and LLM Systems

| Project | Focus | Core Stack |
|---|---|---|
| ClearClause | Legal RAG, hybrid search, grounded Q&A | Python, FastAPI, pgvector, Redis, Kubernetes |
| Spotify Music Popularity Pipeline | ML training, model tuning, serverless inference | Python, XGBoost, LightGBM, Optuna, MLflow, AWS Lambda |
| LLM Evaluation & Inference Stack | Benchmarking, inference serving, experiment tracking | Python, vLLM, FastAPI, MLflow |
| Ads Integrity & Content Moderation Platform | Fraud detection, moderation, policy enforcement | Python, Kafka, Redis, PostgreSQL, React |
| Real-Time Fraud Detection API | Low-latency scoring, drift monitoring, MLOps | Python, FastAPI, Redis, Kubernetes |
| AI Trend Radar | Trend detection, clustering, evidence-backed summarization | Python, embeddings, PostgreSQL, Redis |
| Customer Churn Prediction & Intervention | Explainable ML, intervention design, survival analysis | Python, XGBoost, SHAP, Tableau |

## Backend, Full-Stack, and Product Engineering

| Project | Focus | Core Stack |
|---|---|---|
| BuckyConnect | Real-time collaboration, event fanout | React, Node.js, TypeScript, GraphQL, Redis |
| E-Commerce Backend System | REST APIs, caching, performance tuning | Python, FastAPI, PostgreSQL, Redis |
| Product Metrics & Analytics Framework | Funnels, KPI design, dashboards | SQL, Python, Tableau |
| E-Commerce Conversion Optimization | A/B testing, segmentation, reporting automation | Python, SQL, Tableau |

## Quantitative Finance and Trading Systems

| Project | Focus | Core Stack |
|---|---|---|
| Algorithmic Trading Strategy Backtest | Momentum research, walk-forward validation | C++, Python, PostgreSQL |
| Options Pricing & Greeks Engine | Pricing, simulation, calibration | C++, Eigen, Boost, Python |
| Statistical Arbitrage Pairs Trading | Cointegration, Kalman filters, low-latency signals | Python, R, PostgreSQL, Redis |
| Dynamic Pricing Algorithm Optimization | Pricing strategy, revenue optimization | Python, XGBoost, SQL |

## Data Science, Econometrics, and Forecasting

| Project | Focus | Core Stack |
|---|---|---|
| Healthcare Spending vs Life Expectancy | ETL, fixed effects, data storytelling | Python, R, Tableau |
| Retail Demand Forecasting System | SKU forecasting, external regressors | Python, R, Prophet, ARIMA |
| Retail Demand Elasticity Analysis | VAR, structural breaks, counterfactual analysis | Python, R, statsmodels |
| Randomized Controlled Trial Evaluation | Causal inference, LATE, heterogeneity | Python, R |
| Minimum Wage Employment Effects | Difference-in-differences, event study | R, Stata |
| Marketing Attribution & Response Modeling | Attribution, response modeling, experimentation | Python, SQL, Spark |

## Cloud, Infrastructure, and Systems Engineering

| Project | Focus | Core Stack |
|---|---|---|
| Kubernetes Observability Platform | Metrics, logs, traces, automated monitoring | Kubernetes, Prometheus, Grafana, Helm, Go |
| High-Performance Storage Infrastructure | Distributed storage, caching, performance | Ceph, MinIO, Kubernetes, Redis |
| Cloud-Native Production Platform | AWS infrastructure, scaling, observability | AWS, Kubernetes, Docker, Terraform |
| Infrastructure Automation Framework | GitOps, orchestration, automation tooling | Python, Go, Terraform, Helm |
| Real-Time Control System | Embedded systems, deterministic processing | C++, Python, Linux, RTOS |
| Geometry Processing Pipeline | Mesh optimization, path planning, computational geometry | C++, Python |
| Distributed Data Acquisition System | Streaming systems, lock-free data structures | C++, Python, Linux |

## All projects in this portfolio

### AI, ML, and LLM Systems
1. ClearClause - Production Legal RAG System (Hybrid Search + Reranking)
2. Spotify Music Popularity Pipeline - ML Training + Serverless Inference
3. LLM Evaluation & Inference Stack - Benchmarking + High-Throughput Serving
4. Ads Integrity & Content Moderation Platform - Fraud Detection + Policy Enforcement
5. Real-Time Fraud Detection API - Low-Latency ML Inference + Drift Monitoring
6. AI Trend Radar - Trend Detection + Evidence-Backed Summarization
7. Customer Churn Prediction & Intervention - Explainable ML + Playbook

### Backend, Full-Stack, and Product Engineering
8. BuckyConnect - Real-Time Collaboration Platform (WebSockets + GraphQL)
9. E-Commerce Backend System - REST API Performance + Load Testing
10. Product Metrics & Analytics Framework - Funnels + Health Metrics
11. E-Commerce Conversion Optimization - A/B Testing + Power + Segmentation

### Quantitative Finance and Trading Systems
12. Algorithmic Trading Strategy Backtest - Momentum + Walk-Forward Validation
13. Options Pricing & Greeks Engine - Black-Scholes + Monte Carlo + Calibration
14. Statistical Arbitrage Pairs Trading - Cointegration + Kalman Filters
15. Dynamic Pricing Algorithm Optimization - Revenue Maximization

### Data Science, Econometrics, and Forecasting
16. Healthcare Spending vs Life Expectancy - ETL + Fixed Effects + Tableau Story
17. Retail Demand Forecasting System - SKU Forecasts + External Regressors
18. Retail Demand Elasticity Analysis - ARIMA/VAR + Structural Breaks
19. Randomized Controlled Trial Evaluation - LATE via 2SLS + Heterogeneity
20. Minimum Wage Employment Effects - Modern DID + Event Study
21. Marketing Attribution & Response Modeling - Multi-Touch Attribution

### Cloud, Infrastructure, and Systems Engineering
22. Kubernetes Observability Platform - Metrics, Logs, Traces
23. High-Performance Storage Infrastructure - Distributed Storage at Scale
24. Cloud-Native Production Platform - AWS + K8s Infrastructure
25. Infrastructure Automation Framework - DevOps Tools & Pipelines
26. Real-Time Control System - Embedded + High-Rate Data Processing
27. Geometry Processing Pipeline - 3D Mesh Processing + Optimization
28. Distributed Data Acquisition System - High-Rate Streaming + Storage

## Technical themes across the repository

### 1. Production-minded engineering
I try to build beyond prototype quality. That means caching, monitoring, autoscaling, testing, CI/CD, experiment tracking, and failure-aware design where relevant.

### 2. Measurable outcomes
I prefer projects that can be evaluated clearly, whether through p95 latency, throughput, MAPE, precision/recall, Sharpe ratio, uplift, or causal effect estimates.

### 3. Systems thinking
A lot of the work here sits at the intersection of application logic, infrastructure, data workflows, and analytics. I like building systems where those layers connect cleanly.

### 4. Breadth with depth
This portfolio spans AI/ML, backend, quant, infrastructure, experimentation, and data science, but each project is still framed around implementation details and engineering tradeoffs.

## Core tools and technologies

**Languages:** Python, C++, TypeScript, SQL, R, Go, Stata  
**Backend:** FastAPI, Node.js, GraphQL, REST APIs, WebSockets  
**ML / Data:** scikit-learn, XGBoost, LightGBM, Optuna, MLflow, statsmodels, Spark  
**Infra / DevOps:** Docker, Kubernetes, Terraform, Helm, GitHub Actions, AWS, Redis, PostgreSQL  
**Observability:** Prometheus, Grafana, OpenTelemetry, Jaeger  
**Analytics / Visualization:** Tableau, dashboards, experimentation frameworks, causal inference workflows


