"""
EduGrowth AI - Inference, Diagnostic & Intervention Engine
Provides real-time scoring, explainability (identifying primary risk drivers),
and actionable pedagogical recommendations for academic advisors.
"""

import os
import json
import joblib
import pandas as pd
import numpy as np

from feature_engineering import (
    EduGrowthFeatureEngineer,
    FEATURE_COLUMNS,
    CATEGORICAL_COLUMNS
)

class EduGrowthPredictor:
    def __init__(self, model_dir: str = None):
        if model_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_dir = os.path.join(base_dir, 'models')
            
        self.risk_model = joblib.load(os.path.join(model_dir, 'risk_classifier.joblib'))
        self.gpa_model = joblib.load(os.path.join(model_dir, 'gpa_regressor.joblib'))
        self.engineer = EduGrowthFeatureEngineer()
        
        with open(os.path.join(model_dir, 'model_metadata.json'), 'r') as f:
            self.metadata = json.load(f)
            
        self.risk_labels = {
            0: "On Track (Low Risk)",
            1: "Moderate Attention Needed",
            2: "Critical (High Risk)"
        }
        
    def predict_single(self, student_dict: dict) -> dict:
        """
        Receives raw student dictionary and outputs full diagnostic profile.
        """
        df = pd.DataFrame([student_dict])
        df_eng = self.engineer.transform(df)
        
        X = df_eng[FEATURE_COLUMNS + CATEGORICAL_COLUMNS]
        
        # Risk Prediction
        risk_class = int(self.risk_model.predict(X)[0])
        risk_probs = self.risk_model.predict_proba(X)[0]
        
        # GPA Prediction
        pred_gpa = float(self.gpa_model.predict(X)[0])
        pred_gpa = np.clip(round(pred_gpa, 2), 0.0, 10.0)
        
        # Calculate Diagnostic Trajectory & Drivers
        prev_cgpa = float(student_dict.get('prev_cgpa', 7.0))
        attendance = float(student_dict.get('attendance_rate_pct', 80.0))
        assignment_rate = float(student_dict.get('assignment_completion_pct', 80.0))
        internal_score = float(student_dict.get('internal_assessment_score', 70.0))
        backlogs = int(student_dict.get('backlog_count', 0))
        lms_hours = float(student_dict.get('lms_weekly_hours', 10.0))
        
        gpa_diff = pred_gpa - prev_cgpa
        if gpa_diff > 0.3:
            trajectory = "Upward / Improving"
        elif gpa_diff < -0.3:
            trajectory = "Downward / Declining"
        else:
            trajectory = "Stable / Steady"
            
        # Plain-English Diagnostic Drivers & Next Steps
        drivers = []
        interventions = []
        
        if attendance < 65.0:
            drivers.append(f"Very low class attendance ({attendance:.1f}% — needs to be at least 75%)")
            interventions.append("Check why classes are being missed and set up a quick meeting with an advisor.")
        elif attendance < 75.0:
            drivers.append(f"Attendance is slightly below the 75% rule ({attendance:.1f}%)")
            interventions.append("Send a friendly attendance reminder so they stay above 75%.")
            
        if internal_score < 45.0:
            drivers.append(f"Low mid-term test marks ({internal_score:.1f} out of 100)")
            interventions.append("Join extra tutoring sessions and pair with a senior student mentor.")
        elif internal_score < 60.0:
            drivers.append(f"Test marks have room to grow ({internal_score:.1f} out of 100)")
            interventions.append("Attend teacher office hours to review tough topics before finals.")
            
        if backlogs > 0:
            drivers.append(f"{backlogs} pending subject(s) from earlier semesters still to clear")
            interventions.append("Make a simple weekly study schedule to clear pending subjects before final exams.")
            
        if assignment_rate < 60.0:
            drivers.append(f"Many assignments submitted late or missed (only {assignment_rate:.1f}% on time)")
            interventions.append("Use a weekly assignment checklist to finish homework before deadlines.")
            
        if lms_hours < 4.0:
            drivers.append(f"Very little online study time logged ({lms_hours:.1f} hours/week)")
            interventions.append("Add short 20-minute daily revision sessions on the learning portal.")
            
        if not drivers:
            drivers.append("Doing well across attendance, tests, and homework.")
            interventions.append("Keep up the great pace and explore extra projects or certifications.")
            
        # Practical Portfolio / Employability Score
        portfolio_score = float(df_eng['practical_portfolio_score'].iloc[0])
        
        return {
            'risk_level': risk_class,
            'risk_label': self.risk_labels[risk_class],
            'risk_probabilities': {
                'Low Risk': round(float(risk_probs[0]) * 100, 1),
                'Moderate Risk': round(float(risk_probs[1]) * 100, 1),
                'High Risk': round(float(risk_probs[2]) * 100, 1)
            },
            'predicted_end_term_gpa': pred_gpa,
            'gpa_trajectory': trajectory,
            'gpa_delta': round(gpa_diff, 2),
            'portfolio_score': round(portfolio_score, 1),
            'key_risk_drivers': drivers,
            'prescribed_interventions': interventions
        }
