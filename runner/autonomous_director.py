import json
import time
import subprocess
import sys
import os
import shutil
import signal
from pathlib import Path
from runner.shared import query_model, read_memory, update_memory, BASE_DIR
from runner.novelty_filter import check_hypothesis_novelty

DRIVE_WORKSPACE = Path("/content/drive/MyDrive/Discovery_AI_Workspace")

def sync_to_drive():
    """Automated backup hook to persist memory and manuscripts to Google Drive."""
    try:
        DRIVE_WORKSPACE.mkdir(parents=True, exist_ok=True)
        
        # 1. Sync memory files
        mem_dir = BASE_DIR / "memory"
        if mem_dir.exists():
            dest_mem = DRIVE_WORKSPACE / "memory"
            dest_mem.mkdir(parents=True, exist_ok=True)
            for item in mem_dir.glob("*"):
                if item.is_file():
                    shutil.copy2(item, dest_mem / item.name)

        # 2. Sync generated preprints/drafts
        drafts_dir = BASE_DIR / "vault" / "drafts"
        if drafts_dir.exists():
            dest_drafts = DRIVE_WORKSPACE / "drafts"
            dest_drafts.mkdir(parents=True, exist_ok=True)
            for item in drafts_dir.glob("*"):
                if item.is_file():
                    shutil.copy2(item, dest_drafts / item.name)

        print("\n" + "=" * 60)
        print(f"[+] [AUTO-SAVE] Successfully synced artifacts to {DRIVE_WORKSPACE}")
        print("=" * 60 + "\n")
    except Exception as e:
        print(f"[!] [AUTO-SAVE ERROR] Failed to sync to Drive: {e}")

def emergency_exit_handler(signum, frame):
    """Saves everything immediately if Colab sends a termination signal."""
    print("\n[!] Received termination signal. Running final emergency backup to Drive...")
    sync_to_drive()
    sys.exit(0)

# Register termination handlers
signal.signal(signal.SIGINT, emergency_exit_handler)
signal.signal(signal.SIGTERM, emergency_exit_handler)

def tail_text(text: str, max_chars: int = 1500) -> str:
    if len(text) <= max_chars:
        return text
    return "... [truncated] ...\n" + text[-max_chars:]

def run_director_cycle(cycle_num: int):
    print(f"\n{'='*25} Cycle {cycle_num} {'='*25}")
    
    # 1. Load active memory state
    discoveries = tail_text(read_memory(str(BASE_DIR / "memory" / "discoveries.md")), 1200)
    failed = tail_text(read_memory(str(BASE_DIR / "memory" / "failed_hypotheses.md")), 1200)
    session_mem = tail_text(read_memory(str(BASE_DIR / "memory" / "session_memory.md")), 800)
    
    notes_dir = BASE_DIR / "vault" / "notes"
    notes_summary = ""
    if notes_dir.exists():
        notes_files = list(notes_dir.glob("*.md"))[:3]
        for nf in notes_files:
            notes_summary += f"\nNote ({nf.name}):\n" + tail_text(read_memory(str(nf)), 400)

    prompt = f"""You are Director AI. Review the current state of theoretical research:

[RECENT DISCOVERIES]
{discoveries if discoveries else 'None yet.'}

[RECENT FAILED HYPOTHESES / RED-TEAM LOGS]
{failed if failed else 'None yet.'}

[RECENT SESSION MEMORY]
{session_mem if session_mem else 'None yet.'}

[RESEARCH NOTES]
{notes_summary if notes_summary else 'None.'}

Select an unexamined theoretical gap or paradox in theoretical physics/quantum gravity.
Choose the best runner pipeline: 'full_runner', 'council_runner', 'creative_runner', or 'fast_runner'.

Respond ONLY with a valid JSON object matching this schema:
{{
  "action": "select",
  "topic": "<Specific theoretical conjecture or paradox to investigate>",
  "runner": "<full_runner|council_runner|creative_runner|fast_runner>",
  "reasoning": "<Concise operational reasoning>"
}}"""

    print("[*] Consulting Director AI for triage and pipeline selection...")
    raw_response = query_model("director_ai", prompt, options={"num_predict": 300})
    
    cleaned = raw_response.strip()
    if "```json" in cleaned:
        cleaned = cleaned.split("```json")[1].split("```")[0].strip()
    elif "```" in cleaned:
        cleaned = cleaned.split("```")[1].split("```")[0].strip()

    try:
        decision = json.loads(cleaned)
    except Exception as e:
        print(f"[!] Error parsing Director output as JSON. Raw text:\n{raw_response}")
        raise e

    topic = decision.get("topic", "").strip()
    runner = decision.get("runner", "full_runner").strip()
    reasoning = decision.get("reasoning", "").strip()

    print(f"[+] Director Decision:")
    print(f"    - Topic: {topic}")
    print(f"    - Runner: {runner}")
    print(f"    - Reasoning: {reasoning}")

    # 2. Vector Novelty Check
    print("[*] Evaluating hypothesis novelty against memory archives...")
    novelty_eval = check_hypothesis_novelty(topic, threshold=0.85)
    
    if not novelty_eval.get("is_novel", True):
        print(f"[!] Novelty Check FAILED: {novelty_eval.get('reason')}")
        update_memory(
            str(BASE_DIR / "memory" / "failed_hypotheses.md"),
            f"\n### Rejected Redundant Proposal: {topic}\n- Similarity: {novelty_eval.get('max_similarity')}\n- Reason: Redundancy threshold exceeded.\n"
        )
        return False

    print(f"[+] Novelty Check PASSED: Max similarity is {novelty_eval.get('max_similarity', 0.0)}")

    # 3. Subprocess Execution
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BASE_DIR) + (":" + env["PYTHONPATH"] if "PYTHONPATH" in env else "")

    module_name = f"runner.{runner}"
    print(f"[*] Executing pipeline via `{module_name}`...")
    
    cmd = [sys.executable, "-m", module_name, "--topic", topic]
    res = subprocess.run(cmd, cwd=str(BASE_DIR), env=env)
    
    if res.returncode == 0:
        print(f"[+] Cycle {cycle_num} execution successful.")
        return True
    else:
        print(f"[!] Subprocess `{module_name}` exited with code {res.returncode}.")
        return False

def main():
    print("[*] Starting Fully Infinite Autonomous Director.")
    print("[*] Auto-saving to Google Drive every 5 cycles.")
    print("[*] Running continuously until Colab runtime disconnects or limit is reached...\n")
    
    cycle = 1

    while True:
        try:
            run_director_cycle(cycle)
        except Exception as e:
            print(f"[!] Cycle {cycle} error: {e}. Moving to next cycle in 5s...")
            time.sleep(5)

        # Auto-save to Google Drive after every 5 cycles
        if cycle % 5 == 0:
            sync_to_drive()

        cycle += 1
        time.sleep(2)

if __name__ == "__main__":
    main()
