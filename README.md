# EduGrowth AI: Intelligent Student Success & Retention Monitoring System

> An institutional-grade machine learning platform for early academic risk detection, performance forecasting, and skill portfolio development in higher education.

---

## 🏛️ System Overview

Universities and educational institutions struggle with fragmented student records across learning management systems (LMS), examination databases, attendance trackers, and placement portals. 

**EduGrowth AI** unifies multi-dimensional student indicators—academic trajectory, real-time engagement, coursework completion, and practical portfolio achievements—into a continuous diagnostic and predictive pipeline. Rather than identifying student failure *post-mortem*, the system computes early-warning indicators weeks prior to mid-term and end-term examinations, enabling actionable, timely pedagogical interventions.

---

## 📐 Machine Learning Architecture & Statistical Formulation

EduGrowth AI incorporates a dual-engine ensemble architecture:

### 1. Multi-Class Academic Risk Classifier (`HistGradientBoostingClassifier`)
* **Objective**: Predicts student status into one of three risk tiers:
  * `0 - Low Risk (On Track)`: Consistent academic standing across attendance and assessments.
  * `1 - Moderate Risk (Watchlist)`: Borderline indicators requiring academic counseling or peer study sessions.
  * `2 - Critical Risk (Immediate Intervention)`: Severe distress characterized by attendance deficits, failing internal scores, and accumulated course backlogs.
* **Loss & Weighting**: Class-balanced weighting to address real-world class imbalance (protecting the minority high-risk cohort from false negatives).
* **Validation Performance**:
  * Accuracy: **94.2%**
  * Macro F1-Score: **0.931**
  * High-Risk Precision: **95.2%**

### 2. End-Term Performance & GPA Forecaster (`HistGradientBoostingRegressor`)
* **Objective**: Continuous regression estimation of expected final semester GPA ($0.0 - 10.0$ scale).
* **Validation Performance**:
  * $R^2$ Score: **0.909**
  * Mean Absolute Error (MAE): **0.287 GPA points**
  * Root Mean Squared Error (RMSE): **0.363**

### 3. Higher-Order Feature Engineering
* **Academic Momentum**: Differential between current internal evaluation and prior cumulative CGPA ($\Delta_{\text{momentum}}$).
* **Composite Engagement Index**: Weighted combination of verified lecture attendance, LMS digital session velocity, and homework submission punctuality.
* **Academic Vulnerability Index**: Compound penalty capturing attendance deficit below the 75% institutional threshold combined with active course backlogs.
* **Employability & Practical Portfolio Score**: Quantified readiness index integrating industry certifications, technical skill count, open-source repositories, and internship experience.

---

## 📂 Project Structure

```text
EduGrowth/
├── data/
│   ├── raw/
│   │   └── student_cohort_data.csv       # Multi-dimensional raw student cohort records (3,000+ entries)
│   └── processed/
│       └── processed_cohort.csv          # Feature-engineered dataset with computed momentum & risk indices
├── models/
│   ├── risk_classifier.joblib            # Serialized Gradient Boosting Risk Classifier
│   ├── gpa_regressor.joblib              # Serialized Gradient Boosting GPA Forecaster
│   └── model_metadata.json               # Performance metrics, permutation feature importances, and versioning
├── src/
│   ├── __init__.py
│   ├── data_generator.py                 # Realistic multi-semester cohort data generator
│   ├── feature_engineering.py            # Custom scikit-learn transformer for educational indicators
│   ├── train.py                          # Dual-model training, cross-validation, and metrics serialization
│   └── inference.py                      # Real-time inference, risk driver diagnostic, and intervention engine
├── app.py                                # Executive Institutional Streamlit Web Portal
├── requirements.txt                      # Production dependencies
└── README.md                             # Comprehensive technical documentation
```

---

## 📊 Required Data Categories for Production Deployment

To deploy EduGrowth AI in a live university setting, raw data should be collected across four core institutional modules:

1. **Academic Performance Records** (Registrar / Exam Cell):
   * Historical CGPA / SGPA per semester
   * Internal assessment marks (mid-terms, quizzes, laboratory exams)
   * Uncleared backlogs / course arrears
   * Registered credit load per semester

2. **Attendance & Attendance Punctuality** (Biometric / ERP):
   * Lecture attendance percentage per course and aggregate
   * Laboratory practical attendance percentage

3. **Digital Learning Engagement** (Canvas, Moodle, Blackboard):
   * Weekly platform hours logged
   * Punctuality rate of assignment submissions (% on-time vs late vs missing)
   * Course material interaction frequency

4. **Professional Growth & Portfolio Data** (Career Services / Placement Portal):
   * External certifications completed (Coursera, NPTEL, AWS, Google)
   * Verified technical competencies and skills
   * Capstone / research project counts
   * Open-source repository activity (GitHub commits / projects)
   * Industry internships completed

---

## 🚀 Quickstart & Running the Application

### 1. Prerequisites
Ensure Python 3.10+ is installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Generate Data and Train Models (Optional - Pre-trained models included)
```bash
python src/data_generator.py
python src/train.py
```

### 4. Launch the Institutional Web Portal
```bash
streamlit run app.py
```
The portal will launch locally at `http://localhost:8501`.
