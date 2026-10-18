"""
EduGrowth AI - Feature Engineering & Transformation Pipeline
Computes statistical growth momentum, composite engagement indices,
vulnerability scores, and builds production-ready scikit-learn transformers.
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

class EduGrowthFeatureEngineer(BaseEstimator, TransformerMixin):
    """
    Custom transformer that derives higher-order educational indicators:
    - Academic Momentum (Rate of current internal progress vs historical CGPA)
    - Composite Learning Engagement Index
    - Portfolio & Employability Readiness Score
    - Academic Vulnerability Index
    """
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        df = X.copy()
        
        # 1. Academic Momentum (Current performance vs past benchmark)
        # Scaled on a 10-point basis
        current_est_gpa = df['internal_assessment_score'] / 10.0
        df['gpa_momentum'] = current_est_gpa - df['prev_cgpa']
        
        # 2. Composite Engagement Index (0 to 100)
        # Attendance: 40%, Assignment Rate: 35%, LMS study velocity: 25%
        lms_norm = np.clip(df['lms_weekly_hours'] / 25.0 * 100, 0, 100)
        df['composite_engagement_index'] = (
            0.40 * df['attendance_rate_pct'] +
            0.35 * df['assignment_completion_pct'] +
            0.25 * lms_norm
        )
        
        # 3. Academic Vulnerability Index (0 to 100, higher = higher distress)
        # Penalizes low attendance (<75%), backlogs, and poor assignment completion
        att_deficit = np.maximum(0, 75.0 - df['attendance_rate_pct'])
        df['vulnerability_index'] = np.clip(
            (att_deficit * 1.5) + (df['backlog_count'] * 18.0) + ((100.0 - df['assignment_completion_pct']) * 0.25),
            0, 100
        )
        
        # 4. Skill & Practical Readiness Index (0 to 100)
        # Combines certifications, projects, github activity, technical skills
        df['practical_portfolio_score'] = np.clip(
            (df['certifications_count'] * 7.0) +
            (df['projects_count'] * 6.0) +
            (df['technical_skills_count'] * 2.5) +
            (df['github_activity_score'] * 0.25) +
            (df['internship_completed'] * 20.0),
            0, 100
        )
        
        return df

FEATURE_COLUMNS = [
    'semester',
    'prior_hs_percentage',
    'prev_cgpa',
    'attendance_rate_pct',
    'lms_weekly_hours',
    'lms_logins_per_week',
    'assignment_completion_pct',
    'internal_assessment_score',
    'backlog_count',
    'credit_load',
    'certifications_count',
    'technical_skills_count',
    'projects_count',
    'github_activity_score',
    'internship_completed',
    'gpa_momentum',
    'composite_engagement_index',
    'vulnerability_index',
    'practical_portfolio_score'
]

CATEGORICAL_COLUMNS = ['department']
TARGET_RISK = 'academic_risk_level'
TARGET_GPA = 'target_end_term_gpa'
