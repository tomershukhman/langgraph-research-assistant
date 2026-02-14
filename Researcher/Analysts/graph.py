from langgraph.graph import START, END, StateGraph
from langgraph.types import interrupt, Command
from langchain_core.messages import HumanMessage, SystemMessage
from .state import GenerateAnalystsState, AnalystsInput, AnalystsOutput
from .schemas import Perspectives
from ..configuration import llm


analyst_instructions = """You are tasked with creating a set of AI analyst personas. Follow these instructions carefully:

1. First, review the research topic:
{topic}
        
2. Examine any editorial feedback that has been optionally provided to guide creation of the analysts: 
        
{human_analyst_feedback}
    
3. Determine the most interesting themes based upon documents and / or feedback above.
                    
4. Pick the top {max_analysts} themes.

5. Assign one analyst to each theme."""


def create_analysts(state: GenerateAnalystsState):
    """Create analysts"""

    topic = state.topic
    max_analysts = state.max_analysts
    human_analyst_feedback = state.human_analyst_feedback

    # Enforce structured output
    structured_llm = llm.with_structured_output(Perspectives)

    # System message
    system_message = analyst_instructions.format(
        topic=topic,
        human_analyst_feedback=human_analyst_feedback,
        max_analysts=max_analysts,
    )

    # Generate question
    analysts = structured_llm.invoke(
        [SystemMessage(content=system_message)]
        + [HumanMessage(content="Generate the set of analysts.")]
    )

    # Write the list of analysis to state
    return {"analysts": analysts.analysts}


def human_feedback(state: GenerateAnalystsState):
    """Interrupt to get human feedback on the generated analysts"""
    feedback = interrupt(
        "Please review the analysts above. Provide feedback to regenerate, or approve to proceed."
    )
    if feedback:
        return Command(
            goto="create_analysts", update={"human_analyst_feedback": feedback}
        )
    return Command(goto=END)


# Add nodes and edges
builder = StateGraph(
    GenerateAnalystsState, input_schema=AnalystsInput, output_schema=AnalystsOutput
)
builder.add_node("create_analysts", create_analysts)
builder.add_node("human_feedback", human_feedback)
builder.add_edge(START, "create_analysts")
builder.add_edge("create_analysts", "human_feedback")
builder.add_edge("human_feedback", END)

# Compile the graph
graph = builder.compile()
