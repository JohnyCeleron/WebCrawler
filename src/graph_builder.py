import os
import pickle
import networkx as nx
import matplotlib.pyplot as plt
from src.crawler import ADJESENT_EDGES_URL


def draw_graph():
    G = nx.DiGraph(directed=True)
    plt.figure(figsize=(8, 8))
    path = os.path.join(os.getcwd(), ADJESENT_EDGES_URL)
    with open(path, 'rb') as f:
        edges = pickle.load(f)
    G.add_edges_from(edges)
    pos = nx.spring_layout(G, scale=10)
    nx.draw(G, pos, with_labels=True, arrows=True, font_size=6)
    plt.show()