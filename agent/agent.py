"""
The QA agent.

The model gets a goal and a set of tools, then decides each next step itself:
read the guides, write its own scorer, compare, investigate mismatches, test
hypotheses, and finally submit a report. This file runs that loop.

Usage (from the project folder):
    python -m agent.agent pipeline_01
"""

import argparse

from agent.prompts import (
    AGENT_SYSTEM_PROMPT,
    AGENT_TASK_PROMPT,
    BUDGET_WARNING_PROMPT,
    FINAL_TURN_PROMPT,
    MAX_TURNS,
    NUDGE_PROMPT,
)
from agent.tools import SUBMIT_ONLY, TOOL_DEFINITIONS, Tools
from common.checker_io import build_workspace, clean_findings, remove_workspace, run_dir, save_run
from common.llm_client import LLMClient

CHECKER_NAME = "agent"
MAX_NUDGES = 3
WARN_WHEN_TURNS_LEFT = 6


def message_to_dict(message):
    """Turn the model's reply into a plain dict we can send back and save."""
    entry = {"role": "assistant", "content": message.content or ""}
    if message.tool_calls:
        entry["tool_calls"] = []
        for call in message.tool_calls:
            # model_dump keeps provider-specific extras. Gemini, for example, attaches a
            # "thought signature" to each tool call and rejects the next request without it.
            entry["tool_calls"].append(call.model_dump(exclude_none=True))
    return entry


def run_agent(pipeline_id, folder, client=None, verbose=True):
    """Run the agent on one pipeline output and save its report in folder."""
    if client is None:
        client = LLMClient()

    workspace = build_workspace(pipeline_id)
    tools = Tools(workspace)

    messages = [
        {"role": "system", "content": AGENT_SYSTEM_PROMPT},
        {"role": "user", "content": AGENT_TASK_PROMPT},
    ]
    n_nudges = 0
    stop_reason = "max_turns"

    try:
        for turn in range(1, MAX_TURNS + 1):
            turns_left = MAX_TURNS - turn + 1

            # Near the end, remind the agent of its budget. On the last turn,
            # submit_report is the only tool it is offered.
            available_tools = TOOL_DEFINITIONS
            if turns_left == WARN_WHEN_TURNS_LEFT:
                messages.append({"role": "user", "content": BUDGET_WARNING_PROMPT.format(turns_left=turns_left)})
            if turns_left == 1:
                messages.append({"role": "user", "content": FINAL_TURN_PROMPT})
                available_tools = SUBMIT_ONLY

            reply = client.chat(messages, available_tools)
            messages.append(message_to_dict(reply))

            if not reply.tool_calls:
                n_nudges += 1
                if n_nudges > MAX_NUDGES:
                    stop_reason = "stopped_using_tools"
                    break
                messages.append({"role": "user", "content": NUDGE_PROMPT})
                continue

            for call in reply.tool_calls:
                if verbose:
                    print(f"  turn {turn}: {call.function.name}")
                result = tools.execute(call.function.name, call.function.arguments)
                messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

            if tools.submission is not None:
                stop_reason = "submitted"
                break
    finally:
        remove_workspace(workspace)

    if tools.submission is not None:
        submission = tools.submission
        findings = {
            "verdict": submission.get("verdict", "issues_found"),
            "findings": clean_findings(submission.get("findings", [])),
            "rules_understood": submission.get("rules_understood", {}),
        }
        report = submission.get("report_markdown", "")
    else:
        findings = {"verdict": "no_report", "findings": [], "rules_understood": {}}
        report = f"The agent did not submit a report ({stop_reason}).\n"

    usage = client.usage()
    usage["checker"] = CHECKER_NAME
    usage["stop_reason"] = stop_reason
    usage["python_scripts_run"] = tools.n_scripts

    save_run(folder, findings, report, usage, transcript=messages)
    return findings


def main():
    parser = argparse.ArgumentParser(description="Run the QA agent on one pipeline output.")
    parser.add_argument("pipeline_id")
    parser.add_argument("--run", type=int, default=1, help="Run number (for repeated runs)")
    args = parser.parse_args()

    folder = run_dir(CHECKER_NAME, args.pipeline_id, args.run)
    findings = run_agent(args.pipeline_id, folder)
    print(f"{args.pipeline_id}: {findings['verdict']} ({len(findings['findings'])} findings) -> {folder}")


if __name__ == "__main__":
    main()
