from langgraph.graph import START, END, StateGraph
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain.chat_models import init_chat_model
from langgraph.types import interrupt, Command
from Analysts.state import GenerateAnalystsState
from Analysts.schemas import Perspectives
from typing import Literal

llm = init_chat_model(
    model="gpt-5-nano",
    temperature=0,
)

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
    human_analyst_feedback = state.human_analyst_feedback or ""

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


def human_feedback(
    state: GenerateAnalystsState,
) -> Command[Literal["create_analysts", END]]:
    # Pause execution; payload shows up under result["__interrupt__"]
    feedback_value = interrupt(
        {"question": "Ready to continue?", "options": ["approve", "reject"]}
    )

    # Route based on the response
    if feedback_value == "":
        return Command(goto=END)  # Runs after the resume payload is provided
    else:
        return Command(
            goto="create_analysts", update={"human_analyst_feedback": feedback_value}
        )


# Add nodes and edges


def buid_graph():
    builder = StateGraph(GenerateAnalystsState)
    builder.add_node("create_analysts", create_analysts)
    builder.add_node("human_feedback", human_feedback)
    builder.add_edge(START, "create_analysts")
    builder.add_edge("create_analysts", "human_feedback")

    # Compile
    graph = builder.compile()
    return graph


graph = buid_graph()
