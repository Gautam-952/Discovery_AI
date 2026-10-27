import sys
import argparse
from runner.shared import query_model, print_section, update_memory, BASE_DIR

COUNCIL_MEMBERS = [
    ("builder_ai", "Construct a testable physical conjecture, symmetry group, or equation for:"),
    ("breaker_ai", "Audit the proposal for hidden singularities, causality breaches, and unitary violations:"),
    ("analogist_ai", "Bridge this with dualities or isomorphic mechanics from condensed matter or thermodynamics:"),
    ("reasoner_ai", "Deduce step-by-step observable consequences and falsification thresholds:")
]

def run_council(prompt: str):
    print(f"\n[+] Convening Council on Topic: {prompt}\n")
    session_log = f"\n\n## Council Session: {prompt}\n"

    for agent, instruction in COUNCIL_MEMBERS:
        agent_name = agent.replace("_ai", "").upper()
        print(f"[*] Consulting {agent_name}...")
        
        full_prompt = f"{instruction}\nTopic: {prompt}\n\nContext so far:\n{session_log}"
        response = query_model(agent, full_prompt)
        
        print_section(f"{agent_name} RESPONSE", response)
        session_log += f"\n### {agent_name}\n{response}\n"

    # Save transcript into session memory
    update_memory(str(BASE_DIR / "memory" / "session_memory.md"), session_log)
    print("\n[+] Council deliberations concluded and logged to memory/session_memory.md.")

def main():
    parser = argparse.ArgumentParser(description="Discovery AI Council Runner")
    parser.add_argument("--topic", type=str, default=None, help="Research topic or paradox")
    args, unknown = parser.parse_known_args()

    topic = args.topic
    if not topic:
        if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
            topic = " ".join(sys.argv[1:])
        else:
            # Fallback if invoked manually without flags
            try:
                topic = input("Ask Discovery Council: ").strip()
            except EOFError:
                topic = "The emergence of spacetime in quantum gravity"

    if topic:
        run_council(topic)
    else:
        print("[!] No topic provided.")

if __name__ == "__main__":
    main()
