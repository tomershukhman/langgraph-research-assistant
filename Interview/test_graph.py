import sys
import os

# Add the project root to sys.path to allow imports from Interview
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

load_dotenv()

try:
    from Interview.graph import graph

    print("Graph compiled successfully.")

    # Optional: Print the graph structure or visual
    # print(graph.get_graph().draw_ascii())
    print(f"Graph built: {graph}")

except Exception as e:
    print(f"Error compiling graph: {e}")
    sys.exit(1)
