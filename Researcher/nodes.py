"""Node functions for the main Researcher graph.

This module contains the core logic for orchestrating research interviews,
writing reports, and generating final research outputs.
"""

from typing import List, Dict
from langgraph.types import Send
from langchain_core.messages import HumanMessage, SystemMessage
from .state import ResearchGraphState
from .prompts import report_writer_instructions, intro_conclusion_instructions
from .configuration import llm
from .logger import get_logger, log_error

# Initialize logger for this module
logger = get_logger("Researcher.nodes")


def initiate_all_interviews(state: ResearchGraphState) -> List[Send]:
    """Map step: Initiate parallel interviews with all analysts using Send API.

    This function creates parallel interview tasks for each analyst generated
    by the analysts subgraph. Each interview runs independently via the Send API.

    Args:
        state: Current research graph state containing finalized analysts

    Returns:
        List of Send commands to start parallel interview subgraphs
    """
    try:
        topic = state.topic
        num_analysts = len(state.analysts)
        logger.info(
            f"→ Initiating interviews for {num_analysts} analysts on topic: '{topic}'"
        )

        sends = [
            Send(
                "conduct_interview",
                {
                    "analyst": analyst,
                    "messages": [
                        HumanMessage(
                            content=f"So you said you were writing an article on {topic}?"
                        )
                    ],
                },
            )
            for analyst in state.analysts
        ]

        logger.info(f"✓ Successfully created {len(sends)} interview tasks")
        return sends

    except Exception as e:
        log_error(logger, "initiate_all_interviews", e)
        raise


def write_report(state: ResearchGraphState) -> Dict[str, str]:
    """Generate the main content of the research report.

    Synthesizes all interview sections into a coherent report body.

    Args:
        state: Current research graph state with interview sections

    Returns:
        Dict with 'content' key containing the generated report content
    """
    try:
        sections = state.sections
        topic = state.topic
        logger.info(
            f"→ Writing report for topic: '{topic}' with {len(sections)} sections"
        )

        # Concatenate all sections together
        formatted_str_sections = "\n\n".join([f"{section}" for section in sections])

        # Summarize the sections into a final report
        system_message = report_writer_instructions.format(
            topic=topic, context=formatted_str_sections
        )

        logger.debug("Invoking LLM for report generation")
        report = llm.invoke(
            [SystemMessage(content=system_message)]
            + [HumanMessage(content="Write a report based upon these memos.")]
        )

        logger.info(f"✓ Generated report content ({len(report.content)} chars)")
        return {"content": report.content}

    except Exception as e:
        log_error(logger, "write_report", e)
        raise


def write_introduction(state: ResearchGraphState) -> Dict[str, str]:
    """Generate the introduction section of the research report.

    Args:
        state: Current research graph state with interview sections

    Returns:
        Dict with 'introduction' key containing the generated introduction
    """
    try:
        sections = state.sections
        topic = state.topic
        logger.info(f"→ Writing introduction for topic: '{topic}'")

        # Concatenate all sections together
        formatted_str_sections = "\n\n".join([f"{section}" for section in sections])

        # Generate introduction
        instructions = intro_conclusion_instructions.format(
            topic=topic, formatted_str_sections=formatted_str_sections
        )

        logger.debug("Invoking LLM for introduction generation")
        intro = llm.invoke(
            [instructions] + [HumanMessage(content="Write the report introduction")]
        )

        logger.info(f"✓ Generated introduction ({len(intro.content)} chars)")
        return {"introduction": intro.content}

    except Exception as e:
        log_error(logger, "write_introduction", e)
        raise


def write_conclusion(state: ResearchGraphState) -> Dict[str, str]:
    """Generate the conclusion section of the research report.

    Args:
        state: Current research graph state with interview sections

    Returns:
        Dict with 'conclusion' key containing the generated conclusion
    """
    try:
        sections = state.sections
        topic = state.topic
        logger.info(f"→ Writing conclusion for topic: '{topic}'")

        # Concatenate all sections together
        formatted_str_sections = "\n\n".join([f"{section}" for section in sections])

        # Generate conclusion
        instructions = intro_conclusion_instructions.format(
            topic=topic, formatted_str_sections=formatted_str_sections
        )

        logger.debug("Invoking LLM for conclusion generation")
        conclusion = llm.invoke(
            [instructions] + [HumanMessage(content="Write the report conclusion")]
        )

        logger.info(f"✓ Generated conclusion ({len(conclusion.content)} chars)")
        return {"conclusion": conclusion.content}

    except Exception as e:
        log_error(logger, "write_conclusion", e)
        raise


def finalize_report(state: ResearchGraphState) -> Dict[str, str]:
    """Reduce step: Combine all report sections into final output.

    Assembles the introduction, main content, conclusion, and sources
    into a complete research report.

    Args:
        state: Current research graph state with all sections generated

    Returns:
        Dict with 'final_report' key containing the complete report
    """
    try:
        logger.info("→ Finalizing report assembly")
        content = state.content

        # Clean up content formatting
        if content.startswith("## Insights"):
            content = content.strip("## Insights")
            logger.debug("Cleaned '## Insights' prefix from content")

        # Extract sources if present
        sources = None
        if "## Sources" in content:
            try:
                content, sources = content.split("\n## Sources\n")
                logger.debug("Extracted sources section from content")
            except ValueError:
                # If split fails (e.g., multiple "## Sources" sections), keep content as-is
                logger.warning(
                    "Multiple '## Sources' sections found, keeping content as-is"
                )
                pass

        # Assemble final report
        final_report = (
            state.introduction
            + "\n\n---\n\n"
            + content
            + "\n\n---\n\n"
            + state.conclusion
        )

        if sources is not None:
            final_report += "\n\n## Sources\n" + sources

        logger.info(f"✓ Finalized complete report ({len(final_report)} chars)")
        return {"final_report": final_report}

    except Exception as e:
        log_error(logger, "finalize_report", e)
        raise
