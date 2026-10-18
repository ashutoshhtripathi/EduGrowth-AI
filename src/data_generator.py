"""
EduGrowth AI - Synthetic Multi-Dimensional Student Cohort Generator
Generates realistic institutional data capturing academic performance,
engagement metrics, skill portfolios, and risk ground truths.
"""

import numpy as np
import pandas as pd
import os

def generate_student_dataset(n_samples: int = 2500, random_state: int = 42) -> pd.DataFrame:
    np.random.seed(random_state)
    
    # Department distribution
    departments = ['Computer Science', 'Data Science & AI', 'Information Tech', 'Electrical Eng', 'Mechanical Eng']
    dept_weights = [0.35, 0.25, 0.15, 0.15, 0.10]
    
    # Generate Student IDs
    student_ids = [f"EDG-2026-{1000 + i}" for i in range(n_samples)]
    dept_choices = np.random.choice(departments, size=n_samples, p=dept_weights)
    semesters = np.random.choice([3, 4, 5, 6, 7, 8], size=n_samples, p=[0.2, 0.25, 0.2, 0.15, 0.1, 0.1])
    
    # Background prior academic capability (0 to 100%)
    prior_hs_pct = np.clip(np.random.normal(loc=76, scale=11, size=n_samples), 45, 99)
    
    # Historical CGPA (0 to 10 scale) - correlated with high school pct
    base_cgpa = (prior_hs_pct / 10.0) + np.random.normal(loc=-0.5, scale=0.8, size=n_samples)
    prev_cgpa = np.clip(base_cgpa, 3.5, 9.9)
    
    # Attendance Rate % (0 to 100%)
    # Some students disengage; bimodal distribution
    is_disengaged = np.random.binomial(1, 0.18, size=n_samples)
    att_engaged = np.random.normal(loc=84, scale=8, size=n_samples)
    att_disengaged = np.random.normal(loc=52, scale=12, size=n_samples)
    attendance_pct = np.where(is_disengaged == 1, att_disengaged, att_engaged)
    attendance_pct = np.clip(attendance_pct, 20.0, 100.0)
    
    # LMS Engagement: Weekly hours & Login frequency
    # Correlated with attendance and previous CGPA
    lms_weekly_hours = np.clip((attendance_pct / 10.0) * 1.5 + (prev_cgpa * 0.8) + np.random.normal(0, 3, size=n_samples), 0.5, 32.0)
    lms_logins_per_week = np.clip(lms_weekly_hours * 1.6 + np.random.normal(2, 4, size=n_samples), 1, 50).astype(int)
    
    # Assignment Completion Rate %
    assignment_rate = np.clip(attendance_pct * 0.7 + (lms_weekly_hours * 1.5) + np.random.normal(5, 7, size=n_samples), 15.0, 100.0)
    
    # Internal Assessment Score (Mid-term / Quizzes out of 100)
    internal_scores = np.clip((prev_cgpa * 6.5) + (attendance_pct * 0.3) + (assignment_rate * 0.15) + np.random.normal(0, 6, size=n_samples), 10.0, 99.0)
    
    # Backlog Count (Historical failed courses uncleared)
    # Higher chance if previous CGPA is low and attendance is low
    backlog_prob = np.clip((8.0 - prev_cgpa) * 0.15 + (75 - attendance_pct) * 0.01, 0.02, 0.85)
    backlogs = np.random.binomial(n=4, p=backlog_prob, size=n_samples)
    
    # Course Credit Load
    credit_load = np.random.choice([18, 20, 22, 24, 26], size=n_samples, p=[0.1, 0.25, 0.4, 0.2, 0.05])
    
    # Skill, Portfolio & Employability Data
    # Certifications count
    cert_base = (prev_cgpa / 2.5) + (lms_weekly_hours / 10.0) + np.random.normal(0, 1.2, size=n_samples)
    certifications = np.clip(np.round(cert_base), 0, 8).astype(int)
    
    # Technical Skills count
    skills_base = (semesters * 1.2) + (prev_cgpa * 0.8) + np.random.normal(0, 2, size=n_samples)
    technical_skills = np.clip(np.round(skills_base), 1, 16).astype(int)
    
    # Projects completed
    projects_base = (semesters * 0.8) + (certifications * 0.6) + np.random.normal(0, 1.1, size=n_samples)
    projects_count = np.clip(np.round(projects_base), 0, 12).astype(int)
    
    # GitHub / Portfolio Activity Score (0 to 100)
    github_score = np.clip((projects_count * 7.5) + (technical_skills * 2.2) + (lms_weekly_hours * 1.2) + np.random.normal(0, 10, size=n_samples), 0, 100)
    
    # Internship completed (0 or 1, more likely in senior semesters 6-8 and higher CGPA)
    internship_prob = np.clip((semesters - 3) * 0.12 + (prev_cgpa - 6.0) * 0.1, 0.02, 0.85)
    internship_done = np.random.binomial(1, p=internship_prob, size=n_samples)
    
    # Ground Truth Targets:
    # 1. Target End-Term GPA (0 to 10 scale)
    # Function of internal scores, attendance, past CGPA, assignment rate, backlogs
    pred_gpa = (
        0.35 * (internal_scores / 10.0) +
        0.35 * prev_cgpa +
        0.15 * (attendance_pct / 10.0) +
        0.10 * (assignment_rate / 10.0) -
        0.25 * backlogs +
        np.random.normal(0, 0.35, size=n_samples)
    )
    target_end_term_gpa = np.clip(np.round(pred_gpa, 2), 2.0, 9.95)
    
    # 2. Risk Level Ground Truth:
    # 0 = Low Risk (On Track)
    # 1 = Moderate Risk (Borderline / Needs Intervention)
    # 2 = High Risk (Critical / At Risk of Failing or Suspension)
    risk_level = np.zeros(n_samples, dtype=int)
    
    # Criteria for Risk:
    # High Risk: Target GPA < 5.0 OR (Attendance < 65 and backlogs >= 2) OR (Internal Scores < 40)
    high_risk_mask = (target_end_term_gpa < 5.2) | ((attendance_pct < 65) & (backlogs >= 2)) | (internal_scores < 40)
    
    # Moderate Risk: Target GPA between 5.2 and 6.5 OR (Attendance between 65 and 75) OR backlogs == 1
    moderate_risk_mask = ((target_end_term_gpa >= 5.2) & (target_end_term_gpa < 6.6)) | ((attendance_pct >= 65) & (attendance_pct < 75)) | (backlogs == 1)
    moderate_risk_mask = moderate_risk_mask & (~high_risk_mask)
    
    risk_level[moderate_risk_mask] = 1
    risk_level[high_risk_mask] = 2
    
    # 3. Employability / Skill Readiness Index (0 to 100)
    employability_index = np.clip(
        (target_end_term_gpa * 3.5) +
        (certifications * 3.0) +
        (technical_skills * 2.0) +
        (projects_count * 2.5) +
        (github_score * 0.15) +
        (internship_done * 15.0) +
        np.random.normal(0, 4, size=n_samples),
        10.0,
        99.5
    )
    employability_index = np.round(employability_index, 1)

    df = pd.DataFrame({
        'student_id': student_ids,
        'department': dept_choices,
        'semester': semesters,
        'prior_hs_percentage': np.round(prior_hs_pct, 1),
        'prev_cgpa': np.round(prev_cgpa, 2),
        'attendance_rate_pct': np.round(attendance_pct, 1),
        'lms_weekly_hours': np.round(lms_weekly_hours, 1),
        'lms_logins_per_week': lms_logins_per_week,
        'assignment_completion_pct': np.round(assignment_rate, 1),
        'internal_assessment_score': np.round(internal_scores, 1),
        'backlog_count': backlogs,
        'credit_load': credit_load,
        'certifications_count': certifications,
        'technical_skills_count': technical_skills,
        'projects_count': projects_count,
        'github_activity_score': np.round(github_score, 1),
        'internship_completed': internship_done,
        'target_end_term_gpa': target_end_term_gpa,
        'academic_risk_level': risk_level, # 0: Low Risk, 1: Moderate Risk, 2: High Risk
        'employability_index': employability_index
    })
    
    return df

if __name__ == '__main__':
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
    os.makedirs(data_dir, exist_ok=True)
    df = generate_student_dataset(n_samples=3000)
    out_path = os.path.join(data_dir, 'student_cohort_data.csv')
    df.to_csv(out_path, index=False)
    print(f"Dataset generated successfully with {len(df)} student records at: {out_path}")
    print("Risk distribution:")
    print(df['academic_risk_level'].value_counts(normalize=True))
