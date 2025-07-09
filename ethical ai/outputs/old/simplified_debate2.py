# ethical_ai_debate.py
import ollama
import random
import logging
import os
from datetime import datetime
from typing import List, Dict, Tuple
from dataclasses import dataclass
from graphviz import Digraph
import json
import numpy as np

# ========================
# 1. SETUP & CONFIGURATION
# ========================
os.makedirs("outputs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        logging.FileHandler(f"outputs/debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)

# Disable unnecessary logs
logging.getLogger('urllib3').setLevel(logging.WARNING)

# ========================
# 2. CORE DATA STRUCTURES
# ========================
@dataclass
class DebateNode:
    """Node in rehearsal tree with scoring"""
    content: str
    children: List['DebateNode'] = None
    score: float = 0.0
    reasoning: str = ""

    def __post_init__(self):
        self.children = self.children or []

# ========================
# 3. DEBATE AGENT CLASSES
# ========================
class DebateAgent:
    """Baseline agent using rehearsal trees"""
    def __init__(self, position: str, knowledge_base: List[str], max_depth: int = 2, max_breadth: int = 2):
        self.position = position
        self.knowledge_base = knowledge_base
        self.max_depth = max_depth
        self.max_breadth = max_breadth
        self.tree_visualization_count = 0

    def generate_response(self, opponent_statement: str) -> str:
        """Main debate interface"""
        tree = self.build_rehearsal_tree(opponent_statement)
        best_path = self.select_best_path(tree)
        self.visualize_tree(tree, f"{self.position}_tree_{self.tree_visualization_count}")
        self.tree_visualization_count += 1
        return best_path[0].content

    def build_rehearsal_tree(self, current_statement: str, depth: int = 0) -> DebateNode:
        """Recursively build debate tree with scoring"""
        if depth >= self.max_depth:
            return DebateNode(content="[End of branch]")

        # Generate possible responses
        responses = [
            self._generate_candidate_response(current_statement)
            for _ in range(self.max_breadth)
        ]

        # Build tree recursively
        root = DebateNode(content=current_statement)
        for response in responses:
            child = self.build_rehearsal_tree(response, depth + 1)
            child.score = self.score_response(child.content)
            root.children.append(child)

        return root

    def _generate_candidate_response(self, statement: str) -> str:
        """Generate one possible response"""
        prompt = f"""As {self.position} debating AI in education, respond to:
        "{statement[:300]}"
        
        Use one of: {random.sample(self.knowledge_base, 2)}
        Max 2 sentences. Be persuasive."""
        
        response = ollama.chat(
            model='phi3:instruct',
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.7}
        )
        return response['message']['content'].strip()

    def score_response(self, response: str) -> float:
        """Score response quality (0-1 scale)"""
        criteria = {
            'logic': 0.4,
            'evidence': 0.3,
            'persuasiveness': 0.3
        }
        
        analysis = ollama.chat(
            model='phi3:instruct',
            messages=[{
                'role': 'user',
                'content': f"Rate this debate response (0-10) for:\n"
                          f"1. Logical consistency\n2. Evidence use\n3. Persuasiveness\n\n"
                          f"Response: {response[:500]}\n"
                          f"Return JSON with scores only."
            }]
        )
        
        try:
            scores = json.loads(analysis['message']['content'])
            weighted_score = sum(scores[k]*v for k,v in criteria.items()) / 10
            return min(max(weighted_score, 0), 1)
        except:
            return random.uniform(0.6, 0.8)

    def select_best_path(self, tree: DebateNode) -> List[DebateNode]:
        """Select highest-scoring path through tree"""
        def dfs(node):
            if not node.children:
                return [node], node.score
            best_path, best_score = [], -1
            for child in node.children:
                path, score = dfs(child)
                if score > best_score:
                    best_path, best_score = path, score
            return [node] + best_path, (node.score + best_score)/2
        return dfs(tree)[0]

    def visualize_tree(self, tree: DebateNode, filename: str):
        """Generate debate tree visualization"""
        dot = Digraph()
        def add_nodes(node, parent_id=None):
            node_id = str(id(node))
            label = f"{node.content[:50]}...\n(Score: {node.score:.2f})"
            dot.node(node_id, label)
            if parent_id:
                dot.edge(parent_id, node_id)
            for child in node.children:
                add_nodes(child, node_id)
        add_nodes(tree)
        dot.render(f'outputs/{filename}', format='png', cleanup=True)

class EnhancedDebater(DebateAgent):
    """Agent with Theory of Mind + Emotional Intelligence"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.opponent_model = {
            'beliefs': [],
            'argument_style': 'neutral',
            'emotional_state': 'calm'
        }

    def update_opponent_model(self, statement: str):
        """Analyze opponent's mental state"""
        prompt = f"""Analyze this debate statement:
        "{statement[:500]}"
        
        Extract as JSON with:
        - 'beliefs': list of core beliefs
        - 'argument_style': direct/emotional/technical
        - 'emotional_state': angry/calm/defensive"""
        
        try:
            response = ollama.chat(
                model='phi3:instruct',
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.3}
            )
            self.opponent_model.update(json.loads(response['message']['content']))
        except:
            pass

    def _generate_candidate_response(self, statement: str) -> str:
        """Generate response using opponent modeling"""
        self.update_opponent_model(statement)
        
        # Emotional adaptation
        tone_map = {
            'angry': 'calm and factual',
            'defensive': 'supportive but firm',
            'calm': 'reasoned'
        }
        
        prompt = f"""As {self.position} debating AI in education, respond to:
        "{statement[:300]}"
        
        Opponent Profile:
        - Believes: {self.opponent_model['beliefs'][:2]}
        - Style: {self.opponent_model['argument_style']}
        - Emotion: {self.opponent_model['emotional_state']}
        
        Adapt using:
        - Tone: {tone_map.get(self.opponent_model['emotional_state'], 'neutral')}
        - Counter these beliefs: {self.opponent_model['beliefs'][:1]}
        
        Use one of: {random.sample(self.knowledge_base, 2)}
        Max 2 sentences."""
        
        response = ollama.chat(
            model='phi3:instruct',
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.6}
        )
        return response['message']['content'].strip()

# ========================
# 4. DEBATE ORCHESTRATION
# ========================
def run_comparative_debate():
    """Run baseline vs enhanced debate with evaluation"""
    KNOWLEDGE_BASE = {
        'pro': [
            "AI enables 24/7 personalized tutoring (Stanford 2023)",
            "Automated grading saves teachers 9hrs/week (Brookings)",
            "Adaptive learning improves scores by 22% (MIT)"
        ],
        'con': [
            "AI cannot replicate human mentorship (UNESCO 2024)",
            "Algorithmic bias widens achievement gaps (Harvard)",
            "Over-reliance erases critical thinking (Neuroscience)"
        ]
    }

    logging.info("\n===== BASELINE DEBATE =====")
    baseline_pro = DebateAgent("PRO", KNOWLEDGE_BASE['pro'])
    baseline_con = DebateAgent("CON", KNOWLEDGE_BASE['con'])
    run_debate_rounds(baseline_pro, baseline_con)

    logging.info("\n\n===== ENHANCED DEBATE (ToM+Emotion) =====")
    enhanced_pro = EnhancedDebater("PRO+", KNOWLEDGE_BASE['pro'])
    enhanced_con = EnhancedDebater("CON+", KNOWLEDGE_BASE['con'])
    run_debate_rounds(enhanced_pro, enhanced_con)

def run_debate_rounds(pro: DebateAgent, con: DebateAgent, rounds: int = 3):
    """Run debate between two agents"""
    current_statement = "AI should be widely adopted in college education"
    logging.info(f"\nTOPIC: {current_statement}\n")

    for round_num in range(rounds):
        logging.info(f"\n⭐ ROUND {round_num+1}")
        
        con_response = con.generate_response(current_statement)
        logging.info(f"🔴 {con.position}: {con_response}")
        
        pro_response = pro.generate_response(con_response)
        logging.info(f"🔵 {pro.position}: {pro_response}")
        
        current_statement = pro_response

    logging.info("\n📊 Debate concluded. Check /outputs for visualizations")

# ========================
# 5. MAIN EXECUTION
# ========================
if __name__ == "__main__":
    run_comparative_debate()