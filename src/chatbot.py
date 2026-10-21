"""
EduGrowth AI - Dynamic Data Chatbot Assistant
Powered by Groq API using model openai/gpt-oss-120b.
Enables natural language querying of ANY tabular dataset (CSV, Excel, or default cohort)
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
    def __init__(self, df: pd.DataFrame, api_key: str = None, model: str = None, dataset_name: str = "Institutional Student Cohort"):
        self.df = df
        self.dataset_name = dataset_name
        self.api_key = api_key or DEFAULT_GROQ_API_KEY
        self.model = model or DEFAULT_MODEL
        
    def update_dataset(self, df: pd.DataFrame, dataset_name: str = "Uploaded Dataset"):
        """Swaps the active dataset and updates schema representation dynamically."""
        self.df = df
        self.dataset_name = dataset_name

    def get_system_prompt(self) -> str:
        """Dynamically generates a rich, precise schema description for whatever dataframe is active."""
        num_rows, num_cols = self.df.shape
        lines = [
            f"You are the EduGrowth AI Data Analyst & Institutional Assistant, powered by openai/gpt-oss-120b.",
            f"You have direct query access to a pandas DataFrame named `df` representing the active dataset '{self.dataset_name}'.",
            f"\n### Active Dataset Profile:",
            f"- Dataset Name: {self.dataset_name}",
            f"- Total Rows: {num_rows:,}",
            f"- Total Columns: {num_cols}",
            f"\n### Complete Column Schema & Value Distributions:"
        ]
        
        for col in self.df.columns:
            dtype_str = str(self.df[col].dtype)
            null_count = int(self.df[col].isnull().sum())
            null_info = f", {null_count} nulls" if null_count > 0 else " (no nulls)"
            
            if pd.api.types.is_numeric_dtype(self.df[col]):
                clean_s = self.df[col].dropna()
                if len(clean_s) > 0:
                    min_v = round(float(clean_s.min()), 2)
                    max_v = round(float(clean_s.max()), 2)
                    mean_v = round(float(clean_s.mean()), 2)
                    lines.append(f"- `{col}` ({dtype_str}): numeric, range=[{min_v} to {max_v}], mean={mean_v}{null_info}")
                else:
                    lines.append(f"- `{col}` ({dtype_str}): numeric (all null values)")
            else:
                uniques = int(self.df[col].nunique())
                sample_vals = [str(x) for x in self.df[col].dropna().unique()[:5]]
                if uniques <= 10:
                    lines.append(f"- `{col}` ({dtype_str}): categorical ({uniques} categories: {sample_vals}){null_info}")
                else:
                    lines.append(f"- `{col}` ({dtype_str}): text/identifier ({uniques} unique values, samples: {sample_vals}){null_info}")
                    
        # Check for educational / student dataset domain columns
        if 'academic_risk_level' in self.df.columns:
            lines.append("\n### Domain Guidelines:")
            lines.append("- `academic_risk_level`: 0 = 'On Track (Low Risk)', 1 = 'Moderate Risk (Watchlist)', 2 = 'Critical Risk (Immediate Intervention)'")
        if 'attendance_rate_pct' in self.df.columns:
            lines.append("- Institutional lecture attendance benchmark is 75%. Below 75% indicates attendance deficit.")

        lines.append("""
### Analytical Directives:
1. When asked about counts, percentages, averages, correlations, distributions, outliers, rankings, top/bottom records, or filtering, ALWAYS call the `query_dataset` function to compute the real result directly from `df`.
2. Format your response in clean markdown with bold numbers, key metric cards or bullet points, and neat markdown tables where appropriate.
3. If the user refers to a specific name, identifier, or category, filter `df` specifically for that item.
4. Provide actionable insights, context, and clear takeaways alongside numerical answers.
""")
        return "\n".join(lines)

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
            
        system_content = self.get_system_prompt()
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
