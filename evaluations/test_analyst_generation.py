"""
Quick test to verify improved analyst generation.
Tests the failing example: "Climate change and renewable energy policy"
"""

import uuid
from dotenv import load_dotenv

load_dotenv()

from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from Researcher.Analysts.graph import builder

# Compile with checkpointer to support interrupts
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

# Test the failing example
inputs = {
    "topic": "Climate change and renewable energy policy",
    "max_analysts": 2,
}

thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id}}

print("Testing analyst generation with improved prompt...")
print(f"Topic: {inputs['topic']}")
print(f"Max analysts: {inputs['max_analysts']}")
print("\n" + "=" * 80 + "\n")

# Run first time (will pause at interrupt)
graph.invoke(inputs, config=config)

# Approve immediately (no feedback)
result = graph.invoke(Command(resume=""), config=config)

print("\nGenerated Analysts:")
print("-" * 80)
for i, analyst in enumerate(result["analysts"], 1):
    print(f"\n{i}. {analyst.name}")
    print(f"   Role: {analyst.role}")
    print(f"   Affiliation: {analyst.affiliation}")
    print(f"   Description: {analyst.description}")

print("\n" + "=" * 80)
print("\nExpected diversity:")
print("✓ Should include climate science/modeling perspective")
print("✓ Should include energy policy/regulatory perspective")
print("\nActual roles generated:")
for analyst in result["analysts"]:
    print(f"  - {analyst.role}")
