"""
EduGrowth AI - Data Chatbot Assistant
Powered by Groq API using model openai/gpt-oss-120b.
Enables natural language querying of the institutional student dataset (3,000 students)
with dynamic pandas execution and statistical synthesis.
"""

import os
import json
import re
import urllib.request
import urllib.error
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DEFAULT_GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY",
    "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"
)
DEFAULT_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """You are the EduGrowth AI Data Analyst & Institutional Assistant, powered by openai/gpt-oss-120b.
You have direct access to the institutional student dataset via a pandas DataFrame named `df` (3,000 student records).

### Dataset Schema & Column Reference:
- `student_id` (str): Unique ID, e.g., 'EDG-2026-1042'
- `student_name` (str): Full student name (e.g. 'Aarav Patel')
- `department` (str): One of ['Computer Science', 'Information Tech', 'Data Science & AI', 'Electrical Eng', 'Mechanical Eng']
- `semester` (int): 1 through 8
- `prior_hs_percentage` (float): High-school mark percentage (0-100)
- `prev_cgpa` (float): Cumulative GPA up to prior term (0.0 to 10.0)
- `attendance_rate_pct` (float): Lecture attendance % (institutional requirement: >= 75%)
- `lms_weekly_hours` (float): Digital study hours logged per week on LMS
- `lms_logins_per_week` (int): Digital platform logins per week
- `assignment_completion_pct` (float): Punctual assignment completion %
- `internal_assessment_score` (float): Mid-term / internal score out of 100
- `backlog_count` (int): Active uncleared course arrears / failed subjects
- `credit_load` (int): Registered semester academic credits
- `certifications_count` (int): Number of industry certifications completed
- `technical_skills_count` (int): Verified technical skills count
- `projects_count` (int): Completed practical and capstone projects
- `github_activity_score` (float): Open-source & git repository activity score
- `internship_completed` (int): 1 if industry internship done, 0 otherwise
- `target_end_term_gpa` (float): Forecasted end-term GPA (0.0 to 10.0)
- `academic_risk_level` (int):
    0 = 'On Track (Low Risk)'
    1 = 'Moderate Risk (Watchlist)'
    2 = 'Critical Risk (Immediate Intervention)'
- `employability_index` (float): Industry readiness composite score (0-100)
- `gpa_momentum` (float): (internal_assessment_score / 10.0) - prev_cgpa
- `composite_engagement_index` (float): Attendance + LMS hours + assignment punctuality composite (0-100)
- `vulnerability_index` (float): Compound risk penalty for attendance < 75% combined with backlogs
- `practical_portfolio_score` (float): Quantified technical portfolio index (0-100)

### Guidelines:
1. When asked about counts, averages, specific students, departments, risk cohorts, or rankings, ALWAYS use the `query_dataset` function to compute the exact ground truth numbers from `df`.
2. Format answers with clean markdown (bold numbers, bullet points, concise tables where helpful).
3. If user specifies a name (e.g., 'Aarav Patel') or student ID (e.g., 'EDG-2026-1042'), filter `df` specifically for that student.
4. Provide context and actionable educational insights alongside raw numbers.
"""

TOOLS_SPEC = [
    {
        "type": "function",
        "function": {
            "name": "query_dataset",
            "description": "Execute a Python pandas code snippet on `df` to calculate exact values, aggregations, counts, or student records. Assign the final answer to the variable `result`.",
            "parameters": {
                "type": "object",
                "properties": {
                    "python_code": {
                        "type": "string",
                        "description": "Valid Python pandas code snippet operating on `df`. MUST set `result = ...` with the final answer."
                    }
                },
                "required": ["python_code"]
            }
        }
    }
]

class EduGrowthChatbot:
    def __init__(self, df: pd.DataFrame, api_key: str = None, model: str = None):
        self.df = df
        self.api_key = api_key or DEFAULT_GROQ_API_KEY
        self.model = model or DEFAULT_MODEL
        
    def _execute_code(self, code: str) -> str:
        """Safely executes the pandas query on df and returns stringified result."""
        # Sanitize code for security
        blocked = ["__import__", "os.", "sys.", "subprocess", "eval(", "exec(", "open(", "shutil"]
        for b in blocked:
            if b in code:
                return f"Execution blocked: query contains unauthorized term '{b}'"
                
        local_scope = {
            "df": self.df,
            "pd": pd,
            "np": np
        }
        
        try:
            exec(code, {}, local_scope)
            res = local_scope.get("result", None)
            if res is None:
                # Try evaluating the last line as an expression
                lines = code.strip().split("\n")
                last_line = lines[-1].strip()
                if not last_line.startswith("result"):
                    res = eval(last_line, {}, local_scope)
                    
            if isinstance(res, (pd.DataFrame, pd.Series)):
                if len(res) > 20:
                    return f"{res.head(20).to_string()}\n... (truncated to first 20 rows, total {len(res)})"
                return res.to_string()
            return str(res)
        except Exception as e:
            return f"Error executing query: {str(e)}"

    def chat(self, messages: list, role_context: str = None) -> dict:
        """
        Sends conversation to Groq API, handles tool calling iteratively,
        and returns the final assistant message along with execution audit trail.
        """
        if not self.api_key:
            return {
                "content": "⚠️ Groq API key is missing. Please set `GROQ_API_KEY` in `.env` or pass a valid key.",
                "executed_queries": []
            }
            
        system_content = SYSTEM_PROMPT
        if role_context:
            system_content += f"\n\n### Current User Context:\n{role_context}"
            
        full_messages = [{"role": "system", "content": system_content}]
        # Append history
        for m in messages:
            full_messages.append({"role": m["role"], "content": m["content"]})
            
        executed_queries = []
        
        # Max turns for tool calling loop
        for step in range(3):
            payload = {
                "model": self.model,
                "messages": full_messages,
                "tools": TOOLS_SPEC,
                "tool_choice": "auto",
                "max_tokens": 1500,
                "temperature": 0.2
            }
            
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                GROQ_API_URL,
                data=req_data,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "EduGrowth-AI/1.0"
                },
                method="POST"
            )
            
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    resp_json = json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8", errors="ignore")
                return {
                    "content": f"⚠️ Groq API Error ({e.code}): {err_body}",
                    "executed_queries": executed_queries
                }
            except Exception as e:
                return {
                    "content": f"⚠️ Connection Error: {str(e)}",
                    "executed_queries": executed_queries
                }
                
            choice = resp_json["choices"][0]
            msg = choice["message"]
            
            tool_calls = msg.get("tool_calls", [])
            if not tool_calls:
                # No more tools, return assistant text
                content = msg.get("content", "")
                if not content and "reasoning" in msg:
                    # In case reasoning was provided without content
                    content = msg["reasoning"]
                return {
                    "content": content,
                    "executed_queries": executed_queries
                }
                
            # Process tool calls
            full_messages.append(msg)
            for tc in tool_calls:
                func_name = tc["function"]["name"]
                if func_name == "query_dataset":
                    try:
                        args = json.loads(tc["function"]["arguments"])
                        code = args.get("python_code", "")
                    except Exception:
                        code = ""
                        
                    output = self._execute_code(code)
                    executed_queries.append({
                        "code": code,
                        "output": output
                    })
                    
                    full_messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "name": func_name,
                        "content": output
                    })
                    
        # If loop exited after max steps
        return {
            "content": msg.get("content", "Completed query execution."),
            "executed_queries": executed_queries
        }
