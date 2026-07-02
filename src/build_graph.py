"""
build_graph.py

Builds a knowledge graph from extracted triples and exports it as GraphML

Reads triples.json with the shape {"triples": [{subject, relation, object}, ...]}.
Produces christmas_carol_stave_one_kg.graphml and prints summary statistics.

Prerequisites:
    pip install networkx
"""

import json
import sys
import networkx as nx

INPUT_FILE = "output/triples.json"
GRAPHML_FILE = "output/christmas_carol_stave_one_kg.graphml"


def load_triples(path):
    """Load triples from the JSON file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)["triples"]
    except FileNotFoundError:
        print(f"Error: {path} not found.", file=sys.stderr)
        sys.exit(1)


def build_graph(triples):
    """Build a directed multigraph. Each triple is a distinct edge, so multiple
    relations between the same two entities (for example Scrooge partner_of,
    executor_of, and friend_of Marley) are all preserved."""
    g = nx.MultiDiGraph()
    for t in triples:
        g.add_edge(t["subject"], t["object"], relation=t["relation"])
    return g


def print_summary(g):
    """Print basic graph statistics, useful for the report's evaluation section."""
    print(f"\nGraph summary:")
    print(f"  Nodes: {g.number_of_nodes()}")
    print(f"  Edges: {g.number_of_edges()}")

    # Top nodes by degree: these are the central entities.
    top = sorted(g.degree(), key=lambda x: x[1], reverse=True)[:5]
    print(f"  Most connected entities:")
    for node, deg in top:
        print(f"    {node}: {deg} connections")


def main():
    triples = load_triples(INPUT_FILE)
    g = build_graph(triples)

    # Export GraphML
    nx.write_graphml(g, GRAPHML_FILE)
    print(f"Saved graph to {GRAPHML_FILE}")

    print_summary(g)


if __name__ == "__main__":
    main()