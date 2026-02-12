"""Verify that all three graphs have correct input/output schemas configured."""

from dotenv import load_dotenv

load_dotenv()

from Resercher.Analysts.graph import graph as analysts_graph
from Resercher.Analysts.state import (
    AnalystsInput,
    AnalystsOutput,
    GenerateAnalystsState,
)
from Resercher.Interview.graph import graph as interview_graph
from Resercher.Interview.state import InterviewInput, InterviewOutput, InterviewState
from Resercher.graph import graph as researcher_graph
from Resercher.state import ResearchInput, ResearchOutput, ResearchGraphState


def check_graph(name, graph, expected_input, expected_output):
    """Check a graph has the right input/output schemas."""
    input_channels = (
        set(graph.config_specs[0].annotation.__annotations__.keys())
        if graph.config_specs
        else None
    )

    # Check input schema
    input_schema = graph.get_input_jsonschema()
    output_schema = graph.get_output_jsonschema()

    input_props = set(input_schema.get("properties", {}).keys())
    output_props = set(output_schema.get("properties", {}).keys())

    expected_in_fields = set(expected_input.model_fields.keys())
    expected_out_fields = set(expected_output.model_fields.keys())

    ok = True
    if input_props != expected_in_fields:
        print(f"  ❌ Input mismatch: got {input_props}, expected {expected_in_fields}")
        ok = False
    else:
        print(f"  ✅ Input schema: {input_props}")

    if output_props != expected_out_fields:
        print(
            f"  ❌ Output mismatch: got {output_props}, expected {expected_out_fields}"
        )
        ok = False
    else:
        print(f"  ✅ Output schema: {output_props}")

    return ok


print("=" * 50)
print("Schema Verification")
print("=" * 50)

all_ok = True

print("\n📋 Analysts Subgraph:")
all_ok &= check_graph("Analysts", analysts_graph, AnalystsInput, AnalystsOutput)

print("\n🎙️ Interview Subgraph:")
all_ok &= check_graph("Interview", interview_graph, InterviewInput, InterviewOutput)

print("\n🔬 Main Researcher Graph:")
all_ok &= check_graph("Researcher", researcher_graph, ResearchInput, ResearchOutput)

print("\n" + "=" * 50)
if all_ok:
    print("✅ All schemas verified successfully!")
else:
    print("❌ Some schema checks failed!")
print("=" * 50)
