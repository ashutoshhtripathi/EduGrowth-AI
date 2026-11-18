"""
EduGrowth AI - Institutional Letter & Document Generator
Generates formal official university letters, warning notices, and commendations.
"""

from datetime import datetime

def generate_academic_letter(letter_type: str, student_info: dict, diag: dict, issuer_name: str = "Dr. Eleanor Vance", issuer_role: str = "Dean of Academic Affairs") -> str:
    """
    Produces formatted Markdown and printable institutional documents.
    """
    today_str = datetime.now().strftime("%B %d, %Y")
    ref_num = f"EDU-ACA/{datetime.now().strftime('%Y')}/{student_info.get('student_id', 'EDG-0000')[-4:]}"
    
    s_name = student_info.get('student_name', 'Student')
    s_id = student_info.get('student_id', 'N/A')
    s_dept = student_info.get('department', 'Engineering')
    s_sem = student_info.get('semester', 4)
    att = float(student_info.get('attendance_rate_pct', 80.0))
    internal = float(student_info.get('internal_assessment_score', 70.0))
    pred_gpa = float(diag.get('predicted_end_term_gpa', 7.5))
    backlogs = int(student_info.get('backlog_count', 0))
    
    if letter_type == "commendation":
        return f"""
# 🏛️ APEX INSTITUTE OF TECHNOLOGY & ADVANCED STUDIES
### Office of Academic Affairs & Undergraduate Excellence
**Institutional Reference:** `{ref_num}-COMM`  
**Date of Issuance:** {today_str}

---

### **DEAN'S COMMENDATION OF ACADEMIC EXCELLENCE**

**To:**  
**{s_name}**  
Student Identification: **{s_id}**  
Department: **Department of {s_dept}** (Semester {s_sem})  

Dear {s_name},

It gives the Academic Council and Faculty Senate profound pleasure to formally recognize your exceptional academic diligence, coursework mastery, and exemplary conduct during the ongoing academic semester.

#### **Certified Academic Performance:**
- **Forecasted Semester GPA:** **{pred_gpa:.2f} / 10.00**
- **Verified Classroom Attendance:** **{att:.1f}%**
- **Internal Assessment Benchmark:** **{internal:.1f} / 100**
- **Academic Standing:** **Dean's Honors List (Top Percentile)**

Your sustained intellectual commitment, active participation in practical engineering projects, and leadership in collaborative learning serve as a role model to your peers. The institution commends your perseverance and looks forward to your continued distinction.

Warmest congratulations on this noteworthy achievement.

---

**Sincerely and with Distinction,**  
🖋️ **{issuer_name}**  
*{issuer_role}*  
*Apex Institute of Technology*
"""

    elif letter_type == "warning":
        return f"""
# 🏛️ APEX INSTITUTE OF TECHNOLOGY & ADVANCED STUDIES
### Academic Retention & Coursework Monitoring Council
**Official Notice No:** `{ref_num}-WARN`  
**Date of Issuance:** {today_str}

---

### **FORMAL ACADEMIC EARLY-WARNING & ATTENDANCE DEFICIT NOTICE**

**Delivered To:**  
**{s_name}** (ID: **{s_id}**)  
Department of **{s_dept}**, Semester {s_sem}  

Dear {s_name},

This official correspondence serves as a formal notification from the Institutional Academic Advisory Board regarding your current academic trajectory. Automated diagnostic analysis indicates that your standing is presently at **Critical Risk** of end-semester debarment or academic probation.

#### **Key Diagnostic Discrepancies Recorded:**
- **Lecture Attendance:** **{att:.1f}%** (Institutional statutory minimum: **75.0%**)
- **Continuous Internal Evaluation:** **{internal:.1f} / 100**
- **Uncleared Course Backlogs:** **{backlogs} course(s)**
- **Forecasted End-Term GPA:** **{pred_gpa:.2f} / 10.00**

#### **Mandatory Corrective Directives:**
1. **Attendance Recovery:** You are required to maintain uninterrupted attendance in all scheduled lectures and laboratory practicals for the remainder of the term.
2. **Remedial Tutorials:** You must report to your designated departmental mentor within forty-eight (48) hours of receipt of this notice.
3. **Academic Advisory Session:** An in-person counseling session is mandated to establish a tailored remediation timetable.

Failure to address these deficiencies prior to final examination hall ticket verification may result in statutory disqualification as per Academic Ordinance Sec. 14(B).

---

**By Order of the Academic Council,**  
🖋️ **{issuer_name}**  
*{issuer_role}*  
*Apex Institute of Technology*
"""

    else: # Parent consultation invitation
        return f"""
# 🏛️ APEX INSTITUTE OF TECHNOLOGY & ADVANCED STUDIES
### Department of Student Welfare & Parent-Teacher Liaison
**Communication Ref:** `{ref_num}-PAR`  
**Date:** {today_str}

---

### **PARENT / GUARDIAN ACADEMIC CONSULTATION INVITATION**

**To the Parents / Guardians of {s_name}:**  
Student ID: **{s_id}** | Department: **{s_dept}** (Semester {s_sem})  

Respected Parent / Guardian,

At Apex Institute of Technology, we believe that academic triumph is achieved through a constructive, transparent partnership between faculty, students, and families.

We are writing to provide a transparent progress overview for **{s_name}** and cordially invite you for a virtual or in-person consultative dialogue:

#### **Current Mid-Term Indicators:**
- **Class Attendance Rate:** **{att:.1f}%** (Institutional threshold: 75.0%)
- **Internal Assessment Marks:** **{internal:.1f} / 100**
- **Pending Course Backlogs:** **{backlogs}**
- **Projected Semester Outcome:** **{pred_gpa:.2f} GPA**

Our departmental advisors have established dedicated academic support sessions to ensure your ward reaches their highest potential. We would appreciate the opportunity to discuss collaborative strategies at your earliest convenience.

Please reply to this notice or contact the Academic Support Desk at `academic.welfare@apexinstitute.edu`.

---

**Warm regards,**  
🖋️ **{issuer_name}**  
*{issuer_role}*  
*Apex Institute of Technology*
"""
