# run_debate.py
import logging
import os
from datetime import datetime
from llm_wrapper import LLMWrapper
from debate_system import DebateAgent, TheoryOfMindDebater
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

os.makedirs("outputs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler(f"outputs/debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)

PRO_KNOWLEDGE = [
    "AI enables 24/7 personalized tutoring (Stanford 2023 study)",
    "Automated grading saves teachers 9hrs/week (Brookings Institute)",
    "Adaptive learning improves test scores by 22% (MIT Review)"
]

CON_KNOWLEDGE = [
    "AI cannot replicate human mentorship (UNESCO Report 2024)",
    "Algorithmic bias widens achievement gaps (Harvard Ed. Review)",
    "Over-reliance erases critical thinking skills (Neuroscience Journal)"
]

def run_debate(agent1, agent2, name_suffix):
    logging.info(f"\n--- {name_suffix.upper()} DEBATE ---")
    topic = "AI should be widely adopted in college education"
    logging.info(f"TOPIC: {topic}\n")

    current_statement = topic
    for round_num in range(3):
        logging.info(f"\nROUND {round_num + 1}")
        response1 = agent1.generate_response(current_statement)
        logging.info(f"{agent1.position}: {response1}")
        current_statement = response1

        response2 = agent2.generate_response(current_statement)
        logging.info(f"{agent2.position}: {response2}")
        current_statement = response2

        if round_num == 2:
            tree1 = agent1.build_rehearsal_tree(response2)
            path1 = agent1.select_best_path(tree1)
            logging.info("\nPRO TREE PATH:")
            for i, node in enumerate(path1):
                logging.info(f"Step {i+1}: {node.content[:60]}...")

            tree2 = agent2.build_rehearsal_tree(response1)
            path2 = agent2.select_best_path(tree2)
            logging.info("\nCON TREE PATH:")
            for i, node in enumerate(path2):
                logging.info(f"Step {i+1}: {node.content[:60]}...")

            try:
                agent1.visualize_tree(tree1, f"{name_suffix}_pro_final_tree")
                agent2.visualize_tree(tree2, f"{name_suffix}_con_final_tree")
            except Exception as e:
                logging.warning("Tree visualization failed (Graphviz not installed). Skipping.")

    logging.info(f"\n{name_suffix.upper()} DEBATE COMPLETE\n")

def main():
    llm = LLMWrapper(model='phi3:instruct')

    # Baseline agents
    baseline_pro = DebateAgent("PRO", llm, PRO_KNOWLEDGE)
    baseline_con = DebateAgent("CON", llm, CON_KNOWLEDGE)
    run_debate(baseline_pro, baseline_con, "baseline")

    # Enhanced agents
    enhanced_pro = TheoryOfMindDebater("PRO+", llm, PRO_KNOWLEDGE)
    enhanced_con = TheoryOfMindDebater("CON+", llm, CON_KNOWLEDGE)
    run_debate(enhanced_pro, enhanced_con, "enhanced")

if __name__ == "__main__":
    main()