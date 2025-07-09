# simplified_debate.py
import ollama
import random
import logging
import os
from datetime import datetime
import urllib3
from typing import List  # <-- Add this import

# Disable HTTP request logs
urllib3.disable_warnings()
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('ollama').setLevel(logging.WARNING)

# Setup debate logging
os.makedirs("outputs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler(f"outputs/debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)

class DebateAgent:
    def __init__(self, position: str, knowledge_base: List[str]):
        self.position = position
        self.knowledge_base = knowledge_base

    def generate_response(self, opponent_statement: str) -> str:
        prompt = f"""As a {self.position} debater, respond to this argument:
        "{opponent_statement[:300]}"
        
        Use this fact: {random.choice(self.knowledge_base)}
        Keep response under 3 sentences."""

        response = ollama.chat(
            model='phi3:instruct',
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.5}
        )
        return response['message']['content'].strip()

def run_debate():
    PRO_KNOWLEDGE = [
        "AI tutors provide 24/7 personalized help",
        "Automated grading saves teachers hours each week",
        "Adaptive learning improves student outcomes"
    ]
    
    CON_KNOWLEDGE = [
        "AI lacks human empathy in teaching",
        "Algorithmic bias can disadvantage some students",
        "Overuse of AI reduces critical thinking skills"
    ]

    print("\n=== AI EDUCATION DEBATE ===")
    pro = DebateAgent("PRO (supports AI)", PRO_KNOWLEDGE)
    con = DebateAgent("CON (opposes AI)", CON_KNOWLEDGE)

    current_topic = "AI should be widely used in education"
    print(f"\nTOPIC: {current_topic}")

    for round_num in range(3):
        print(f"\nROUND {round_num + 1}:")
        
        con_response = con.generate_response(current_topic)
        print(f"\nCON: {con_response}")
        
        pro_response = pro.generate_response(con_response)
        print(f"\nPRO: {pro_response}")
        
        current_topic = pro_response

    print("\n=== DEBATE CONCLUDED ===")

if __name__ == "__main__":
    run_debate()