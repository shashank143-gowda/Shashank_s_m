"""Generates diagrams/chatbot_architecture.png"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(figsize=(11, 6.5))
ax.set_xlim(0, 11); ax.set_ylim(0, 6.5); ax.axis('off')

def box(x, y, w, h, text, color):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.05',
                                fc=color, ec='#333', lw=1.2))
    ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=9.5)

def arrow(x1, y1, x2, y2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', lw=1.4, color='#333'))

ax.text(5.5, 6.25, 'LLM Chatbot: High-Level Architecture', ha='center',
        fontsize=14, fontweight='bold')

box(0.2, 3.0, 1.6, 1.0, 'User\n(web / mobile\n/ Slack)', '#cfe8ff')
box(2.3, 3.0, 1.7, 1.0, 'Backend API\n(auth, sessions,\nrate limits)', '#d9f2d9')
box(4.5, 3.0, 2.0, 1.0, 'Orchestrator\n(controls the flow)', '#ffe9b3')
box(7.0, 3.0, 1.7, 1.0, 'Prompt builder\n(system prompt +\ncontext + history)', '#ffe9b3')
box(9.1, 3.0, 1.7, 1.0, 'LLM\n(GPT / Claude /\nLlama)', '#f4c7c3')

arrow(1.8, 3.5, 2.3, 3.5); arrow(4.0, 3.5, 4.5, 3.5)
arrow(6.5, 3.5, 7.0, 3.5); arrow(8.7, 3.5, 9.1, 3.5)

# supporting components under the orchestrator
box(2.3, 0.9, 2.0, 1.3, 'Retriever\n(RAG)\nembed question,\nsearch', '#e6d9f2')
box(4.7, 0.9, 1.8, 1.3, 'Vector database\n(document chunks\n+ metadata)', '#e6d9f2')
box(6.9, 0.9, 1.6, 1.3, 'Memory\n(chat history,\nuser profile)', '#e6d9f2')
box(8.9, 0.9, 1.9, 1.3, 'Tools / APIs\n(search, SQL,\ncalculator)', '#e6d9f2')
arrow(5.5, 3.0, 3.6, 2.2); arrow(4.3, 1.55, 4.7, 1.55)
arrow(5.8, 3.0, 7.5, 2.2); arrow(6.0, 3.0, 9.4, 2.2)

# top: guardrails and monitoring
box(4.5, 4.7, 2.0, 0.9, 'Guardrails\n(input/output safety, PII)', '#ffd6d6')
box(7.0, 4.7, 3.8, 0.9, 'Monitoring and evaluation\n(logs, latency, cost, feedback)', '#e0e0e0')
arrow(5.5, 4.0, 5.5, 4.7)
ax.text(5.5, 0.35, 'Offline pipeline: documents -> clean -> chunk -> embed -> store in vector database',
        ha='center', fontsize=9.5, style='italic')
plt.tight_layout()
plt.savefig('../diagrams/chatbot_architecture.png', dpi=150)
