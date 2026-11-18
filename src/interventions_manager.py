"""
EduGrowth AI - Pedagogical Intervention & Action Tracking Engine
Maintains institutional counseling, remedial tutoring, and advisory interventions.
"""

from datetime import datetime

DEFAULT_INTERVENTIONS = [
    {
        "id": "INT-2026-081",
        "student_id": "EDG-2026-1001",
        "student_name": "Rohan Verma",
        "department": "Mechanical Eng",
        "risk_tier": "Critical Risk",
        "intervention_type": "Attendance Mandate & Counseling",
        "priority": "Urgent",
        "assigned_to": "Prof. S. Nambiar",
        "status": "In Progress",
        "created_date": "2026-03-12",
        "notes": "Attendance dropped to 41.1%. Notice issued to student; parent counseling scheduled for Thursday."
    },
    {
        "id": "INT-2026-082",
        "student_id": "EDG-2026-1042",
        "student_name": "Aarav Patel",
        "department": "Computer Science",
        "risk_tier": "Moderate Risk",
        "intervention_type": "Peer Mentorship & Lab Support",
        "priority": "Medium",
        "assigned_to": "Prof. Arvind Sharma",
        "status": "Pending",
        "created_date": "2026-03-14",
        "notes": "Internal evaluation score requires 8-point recovery. Paired with senior mentor Divya Mehta."
    },
    {
        "id": "INT-2026-083",
        "student_id": "EDG-2026-1018",
        "student_name": "Kavya Iyer",
        "department": "Electronics & Comm",
        "risk_tier": "Critical Risk",
        "intervention_type": "Backlog Remedial Plan",
        "priority": "Urgent",
        "assigned_to": "Dr. Eleanor Vance",
        "status": "In Progress",
        "created_date": "2026-03-10",
        "notes": "2 uncleared course arrears from Semester 3. Extra weekend tutoring sessions assigned."
    },
    {
        "id": "INT-2026-084",
        "student_id": "EDG-2026-1055",
        "student_name": "Vikram Singh",
        "department": "Information Tech",
        "risk_tier": "Moderate Risk",
        "intervention_type": "Assignment Submission Advisory",
        "priority": "Low",
        "assigned_to": "Prof. M. Joshi",
        "status": "Resolved",
        "created_date": "2026-02-28",
        "notes": "Assignment completion rose from 58% to 88% following time-management coaching."
    }
]

def get_initial_interventions():
    return [item.copy() for item in DEFAULT_INTERVENTIONS]

def create_intervention(student_id, student_name, department, risk_tier, intervention_type, priority, assigned_to, notes):
    new_id = f"INT-2026-{datetime.now().strftime('%m%d%S')[-4:]}"
    return {
        "id": new_id,
        "student_id": student_id,
        "student_name": student_name,
        "department": department,
        "risk_tier": risk_tier,
        "intervention_type": intervention_type,
        "priority": priority,
        "assigned_to": assigned_to,
        "status": "Pending",
        "created_date": datetime.now().strftime("%Y-%m-%d"),
        "notes": notes
    }
