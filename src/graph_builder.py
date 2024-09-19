import os
import pickle
import networkx as nx
import matplotlib.pyplot as plt
from src.crawler import ADJESENT_EDGES_URL


COLOR = ['cyan', 'orange', 'yellow', 'pink']


def draw_graph():
    G = nx.DiGraph(directed=True)
    plt.figure(figsize=(8, 8))
    path = os.path.join(os.getcwd(), ADJESENT_EDGES_URL)

    color_map = dict()

    with open(path, 'rb') as f:
        edge_groups = pickle.load(f)
    for i, edges in enumerate(edge_groups.values()):
        G.add_edges_from(edges)
        for v1, v2 in edges:
            color_map[v1] = COLOR[i % len(COLOR)]
            color_map[v2] = COLOR[i % len(COLOR)]
    size_map = {start_vertixes: 300 for start_vertixes in edge_groups.keys()}
    edge_colors = {start_vertixes: 'purple' for start_vertixes in edge_groups.keys()}
    pos = nx.spring_layout(G, scale=8)
    nx.draw(G, pos, node_color=[color_map.get(node, 'gray') for node in G.nodes()],
            node_size=[size_map.get(node, 70) for node in G.nodes],
            edgecolors=[edge_colors.get(node, 'black') for node in G.nodes()],
            with_labels=True,
            arrows=True, font_size=5)
    #print('asdf')
    plt.show()