# Two-Agent Debate System with Rehearsal Trees and Cognitive Extension

## Overview
This project implements a structured two-agent debate system using rehearsal trees and theory-of-mind modeling. The goal is to simulate strategic argumentation between two AI agents and evaluate how cognitive modeling improves persuasive reasoning.

## 📽️ Watch the Presentation Video
[![Watch on YouTube](https://img.youtube.com/vi/3Fl0287ug4s/0.jpg)](https://youtu.be/3Fl0287ug4s)
Click the thumbnail above or use this link: [https://youtu.be/3Fl0287ug4s](https://youtu.be/3Fl0287ug4s)

## Methodology
### Rehearsal Trees
Agents build trees of potential responses before answering. Each node is scored based on logical consistency, evidence, and persuasiveness.

### Theory of Mind Enhancement
The enhanced agent models emotional states and argument styles of its opponent, adapting tone and strategy accordingly.

## Theoretical Foundation

- [Rehearsal Trees Paper](https://arxiv.org/abs/2505.14886 )
- [Theory of Mind](https://www.sciencedirect.com/science/article/pii/S0010027718303423 )
- [Emotional Intelligence](https://psycnet.apa.org/record/1997-04519-000 )

## Assumptions

- Simulated knowledge base instead of real-world sources
- Model limitations due to Phi-3 capabilities
- Fixed tree depth/breadth

## Evaluation

- Qualitative comparison of debate transcripts
- Tree visualization showing planned reasoning paths
- Scoring of responses via LLM evaluation prompts

## Future Work

- Real-time user input integration
- Reinforcement learning for adaptive strategies
- Multimodal interaction support

## How to Run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
2. Install Graphviz: https://graphviz.org/download/ 
3. Add Graphviz/bin to PATH
4. Run: `python run_debate.py`

## Dependencies
- Ollama (phi3:instruct)
- graphviz
