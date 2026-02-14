"""
Programmatically creates the LangSmith dataset for evaluating the Analysts agent.

Dataset: "Analysts Generation Eval"
Each example simulates a full agent run including human-in-the-loop feedback.

Inputs match AnalystsInput state: {topic, max_analysts, human_feedback}
Outputs match AnalystsOutput state: {analysts: [{name, role, affiliation, description}, ...]}
"""

from dotenv import load_dotenv
from langsmith import Client
from Researcher.Analysts.schemas import Analyst

load_dotenv()


DATASET_NAME = "Analysts Generation Eval"
DATASET_DESCRIPTION = (
    "Evaluation dataset for the Analysts agent. "
    "Tests analyst generation across diverse topics with and without human feedback."
)


# Helper function to create examples with proper Pydantic serialization
def create_example(
    topic: str, max_analysts: int, human_feedback: str | None, analysts: list[Analyst]
):
    """Create an example with inputs and outputs using Pydantic models."""
    return {
        "inputs": {
            "topic": topic,
            "max_analysts": max_analysts,
            "human_feedback": human_feedback,
        },
        "outputs": {"analysts": [analyst.model_dump() for analyst in analysts]},
    }


# Each example defines inputs (topic + feedback scenario) and expected output structure.
# human_feedback=None means approve immediately; a string means provide feedback then approve.
# The reference outputs follow the AnalystsOutput schema: {analysts: List[Analyst]}
EXAMPLES = [
    create_example(
        topic="The impact of AI on healthcare",
        max_analysts=3,
        human_feedback=None,
        analysts=[
            Analyst(
                name="Dr. Sarah Chen",
                role="Medical AI Researcher",
                affiliation="Stanford Medical School",
                description="Focuses on AI applications in diagnostics and patient care, concerned with accuracy and patient safety.",
            ),
            Analyst(
                name="James Morrison",
                role="Healthcare Policy Analyst",
                affiliation="World Health Organization",
                description="Examines regulatory frameworks and ethical implications of AI adoption in healthcare systems.",
            ),
            Analyst(
                name="Dr. Aisha Patel",
                role="Clinical Data Scientist",
                affiliation="Mayo Clinic",
                description="Specializes in leveraging health data and AI for predictive analytics and personalized medicine.",
            ),
        ],
    ),
    create_example(
        topic="Climate change and renewable energy policy",
        max_analysts=2,
        human_feedback=None,
        analysts=[
            Analyst(
                name="Dr. Elena Vasquez",
                role="Climate Scientist",
                affiliation="IPCC",
                description="Researches climate modeling and the scientific basis for renewable energy transitions.",
            ),
            Analyst(
                name="Marcus Thompson",
                role="Energy Policy Advisor",
                affiliation="International Energy Agency",
                description="Advises governments on renewable energy policy design and implementation strategies.",
            ),
        ],
    ),
    create_example(
        topic="Cybersecurity threats in the financial sector",
        max_analysts=3,
        human_feedback="Focus more on insider threats and social engineering",
        analysts=[
            Analyst(
                name="Rachel Kim",
                role="Insider Threat Analyst",
                affiliation="JP Morgan Chase",
                description="Specializes in detecting and preventing insider threats within financial institutions.",
            ),
            Analyst(
                name="David Okonkwo",
                role="Social Engineering Expert",
                affiliation="SANS Institute",
                description="Researches social engineering attack vectors targeting financial sector employees and customers.",
            ),
            Analyst(
                name="Dr. Lisa Wang",
                role="Financial Cybersecurity Researcher",
                affiliation="MIT Lincoln Laboratory",
                description="Studies the intersection of human factors and technical vulnerabilities in banking systems.",
            ),
        ],
    ),
    create_example(
        topic="The future of remote work and digital collaboration",
        max_analysts=2,
        human_feedback="Include a perspective from developing countries",
        analysts=[
            Analyst(
                name="Priya Sharma",
                role="Digital Workforce Researcher",
                affiliation="Indian Institute of Management",
                description="Studies remote work adoption and digital infrastructure challenges in developing economies.",
            ),
            Analyst(
                name="Carlos Mendes",
                role="Collaboration Technology Analyst",
                affiliation="Gartner",
                description="Evaluates digital collaboration tools and their impact on global workforce productivity.",
            ),
        ],
    ),
    create_example(
        topic="Quantum computing and its implications for cryptography",
        max_analysts=2,
        human_feedback=None,
        analysts=[
            Analyst(
                name="Dr. Michael Zhang",
                role="Quantum Computing Researcher",
                affiliation="IBM Research",
                description="Focuses on quantum algorithm development and near-term quantum computing applications.",
            ),
            Analyst(
                name="Dr. Anna Kowalski",
                role="Post-Quantum Cryptographer",
                affiliation="NIST",
                description="Works on developing cryptographic standards resistant to quantum computing attacks.",
            ),
        ],
    ),
]


def create_dataset():
    """Create or update the Analysts evaluation dataset in LangSmith."""
    client = Client()

    # Check if dataset already exists
    existing = list(client.list_datasets(dataset_name=DATASET_NAME))
    if existing:
        print(
            f"Dataset '{DATASET_NAME}' already exists (id={existing[0].id}). Skipping creation."
        )
        print("Delete it in LangSmith UI if you want to recreate it.")
        return existing[0]

    # Create the dataset
    dataset = client.create_dataset(
        dataset_name=DATASET_NAME,
        description=DATASET_DESCRIPTION,
    )
    print(f"Created dataset '{DATASET_NAME}' (id={dataset.id})")

    # Add examples
    client.create_examples(
        dataset_id=dataset.id,
        examples=EXAMPLES,
    )
    print(f"Added {len(EXAMPLES)} examples to dataset")

    return dataset


if __name__ == "__main__":
    create_dataset()
