import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Ensure imports work from project root or runner directory
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from runner.shared import query_model, read_memory, update_memory

VALID_RUNNERS = {
    "fast_runner": "runner/fast_runner.py",
    "creative_runner": "runner/creative_runner.py",
    "council_runner": "runner/council_runner.py",
    "full_runner": "runner/full_runner.py"
}

def load_research_context() -> dict:
    """Reads vault notes, persistent discoveries, and failed hypotheses."""
    notes = []
    notes_dir = BASE_DIR / "vault" / "notes"
    if notes_dir.exists():
        for note_file in notes_dir.glob("*.md"):
            try:
                with open(note_file, "r", encoding="utf-8") as f:
                    notes.append(f"### File: {note_file.name}\n{f.read()}")
            except Exception as e:
                print(f"[!] Warning reading note {note_file.name}: {e}")

    failed = read_memory(str(BASE_DIR / "memory" / "failed_hypotheses.md")) or "None logged yet."
    discoveries = read_memory(str(BASE_DIR / "memory" / "discoveries.md")) or "None logged yet."
    patterns = read_memory(str(BASE_DIR / "memory" / "patterns.md")) or "None logged yet."

    return {
        "notes": "\n\n".join(notes) if notes else "No theory notes found.",
        "failed": failed,
        "discoveries": discoveries,
        "patterns": patterns
    }

def clean_json_response(raw_text: str) -> dict:
    """Strips markdown code fence wrappers to ensure clean JSON parsing."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return json.loads(cleaned.strip())

def decide_next_step(context: dict) -> dict:
    """Prompts director_ai to triage assumptions and pick the optimal execution runner."""
    director_brain_path = BASE_DIR / "brains" / "director_brain.md"
    brain_instructions = ""
    if director_brain_path.exists():
        with open(director_brain_path, "r", encoding="utf-8") as f:
            brain_instructions = f.read()

    prompt = f"""{brain_instructions}

=== CURRENT WORKING THEORIES & NOTES ===
{context['notes'][:3000]}

=== RECENT DETECTED PATTERNS ===
{context['patterns'][:1000]}

=== KNOWN FAILED HYPOTHESES ===
{context['failed'][:1500]}

=== CONFIRMED DISCOVERIES ===
{context['discoveries'][:1500]}

Evaluate the active theoretical assumptions and select the single next priority test.
Provide your output strictly as a JSON object matching the specification.
"""

    print("[*] Consulting Director AI for triage and pipeline selection...")
    raw_response = query_model("director_ai", prompt)
    
    try:
        decision = clean_json_response(raw_response)
    except Exception as e:
        print(f"[!] Error parsing Director output as JSON. Raw text:\n{raw_response}")
        raise e

    return decision

def execute_triage_decision(decision: dict):
    """Launches the runner chosen by the Director."""
    runner_key = decision.get("runner", "").strip().lower()
    hypothesis = decision.get("target_hypothesis", "Theoretical verification")
    reasoning = decision.get("reasoning", "No reasoning provided.")
    priority = decision.get("priority", 3)

    if runner_key not in VALID_RUNNERS:
        print(f"[!] Unrecognized runner '{runner_key}', falling back to fast_runner.")
        runner_key = "fast_runner"

    target_script = BASE_DIR / VALID_RUNNERS[runner_key]

    print("\n" + "=" * 60)
    print(f"[*] Autonomous Director Decision:")
    print(f"    - Target Hypothesis: {hypothesis}")
    print(f"    - Selected Runner  : {runner_key}.py (Priority: {priority})")
    print(f"    - Strategy/Reason  : {reasoning}")
    print("=" * 60 + "\n")

    # Run the selected script as a subprocess passing the target hypothesis as a parameter
    cmd = [sys.executable, str(target_script), "--topic", hypothesis]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] Error executing {runner_key}.py: {e}")
    except Exception as e:
        print(f"[!] Unexpected error during execution: {e}")

def run_loop(max_cycles: int = 5, sleep_interval: int = 2):
    """Main execution loop for continuous autonomous research."""
    cycle = 1
    while cycle <= max_cycles:
        print(f"\n>>> Autonomous Research Cycle {cycle}/{max_cycles} <<<")
        try:
            context = load_research_context()
            decision = decide_next_step(context)
            execute_triage_decision(decision)
            
            # Log state update to session memory
            log_entry = (
                f"\n### Cycle {cycle} Execution\n"
                f"- **Target**: {decision.get('target_hypothesis')}\n"
                f"- **Pipeline**: `{decision.get('runner')}.py`\n"
                f"- **Reasoning**: {decision.get('reasoning')}\n"
            )
            update_memory(str(BASE_DIR / "memory" / "session_memory.md"), log_entry)

        except Exception as e:
            print(f"[!] Cycle {cycle} failed: {e}")

        cycle += 1
        if cycle <= max_cycles:
            print(f"[*] Pausing for {sleep_interval}s before next cycle...")
            time.sleep(sleep_interval)

    print("\n[*] Autonomous director session finished.")

if __name__ == "__main__":
    run_loop(max_cycles=5)