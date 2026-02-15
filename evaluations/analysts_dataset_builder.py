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


def sync_dataset(dataset_name: str, local_examples: list[dict], delete_obsolete: bool = True):
    """
    Syncs a local list of examples to LangSmith.
    - Creates new examples.
    - Updates existing examples (if inputs/outputs changed).
    - Deletes remote examples that are no longer in the local list.
    """
    client = Client()

    # 1. Get or Create Dataset
    if client.has_dataset(dataset_name=dataset_name):
        dataset = client.read_dataset(dataset_name=dataset_name)
        print(f"🔹 Found dataset '{dataset_name}' (ID: {dataset.id})")
    else:
        dataset = client.create_dataset(dataset_name=dataset_name)
        print(f"🔹 Created dataset '{dataset_name}' (ID: {dataset.id})")

    # 2. Fetch Remote Data & Index by Key
    # Assumes 'topic' is the unique key in inputs. Change if needed.
    remote_examples = list(client.list_examples(dataset_id=dataset.id))
    remote_map = {r.inputs["topic"]: r for r in remote_examples}
    
    local_map = {e["inputs"]["topic"]: e for e in local_examples}
    
    # 3. Determine Actions
    local_topics = set(local_map.keys())
    remote_topics = set(remote_map.keys())

    to_create = local_topics - remote_topics
    to_update = local_topics & remote_topics
    to_delete = remote_topics - local_topics

    print(f"Syncing: {len(to_create)} to create, {len(to_update)} to check/update, {len(to_delete)} to delete.")

    # 4. Execute Actions
    
    # A) CREATE (Batch)
    if to_create:
        batch_create = [local_map[topic] for topic in to_create]
        client.create_examples(dataset_id=dataset.id, examples=batch_create)
        print(f"✅ Created {len(batch_create)} new examples.")

    # B) UPDATE (Iterative check to minimize API calls)
    updates_count = 0
    for topic in to_update:
        local_ex = local_map[topic]
        remote_ex = remote_map[topic]

        # Only update if content actually changed
        if (local_ex["inputs"] != remote_ex.inputs or 
            local_ex["outputs"] != remote_ex.outputs):
            
            client.update_example(
                example_id=remote_ex.id,
                inputs=local_ex["inputs"],
                outputs=local_ex["outputs"]
            )
            updates_count += 1
            print(f"   Updated: {topic}")
    
    if updates_count == 0 and to_update:
        print("   (No existing examples needed updates)")

    # C) DELETE (Batch)
    if delete_obsolete and to_delete:
        # Note: client.delete_examples takes a list of IDs
        ids_to_delete = [remote_map[topic].id for topic in to_delete]
        client.delete_examples(example_ids=ids_to_delete)
        print(f"🗑️ Deleted {len(ids_to_delete)} obsolete examples.")


if __name__ == "__main__":
    sync_dataset(DATASET_NAME, EXAMPLES)
