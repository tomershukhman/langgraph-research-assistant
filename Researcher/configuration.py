"""
Centralized configuration for the Researcher application.

This module provides shared configuration and LLM instances used across
all subgraphs to ensure consistency and avoid duplicate initialization.
"""

import os
from langchain.chat_models import init_chat_model

# LLM Configuration
# Model can be overridden via RESEARCHER_MODEL env var
DEFAULT_MODEL = "gpt-5-nano"
DEFAULT_TEMPERATURE = 0

model_name = os.getenv("RESEARCHER_MODEL", DEFAULT_MODEL)
temperature = float(os.getenv("RESEARCHER_TEMPERATURE", str(DEFAULT_TEMPERATURE)))

# Shared LLM instance used across all subgraphs
llm = init_chat_model(
    model=model_name,
    temperature=temperature,
)

# Interview Constants
EXPERT_NAME = "expert"
INTERVIEW_CLOSING_PHRASE = "Thank you so much for your help"

# Analysts Constants
DEFAULT_MAX_ANALYSTS = 2
MIN_ANALYSTS = 1
MAX_ANALYSTS = 10

# Interview Defaults
DEFAULT_MAX_TURNS = 2
MIN_TURNS = 1
MAX_TURNS = 20
