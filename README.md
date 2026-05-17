# 🚀 QuantumForge AI: Autonomous Legacy Migration Pipeline

## 📉 The $50 Billion Business Challenge

The global financial, governmental, and healthcare infrastructures run on legacy mainframes. Today, it costs enterprises an estimated **$50 Billion a year** just to service, maintain, and patch archaic COBOL programming code for standard service management updates. 

This presents an existential crisis for modern enterprises:
1. **The Talent Cliff:** The pool of COBOL developers is retiring, making maintenance impossibly expensive and dangerous.
2. **Cloud Immobility:** Mainframes cannot natively integrate with modern AI, cloud microservices, or scalable web infrastructure.
3. **MIPS Extortion:** Enterprises are paying millions annually in CPU cycle (MIPS) costs for tasks that could run for pennies on AWS or GCP.

## 🌟 The Solution

Welcome to the **QuantumForge AI Pipeline**, an enterprise-grade engine designed to autonomously translate monolithic legacy codebases into modern, secure, and cloud-native architectures. 

This is not a simple string-translator. It is an intelligent autonomous agent capable of self-healing, database modernization, and compliance auditing. By utilizing this software, enterprises can eliminate technical debt, slash infrastructure costs by over 75%, and rapidly transition to Python/SQLAlchemy cloud stacks.

---

## 📖 Key Capabilities

### 1. Massive Infrastructure Cost Reduction (ROI)
Instantly bypass the massive yearly COBOL service management costs. The pipeline analyzes legacy code and generates an **Executive ROI Dashboard** proving exactly how many MIPS are saved and projecting the massive Cloud ROI.

### 2. Autonomous Self-Healing 
Translating code is easy; proving it works is hard. QuantumForge generates modern Python code, writes a Pytest suite, and runs it in a local sandbox. **If tests fail, it captures the traceback logs and autonomously rewrites its own code until it achieves a passing build.**

### 3. Database & Architecture Modernization
Legacy mainframes rely on flat VSAM files or ancient DB2 SQL. The engine seamlessly refactors legacy `EXEC SQL` blocks into modern **SQLAlchemy ORM** configurations for PostgreSQL. Furthermore, it natively converts legacy IBM Mainframe JCL scripts into **Apache Airflow Python DAGs**.

### 4. Regulatory & Security Compliance
Strict financial regulations require traceability. The pipeline generates a Line-by-Line Audit Traceability Matrix mapping exact COBOL procedures to Python methods. During translation, it actively scans for legacy anti-patterns (like hardcoded passwords) and patches them to modern security standards.

---

## 🚀 Getting Started

### 1. Setup & Installation
1. Clone this repository.
2. Ensure you have Python 3.10+ installed.
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure your API Key:** Please read [API_SETUP.md](API_SETUP.md) for mandatory authentication instructions.

### 2. Launching the Interactive Studio
To visualize the translation process and access the ROI Dashboards, start the Vercel-inspired React UI server:
```bash
python -m uvicorn bot:app --reload
```
Navigate to `http://127.0.0.1:8000` in your web browser to view the real-time Migration Command Center.

### 3. Running a Headless Bulk Migration
To translate a legacy file via the CLI orchestrator:
```bash
python main.py --input sample_db2.cbl --output modern_app.py
```
