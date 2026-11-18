"""
EduGrowth AI - Goal Seek & Reverse Performance Optimizer (High-Performance Vectorized)
Computes the exact academic parameters (internals, attendance, study velocity)
required to achieve a student's desired target GPA in milliseconds.
"""

import numpy as np
import pandas as pd
from feature_engineering import FEATURE_COLUMNS, CATEGORICAL_COLUMNS

def optimize_gpa_target(student_dict: dict, target_gpa: float, predictor) -> dict:
    """
    Reverse-engineers the necessary academic improvements to reach target_gpa.
    Uses vectorized batch evaluation for instantaneous (<50ms) inference.
    """
    current_diag = predictor.predict_single(student_dict)
    current_pred_gpa = current_diag['predicted_end_term_gpa']
    
    cur_internal = float(student_dict.get('internal_assessment_score', 65.0))
    cur_attendance = float(student_dict.get('attendance_rate_pct', 75.0))
    cur_study = float(student_dict.get('lms_weekly_hours', 10.0))
    cur_assignment = float(student_dict.get('assignment_completion_pct', 80.0))
    
    if target_gpa <= current_pred_gpa:
        return {
            "feasible": True,
            "status": "Target Already Met",
            "message": f"Your current trajectory ({current_pred_gpa:.2f} GPA) already satisfies or exceeds your goal of {target_gpa:.2f}!",
            "required_internal": cur_internal,
            "required_attendance": max(75.0, cur_attendance),
            "required_study_hours": cur_study,
            "required_assignment": cur_assignment,
            "internal_delta": 0.0,
            "attendance_delta": 0.0,
            "study_delta": 0.0,
            "feasibility_score": 100,
            "projected_gpa": current_pred_gpa,
            "action_steps": [
                "Maintain your current attendance consistency above 75%.",
                "Keep submitting all continuous evaluation coursework on schedule.",
                "Dedicate regular revision hours ahead of the final examination period."
            ]
        }
        
    # Generate candidate grid
    internal_candidates = np.linspace(cur_internal, 98.0, 10)
    attendance_candidates = np.linspace(max(cur_attendance, 75.0), 98.0, 8)
    study_candidates = np.linspace(cur_study, min(32.0, cur_study + 14.0), 6)
    
    records = []
    grid_params = []
    
    for att in attendance_candidates:
        for study in study_candidates:
            for internal in internal_candidates:
                rec = student_dict.copy()
                rec['attendance_rate_pct'] = att
                rec['internal_assessment_score'] = internal
                rec['lms_weekly_hours'] = study
                rec['assignment_completion_pct'] = min(100.0, cur_assignment + (att - cur_attendance)*0.25)
                rec['lms_logins_per_week'] = int(study * 1.6)
                records.append(rec)
                grid_params.append((att, study, internal))
                
    batch_df = pd.DataFrame(records)
    batch_eng = predictor.engineer.transform(batch_df)
    X = batch_eng[FEATURE_COLUMNS + CATEGORICAL_COLUMNS]
    
    preds = predictor.gpa_model.predict(X)
    
    best_idx = None
    min_penalty = float('inf')
    
    for idx, gpa_val in enumerate(preds):
        if gpa_val >= target_gpa:
            att, study, internal = grid_params[idx]
            delta_int = internal - cur_internal
            delta_att = att - cur_attendance
            delta_study = study - cur_study
            penalty = delta_int * 1.0 + delta_att * 0.8 + delta_study * 1.4
            if penalty < min_penalty:
                min_penalty = penalty
                best_idx = idx
                
    if best_idx is not None:
        att, study, internal = grid_params[best_idx]
        sim_gpa = round(float(preds[best_idx]), 2)
        delta_int = round(float(internal - cur_internal), 1)
        delta_att = round(float(att - cur_attendance), 1)
        delta_study = round(float(study - cur_study), 1)
        
        gap = target_gpa - current_pred_gpa
        if gap <= 0.6:
            feasibility = 94
            status = "Highly Achievable"
        elif gap <= 1.3:
            feasibility = 80
            status = "Achievable with Dedication"
        elif gap <= 2.2:
            feasibility = 62
            status = "Challenging Stretch Goal"
        else:
            feasibility = 42
            status = "Long-Term Goal"
            
        steps = []
        if delta_att > 0:
            steps.append(f"Raise lecture attendance to **{att:.1f}%** (+{delta_att:.1f}% improvement).")
        else:
            steps.append(f"Keep attendance steady at **{att:.1f}%**.")
            
        if delta_int > 0:
            steps.append(f"Target at least **{internal:.1f}/100** on upcoming mid-terms and laboratory tests (+{delta_int:.1f} pts).")
            
        if delta_study > 0:
            steps.append(f"Increase weekly digital learning time to **{study:.1f} hrs/week** (+{delta_study:.1f} hrs).")
            
        steps.append("Maintain 100% homework submission punctuality.")
        
        return {
            "feasible": True,
            "status": status,
            "message": f"To advance from your current {current_pred_gpa:.2f} to a target of **{target_gpa:.2f} GPA**, follow this strategic plan:",
            "required_internal": round(float(internal), 1),
            "required_attendance": round(float(att), 1),
            "required_study_hours": round(float(study), 1),
            "required_assignment": min(100.0, cur_assignment + 15.0),
            "internal_delta": delta_int,
            "attendance_delta": delta_att,
            "study_delta": delta_study,
            "feasibility_score": feasibility,
            "projected_gpa": sim_gpa,
            "action_steps": steps
        }
    else:
        max_idx = int(np.argmax(preds))
        max_possible = round(float(preds[max_idx]), 2)
        att, study, internal = grid_params[max_idx]
        
        return {
            "feasible": False,
            "status": "Exceeds Single-Semester Horizon",
            "message": f"A target GPA of {target_gpa:.2f} exceeds the single-semester statistical projection ceiling ({max_possible:.2f}) from your historical baseline.",
            "required_internal": round(float(internal), 1),
            "required_attendance": round(float(att), 1),
            "required_study_hours": round(float(study), 1),
            "required_assignment": 100.0,
            "internal_delta": round(float(internal - cur_internal), 1),
            "attendance_delta": round(float(att - cur_attendance), 1),
            "study_delta": round(float(study - cur_study), 1),
            "feasibility_score": 30,
            "projected_gpa": max_possible,
            "action_steps": [
                f"Target an intermediate semester milestone GPA of **{max_possible:.2f}** first.",
                "Focus on eliminating course backlogs to raise baseline momentum.",
                "Compounding improvement across the next two semesters will achieve your ultimate target."
            ]
        }
