import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox
from geopy.distance import geodesic

G = ox.graph_from_place("Montreal, Quebec, Canada", network_type="drive", simplify=True)

def make_graph_eulerian(G):
    
    odd_nodes = [node for node, degree in G.degree() if degree % 2 != 0]
    
    while odd_nodes:
        node = odd_nodes.pop(0)
        min_distance = float('inf')
        closest_node = None

        x = (G.nodes[node]['y'], G.nodes[node]['x'])

        for i in odd_nodes:
            y = (G.nodes[i]['y'], G.nodes[i]['x'])
            dist = geodesic(x, y).kilometers
            if dist < min_distance:
                min_distance = dist
                closest_node = i

        if closest_node is not None:
            G.add_edge(node, closest_node, length=min_distance)
            odd_nodes.remove(closest_node)


def Chinese_postman(G):

    G = G.to_undirected()

    # La fonction native de networkx ne fonctionne pas ici, on utilise donc la notre   
    make_graph_eulerian(G)

    eulerian_circuit = list(nx.eulerian_circuit(G))

    nodes = [node for node, _ in eulerian_circuit]

    fig, ax = ox.plot_graph(G, show=False, close=False)
    ox.plot_graph_route(G, nodes, route_linewidth=2, route_color='r', ax=ax)

#Prend pres d'une heure sur les pc corrects de l'ecole, armez vous de patience
Chinese_postman(G)


