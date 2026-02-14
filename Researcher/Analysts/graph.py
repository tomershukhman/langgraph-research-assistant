from langgraph.graph import START, END, StateGraph
from langgraph.types import interrupt, Command
from langchain_core.messages import HumanMessage, SystemMessage
from .state import GenerateAnalystsState, AnalystsInput, AnalystsOutput
from .schemas import Perspectives
from ..configuration import llm
from ..logger import get_logger, log_error

# Initialize logger for this module
logger = get_logger("Analysts.graph")


analyst_instructions = """You are tasked with creating a set of AI analyst personas. Follow these instructions carefully:

1. First, review the research topic:
{topic}
        
2. Examine any editorial feedback that has been optionally provided to guide creation of the analysts: 
        
{human_analyst_feedback}
    
3. Identify the key dimensions and perspectives needed to thoroughly research this topic.
   Consider diverse viewpoints across:
   - Scientific/technical expertise (research, modeling, empirical analysis)
   - Policy and regulatory perspectives (government advisors, policy analysts)
   - Industry and implementation (practitioners, engineers, business)
   - Social and equity considerations (community impact, justice, accessibility)
                    
4. Select {max_analysts} complementary expert roles that provide broad coverage across these dimensions.
   Prioritize foundational roles (e.g., core scientists, policy experts) before specialized niches.
   
5. For each role, create a distinct analyst persona with appropriate credentials and focus area."""


def create_analysts(state: GenerateAnalystsState):
    """Create analysts"""
    try:
        topic = state.topic
        max_analysts = state.max_analysts
        human_analyst_feedback = state.human_analyst_feedback

        logger.info(f"→ Creating analysts for topic: '{topic}' (max: {max_analysts})")
        if human_analyst_feedback:
            logger.debug(f"Feedback provided: {human_analyst_feedback[:100]}...")

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

        logger.info(f"✓ Generated {len(analysts.analysts)} analysts")
        # Write the list of analysis to state
        return {"analysts": analysts.analysts}

    except Exception as e:
        log_error(logger, "create_analysts", e)
        raise


def human_feedback(state: GenerateAnalystsState):
    """Interrupt to get human feedback on the generated analysts"""
    try:
        num_analysts = len(state.analysts) if state.analysts else 0
        logger.info(f"→ Requesting human feedback on {num_analysts} analysts")

        feedback = interrupt(
            "Please review the analysts above. Provide feedback to regenerate, or approve to proceed."
        )

        if feedback:
            logger.info(f"Human feedback received: '{feedback[:100]}...'")
            return Command(
                goto="create_analysts", update={"human_analyst_feedback": feedback}
            )

        logger.info("Analysts approved, proceeding to END")
        return Command(goto=END)

    except Exception as e:
        log_error(logger, "human_feedback", e)
        raise


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
