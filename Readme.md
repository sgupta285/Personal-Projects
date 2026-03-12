# Srijan Gupta | Project Portfolio

<p align="center">
  <strong>AI Systems • Backend Engineering • Distributed Infrastructure • Quantitative Finance • Data Science • Econometrics</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Projects-29-111827?style=for-the-badge" alt="29 projects" />
  <img src="https://img.shields.io/badge/Focus-AI%20%7C%20Backend%20%7C%20Infra%20%7C%20Quant-2563eb?style=for-the-badge" alt="focus areas" />
  <img src="https://img.shields.io/badge/Build%20Style-Production%20Minded-059669?style=for-the-badge" alt="production minded" />
  <img src="https://img.shields.io/badge/Stack-Python%20%7C%20C%2B%2B%20%7C%20React%20%7C%20K8s-f59e0b?style=for-the-badge" alt="stack" />
</p>

---

## Overview

This repository is a curated portfolio of projects spanning **AI systems, machine learning, backend engineering, distributed systems, cloud infrastructure, quantitative finance, forecasting, experimentation, and applied econometrics**.

The goal of this README is not just to list projects. It is to show how I think about building systems end to end: from **modeling and experimentation** to **latency, observability, deployment, scalability, reliability, and product impact**.

Across these builds, I focus on systems that are not only technically correct, but also **usable in real environments**.

## At a Glance

- **Core themes:** AI/LLM systems, MLOps, backend platforms, real-time systems, cloud-native infrastructure, quantitative research, analytics, experimentation, and forecasting
- **Representative tools:** Python, C++, FastAPI, React, Kotlin, Kubernetes, Docker, PostgreSQL, Redis, AWS, Terraform, MLflow, Spark, Tableau, Prometheus, Grafana
- **Build philosophy:** measurable impact, reproducibility, scalability, observability, and production-minded engineering

## Repository Navigation

- [Featured Projects](#featured-projects)
- [Project Categories](#project-categories)
- [Detailed Project Summaries](#detailed-project-summaries)
  - [AI, ML, and LLM Systems](#ai-ml-and-llm-systems)
  - [Backend, Full-Stack, Mobile, and Product Engineering](#backend-full-stack-mobile-and-product-engineering)
  - [Quantitative Finance and Trading Systems](#quantitative-finance-and-trading-systems)
  - [Data Science, Econometrics, and Forecasting](#data-science-econometrics-and-forecasting)
  - [Cloud, Infrastructure, and Systems Engineering](#cloud-infrastructure-and-systems-engineering)
- [Skills Represented Across This Repo](#skills-represented-across-this-repo)

## Featured Projects

| Project | What it showcases | Core stack |
|---|---|---|
| **ClearClause** | Production-minded legal RAG, hybrid retrieval, reranking, low-latency inference, observability | `Python` `FastAPI` `pgvector` `Redis` `Kubernetes` |
| **Ads Integrity & Content Moderation Platform** | Event-driven moderation, risk scoring, fraud detection, dashboarding | `Python` `Kafka` `Redis` `PostgreSQL` `React` |
| **LLM Evaluation & Inference Stack** | Benchmarking, vLLM serving, async inference, reproducible evaluation | `Python` `vLLM` `FastAPI` `MLflow` |
| **BuckyConnect** | Real-time product engineering, GraphQL, WebSockets, AWS deployment | `React` `TypeScript` `GraphQL` `Redis` `AWS` |
| **Algorithmic Trading Strategy Backtest** | Research-grade simulation, walk-forward validation, high-performance compute | `C++` `Python` `PostgreSQL` `OpenMP` |
| **ConnecTech** | B2B marketplace product, Android app architecture, auth flows, matchmaking UX | `Kotlin` `XML` `MVVM` `Retrofit` |

## Project Categories

### AI, ML, and LLM Systems

- [ClearClause - Production Legal RAG System](#clearclause---production-legal-rag-system)
- [Spotify Music Popularity Pipeline](#spotify-music-popularity-pipeline)
- [LLM Evaluation & Inference Stack](#llm-evaluation--inference-stack)
- [Ads Integrity & Content Moderation Platform](#ads-integrity--content-moderation-platform)
- [Real-Time Fraud Detection API](#real-time-fraud-detection-api)
- [AI Trend Radar](#ai-trend-radar)
- [Customer Churn Prediction & Intervention](#customer-churn-prediction--intervention)

### Backend, Full-Stack, Mobile, and Product Engineering

- [BuckyConnect - Real-Time Collaboration Platform](#buckyconnect---real-time-collaboration-platform)
- [ConnecTech - B2B Tech Matchmaking Platform](#connectech---b2b-tech-matchmaking-platform)
- [E-Commerce Backend System](#e-commerce-backend-system)
- [Product Metrics & Analytics Framework](#product-metrics--analytics-framework)
- [E-Commerce Conversion Optimization](#e-commerce-conversion-optimization)

### Quantitative Finance and Trading Systems

- [Algorithmic Trading Strategy Backtest](#algorithmic-trading-strategy-backtest)
- [Options Pricing & Greeks Engine](#options-pricing--greeks-engine)
- [Statistical Arbitrage Pairs Trading](#statistical-arbitrage-pairs-trading)
- [Dynamic Pricing Algorithm Optimization](#dynamic-pricing-algorithm-optimization)

### Data Science, Econometrics, and Forecasting

- [Healthcare Spending vs Life Expectancy](#healthcare-spending-vs-life-expectancy)
- [Retail Demand Forecasting System](#retail-demand-forecasting-system)
- [Retail Demand Elasticity Analysis](#retail-demand-elasticity-analysis)
- [Randomized Controlled Trial Evaluation](#randomized-controlled-trial-evaluation)
- [Minimum Wage Employment Effects](#minimum-wage-employment-effects)
- [Marketing Attribution & Response Modeling](#marketing-attribution--response-modeling)

### Cloud, Infrastructure, and Systems Engineering

- [Kubernetes Observability Platform](#kubernetes-observability-platform)
- [High-Performance Storage Infrastructure](#high-performance-storage-infrastructure)
- [Cloud-Native Production Platform](#cloud-native-production-platform)
- [Infrastructure Automation Framework](#infrastructure-automation-framework)
- [Real-Time Control System](#real-time-control-system)
- [Geometry Processing Pipeline](#geometry-processing-pipeline)
- [Distributed Data Acquisition System](#distributed-data-acquisition-system)

---

# Detailed Project Summaries

## AI, ML, and LLM Systems

### ClearClause - Production Legal RAG System

**Overview**  
Built a production-grade legal retrieval and grounded Q&A platform for contracts using hybrid search, semantic retrieval, lexical retrieval, and reranking for high-precision passage selection.

**Key results**
- Achieved **0.87 precision@10** and reduced **p95 latency by 93%** from **4.3s to 300ms** using Redis semantic caching and response streaming.
- Deployed on Kubernetes with HPA supporting **200+ QPS**, plus PII redaction, structured validation, and observability guardrails.

**Focus areas**  
`RAG` `Hybrid Search` `BM25` `Embeddings` `Reranking` `Caching` `Streaming` `Observability` `PII Redaction` `Scalability`

**Tech stack**  
`Python` `FastAPI` `pgvector` `Redis` `BM25` `Docker` `Kubernetes` `Prometheus` `Grafana` `OpenTelemetry`

### Spotify Music Popularity Pipeline

**Overview**  
Built a reproducible ML pipeline to predict track popularity using tuned ensemble models with Optuna-based hyperparameter optimization and production-minded inference workflows.

**Key results**
- Improved accuracy by **45%** and achieved **MAE ~10.0** on a 0 to 100 target, processing **1M+ records** end to end.
- Deployed inference on AWS Lambda with MLflow model versioning and a Redis-backed feature store, reducing latency by roughly **30%**.

**Focus areas**  
`Supervised Learning` `Feature Engineering` `Hyperparameter Tuning` `Model Registry` `Serverless Inference` `MLOps` `Pipeline Automation`

**Tech stack**  
`Python` `XGBoost` `LightGBM` `scikit-learn` `Optuna` `MLflow` `AWS Lambda` `Redis` `Docker`

### LLM Evaluation & Inference Stack

**Overview**  
Built a scalable evaluation and serving stack for transformer-based LLMs, benchmarking latency, throughput, retrieval quality, and answer relevance across checkpoints, prompts, and serving configurations.

**Key results**
- Optimized serving with vLLM, async FastAPI endpoints, and dynamic batching for rapid side-by-side experiments.
- Integrated MLflow for reproducible tracking of prompts, checkpoints, decoding settings, metrics, and artifacts across runs.

**Focus areas**  
`LLM Serving` `Benchmarking` `Experiment Tracking` `Dynamic Batching` `Async APIs` `Evaluation` `Reproducibility` `Inference Optimization`

**Tech stack**  
`Python` `Transformers` `vLLM` `FastAPI` `MLflow` `Docker` `Structured Logging`

### Ads Integrity & Content Moderation Platform

**Overview**  
Built an ads integrity platform that screens creatives and metadata before serving using event-driven moderation services, policy-aware review workflows, and real-time risk scoring.

**Key results**
- Combined a lightweight ML classifier with a rules engine to detect spam, scams, misleading content, and policy violations.
- Added Kafka-based event streaming, Redis risk caching, Postgres-backed metadata, and a React analytics dashboard for fraud trends and moderation insights.

**Focus areas**  
`Fraud Detection` `Content Moderation` `Risk Scoring` `Event-Driven Systems` `Policy Enforcement` `Analytics Dashboards` `Review Workflows`

**Tech stack**  
`Python` `FastAPI` `Kafka` `Redis` `PostgreSQL` `scikit-learn` `React` `Docker` `AWS` `GCP`

### Real-Time Fraud Detection API

**Overview**  
Built a production-style fraud scoring API using FastAPI, Redis caching, Kubernetes autoscaling, and reliability patterns such as circuit breakers and drift-aware retraining triggers.

**Key results**
- Trained on **284K transactions** with imbalance handling via SMOTE and ensembles, achieving **96% precision** and **89% recall**.
- Sustained **500+ QPS** with roughly **80 to 100ms p95 latency**, backed by Prometheus, Grafana, Jaeger, and retraining workflows.

**Focus areas**  
`Real-Time Inference` `Fraud Scoring` `Model Drift` `Monitoring` `Autoscaling` `Reliability Engineering` `MLOps`

**Tech stack**  
`Python` `FastAPI` `XGBoost` `scikit-learn` `SMOTE` `Redis` `Kubernetes` `Prometheus` `Grafana` `Jaeger` `GitHub Actions`

### AI Trend Radar

**Overview**  
Built a multi-source trend intelligence pipeline that identifies emerging topics using time-window velocity, novelty, persistence, deduplication, clustering, and evidence-backed LLM summarization.

**Key results**
- Reduced noise with semantic clustering and deduplication so repeated reposts do not inflate trend strength.
- Added concise summary generation covering key entities, sentiment direction, supporting evidence, and verification-friendly drill-down views.

**Focus areas**  
`Trend Detection` `Semantic Clustering` `Deduplication` `Entity Extraction` `LLM Summarization` `Signal Ranking` `Dashboarding`

**Tech stack**  
`Python` `Embeddings` `PostgreSQL` `Redis` `Docker` `React` `Next.js`

### Customer Churn Prediction & Intervention

**Overview**  
Built churn prediction workflows across **500K+ customers** using XGBoost and scikit-learn, combining predictive modeling with operational intervention design.

**Key results**
- Achieved **87% precision** and **82% recall**, with SHAP-based explainability to identify key drivers and prioritize actions.
- Reduced churn from **12% to 7%** and cut time-to-intervention from **14 days to 2 days** through workflow redesign.

**Focus areas**  
`Classification` `Explainable AI` `Retention Analytics` `Survival Analysis` `Operational Analytics` `Intervention Design`

**Tech stack**  
`SQL` `PostgreSQL` `Python` `XGBoost` `scikit-learn` `SHAP` `Tableau` `Cox Models`

## Backend, Full-Stack, Mobile, and Product Engineering

### BuckyConnect - Real-Time Collaboration Platform

**Overview**  
Built a real-time collaboration platform using WebSockets for live updates and GraphQL for structured reads, with Redis Pub/Sub for cross-instance event fanout.

**Key results**
- Supported **280+ concurrent users**, sustained **1,000+ events/sec**, and maintained sub-500ms latency targets under load.
- Improved frontend UX using code splitting, lazy loading, and Web Workers, reducing bundle weight by **40%**.

**Focus areas**  
`Real-Time Systems` `WebSockets` `GraphQL` `Fanout` `Frontend Performance` `Cloud Deployment` `Autoscaling`

**Tech stack**  
`React` `Node.js` `TypeScript` `GraphQL` `Redis` `AWS ECS` `CloudFront` `DynamoDB`

### ConnecTech - B2B Tech Matchmaking Platform

**Overview**  
Built a B2B matchmaking platform designed to connect businesses needing technology solutions with pre-vetted service providers. The platform focuses on transparency, trust, secure communication, and efficient matching between client needs and provider capabilities.

**Key results**
- Designed user flows for business onboarding, authentication, provider discovery, matchmaking, and password recovery in an Android-first product.
- Structured the application around clean MVVM boundaries with repositories, LiveData-driven state management, Retrofit-based API integration, and encryption utilities for sensitive information handling.

**Key features**
- **For businesses:** search pre-vetted providers, communicate requirements, negotiate contracts, and manage secure interactions.
- **For providers:** access aligned client leads, improve visibility through ratings, and match with work suited to expertise and capacity.
- **Platform strengths:** trust-oriented marketplace design, support for app development, cybersecurity, cloud migration, and broad tech service categories.

**Architecture highlights**
- MVVM design with clear separation across **Model**, **ViewModel**, and **View** layers.
- Auth flows covering login, registration, and password reset.
- Matchmaking logic via repository-backed modules.
- Fragment-based navigation and responsive XML-driven UI.

**Focus areas**  
`Mobile Product Engineering` `Android` `Marketplace Design` `Authentication` `MVVM` `Repository Pattern` `State Management` `REST Integration` `Security`

**Tech stack**  
`Kotlin` `XML` `Android` `MVVM` `Retrofit` `LiveData` `View Binding` `FragmentManager` `Encryption Utilities` `Gradle`

### E-Commerce Backend System

**Overview**  
Built FastAPI REST services backed by PostgreSQL and optimized them with indexing, connection pooling, caching, and concurrency-aware performance tuning.

**Key results**
- Implemented Redis cache-aside and rate limiting for stable performance under concurrent traffic.
- Achieved roughly **35% latency reduction** and **60% database load reduction**, validated using Locust load tests simulating **1,000+ concurrent users**.

**Focus areas**  
`REST APIs` `Database Performance` `Caching` `Rate Limiting` `Load Testing` `Backend Scalability`

**Tech stack**  
`Python` `FastAPI` `PostgreSQL` `Redis` `Docker` `pytest` `Locust`

### Product Metrics & Analytics Framework

**Overview**  
Built a product analytics framework tracking **15+ health metrics** across **10K+ users**, with standardized KPI definitions, funnel analysis, and dashboard-driven product insights.

**Key results**
- Reduced time-to-insight from **3 days to 10 minutes** through reusable metric logic and repeatable dashboards.
- Identified onboarding drop-offs that informed roadmap improvements and drove **15% engagement growth**.

**Focus areas**  
`Product Analytics` `Funnels` `KPI Design` `Dashboarding` `Growth Analysis` `Decision Support`

**Tech stack**  
`SQL` `Python` `Tableau` `Dashboarding` `Product Metrics`

### E-Commerce Conversion Optimization

**Overview**  
Designed and analyzed statistically rigorous A/B tests over **50K+ users**, including power analysis, covariate balance checks, and segmentation workflows.

**Key results**
- Measured a **2.2% conversion lift** with statistical significance and identified stronger mobile effects at **3.5% lift**.
- Automated reporting that reduced repetitive manual analysis by **95%** while improving stakeholder readability.

**Focus areas**  
`Experimentation` `A/B Testing` `Power Analysis` `Segmentation` `Conversion Analytics` `Stakeholder Reporting`

**Tech stack**  
`Python` `SciPy` `SQL` `Tableau` `Statistics`

## Quantitative Finance and Trading Systems

### Algorithmic Trading Strategy Backtest

**Overview**  
Built a research-grade backtesting engine in C++ with Python analysis tooling and PostgreSQL storage for systematic momentum strategies.

**Key results**
- Applied walk-forward validation, slippage modeling, and volatility-adaptive sizing to improve realism and reduce overfitting risk.
- Achieved **18.2% annualized return**, **1.47 Sharpe**, and outperformed SPY by **820 bps**, while accelerating simulation throughput by **3x** on **100K+ simulations**.

**Focus areas**  
`Backtesting` `Execution Realism` `Walk-Forward Validation` `High-Performance Compute` `Systematic Trading` `Quant Research`

**Tech stack**  
`C++` `Python` `NumPy` `pandas` `PostgreSQL` `OpenMP` `SIMD`

### Options Pricing & Greeks Engine

**Overview**  
Implemented an options pricing and risk engine supporting Black-Scholes and Monte Carlo, with Greeks computed via finite differences and volatility calibration workflows.

**Key results**
- Calibrated implied volatility surfaces using Newton-Raphson for real-time risk analysis use cases.
- Achieved **99.8% pricing accuracy** vs Bloomberg benchmarks, Greeks error below **0.1%**, and sub-2-second runtime performance.

**Focus areas**  
`Derivatives Pricing` `Monte Carlo` `Greeks` `Calibration` `Numerical Methods` `Risk Analytics` `Performance Optimization`

**Tech stack**  
`C++` `Eigen` `Boost` `Python` `NumPy` `SciPy` `SIMD`

### Statistical Arbitrage Pairs Trading

**Overview**  
Built a pairs trading research and execution pipeline identifying **200+ equity pairs** via cointegration and trading mean reversion with dynamic hedge ratios.

**Key results**
- Used Kalman filtering to adapt hedge ratios to changing market regimes.
- Achieved a **65% win rate** and **2.1 profit factor**, with infrastructure processing **50K+ ticks/sec** and under-100ms signal-to-order latency.

**Focus areas**  
`Pairs Trading` `Cointegration` `Kalman Filters` `Low-Latency Systems` `Tick Data` `Quantitative Signals`

**Tech stack**  
`Python` `statsmodels` `R` `PostgreSQL` `TimescaleDB` `Redis`

### Dynamic Pricing Algorithm Optimization

**Overview**  
Designed dynamic pricing algorithms that incorporate demand elasticity, competition, and marketplace dynamics to improve revenue and conversion outcomes.

**Key results**
- Built experimentation frameworks for pricing strategy testing and connected statistical findings to strategic pricing decisions.
- Improved pricing efficiency by **12%** through better demand modeling and more disciplined pricing iteration.

**Focus areas**  
`Pricing Algorithms` `Revenue Optimization` `Elasticity Modeling` `Experimentation` `Marketplace Analytics`

**Tech stack**  
`Python` `XGBoost` `SQL` `Optimization` `A/B Testing`

## Data Science, Econometrics, and Forecasting

### Healthcare Spending vs Life Expectancy

**Overview**  
Built a reproducible data pipeline ingesting **150+ state-level indicators** from **2020 to 2023**, dramatically reducing manual cleaning time with automated validation and standardized joins.

**Key results**
- Fitted multivariate models with region fixed effects and robustness checks to quantify the relationship between spending and longevity.
- Published an interactive Tableau story with drill-downs by region, income, and mortality-linked categories.

**Focus areas**  
`ETL` `Fixed Effects` `Public Policy Analytics` `Data Storytelling` `Robustness Checks` `Visualization`

**Tech stack**  
`Python` `pandas` `statsmodels` `R` `fixest` `plm` `Tableau`

### Retail Demand Forecasting System

**Overview**  
Built demand forecasts for **50+ SKUs** using classical and ensemble models, incorporating external regressors such as holidays, promotions, and weather.

**Key results**
- Achieved **8.2% MAPE**, about **40% better than baseline**, through disciplined feature and model iteration.
- Delivered dashboards with uncertainty bands to support safety-stock planning and scenario analysis.

**Focus areas**  
`Forecasting` `Time Series` `External Regressors` `Scenario Planning` `Inventory Analytics`

**Tech stack**  
`Python` `Prophet` `ARIMA` `XGBoost` `R` `Tableau`

### Retail Demand Elasticity Analysis

**Overview**  
Modeled demand dynamics using ARIMA and VAR approaches, validated long-run relationships with cointegration diagnostics, and stress-tested stability using structural break analysis.

**Key results**
- Applied Chow tests to avoid fragile elasticity estimates under changing regimes.
- Used impulse response functions to run counterfactuals and explain shock propagation over time.

**Focus areas**  
`Econometrics` `Elasticity Modeling` `VAR` `Cointegration` `Structural Breaks` `Counterfactual Analysis`

**Tech stack**  
`Python` `statsmodels` `R` `forecast` `vars`

### Randomized Controlled Trial Evaluation

**Overview**  
Analyzed a stratified randomized controlled trial with **50K+ participants**, including power calculations, compliance-aware causal estimation, and heterogeneity analysis.

**Key results**
- Estimated LATE via 2SLS with clustered standard errors for robust causal inference.
- Quantified treatment effect heterogeneity using causal forests and produced policy-ready, reproducible outputs.

**Focus areas**  
`Causal Inference` `RCT Analysis` `LATE` `2SLS` `Power Analysis` `Heterogeneity` `Experimental Design`

**Tech stack**  
`Python` `statsmodels` `R` `estimatr` `randomizr`

### Minimum Wage Employment Effects

**Overview**  
Evaluated policy impact using Callaway-Sant'Anna DID to avoid common pitfalls in staggered adoption settings and better estimate dynamic treatment effects.

**Key results**
- Validated assumptions through event-study pre-trend checks and communicated time dynamics clearly.
- Reported heterogeneous employment effects and delivered a structured policy brief with defensible methodology.

**Focus areas**  
`Difference-in-Differences` `Event Study` `Policy Evaluation` `Causal Diagnostics` `Labor Economics`

**Tech stack**  
`R` `did` `fixest` `Stata` `BLS Microdata`

### Marketing Attribution & Response Modeling

**Overview**  
Built multi-touch attribution and market response models across **1M+ customer journeys**, quantifying channel contribution to conversions and supporting smarter budget allocation.

**Key results**
- Combined machine learning, experimentation, and causal inference to evaluate cross-channel effectiveness.
- Developed scalable analytics workflows on Spark for large-scale marketing data processing.

**Focus areas**  
`Marketing Analytics` `Attribution Modeling` `Response Modeling` `Causal Inference` `Large-Scale Analytics` `Spend Optimization`

**Tech stack**  
`Python` `SQL` `Spark` `Machine Learning` `A/B Testing`

## Cloud, Infrastructure, and Systems Engineering

### Kubernetes Observability Platform

**Overview**  
Built scalable observability infrastructure for Kubernetes clusters using metrics, logs, dashboards, and distributed tracing deployed through repeatable infrastructure workflows.

**Key results**
- Implemented custom Kubernetes operators in Go for automated monitoring configuration.
- Built alerting and dashboards for latency, health, and failure visibility in production-style environments.

**Focus areas**  
`Observability` `Metrics` `Logs` `Distributed Tracing` `Kubernetes` `Helm` `Alerting` `Platform Engineering`

**Tech stack**  
`Kubernetes` `Prometheus` `Grafana` `OpenTelemetry` `Helm` `Go` `Terraform`

### High-Performance Storage Infrastructure

**Overview**  
Deployed distributed storage infrastructure using Ceph and MinIO on Kubernetes for high-throughput, concurrent data access patterns.

**Key results**
- Automated storage provisioning and operational workflows using Terraform and Python-based automation.
- Added Prometheus and Grafana monitoring plus caching strategies to improve read performance and operational visibility.

**Focus areas**  
`Distributed Storage` `Kubernetes` `Provisioning` `Performance Tuning` `Caching` `Infrastructure Monitoring`

**Tech stack**  
`Ceph` `MinIO` `Kubernetes` `Terraform` `Python` `Prometheus` `Grafana` `Redis`

### Cloud-Native Production Platform

**Overview**  
Architected production infrastructure on AWS using Kubernetes, autoscaling, load balancing, and Terraform-based infrastructure as code.

**Key results**
- Designed systems capable of handling **500+ QPS** with **80ms p95 latency** targets.
- Added full observability with Prometheus, Grafana, and distributed tracing for debugging and reliability.

**Focus areas**  
`Cloud Infrastructure` `Production Systems` `Autoscaling` `Reliability` `Infrastructure as Code` `Monitoring`

**Tech stack**  
`AWS` `Kubernetes` `Docker` `Terraform` `Prometheus` `Grafana` `Jaeger`

### Infrastructure Automation Framework

**Overview**  
Developed infrastructure automation tooling in Python and Go for orchestrating Kubernetes deployments and operational workflows at scale.

**Key results**
- Implemented GitOps workflows with Terraform and Helm for repeatable, production-minded releases.
- Built dashboards and clean automation pipelines to support operational reliability and reduce manual overhead.

**Focus areas**  
`Automation` `GitOps` `Kubernetes` `CI/CD` `Infrastructure Tooling` `Operational Excellence`

**Tech stack**  
`Python` `Go` `Terraform` `Ansible` `Helm` `Git` `Kubernetes`

### Real-Time Control System

**Overview**  
Developed real-time control algorithms and data acquisition systems processing high-rate sensor data with deterministic timing and concurrent execution constraints.

**Key results**
- Implemented testing, deployment, and monitoring workflows to support reliability under sustained workloads.
- Focused on efficient data structures, concurrency, and debugging for performance-sensitive runtime environments.

**Focus areas**  
`Embedded Systems` `Real-Time Processing` `Concurrency` `Control Algorithms` `Sensor Systems` `Deterministic Performance`

**Tech stack**  
`C++` `Python` `Linux` `RTOS` `Embedded Systems`

### Geometry Processing Pipeline

**Overview**  
Architected a geometry processing pipeline that converts complex 3D models into optimized machine instructions using efficient mesh processing, path planning, and collision detection.

**Key results**
- Optimized performance through C++ metaprogramming, SIMD instructions, and parallelization.
- Maintained high throughput while preserving numerical precision and geometric robustness.

**Focus areas**  
`Computational Geometry` `Mesh Processing` `Path Planning` `Collision Detection` `Performance Optimization` `Parallel Computing`

**Tech stack**  
`C++` `Python` `SIMD` `Parallel Computing` `Numerical Algorithms`

### Distributed Data Acquisition System

**Overview**  
Built a high-rate data acquisition and storage system handling streaming sensor data at scale with lock-free structures and zero-copy networking.

**Key results**
- Developed a production-grade C++ system with profiling-driven tuning, strong error handling, and automated testing.
- Optimized throughput and latency using efficient resource management and concurrency-aware design.

**Focus areas**  
`Data Acquisition` `Streaming Systems` `Lock-Free Programming` `Zero-Copy Networking` `Performance Engineering` `Systems Programming`

**Tech stack**  
`C++` `Python` `Linux` `Concurrent Data Structures` `Real-Time Systems`

## Skills Represented Across This Repo

### Languages
`Python` `C++` `SQL` `TypeScript` `JavaScript` `Kotlin` `R` `Stata`

### AI and Machine Learning
`XGBoost` `LightGBM` `scikit-learn` `Transformers` `vLLM` `MLflow` `Embeddings` `RAG` `Reranking` `SHAP`

### Backend and Product Engineering
`FastAPI` `Node.js` `React` `GraphQL` `WebSockets` `REST APIs` `Redis` `PostgreSQL` `DynamoDB`

### Cloud and Infrastructure
`AWS` `Docker` `Kubernetes` `Terraform` `Helm` `Prometheus` `Grafana` `Jaeger` `OpenTelemetry` `GitHub Actions`

### Data, Analytics, and Econometrics
`Tableau` `Spark` `Fixed Effects` `DID` `2SLS` `Power Analysis` `Forecasting` `Time Series` `Causal Inference`

---

## Notes

Some projects in this repository are fully implemented codebases, while others are portfolio-quality builds, research systems, or engineering blueprints designed to demonstrate architecture, technical depth, and system design thinking.



