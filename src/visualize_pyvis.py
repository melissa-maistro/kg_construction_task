"""
visualize_pyvis.py

Renders the knowledge graph as an interactive HTML page using pyvis.
Unlike a static image, this keeps every parallel edge separate (the several
Scrooge-Marley relations curve apart) and shows each relation on hover.

Parallel edges are split above and below the line (alternating curve direction)
and the relation is shown on hover rather than stacked on the edge, so the
labels do not overlap. Open the HTML in a browser, drag nodes apart if you want
more separation, then screenshot for the report or show it live.

Prerequisites:
    pip install pyvis networkx
"""

import networkx as nx
from pyvis.network import Network

GRAPHML_FILE = "output/christmas_carol_stave_one_kg.graphml"
OUTPUT_HTML = "output/christmas_carol_stave_one_kg.html"


def main():
    # Read the multigraph. force_multigraph=True keeps parallel edges separate
    # instead of collapsing the several Scrooge-Marley relations into one.
    g = nx.read_graphml(GRAPHML_FILE, force_multigraph=True)

    net = Network(
        height="800px",
        width="100%",
        directed=True,
        bgcolor="#ffffff",
        font_color="#222222",
    )

    # Size nodes by degree so the hubs (Scrooge, Marley, chain) stand out.
    degrees = dict(g.degree())

    for node in g.nodes():
        deg = degrees[node]
        net.add_node(
            node,
            label=node,
            size=10 + deg * 4,        # scale node size with degree
            title=f"{node} (degree {deg})",
        )

    # Add each edge separately. Give each parallel edge its own roundness so the
    # several Scrooge-Marley relations fan out individually instead of overlapping.
    # Track how many edges we have already drawn between each node pair.
    from collections import defaultdict
    pair_count = defaultdict(int)

    for u, v, data in g.edges(data=True):
        rel = data.get("relation", "")
        k = pair_count[(u, v)]
        pair_count[(u, v)] += 1
        # alternate side, and increase roundness for each successive parallel edge
        direction = "curvedCW" if k % 2 == 0 else "curvedCCW"
        roundness = 0.15 + 0.13 * (k // 2)   # 0.15, 0.15, 0.28, 0.28, 0.41, ...
        net.add_edge(u, v, label=rel, title=rel, smooth={"type": direction, "roundness": roundness})

    # Physics spreads the nodes out. No global "smooth" here because it is set
    # per-edge above.
    net.set_options("""
    {
      "physics": {
        "barnesHut": { "gravitationalConstant": -9000, "springLength": 180 },
        "minVelocity": 0.75
      },
      "edges": {
        "color": { "color": "#888888" },
        "arrows": { "to": { "enabled": true, "scaleFactor": 0.6 } }
      },
      "nodes": {
        "font": { "size": 14, "bold": true },
        "color": { "background": "#f4a259", "border": "#d17a30" }
      }
    }
    """)

    net.write_html(OUTPUT_HTML, notebook=False)
    print(f"Wrote {OUTPUT_HTML}. Open it in a browser.")


if __name__ == "__main__":
    main()