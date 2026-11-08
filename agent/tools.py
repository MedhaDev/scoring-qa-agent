"""
The tools the agent can use. All of them work only inside its workspace folder.

  list_files     see which files are in the workspace
  read_file      read a text file (the scoring guides)
  run_python     run Python code inside the workspace (pandas is available)
  submit_report  hand in the final QA report and structured findings

Note: run_python runs model-written code on this computer, with the workspace as
its working folder. The workspace lives outside the project folder, and every
piece of code is saved in the transcript so it can be audited afterwards.
"""

import json
import os
import subprocess
import sys

from common.checker_io import CATEGORIES, INSTRUMENTS

MAX_READ_CHARS = 20000
MAX_OUTPUT_CHARS = 10000
PYTHON_TIMEOUT_SECONDS = 120

RULES_SCHEMA = {
    "type": "object",
    "properties": {
        "n_items": {"type": "integer"},
        "reverse_items": {"type": "array", "items": {"type": "integer"}},
        "max_missing_items": {"type": "integer"},
        "half_rounding": {"type": "string", "enum": ["up", "down", "even"]},
        "band_starts": {
            "type": "array",
            "items": {"type": "integer"},
            "description": "Lowest total of each severity band, in order. Empty if no bands.",
        },
    },
}

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List the files in your workspace.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a text file from your workspace. For CSV files, prefer run_python with pandas.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "File name inside the workspace"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": (
                "Run a Python script in your workspace and get back what it prints. "
                "pandas and numpy are installed. Files in the workspace can be opened by name. "
                "Each call is a fresh script: nothing is remembered between calls unless you save it to a file."
            ),
            "parameters": {
                "type": "object",
                "properties": {"code": {"type": "string", "description": "Complete Python script"}},
                "required": ["code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "submit_report",
            "description": "Submit your final QA report. Call this exactly once, at the end.",
            "parameters": {
                "type": "object",
                "properties": {
                    "verdict": {"type": "string", "enum": ["pass", "issues_found"]},
                    "findings": {
                        "type": "array",
                        "description": "One entry per distinct root cause. Empty if the verdict is pass.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "instrument": {"type": "string", "enum": INSTRUMENTS},
                                "category": {"type": "string", "enum": CATEGORIES},
                                "columns": {"type": "string", "description": "Output column(s) affected"},
                                "description": {"type": "string", "description": "What the pipeline does wrong"},
                                "evidence": {"type": "string", "description": "Counts and example respondent IDs"},
                                "rows_affected": {"type": "integer"},
                                "confirmed": {
                                    "type": "boolean",
                                    "description": "True if you reproduced the pipeline's output exactly by applying your hypothesised mistake",
                                },
                            },
                            "required": ["instrument", "category", "description", "evidence", "rows_affected", "confirmed"],
                        },
                    },
                    "rules_understood": {
                        "type": "object",
                        "description": "The scoring rules you applied, per questionnaire.",
                        "properties": {"phq9": RULES_SCHEMA, "gad7": RULES_SCHEMA, "rses": RULES_SCHEMA},
                    },
                    "report_markdown": {"type": "string", "description": "Plain-English QA report for a research team"},
                },
                "required": ["verdict", "findings", "report_markdown"],
            },
        },
    },
]


# Only the submit tool, offered on the agent's last turn
SUBMIT_ONLY = [tool for tool in TOOL_DEFINITIONS if tool["function"]["name"] == "submit_report"]


class Tools:
    def __init__(self, workspace):
        self.workspace = workspace
        self.n_scripts = 0
        self.submission = None

    def _safe_path(self, path):
        """Return the full path only if it stays inside the workspace."""
        full_path = os.path.realpath(os.path.join(self.workspace, path))
        if not full_path.startswith(os.path.realpath(self.workspace) + os.sep):
            return None
        return full_path

    def list_files(self):
        names = []
        for name in sorted(os.listdir(self.workspace)):
            if not name.startswith("_agent_script_"):
                names.append(name)
        return "\n".join(names)

    def read_file(self, path):
        full_path = self._safe_path(path)
        if full_path is None or not os.path.isfile(full_path):
            return f"Error: '{path}' is not a file in your workspace."
        with open(full_path, errors="replace") as f:
            text = f.read()
        if len(text) > MAX_READ_CHARS:
            text = text[:MAX_READ_CHARS] + f"\n... [truncated, file has {len(text)} characters]"
        return text

    def run_python(self, code):
        self.n_scripts += 1
        script_path = os.path.join(self.workspace, f"_agent_script_{self.n_scripts}.py")
        with open(script_path, "w") as f:
            f.write(code)

        try:
            result = subprocess.run(
                [sys.executable, "-I", script_path],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=PYTHON_TIMEOUT_SECONDS,
            )
            output = result.stdout
            if result.stderr:
                output += "\n[stderr]\n" + result.stderr
        except subprocess.TimeoutExpired:
            output = f"Error: script took longer than {PYTHON_TIMEOUT_SECONDS} seconds and was stopped."

        if not output.strip():
            output = "(no output - use print() to see results)"
        if len(output) > MAX_OUTPUT_CHARS:
            output = output[:MAX_OUTPUT_CHARS] + "\n... [output truncated]"
        return output

    def submit_report(self, arguments):
        self.submission = arguments
        return "Report received. You are done."

    def execute(self, name, arguments_json):
        """Run one tool call and return its result as text."""
        try:
            arguments = json.loads(arguments_json) if arguments_json else {}
        except json.JSONDecodeError:
            return "Error: tool arguments were not valid JSON. Please try again."

        if name == "list_files":
            return self.list_files()
        if name == "read_file":
            return self.read_file(arguments.get("path", ""))
        if name == "run_python":
            return self.run_python(arguments.get("code", ""))
        if name == "submit_report":
            return self.submit_report(arguments)
        return f"Error: unknown tool '{name}'."
