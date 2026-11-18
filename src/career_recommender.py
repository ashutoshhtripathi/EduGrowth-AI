"""
EduGrowth AI - Career Pathways & Industry Readiness Engine
Translates academic credentials, skill counts, and portfolio indicators
into actionable career tracks, skill gap analysis, and industry recommendations.
"""

CAREER_TRACKS = [
    {
        "title": "Machine Learning & AI Systems Engineer",
        "departments": ["Data Science & AI", "Computer Science", "Information Tech"],
        "min_skills": 8,
        "min_projects": 4,
        "min_cgpa": 7.5,
        "key_skills": ["Python", "PyTorch / TensorFlow", "Data Pipelines", "MLOps", "Model Deployment"],
        "certifications": ["AWS Certified Machine Learning", "Google Cloud ML Engineer", "DeepLearning.AI Specialization"],
        "description": "Design and deploy scalable machine learning architectures and deep learning models into production environments."
    },
    {
        "title": "Full-Stack Software Engineer",
        "departments": ["Computer Science", "Information Tech", "Data Science & AI", "Electronics & Comm"],
        "min_skills": 7,
        "min_projects": 3,
        "min_cgpa": 6.8,
        "key_skills": ["TypeScript / React", "Node.js / FastAPI", "PostgreSQL", "Docker", "REST & GraphQL APIs"],
        "certifications": ["Meta Front-End / Back-End Developer", "AWS Certified Developer", "Docker Certified Associate"],
        "description": "Build high-throughput web applications, cloud microservices, and interactive responsive user experiences."
    },
    {
        "title": "Cloud Infrastructure & DevOps Architect",
        "departments": ["Information Tech", "Computer Science", "Electronics & Comm"],
        "min_skills": 6,
        "min_projects": 3,
        "min_cgpa": 7.0,
        "key_skills": ["Linux Systems", "Kubernetes", "Terraform", "CI/CD Pipelines", "AWS / Azure"],
        "certifications": ["AWS Solutions Architect Associate", "CKA (Certified Kubernetes Admin)", "HashiCorp Terraform Associate"],
        "description": "Architect resilient, high-availability multi-cloud infrastructure, automation pipelines, and site reliability systems."
    },
    {
        "title": "Data Analytics & Business Intelligence Lead",
        "departments": ["Data Science & AI", "Information Tech", "Computer Science", "Mechanical Eng"],
        "min_skills": 5,
        "min_projects": 2,
        "min_cgpa": 6.5,
        "key_skills": ["SQL Mastery", "Tableau / PowerBI", "Pandas & Statistical Analysis", "Executive Storytelling", "A/B Testing"],
        "certifications": ["Google Data Analytics Professional", "Tableau Certified Data Analyst", "Microsoft PowerBI Data Analyst"],
        "description": "Transform multi-dimensional business datasets into predictive KPIs, executive dashboards, and strategic growth drivers."
    },
    {
        "title": "Embedded Systems & IoT Hardware Engineer",
        "departments": ["Electronics & Comm", "Mechanical Eng", "Computer Science"],
        "min_skills": 5,
        "min_projects": 3,
        "min_cgpa": 6.8,
        "key_skills": ["C / C++", "Microcontrollers (ARM, ESP32)", "RTOS", "Circuit Design", "IoT Protocols (MQTT, BLE)"],
        "certifications": ["Arm Accredited Engineer", "Certified IPC Specialist", "Embedded Linux Development"],
        "description": "Develop low-latency firmware, sensory robotics, microcontroller hardware, and smart connected devices."
    }
]

def evaluate_career_readiness(student_dict: dict) -> dict:
    dept = student_dict.get('department', 'Computer Science')
    skills_cnt = int(student_dict.get('technical_skills_count', 5))
    proj_cnt = int(student_dict.get('projects_count', 2))
    cert_cnt = int(student_dict.get('certifications_count', 1))
    cgpa = float(student_dict.get('prev_cgpa', 7.0))
    github_score = float(student_dict.get('github_activity_score', 50.0))
    internship = int(student_dict.get('internship_completed', 0))
    
    ranked_tracks = []
    for track in CAREER_TRACKS:
        # Compatibility score
        dept_match = 1.0 if dept in track['departments'] else 0.6
        skill_ratio = min(1.2, skills_cnt / max(1, track['min_skills']))
        proj_ratio = min(1.2, proj_cnt / max(1, track['min_projects']))
        cgpa_ratio = min(1.1, cgpa / max(1.0, track['min_cgpa']))
        intern_boost = 1.1 if internship == 1 else 1.0
        
        score = (dept_match * 0.35 + skill_ratio * 0.30 + proj_ratio * 0.20 + cgpa_ratio * 0.15) * intern_boost * 80.0
        score = min(98.5, round(score, 1))
        
        ranked_tracks.append({
            "track": track,
            "match_score": score
        })
        
    ranked_tracks.sort(key=lambda x: x['match_score'], reverse=True)
    top_tracks = ranked_tracks[:3]
    
    # Identify gaps for #1 track
    primary = top_tracks[0]['track']
    gaps = []
    if skills_cnt < primary['min_skills']:
        gaps.append(f"Acquire {primary['min_skills'] - skills_cnt} more verified technical competencies in {', '.join(primary['key_skills'][:2])}.")
    if proj_cnt < primary['min_projects']:
        gaps.append(f"Build {primary['min_projects'] - proj_cnt} more end-to-end practical capstone projects to showcase in portfolio.")
    if github_score < 70.0:
        gaps.append("Elevate open-source GitHub commit velocity and repository documentation.")
    if cert_cnt < 2:
        gaps.append(f"Pursue an industry-standard credential such as **{primary['certifications'][0]}**.")
    if internship == 0:
        gaps.append("Apply for summer industry internship programs through the university placement cell.")
        
    if not gaps:
        gaps.append("Outstanding technical portfolio! Focus on mock interview technical rounds and system design.")
        
    return {
        "top_tracks": top_tracks,
        "primary_track": primary['title'],
        "gaps": gaps,
        "recommended_certifications": primary['certifications'],
        "recommended_skills": primary['key_skills']
    }
