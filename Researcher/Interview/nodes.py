"""Node functions for the Interview subgraph.

This module implements the interview process where an AI analyst asks questions,
searches for information, and generates a research section based on the findings.
"""

from typing import Dict, List
from langchain_core.messages import (
    get_buffer_string,
    AIMessage,
    HumanMessage,
    SystemMessage,
)
from .state import InterviewState
from .schemas import SearchQuery
from ..configuration import llm, EXPERT_NAME, INTERVIEW_CLOSING_PHRASE
from .prompts import (
    question_instructions,
    search_instructions,
    answer_instructions,
    section_writer_instructions,
)
from .tools import tavily_search
from langchain_community.document_loaders import WikipediaLoader
from ..logger import get_logger, log_error, log_search

# Initialize logger for this module
logger = get_logger("Interview.nodes")


def generate_question(state: InterviewState) -> Dict[str, List[AIMessage]]:
    """Generate the next interview question from the analyst.

    Args:
        state: Current interview state with analyst persona and message history

    Returns:
        Dict with 'messages' key containing the generated question
    """
    try:
        analyst = state.analyst
        messages = state.messages
        analyst_name = analyst.name if hasattr(analyst, "name") else "Unknown"
        logger.info(f"→ Generating question for analyst: {analyst_name}")

        # Generate question based on analyst's persona and conversation history
        system_message = question_instructions.format(goals=analyst.persona)
        question = llm.invoke([SystemMessage(content=system_message)] + messages)

        logger.info(f"✓ Generated question ({len(question.content)} chars)")
        return {"messages": [question]}

    except Exception as e:
        log_error(logger, "generate_question", e)
        raise


def search_web(state: InterviewState) -> Dict[str, List[str]]:
    """Retrieve documents from web search using Tavily.

    Args:
        state: Current interview state with recent messages

    Returns:
        Dict with 'context' key containing formatted search results
    """
    try:
        logger.info("→ Performing web search")

        # Extract search query from conversation
        structured_llm = llm.with_structured_output(SearchQuery)
        search_query = structured_llm.invoke([search_instructions] + state.messages)

        logger.debug(f"Search query: '{search_query.search_query}'")

        # Perform web search
        data = tavily_search.invoke({"query": search_query.search_query})
        search_docs = data.get("results", [])

        # Format results as XML-style documents
        formatted_search_docs = "\n\n---\n\n".join(
            [
                f'<Document href="{doc["url"]}"/>\n{doc["content"]}\n</Document>'
                for doc in search_docs
            ]
        )

        log_search(logger, search_query.search_query, len(search_docs))
        return {"context": [formatted_search_docs]}

    except Exception as e:
        log_error(logger, "search_web", e)
        raise


def search_wikipedia(state: InterviewState) -> Dict[str, List[str]]:
    """Retrieve documents from Wikipedia.

    Args:
        state: Current interview state with recent messages

    Returns:
        Dict with 'context' key containing formatted Wikipedia articles
    """
    try:
        logger.info("→ Performing Wikipedia search")

        # Extract search query from conversation
        structured_llm = llm.with_structured_output(SearchQuery)
        search_query = structured_llm.invoke([search_instructions] + state.messages)

        logger.debug(f"Wikipedia query: '{search_query.search_query}'")

        # Search Wikipedia
        search_docs = WikipediaLoader(
            query=search_query.search_query, load_max_docs=2
        ).load()

        # Format results as XML-style documents
        formatted_search_docs = "\n\n---\n\n".join(
            [
                f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content}\n</Document>'
                for doc in search_docs
            ]
        )

        log_search(logger, search_query.search_query, len(search_docs))
        return {"context": [formatted_search_docs]}

    except Exception as e:
        log_error(logger, "search_wikipedia", e)
        raise


def generate_answer(state: InterviewState) -> Dict[str, List[AIMessage]]:
    """Generate expert's answer to analyst's question using retrieved context.

    Args:
        state: Current interview state with analyst, messages, and search context

    Returns:
        Dict with 'messages' key containing the expert's answer
    """
    try:
        analyst = state.analyst
        messages = state.messages
        context = state.context
        analyst_name = analyst.name if hasattr(analyst, "name") else "Unknown"

        context_size = sum(len(c) for c in context) if context else 0
        logger.info(
            f"→ Generating answer for analyst: {analyst_name} (context: {context_size} chars)"
        )

        # Generate answer using retrieved context
        system_message = answer_instructions.format(
            goals=analyst.persona, context=context
        )
        answer = llm.invoke([SystemMessage(content=system_message)] + messages)

        # Tag message as coming from the expert
        answer.name = EXPERT_NAME

        logger.info(f"✓ Generated expert answer ({len(answer.content)} chars)")
        return {"messages": [answer]}

    except Exception as e:
        log_error(logger, "generate_answer", e)
        raise


def save_interview(state: InterviewState) -> Dict[str, str]:
    """Save the complete interview transcript as a string.

    Args:
        state: Current interview state with full message history

    Returns:
        Dict with 'interview' key containing the formatted transcript
    """
    try:
        logger.info("→ Saving interview transcript")
        messages = state.messages

        # Convert message history to a formatted string
        interview = get_buffer_string(messages)

        logger.info(
            f"✓ Saved interview transcript ({len(interview)} chars, {len(messages)} messages)"
        )
        return {"interview": interview}

    except Exception as e:
        log_error(logger, "save_interview", e)
        raise


def route_messages(state: InterviewState, name: str = EXPERT_NAME) -> str:
    """Route to next step: continue interview or save and finish.

    Decides whether to ask another question or end the interview based on:
    - Number of question-answer turns (max_num_turns)
    - Presence of closing phrase in conversation

    Args:
        state: Current interview state
        name: Role name to count responses for (default: expert)

    Returns:
        Next node name: 'ask_question' to continue or 'save_interview' to end
    """
    try:
        messages = state.messages
        max_num_turns = state.max_num_turns

        # Check the number of expert responses
        num_responses = len(
            [m for m in messages if isinstance(m, AIMessage) and m.name == name]
        )

        # End if expert has answered the maximum number of turns
        if num_responses >= max_num_turns:
            logger.info(
                f"→ Routing to save_interview (max turns reached: {num_responses}/{max_num_turns})"
            )
            return "save_interview"

        # Check if the last question signals end of discussion
        last_question = messages[-2]
        if INTERVIEW_CLOSING_PHRASE in last_question.content:
            logger.info("→ Routing to save_interview (closing phrase detected)")
            return "save_interview"

        logger.info(f"→ Routing to ask_question (turn {num_responses}/{max_num_turns})")
        return "ask_question"

    except Exception as e:
        log_error(logger, "route_messages", e)
        raise


def write_section(state: InterviewState) -> Dict[str, List[str]]:
    """Write the final research section based on retrieved sources.

    Args:
        state: Current interview state with context and analyst persona

    Returns:
        Dict with 'sections' key containing the written section
    """
    try:
        context = state.context
        analyst = state.analyst
        analyst_name = analyst.name if hasattr(analyst, "name") else "Unknown"

        logger.info(f"→ Writing section for analyst: {analyst_name}")

        # Generate section using retrieved sources and analyst focus
        system_message = section_writer_instructions.format(focus=analyst.description)
        section = llm.invoke(
            [SystemMessage(content=system_message)]
            + [
                HumanMessage(
                    content=f"Use this source to write your section: {context}"
                )
            ]
        )

        logger.info(f"✓ Generated section ({len(section.content)} chars)")
        return {"sections": [section.content]}

    except Exception as e:
        log_error(logger, "write_section", e)
        raise
