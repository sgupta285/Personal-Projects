# Projects

---

## ClearClause — Production Legal RAG System (Hybrid Search + Reranking)
- Built a production-grade legal retrieval + grounded Q&A system for contracts using hybrid search (semantic + lexical/BM25) with reranking for high-precision passage selection.
- Achieved 0.87 precision@10 and reduced p95 latency 93% (4.3s → 300ms) using Redis semantic caching + response streaming.
- Deployed on Kubernetes with HPA (3–15 replicas) to support 200+ QPS, with observability and reliability guardrails (PII redaction, structured validation).
**Skills/Tools:** Python, FastAPI, pgvector, Redis, BM25, embeddings, reranking, Docker, Kubernetes (HPA), OpenTelemetry/Prometheus/Grafana, PII redaction

## BuckyConnect — Real-Time Collaboration Platform (WebSockets + GraphQL)
- Built a real-time collaboration platform using WebSockets for live updates and GraphQL for structured reads, with Redis Pub/Sub for event fanout across instances.
- Supported 280+ concurrent users, sustained 1,000+ events/sec, and maintained <500ms latency targets under real-time load.
- Deployed cloud-native infrastructure on AWS ECS + CloudFront + DynamoDB with autoscaling; improved UX performance via code splitting, lazy loading, and Web Workers (40% bundle reduction).
**Skills/Tools:** React, Node.js/TypeScript, WebSockets, GraphQL, Redis Pub/Sub, AWS ECS, CloudFront, DynamoDB, autoscaling, frontend performance optimization

## Spotify Music Popularity Pipeline — ML Training + Serverless Inference
- Built a reproducible ML pipeline to predict track popularity using tuned ensemble models (XGBoost/LightGBM + stacking) with Optuna hyperparameter optimization (100+ trials).
- Improved accuracy by 45% and achieved MAE ~10.0 (0–100); processed 1M+ records end-to-end.
- Deployed inference on AWS Lambda with MLflow model versioning and a Redis-backed feature store; reduced latency ~30% via parallelization/provisioned concurrency.
**Skills/Tools:** Python, XGBoost, LightGBM, scikit-learn, Optuna, MLflow, AWS Lambda, Redis, feature engineering, pipeline automation, Docker

## LLM Evaluation & Inference Stack — Benchmarking + High-Throughput Serving
- Built a scalable evaluation + inference stack for transformer-based LLMs, benchmarking latency, throughput, retrieval quality, and answer relevance across prompts, checkpoints, and serving configurations.
- Optimized serving with vLLM, dynamic batching, and async FastAPI endpoints to support fast side-by-side experiments; added structured logging and traceable run metadata for safer debugging and deployment decisions.
- Integrated MLflow to track parameters, metrics, and artifacts across model iterations, making it easier to compare prompt changes, model checkpoints, decoding settings, and serving strategies reproducibly.
**Skills/Tools:** Python, Hugging Face Transformers, vLLM, FastAPI, MLflow, async inference, dynamic batching, retrieval evaluation, answer relevance scoring, structured logging, Docker

## Ads Integrity & Content Moderation Platform — Fraud Detection + Policy Enforcement
- Built an ads integrity platform that screens creatives and metadata before serving using event-driven moderation services, real-time scoring, and policy-aware review workflows.
- Combined a lightweight ML classifier with a rules engine to detect spam, scams, misleading content, and policy violations; routed high-risk ads to manual review while approved ads continued into the serving pipeline.
- Added Kafka-based event streaming, Redis risk caching, Postgres-backed advertiser/ad metadata, and a React analytics dashboard to surface fraud trends, moderation actions, and advertiser risk scores.
**Skills/Tools:** Python, FastAPI, Kafka, Redis, PostgreSQL, scikit-learn, rule engines, content moderation, fraud detection, React, Docker, AWS/GCP

## Real-Time Fraud Detection API — Low-Latency ML Inference + Drift Monitoring
- Built a production fraud scoring API using FastAPI + Redis caching, deployed on Kubernetes with autoscaling and circuit-breaker reliability patterns.
- Trained models on 284K transactions, handling class imbalance with SMOTE + ensembles; achieved 96% precision / 89% recall.
- Sustained 500+ QPS with ~80–100ms p95 latency, backed by Prometheus/Grafana monitoring, Jaeger tracing, and drift tracking + retraining triggers.
**Skills/Tools:** Python, FastAPI, scikit-learn/XGBoost, SMOTE, Redis, Kubernetes, Prometheus, Grafana, Jaeger, CI/CD (GitHub Actions), Trivy, MLOps monitoring

## E-Commerce Backend System — REST API Performance + Load Testing
- Built FastAPI REST services backed by PostgreSQL and improved read performance using indexing + connection pooling.
- Implemented Redis cache-aside and rate limiting for stable performance under concurrency.
- Achieved ~35% latency reduction and ~60% DB load reduction, validated via Locust load tests simulating 1,000+ concurrent users.
**Skills/Tools:** Python, FastAPI, PostgreSQL, Redis, indexing, connection pooling, rate limiting, Docker, pytest, Locust, performance benchmarking

## Algorithmic Trading Strategy Backtest — Momentum + Walk-Forward Validation
- Built a research-grade backtesting engine in C++ with Python analysis tooling and PostgreSQL storage for systematic momentum strategies.
- Applied walk-forward validation and execution realism (slippage + volatility-adaptive sizing) to reduce overfitting risk.
- Achieved 18.2% annualized return, 1.47 Sharpe, outperformed SPY by 820 bps; accelerated simulation throughput 3× (15s → 5s) for 100K+ sims using OpenMP + SIMD.
**Skills/Tools:** C++, Python (NumPy/pandas), PostgreSQL, walk-forward validation, backtesting, OpenMP, SIMD, time-series evaluation, quantitative research

## Options Pricing & Greeks Engine — Black-Scholes + Monte Carlo + Calibration
- Implemented an options pricing and risk engine supporting Black-Scholes and Monte Carlo (10K paths), with Greeks via finite differences.
- Calibrated volatility surfaces using Newton–Raphson for real-time risk analysis workflows.
- Achieved 99.8% accuracy vs Bloomberg, Greeks <0.1% error, <2s runtimes; delivered 85% performance optimization using SIMD + variance reduction.
**Skills/Tools:** C++, Eigen, Boost, Python (NumPy/SciPy), Monte Carlo simulation, finite differences, Newton–Raphson, volatility surface calibration, SIMD, variance reduction

## Statistical Arbitrage Pairs Trading — Cointegration + Kalman Filters
- Built a pairs trading pipeline identifying 200+ equity pairs via Johansen cointegration and trading mean reversion with z-score signals.
- Used Kalman filtering to estimate dynamic hedge ratios under changing market regimes.
- Achieved 65% win rate and 2.1 profit factor; engineered a low-latency system processing 50K+ ticks/sec with <100ms signal-to-order latency and degradation alerts.
**Skills/Tools:** Python (statsmodels), R, PostgreSQL/TimescaleDB, Redis, Johansen cointegration, Kalman filters, low-latency pipelines, monitoring/alerting

## Healthcare Spending vs Life Expectancy — ETL + Fixed Effects + Tableau Story
- Built a reproducible pipeline ingesting 150+ state-level indicators (2020–2023), cutting data prep 2 days → 2 hours via automated validation and standardized joins.
- Fitted multivariate models with region fixed effects and robustness checks; quantified interpretable relationships between per-capita spending and longevity outcomes.
- Published an interactive Tableau story with coefficient plots and drill-downs by region, income quintile, and mortality-linked categories for stakeholder-ready analysis.
**Skills/Tools:** Python (pandas/statsmodels), R (fixest/plm/did variants), ETL automation, regression modeling, fixed effects, robustness checks, Tableau, data storytelling

## Customer Churn Prediction & Intervention — Explainable ML + Playbook
- Built churn models across 500K+ customers using XGBoost/scikit-learn, achieving 87% precision / 82% recall.
- Added SHAP explainability to surface drivers and prioritize interventions; modeled time-to-churn using Cox proportional hazards in a consulting variant.
- Reduced churn 12% → 7% and improved operational speed with workflows that cut time-to-intervention 14 days → 2 days.
**Skills/Tools:** SQL (PostgreSQL), Python, XGBoost, scikit-learn, SHAP, Tableau, survival analysis (Cox), intervention design, KPI monitoring

## Retail Demand Forecasting System — SKU Forecasts + External Regressors
- Built demand forecasts for 50+ SKUs using Prophet/ARIMA and ensemble methods, incorporating external drivers (holidays, promotions, weather).
- Achieved 8.2% MAPE (~40% better than baseline) through feature + model iteration and evaluation discipline.
- Delivered dashboards with forecast uncertainty bands to support safety-stock and scenario planning for decision-makers.
**Skills/Tools:** Python (Prophet, ARIMA, XGBoost), R, time-series modeling, feature engineering, Tableau, uncertainty bands, scenario analysis

## Retail Demand Elasticity Analysis — ARIMA/VAR + Structural Breaks
- Modeled demand dynamics using ARIMA + VAR and validated long-run relationships with cointegration diagnostics.
- Tested stability using Chow structural break tests to avoid fragile elasticity estimates under regime changes.
- Used impulse response functions to run counterfactual simulations and communicate how shocks propagate through demand over time.
**Skills/Tools:** Python (statsmodels), R (forecast/vars), ARIMA, VAR, cointegration, Chow tests, impulse response functions, time-series diagnostics

## E-Commerce Conversion Optimization — A/B Testing + Power + Segmentation
- Designed and analyzed A/B tests over 50K+ users, including power analysis and covariate balance checks for statistical rigor.
- Measured 2.2% conversion lift (p < 0.05, 95% CI) and quantified heterogeneity (e.g., 3.5% lift on mobile).
- Built automated reporting that reduced repetitive manual analysis by 95% and packaged insights in stakeholder-ready dashboards.
**Skills/Tools:** Python (SciPy/stats), SQL, Tableau, A/B testing, power analysis, covariate balance, segmentation, confidence intervals, reporting automation

## Product Metrics & Analytics Framework — Funnels + Health Metrics
- Built a product analytics framework tracking 15+ health metrics across 10K+ users, including funnel views and onboarding breakdowns.
- Reduced time-to-insight 3 days → 10 minutes by standardizing metric definitions and building dashboards for repeat analysis.
- Identified onboarding drop-offs and guided roadmap decisions that drove +15% engagement after iteration.
**Skills/Tools:** SQL, Python, Tableau, funnel analysis, KPI design, dashboarding, metric definition, product analytics

## Randomized Controlled Trial Evaluation — LATE via 2SLS + Heterogeneity
- Analyzed a stratified RCT with 50K+ participants, including power calculations (MDE=1.5%) and compliance-aware estimation.
- Estimated causal impacts using LATE via 2SLS with clustered standard errors for robustness.
- Quantified heterogeneity using causal forests (e.g., 3.5% mobile vs 1.1% desktop) and delivered reproducible, policy-ready results.
**Skills/Tools:** Python (statsmodels), R (estimatr/randomizr), causal inference, 2SLS, LATE, clustered SE, power analysis, causal forests, experimental design

## Minimum Wage Employment Effects — Modern DID + Event Study
- Evaluated policy impact using Callaway–Sant'Anna DID to address pitfalls of TWFE under staggered adoption.
- Validated assumptions using event study pre-trend checks and communicated time dynamics clearly.
- Reported heterogeneous effects (e.g., -2.1% food service) and produced a structured 15-page policy brief with defensible methodology.
**Skills/Tools:** R (did, fixest), Stata, difference-in-differences, Callaway–Sant'Anna, event study, BLS microdata, policy writing, causal diagnostics

## AI Trend Radar — Trend Detection + Evidence-Backed Summarization
- Built a multi-source trend intelligence pipeline that surfaces emerging topics using time-window velocity/momentum scoring and novelty/persistence signals.
- Reduced noise via deduplication and semantic clustering so repeated reposts don't inflate trend strength; grouped scattered mentions into coherent trend clusters.
- Added an LLM layer to generate concise, evidence-backed trend summaries (key entities, sentiment direction, why it's trending) with drill-down examples for verification.
**Skills/Tools:** Python, embeddings, semantic clustering, deduplication, trend scoring, LLM summarization, entity extraction, sentiment signals, PostgreSQL, Redis, Docker, dashboarding (React/Next.js)

## Kubernetes Observability Platform — Metrics, Logs, Traces
- Built scalable observability infrastructure for Kubernetes clusters using Prometheus metrics collection, Grafana dashboards, and OpenTelemetry distributed tracing deployed via Helm charts.
- Implemented custom K8s operators in Go for automated monitoring configuration, developed infrastructure-as-code with Terraform, and created alerting rules maintaining sub-500ms latency.
**Skills/Tools:** Kubernetes, Prometheus, Grafana, OpenTelemetry, Helm, Go, Terraform, custom operators, distributed tracing, alerting

## High-Performance Storage Infrastructure — Distributed Storage at Scale
- Deployed distributed storage system using Ceph and MinIO on Kubernetes, achieving high-throughput data access patterns and optimizing performance for concurrent workloads.
- Automated storage provisioning with Terraform and Python operators, implemented monitoring via Prometheus/Grafana, and optimized Redis caching for improved read performance.
**Skills/Tools:** Ceph, MinIO, Kubernetes, Terraform, Python, Prometheus, Grafana, Redis, distributed storage, performance optimization

## Cloud-Native Production Platform — AWS + K8s Infrastructure
- Architected production infrastructure on AWS using Kubernetes with auto-scaling, deploying via Terraform IaC, processing 500+ QPS with 80ms p95 latency.
- Built comprehensive observability using Prometheus, Grafana, and distributed tracing for monitoring system health, debugging production issues, and tracking performance with automated alerting.
**Skills/Tools:** AWS, Kubernetes, Docker, Terraform, Prometheus, Grafana, Jaeger, auto-scaling, load balancing, production infrastructure

## Infrastructure Automation Framework — DevOps Tools & Pipelines
- Developed infrastructure automation tools in Python and Go for Kubernetes deployment orchestration, processing 100K+ operations with optimized throughput via parallelization.
- Implemented GitOps workflows with Terraform and Helm, built monitoring dashboards, and created clean production-grade code for operational excellence and reliability.
**Skills/Tools:** Python, Go, Terraform, Ansible, Helm, Git, GitOps, Kubernetes, automation, CI/CD

## Real-Time Control System — Embedded + High-Rate Data Processing
- Developed real-time control algorithms and data acquisition systems processing high-rate sensor data, implementing efficient data structures and concurrent processing to maintain deterministic timing constraints.
- Built automated deployment pipelines and monitoring infrastructure, implementing comprehensive testing frameworks and debugging tools to ensure system reliability and performance under production workloads.
**Skills/Tools:** C++, Python, embedded systems, real-time systems, Linux, RTOS, control algorithms, data acquisition, concurrency

## Geometry Processing Pipeline — 3D Mesh Processing + Optimization
- Architected geometry processing pipeline converting complex 3D models into optimized machine instructions, implementing efficient algorithms for mesh processing, path planning, and collision detection with sub-millisecond latency.
- Optimized computational performance through C++ template metaprogramming, SIMD instructions, and parallel processing, achieving high-throughput geometry conversion while maintaining numerical precision and robustness.
**Skills/Tools:** C++, Python, computational geometry, mesh processing, SIMD, parallel computing, optimization, numerical algorithms

## Distributed Data Acquisition System — High-Rate Streaming + Storage
- Built high-rate data acquisition and storage system handling streaming sensor data at scale, implementing lock-free concurrent data structures and zero-copy networking for minimal latency overhead.
- Developed production-grade C++ system with comprehensive error handling, automated testing, and monitoring, optimizing throughput via profiling-driven performance tuning and efficient resource management.
**Skills/Tools:** C++, Python, Linux, concurrent data structures, lock-free programming, zero-copy networking, real-time systems, performance optimization

## Marketing Attribution & Response Modeling — Multi-Touch Attribution
- Built multi-touch attribution models analyzing 1M+ customer journeys using machine learning and causal inference, quantifying channel contribution to conversions and optimizing marketing spend.
- Developed market response models using Python on Spark, integrated third-party data sources, and designed experiments measuring advertising effectiveness across channels with statistical rigor.
**Skills/Tools:** Python, SQL, Spark, causal inference, attribution modeling, machine learning, A/B testing, marketing analytics

## Dynamic Pricing Algorithm Optimization — Revenue Maximization
- Designed dynamic pricing algorithms incorporating marketplace dynamics, demand elasticity, and competitive positioning using machine learning on 284K transactions, maximizing revenue and conversion rates.
- Built experimental frameworks testing pricing strategies via A/B testing, analyzed statistical significance, and connected technical insights to strategic pricing decisions increasing efficiency 12%.
**Skills/Tools:** Python, XGBoost, SQL, optimization, pricing algorithms, A/B testing, demand modeling, revenue optimization

---