# Analysts Evaluation Suite

Evaluation tests for the **Analysts agent** using LangSmith + openevals.

## What It Tests

The full Analysts graph including the human-in-the-loop interrupt flow:
- **Direct approval**: topic → generate analysts → approve → done
- **Feedback loop**: topic → generate → feedback → regenerate → approve → done

## Evaluators

| Evaluator | Type | What It Checks |
|-----------|------|---------------|
| `analyst_relevance` | LLM-as-judge | Are analysts relevant to the topic? |
| `feedback_incorporation` | LLM-as-judge | Did regeneration reflect human feedback? |
| `analyst_count` | Code | Count ≤ requested max_analysts |
| `schema_completeness` | Code | All fields non-empty (name, role, affiliation, description) |

## How to Run

```bash
# 1. Create the dataset in LangSmith (one-time, idempotent)
uv run python -m evaluations.analysts_dataset_builder

# 2. Run the evaluation
uv run python -m evaluations.run_analysts_evaluation
```

Results appear in [LangSmith](https://smith.langchain.com) under the `"Analysts Generation Eval"` dataset.
