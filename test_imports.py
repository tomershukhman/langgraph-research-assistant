try:
    from Analysts.graph import graph

    print("Analysts graph loaded successfully")
except Exception as e:
    print(f"Failed to load Analysts graph: {e}")

try:
    from Interview.graph import graph

    print("Interview graph loaded successfully")
except Exception as e:
    print(f"Failed to load Interview graph: {e}")
