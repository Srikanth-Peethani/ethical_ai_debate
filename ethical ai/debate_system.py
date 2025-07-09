# debate_system.py
from typing import List, Dict
from dataclasses import dataclass
import random
from graphviz import Digraph
import json
import subprocess

@dataclass
class DebateNode:
    content: str
    children: List['DebateNode'] = None
    score: float = 0.0

    def __post_init__(self):
        if self.children is None:
            self.children = []

class DebateAgent:
    def __init__(self, position: str, llm: 'LLMWrapper', knowledge_base: List[str],
                 max_depth: int = 2, max_breadth: int = 2):
        self.position = position
        self.llm = llm
        self.knowledge_base = knowledge_base
        self.max_depth = max_depth
        self.max_breadth = max_breadth

    def build_rehearsal_tree(self, opponent_statement: str, depth: int = None) -> DebateNode:
        if depth is None:
            depth = self.max_depth
        root = DebateNode(opponent_statement)

        def expand(node, current_depth):
            if current_depth == 0:
                node.score = self.score_response(node.content)
                return
            for _ in range(self.max_breadth):
                response = self.generate_response(node.content)
                child = DebateNode(response)
                node.children.append(child)
                expand(child, current_depth - 1)

        expand(root, depth)
        return root

    def select_best_path(self, tree: DebateNode) -> List[DebateNode]:
        best_path = []

        def recurse(node):
            best_path.append(node)
            if not node.children:
                return
            best_child = max(node.children, key=lambda c: c.score)
            recurse(best_child)

        recurse(tree)
        return best_path

    def generate_response(self, opponent_statement: str) -> str:
        prompt = f"""As a {self.position} debater on AI in education, craft a response that:
        1. Acknowledges 1 valid point from: {opponent_statement[:200]}
        2. Presents 2 counterpoints from: {', '.join(random.sample(self.knowledge_base, 2))}
        3. Concludes with a strong position statement
        Respond in exactly 3 sentences:"""
        return self.llm.generate(prompt)
    def score_response(self, response: str) -> float:
        criteria = {
            'logic': 0.4,
            'evidence': 0.3,
            'persuasiveness': 0.3
        }

        analysis = self.llm.generate(
            f"""Rate this response on a scale of 1-10 for:
            1. Logical consistency
            2. Evidence quality
            3. Persuasiveness
            
            Response: {response}
            Return JSON format with keys: logic, evidence, persuasiveness"""
        )

        try:
            scores = json.loads(analysis)
            return sum(scores[k] * v for k, v in criteria.items()) / 10
        except Exception:
            return 0.5  # Default score if parsing fails
    
    

    def visualize_tree(self, tree: DebateNode, filename: str):
        """Generate debate tree visualization using subprocess"""
        dot = Digraph()
        def add_nodes(node, parent_id=None):
            node_id = str(id(node))
            dot.node(node_id, node.content[:50].replace('\n', ' ') + "...")
            if parent_id:
                dot.edge(parent_id, node_id)
            for child in node.children:
                add_nodes(child, node_id)
        add_nodes(tree)

        # Save .dot file (for debugging)
        dot.save(f'outputs/{filename}.dot')
        logging.debug(f".dot file saved as outputs/{filename}.dot")

        # Render to .png using subprocess
        try:
            subprocess.run([
                'dot',
                '-Tpng',
                f'outputs/{filename}.dot',
                '-o',
                f'outputs/{filename}.png'
            ], check=True)
            logging.info(f"Visualization saved as outputs/{filename}.png")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to render {filename}.png: {str(e)}")

        def score_response(self, response: str) -> float:
            criteria = {
                'logic': 0.4,
                'evidence': 0.3,
                'persuasiveness': 0.3
            }

            analysis = self.llm.generate(
                f"""Rate this response on a scale of 1-10 for:
                1. Logical consistency
                2. Evidence quality
                3. Persuasiveness
                
                Response: {response}
                Return JSON format with keys: logic, evidence, persuasiveness"""
            )

            try:
                scores = json.loads(analysis)
                return sum(scores[k] * v for k, v in criteria.items()) / 10
            except Exception:
                return 0.5

class TheoryOfMindDebater(DebateAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.opponent_model = {
            'beliefs': [],
            'emotional_state': 'neutral',
            'argument_style': 'neutral',
            'weaknesses': []
        }

    def update_opponent_model(self, statement: str):
        analysis = self.llm.generate(
            f"""Analyze this debate statement for:
            1. Core beliefs (JSON list)
            2. Emotional state (angry/calm/defensive)
            3. Argument style (direct/emotional/technical)
            4. Logical weaknesses (list)
            
            Statement: {statement[:500]}
            Return JSON format."""
        )
        try:
            self.opponent_model.update(json.loads(analysis))
        except:
            pass

    def generate_response(self, opponent_statement: str) -> str:
        self.update_opponent_model(opponent_statement)

        strategy = {
            'angry': {'tone': 'calm', 'approach': 'acknowledge->refute'},
            'defensive': {'tone': 'supportive', 'approach': 'find common ground'},
            'calm': {'tone': 'reasoned', 'approach': 'logical rebuttal'}
        }.get(self.opponent_model['emotional_state'], {'tone': 'neutral', 'approach': 'direct'})

        prompt = f"""As {self.position} debater:
        - Opponent is feeling {self.opponent_model['emotional_state']}
        - Strategy: {strategy['approach']} (tone: {strategy['tone']})
        - Target weakness: {self.opponent_model['weaknesses'][0] if self.opponent_model['weaknesses'] else 'unknown'}

        Respond to: "{opponent_statement[:200]}"
        Use: {random.choice(self.knowledge_base)}
        Max 3 sentences."""
        
        return self.llm.generate(prompt)