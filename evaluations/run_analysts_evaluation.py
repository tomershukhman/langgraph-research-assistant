"""
Runs LangSmith evaluation for the Analysts agent.

Tests the full agent graph including the human-in-the-loop interrupt flow.
Uses openevals built-in LLM-as-judge evaluators and code-based evaluators.
"""

import uuid
from dotenv import load_dotenv

load_dotenv()  # Must load env vars before importing graph (LLM init at import time)

from langsmith import Client
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from openevals.llm import create_llm_as_judge
from openevals.prompts import ANSWER_RELEVANCE_PROMPT, CORRECTNESS_PROMPT

from Researcher.Analysts.graph import builder
from evaluations.analysts_dataset_builder import DATASET_NAME

MODEL = "gpt-5"

# ---------------------------------------------------------------------------
# Target function: runs the full Analysts agent graph
# ---------------------------------------------------------------------------


def run_analysts_agent(inputs: dict) -> dict:
    """
    Run the full Analysts graph with human-in-the-loop handling.

    The graph uses interrupt() to pause for human feedback.
    We handle this by:
    1. Invoking the graph (pauses at interrupt)
    2. Resuming with feedback if provided, then approving
    3. Or resuming with None to approve immediately
    """
    # Compile with checkpointer to support interrupts
    checkpointer = MemorySaver()
    graph = builder.compile(checkpointer=checkpointer)

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    # Prepare agent input (matches AnalystsInput schema)
    agent_input = {
        "topic": inputs["topic"],
    }
    if inputs.get("max_analysts"):
        agent_input["max_analysts"] = inputs["max_analysts"]

    # First invocation - runs create_analysts, then pauses at interrupt
    graph.invoke(agent_input, config=config)

    human_feedback = inputs.get("human_feedback")

    if human_feedback:
        # Resume with feedback string -> loops back to create_analysts -> pauses again
        graph.invoke(Command(resume=human_feedback), config=config)
        # Now approve (resume with empty string) -> goes to END
        result = graph.invoke(Command(resume=""), config=config)
    else:
        # Approve immediately (resume with empty string) -> goes to END
        result = graph.invoke(Command(resume=""), config=config)

    # Serialize Pydantic Analyst objects to dicts for JSON compatibility
    result["analysts"] = [a.model_dump() for a in result["analysts"]]
    return result


# ---------------------------------------------------------------------------
# Evaluators
# ---------------------------------------------------------------------------

# 1. LLM-as-judge: Are the analysts relevant to the topic?
relevance_evaluator = create_llm_as_judge(
    prompt=ANSWER_RELEVANCE_PROMPT,
    feedback_key="analyst_relevance",
    model=MODEL,
)



# 3. Code-based: Check analyst count
def analyst_count_evaluator(
    inputs: dict, outputs: dict, reference_outputs: dict
) -> dict:
    """Check that the number of generated analysts does not exceed max_analysts."""
    max_analysts = inputs.get("max_analysts", 3)
    analysts = outputs.get("analysts", [])
    actual_count = len(analysts)
    passed = actual_count <= max_analysts

    return {
        "key": "analyst_count",
        "score": int(passed),
        "comment": f"Generated {actual_count} analysts (max: {max_analysts}). {'Pass' if passed else 'FAIL: exceeded max'}",
    }


# 4. Code-based: Check schema completeness
def schema_completeness_evaluator(
    inputs: dict, outputs: dict, reference_outputs: dict
) -> dict:
    """Verify each analyst has all required non-empty fields."""
    analysts = outputs.get("analysts", [])
    required_fields = ["name", "role", "affiliation", "description"]

    if not analysts:
        return {
            "key": "schema_completeness",
            "score": 0,
            "comment": "No analysts generated",
        }

    issues = []
    for i, analyst in enumerate(analysts):
        for field in required_fields:
            value = analyst.get(field, "")
            if not value or not str(value).strip():
                issues.append(f"Analyst {i}: missing '{field}'")

    passed = len(issues) == 0
    return {
        "key": "schema_completeness",
        "score": int(passed),
        "comment": "All fields present" if passed else f"Issues: {'; '.join(issues)}",
    }


# ---------------------------------------------------------------------------
# Run evaluation
# ---------------------------------------------------------------------------


def run_evaluation():
    """Execute the full evaluation against the Analysts dataset."""
    client = Client()

    # Determine which evaluators to use based on each example
    evaluators = [
        relevance_evaluator,
        analyst_count_evaluator,
        schema_completeness_evaluator,
    ]

    results = client.evaluate(
        run_analysts_agent,
        data=DATASET_NAME,
        evaluators=evaluators,
        experiment_prefix="analysts-full-eval",
        description="Full Analysts agent evaluation with human-in-the-loop testing",
        max_concurrency=2,
    )

    print("\n=== Evaluation Complete ===")
    print(f"View results in LangSmith UI under dataset: '{DATASET_NAME}'")
    return results


if __name__ == "__main__":
    run_evaluation()
