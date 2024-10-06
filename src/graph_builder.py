import os
import pickle
import random

import networkx as nx
import plotly.graph_objects as go
import plotly.offline as py

from src.metadata_controller import ADJESENT_EDGES_URL
from src.settings_constants import get_constants

settings_constants = get_constants()

NODE_SIZE = settings_constants.NODE_SIZE
START_NODE_SIZE = settings_constants.START_NODE_SIZE
ARROW_HEAD = settings_constants.ARROW_HEAD
ARROW_SIZE = settings_constants.ARROW_SIZE
ARROW_WIDTH = settings_constants.ARROW_WIDTH

COLOR = ['cyan', 'orange', 'yellow', 'pink']


def draw_graph():
    G = nx.DiGraph(directed=True)
    fig = go.Figure()

    edge_groups = _load_graph()
    color_map = {}
    node_pos = dict()
    for i, edges in enumerate(edge_groups.values()):
        for v1, v2 in edges:
            color_map[v1] = COLOR[i % len(COLOR)]
            color_map[v2] = COLOR[i % len(COLOR)]
            if v2 not in node_pos:
                v2_pos = (random.random(), random.random())
                node_pos[v2] = v2_pos
            G.add_node(v2, pos=node_pos[v2])

            if v1 is None:
                continue

            if v1 not in node_pos:
                v1_pos = (random.random(), random.random())
                node_pos[v1] = v1_pos
            G.add_node(v1, pos=node_pos[v1])
            fig.add_annotation(ax=node_pos[v1][0], ay=node_pos[v1][1],
                               x=node_pos[v2][0], y=node_pos[v2][1],
                               axref='x', ayref='y', xref='x', yref='y',
                               arrowwidth=ARROW_WIDTH, arrowcolor="black",
                               arrowsize=ARROW_SIZE, showarrow=True, arrowhead=ARROW_HEAD, )
            G.add_edge(v1, v2)

    size_map = {start_vertices: START_NODE_SIZE for start_vertices in edge_groups.keys()}
    pos = nx.get_node_attributes(G, 'pos')
    edge_trace = _get_edge_trace(G, pos)
    node_trace = _get_node_trace(G, color_map, pos, size_map)
    _customize_layout(edge_trace, fig, node_trace)

    output_file_path = 'graph.html'
    py.plot(fig, filename=output_file_path, auto_open=False)

    print(f"Граф сохранен в файл: {os.path.abspath(output_file_path)}.")


def _customize_layout(edge_trace, fig, node_trace):
    fig.add_trace(edge_trace)
    fig.add_trace(node_trace)
    fig.update_layout(
        title='<br>WebCrawler Network',
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )


def _get_edge_trace(G, pos):
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')
    return edge_trace


def _get_node_trace(G, color_map, pos, size_map):
    node_x = []
    node_y = []
    for node, (x, y) in pos.items():
        node_x.append(x)
        node_y.append(y)
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            color=[],
            size=10
        ),
        line_width=2)
    node_trace.text = [node for node in G.nodes]
    node_trace.marker.size = [size_map.get(node, NODE_SIZE) for node in G.nodes]
    node_trace.marker.color = [color_map[node] for node in G.nodes]
    return node_trace


def _load_graph():
    path = os.path.join(os.getcwd(), ADJESENT_EDGES_URL)
    with open(path, 'rb') as f:
        edge_groups = pickle.load(f)
    return edge_groups