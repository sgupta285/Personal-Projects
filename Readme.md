# Srijan Gupta - Project Portfolio

This repository is a curated portfolio of projects spanning AI systems, machine learning, distributed infrastructure, backend engineering, quantitative finance, data science, and econometrics. Instead of acting as a simple list, this README is designed to communicate the technical range, system thinking, and measurable impact behind each build.

Across these projects, I focus on building systems that are not only correct on paper, but useful in practice. That means thinking about latency, scalability, observability, deployment, experimentation, data quality, and product impact from the start.

## Repository Highlights

- **Core themes:** AI/LLM systems, MLOps, backend platforms, cloud-native infrastructure, quantitative research, analytics, experimentation, and forecasting
- **Representative tools:** Python, C++, FastAPI, React, Kubernetes, Docker, PostgreSQL, Redis, AWS, Terraform, MLflow, Spark, Tableau, and observability tooling

## Project Categories

### AI, ML, and LLM Systems

- [ClearClause - Production Legal RAG System (Hybrid Search + Reranking)](#clearclause---production-legal-rag-system-hybrid-search--reranking)
- [Spotify Music Popularity Pipeline - ML Training + Serverless Inference](#spotify-music-popularity-pipeline---ml-training--serverless-inference)
- [LLM Evaluation & Inference Stack - Benchmarking + High-Throughput Serving](#llm-evaluation--inference-stack---benchmarking--high-throughput-serving)
- [Ads Integrity & Content Moderation Platform - Fraud Detection + Policy Enforcement](#ads-integrity--content-moderation-platform---fraud-detection--policy-enforcement)
- [Real-Time Fraud Detection API - Low-Latency ML Inference + Drift Monitoring](#real-time-fraud-detection-api---low-latency-ml-inference--drift-monitoring)
- [AI Trend Radar - Trend Detection + Evidence-Backed Summarization](#ai-trend-radar---trend-detection--evidence-backed-summarization)
- [Customer Churn Prediction & Intervention - Explainable ML + Playbook](#customer-churn-prediction--intervention---explainable-ml--playbook)

### Backend, Full-Stack, and Product Engineering

- [BuckyConnect - Real-Time Collaboration Platform (WebSockets + GraphQL)](#buckyconnect---real-time-collaboration-platform-websockets--graphql)
- [E-Commerce Backend System - REST API Performance + Load Testing](#e-commerce-backend-system---rest-api-performance--load-testing)
- [Product Metrics & Analytics Framework - Funnels + Health Metrics](#product-metrics--analytics-framework---funnels--health-metrics)
- [E-Commerce Conversion Optimization - A/B Testing + Power + Segmentation](#e-commerce-conversion-optimization---ab-testing--power--segmentation)

### Quantitative Finance and Trading Systems

- [Algorithmic Trading Strategy Backtest - Momentum + Walk-Forward Validation](#algorithmic-trading-strategy-backtest---momentum--walk-forward-validation)
- [Options Pricing & Greeks Engine - Black-Scholes + Monte Carlo + Calibration](#options-pricing--greeks-engine---black-scholes--monte-carlo--calibration)
- [Statistical Arbitrage Pairs Trading - Cointegration + Kalman Filters](#statistical-arbitrage-pairs-trading---cointegration--kalman-filters)
- [Dynamic Pricing Algorithm Optimization - Revenue Maximization](#dynamic-pricing-algorithm-optimization---revenue-maximization)

### Data Science, Econometrics, and Forecasting

- [Healthcare Spending vs Life Expectancy - ETL + Fixed Effects + Tableau Story](#healthcare-spending-vs-life-expectancy---etl--fixed-effects--tableau-story)
- [Retail Demand Forecasting System - SKU Forecasts + External Regressors](#retail-demand-forecasting-system---sku-forecasts--external-regressors)
- [Retail Demand Elasticity Analysis - ARIMA/VAR + Structural Breaks](#retail-demand-elasticity-analysis---arimavar--structural-breaks)
- [Randomized Controlled Trial Evaluation - LATE via 2SLS + Heterogeneity](#randomized-controlled-trial-evaluation---late-via-2sls--heterogeneity)
- [Minimum Wage Employment Effects - Modern DID + Event Study](#minimum-wage-employment-effects---modern-did--event-study)
- [Marketing Attribution & Response Modeling - Multi-Touch Attribution](#marketing-attribution--response-modeling---multi-touch-attribution)

### Cloud, Infrastructure, and Systems Engineering

- [Kubernetes Observability Platform - Metrics, Logs, Traces](#kubernetes-observability-platform---metrics-logs-traces)
- [High-Performance Storage Infrastructure - Distributed Storage at Scale](#high-performance-storage-infrastructure---distributed-storage-at-scale)
- [Cloud-Native Production Platform - AWS + K8s Infrastructure](#cloud-native-production-platform---aws--k8s-infrastructure)
- [Infrastructure Automation Framework - DevOps Tools & Pipelines](#infrastructure-automation-framework---devops-tools--pipelines)
- [Real-Time Control System - Embedded + High-Rate Data Processing](#real-time-control-system---embedded--high-rate-data-processing)
- [Geometry Processing Pipeline - 3D Mesh Processing + Optimization](#geometry-processing-pipeline---3d-mesh-processing--optimization)
- [Distributed Data Acquisition System - High-Rate Streaming + Storage](#distributed-data-acquisition-system---high-rate-streaming--storage)

## Detailed Project Summaries

### AI, ML, and LLM Systems

#### ClearClause - Production Legal RAG System (Hybrid Search + Reranking)

**Overview**  
Built a production-grade legal retrieval + grounded Q&A system for contracts using hybrid search (semantic + lexical/BM25) with reranking for high-precision passage selection.

**Key results**
- Achieved 0.87 precision@10 and reduced p95 latency 93% (4.3s -> 300ms) using Redis semantic caching + response streaming.
- Deployed on Kubernetes with HPA (3–15 replicas) to support 200+ QPS, with observability and reliability guardrails (PII redaction, structured validation).

**Tech stack**  
Python, FastAPI, pgvector, Redis, BM25, embeddings, reranking, Docker, Kubernetes (HPA), OpenTelemetry/Prometheus/Grafana, PII redaction

#### Spotify Music Popularity Pipeline - ML Training + Serverless Inference

**Overview**  
Built a reproducible ML pipeline to predict track popularity using tuned ensemble models (XGBoost/LightGBM + stacking) with Optuna hyperparameter optimization (100+ trials).

**Key results**
- Improved accuracy by 45% and achieved MAE ~10.0 (0–100); processed 1M+ records end-to-end.
- Deployed inference on AWS Lambda with MLflow model versioning and a Redis-backed feature store; reduced latency ~30% via parallelization/provisioned concurrency.

**Tech stack**  
Python, XGBoost, LightGBM, scikit-learn, Optuna, MLflow, AWS Lambda, Redis, feature engineering, pipeline automation, Docker

#### LLM Evaluation & Inference Stack - Benchmarking + High-Throughput Serving

**Overview**  
Built a scalable evaluation + inference stack for transformer-based LLMs, benchmarking latency, throughput, retrieval quality, and answer relevance across prompts, checkpoints, and serving configurations.

**Key results**
- Optimized serving with vLLM, dynamic batching, and async FastAPI endpoints to support fast side-by-side experiments; added structured logging and traceable run metadata for safer debugging and deployment decisions.
- Integrated MLflow to track parameters, metrics, and artifacts across model iterations, making it easier to compare prompt changes, model checkpoints, decoding settings, and serving strategies reproducibly.

**Tech stack**  
Python, Hugging Face Transformers, vLLM, FastAPI, MLflow, async inference, dynamic batching, retrieval evaluation, answer relevance scoring, structured logging, Docker

#### Ads Integrity & Content Moderation Platform - Fraud Detection + Policy Enforcement

**Overview**  
Built an ads integrity platform that screens creatives and metadata before serving using event-driven moderation services, real-time scoring, and policy-aware review workflows.

**Key results**
- Combined a lightweight ML classifier with a rules engine to detect spam, scams, misleading content, and policy violations; routed high-risk ads to manual review while approved ads continued into the serving pipeline.
- Added Kafka-based event streaming, Redis risk caching, Postgres-backed advertiser/ad metadata, and a React analytics dashboard to surface fraud trends, moderation actions, and advertiser risk scores.

**Tech stack**  
Python, FastAPI, Kafka, Redis, PostgreSQL, scikit-learn, rule engines, content moderation, fraud detection, React, Docker, AWS/GCP

#### Real-Time Fraud Detection API - Low-Latency ML Inference + Drift Monitoring

**Overview**  
Built a production fraud scoring API using FastAPI + Redis caching, deployed on Kubernetes with autoscaling and circuit-breaker reliability patterns.

**Key results**
- Trained models on 284K transactions, handling class imbalance with SMOTE + ensembles; achieved 96% precision / 89% recall.
- Sustained 500+ QPS with ~80–100ms p95 latency, backed by Prometheus/Grafana monitoring, Jaeger tracing, and drift tracking + retraining triggers.

**Tech stack**  
Python, FastAPI, scikit-learn/XGBoost, SMOTE, Redis, Kubernetes, Prometheus, Grafana, Jaeger, CI/CD (GitHub Actions), Trivy, MLOps monitoring

#### AI Trend Radar - Trend Detection + Evidence-Backed Summarization

**Overview**  
Built a multi-source trend intelligence pipeline that surfaces emerging topics using time-window velocity/momentum scoring and novelty/persistence signals.

**Key results**
- Reduced noise via deduplication and semantic clustering so repeated reposts don't inflate trend strength; grouped scattered mentions into coherent trend clusters.
- Added an LLM layer to generate concise, evidence-backed trend summaries (key entities, sentiment direction, why it's trending) with drill-down examples for verification.

**Tech stack**  
Python, embeddings, semantic clustering, deduplication, trend scoring, LLM summarization, entity extraction, sentiment signals, PostgreSQL, Redis, Docker, dashboarding (React/Next.js)

#### Customer Churn Prediction & Intervention - Explainable ML + Playbook

**Overview**  
Built churn models across 500K+ customers using XGBoost/scikit-learn, achieving 87% precision / 82% recall.

**Key results**
- Added SHAP explainability to surface drivers and prioritize interventions; modeled time-to-churn using Cox proportional hazards in a consulting variant.
- Reduced churn 12% -> 7% and improved operational speed with workflows that cut time-to-intervention 14 days -> 2 days.

**Tech stack**  
SQL (PostgreSQL), Python, XGBoost, scikit-learn, SHAP, Tableau, survival analysis (Cox), intervention design, KPI monitoring

### Backend, Full-Stack, and Product Engineering

#### BuckyConnect - Real-Time Collaboration Platform (WebSockets + GraphQL)

**Overview**  
Built a real-time collaboration platform using WebSockets for live updates and GraphQL for structured reads, with Redis Pub/Sub for event fanout across instances.

**Key results**
- Supported 280+ concurrent users, sustained 1,000+ events/sec, and maintained <500ms latency targets under real-time load.
- Deployed cloud-native infrastructure on AWS ECS + CloudFront + DynamoDB with autoscaling; improved UX performance via code splitting, lazy loading, and Web Workers (40% bundle reduction).

**Tech stack**  
React, Node.js/TypeScript, WebSockets, GraphQL, Redis Pub/Sub, AWS ECS, CloudFront, DynamoDB, autoscaling, frontend performance optimization

#### E-Commerce Backend System - REST API Performance + Load Testing

**Overview**  
Built FastAPI REST services backed by PostgreSQL and improved read performance using indexing + connection pooling.

**Key results**
- Implemented Redis cache-aside and rate limiting for stable performance under concurrency.
- Achieved ~35% latency reduction and ~60% DB load reduction, validated via Locust load tests simulating 1,000+ concurrent users.

**Tech stack**  
Python, FastAPI, PostgreSQL, Redis, indexing, connection pooling, rate limiting, Docker, pytest, Locust, performance benchmarking

#### Product Metrics & Analytics Framework - Funnels + Health Metrics

**Overview**  
Built a product analytics framework tracking 15+ health metrics across 10K+ users, including funnel views and onboarding breakdowns.

**Key results**
- Reduced time-to-insight 3 days -> 10 minutes by standardizing metric definitions and building dashboards for repeat analysis.
- Identified onboarding drop-offs and guided roadmap decisions that drove +15% engagement after iteration.

**Tech stack**  
SQL, Python, Tableau, funnel analysis, KPI design, dashboarding, metric definition, product analytics

#### E-Commerce Conversion Optimization - A/B Testing + Power + Segmentation

**Overview**  
Designed and analyzed A/B tests over 50K+ users, including power analysis and covariate balance checks for statistical rigor.

**Key results**
- Measured 2.2% conversion lift (p < 0.05, 95% CI) and quantified heterogeneity (e.g., 3.5% lift on mobile).
- Built automated reporting that reduced repetitive manual analysis by 95% and packaged insights in stakeholder-ready dashboards.

**Tech stack**  
Python (SciPy/stats), SQL, Tableau, A/B testing, power analysis, covariate balance, segmentation, confidence intervals, reporting automation

### Quantitative Finance and Trading Systems

#### Algorithmic Trading Strategy Backtest - Momentum + Walk-Forward Validation

**Overview**  
Built a research-grade backtesting engine in C++ with Python analysis tooling and PostgreSQL storage for systematic momentum strategies.

**Key results**
- Applied walk-forward validation and execution realism (slippage + volatility-adaptive sizing) to reduce overfitting risk.
- Achieved 18.2% annualized return, 1.47 Sharpe, outperformed SPY by 820 bps; accelerated simulation throughput 3× (15s -> 5s) for 100K+ sims using OpenMP + SIMD.

**Tech stack**  
C++, Python (NumPy/pandas), PostgreSQL, walk-forward validation, backtesting, OpenMP, SIMD, time-series evaluation, quantitative research

#### Options Pricing & Greeks Engine - Black-Scholes + Monte Carlo + Calibration

**Overview**  
Implemented an options pricing and risk engine supporting Black-Scholes and Monte Carlo (10K paths), with Greeks via finite differences.

**Key results**
- Calibrated volatility surfaces using Newton–Raphson for real-time risk analysis workflows.
- Achieved 99.8% accuracy vs Bloomberg, Greeks <0.1% error, <2s runtimes; delivered 85% performance optimization using SIMD + variance reduction.

**Tech stack**  
C++, Eigen, Boost, Python (NumPy/SciPy), Monte Carlo simulation, finite differences, Newton–Raphson, volatility surface calibration, SIMD, variance reduction

#### Statistical Arbitrage Pairs Trading - Cointegration + Kalman Filters

**Overview**  
Built a pairs trading pipeline identifying 200+ equity pairs via Johansen cointegration and trading mean reversion with z-score signals.

**Key results**
- Used Kalman filtering to estimate dynamic hedge ratios under changing market regimes.
- Achieved 65% win rate and 2.1 profit factor; engineered a low-latency system processing 50K+ ticks/sec with <100ms signal-to-order latency and degradation alerts.

**Tech stack**  
Python (statsmodels), R, PostgreSQL/TimescaleDB, Redis, Johansen cointegration, Kalman filters, low-latency pipelines, monitoring/alerting

#### Dynamic Pricing Algorithm Optimization - Revenue Maximization

**Overview**  
Designed dynamic pricing algorithms incorporating marketplace dynamics, demand elasticity, and competitive positioning using machine learning on 284K transactions, maximizing revenue and conversion rates.

**Key results**
- Built experimental frameworks testing pricing strategies via A/B testing, analyzed statistical significance, and connected technical insights to strategic pricing decisions increasing efficiency 12%.

**Tech stack**  
Python, XGBoost, SQL, optimization, pricing algorithms, A/B testing, demand modeling, revenue optimization

### Data Science, Econometrics, and Forecasting

#### Healthcare Spending vs Life Expectancy - ETL + Fixed Effects + Tableau Story

**Overview**  
Built a reproducible pipeline ingesting 150+ state-level indicators (2020–2023), cutting data prep 2 days -> 2 hours via automated validation and standardized joins.

**Key results**
- Fitted multivariate models with region fixed effects and robustness checks; quantified interpretable relationships between per-capita spending and longevity outcomes.
- Published an interactive Tableau story with coefficient plots and drill-downs by region, income quintile, and mortality-linked categories for stakeholder-ready analysis.

**Tech stack**  
Python (pandas/statsmodels), R (fixest/plm/did variants), ETL automation, regression modeling, fixed effects, robustness checks, Tableau, data storytelling

#### Retail Demand Forecasting System - SKU Forecasts + External Regressors

**Overview**  
Built demand forecasts for 50+ SKUs using Prophet/ARIMA and ensemble methods, incorporating external drivers (holidays, promotions, weather).

**Key results**
- Achieved 8.2% MAPE (~40% better than baseline) through feature + model iteration and evaluation discipline.
- Delivered dashboards with forecast uncertainty bands to support safety-stock and scenario planning for decision-makers.

**Tech stack**  
Python (Prophet, ARIMA, XGBoost), R, time-series modeling, feature engineering, Tableau, uncertainty bands, scenario analysis

#### Retail Demand Elasticity Analysis - ARIMA/VAR + Structural Breaks

**Overview**  
Modeled demand dynamics using ARIMA + VAR and validated long-run relationships with cointegration diagnostics.

**Key results**
- Tested stability using Chow structural break tests to avoid fragile elasticity estimates under regime changes.
- Used impulse response functions to run counterfactual simulations and communicate how shocks propagate through demand over time.

**Tech stack**  
Python (statsmodels), R (forecast/vars), ARIMA, VAR, cointegration, Chow tests, impulse response functions, time-series diagnostics

#### Randomized Controlled Trial Evaluation - LATE via 2SLS + Heterogeneity

**Overview**  
Analyzed a stratified RCT with 50K+ participants, including power calculations (MDE=1.5%) and compliance-aware estimation.

**Key results**
- Estimated causal impacts using LATE via 2SLS with clustered standard errors for robustness.
- Quantified heterogeneity using causal forests (e.g., 3.5% mobile vs 1.1% desktop) and delivered reproducible, policy-ready results.

**Tech stack**  
Python (statsmodels), R (estimatr/randomizr), causal inference, 2SLS, LATE, clustered SE, power analysis, causal forests, experimental design

#### Minimum Wage Employment Effects - Modern DID + Event Study

**Overview**  
Evaluated policy impact using Callaway–Sant'Anna DID to address pitfalls of TWFE under staggered adoption.

**Key results**
- Validated assumptions using event study pre-trend checks and communicated time dynamics clearly.
- Reported heterogeneous effects (e.g., -2.1% food service) and produced a structured 15-page policy brief with defensible methodology.

**Tech stack**  
R (did, fixest), Stata, difference-in-differences, Callaway–Sant'Anna, event study, BLS microdata, policy writing, causal diagnostics

#### Marketing Attribution & Response Modeling - Multi-Touch Attribution

**Overview**  
Built multi-touch attribution models analyzing 1M+ customer journeys using machine learning and causal inference, quantifying channel contribution to conversions and optimizing marketing spend.

**Key results**
- Developed market response models using Python on Spark, integrated third-party data sources, and designed experiments measuring advertising effectiveness across channels with statistical rigor.

**Tech stack**  
Python, SQL, Spark, causal inference, attribution modeling, machine learning, A/B testing, marketing analytics

### Cloud, Infrastructure, and Systems Engineering

#### Kubernetes Observability Platform - Metrics, Logs, Traces

**Overview**  
Built scalable observability infrastructure for Kubernetes clusters using Prometheus metrics collection, Grafana dashboards, and OpenTelemetry distributed tracing deployed via Helm charts.

**Key results**
- Implemented custom K8s operators in Go for automated monitoring configuration, developed infrastructure-as-code with Terraform, and created alerting rules maintaining sub-500ms latency.

**Tech stack**  
Kubernetes, Prometheus, Grafana, OpenTelemetry, Helm, Go, Terraform, custom operators, distributed tracing, alerting

#### High-Performance Storage Infrastructure - Distributed Storage at Scale

**Overview**  
Deployed distributed storage system using Ceph and MinIO on Kubernetes, achieving high-throughput data access patterns and optimizing performance for concurrent workloads.

**Key results**
- Automated storage provisioning with Terraform and Python operators, implemented monitoring via Prometheus/Grafana, and optimized Redis caching for improved read performance.

**Tech stack**  
Ceph, MinIO, Kubernetes, Terraform, Python, Prometheus, Grafana, Redis, distributed storage, performance optimization

#### Cloud-Native Production Platform - AWS + K8s Infrastructure

**Overview**  
Architected production infrastructure on AWS using Kubernetes with auto-scaling, deploying via Terraform IaC, processing 500+ QPS with 80ms p95 latency.

**Key results**
- Built comprehensive observability using Prometheus, Grafana, and distributed tracing for monitoring system health, debugging production issues, and tracking performance with automated alerting.

**Tech stack**  
AWS, Kubernetes, Docker, Terraform, Prometheus, Grafana, Jaeger, auto-scaling, load balancing, production infrastructure

#### Infrastructure Automation Framework - DevOps Tools & Pipelines

**Overview**  
Developed infrastructure automation tools in Python and Go for Kubernetes deployment orchestration, processing 100K+ operations with optimized throughput via parallelization.

**Key results**
- Implemented GitOps workflows with Terraform and Helm, built monitoring dashboards, and created clean production-grade code for operational excellence and reliability.

**Tech stack**  
Python, Go, Terraform, Ansible, Helm, Git, GitOps, Kubernetes, automation, CI/CD

#### Real-Time Control System - Embedded + High-Rate Data Processing

**Overview**  
Developed real-time control algorithms and data acquisition systems processing high-rate sensor data, implementing efficient data structures and concurrent processing to maintain deterministic timing constraints.

**Key results**
- Built automated deployment pipelines and monitoring infrastructure, implementing comprehensive testing frameworks and debugging tools to ensure system reliability and performance under production workloads.

**Tech stack**  
C++, Python, embedded systems, real-time systems, Linux, RTOS, control algorithms, data acquisition, concurrency

#### Geometry Processing Pipeline - 3D Mesh Processing + Optimization

**Overview**  
Architected geometry processing pipeline converting complex 3D models into optimized machine instructions, implementing efficient algorithms for mesh processing, path planning, and collision detection with sub-millisecond latency.

**Key results**
- Optimized computational performance through C++ template metaprogramming, SIMD instructions, and parallel processing, achieving high-throughput geometry conversion while maintaining numerical precision and robustness.

**Tech stack**  
C++, Python, computational geometry, mesh processing, SIMD, parallel computing, optimization, numerical algorithms

#### Distributed Data Acquisition System - High-Rate Streaming + Storage

**Overview**  
Built high-rate data acquisition and storage system handling streaming sensor data at scale, implementing lock-free concurrent data structures and zero-copy networking for minimal latency overhead.

**Key results**
- Developed production-grade C++ system with comprehensive error handling, automated testing, and monitoring, optimizing throughput via profiling-driven performance tuning and efficient resource management.

**Tech stack**  
C++, Python, Linux, concurrent data structures, lock-free programming, zero-copy networking, real-time systems, performance optimization

