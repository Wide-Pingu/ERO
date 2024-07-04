import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox
from collections import deque

def lengthGraph(G):
    res = 0.0
    for _, _, data in G.edges(data=True):
        res += data['length'] / 1000.0
    return res

def find_color(arg, tuple_list):
    for i in range(len(tuple_list)):
        if arg == tuple_list[i][0]:
            return i
    return -1

def getLengths(G):
    res = {}
    for u, v, key, data in G.edges(keys=True, data=True):
        res[(u, v, key)] = data.get('length', None)
    return res

def chooseSources(G, i):
    centrality = nx.degree_centrality(G)
    res = sorted(centrality, key=centrality.get, reverse=True)
    return res[:i]

def draw_graph(G, pos, edges_c):
    plt.figure(figsize=(7, 7))
    nx.draw(G, pos, with_labels=False, node_size=30, node_color="black")
    edges = list(edges_c.keys())
    colors = [edges_c[edge][0] for edge in edges]
    nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color=colors, arrows=False)
    plt.show()

def mapOfsector(sector):
    res = nx.MultiDiGraph()
    G = ox.graph_from_place(sector, network_type='drive', simplify=True, retain_all=True)
    res = nx.compose(res, G)
    rm = []

    for node, data in  G.nodes(data=True):
        if (data['street_count'] == 1):
            for u, v, k, data in res.edges(keys=True, data=True):
                if (node == u):
                    rm.append((u, v, k))
                if (node == v):
                    rm.append((u, v, k))
                
    res.remove_edges_from(rm)
    res.remove_nodes_from(list(nx.isolates(res)))
    print(f"Total distance of the sector {sector}: {lengthGraph(res):.2f} km")
    ox.plot_graph(res, node_size=10, node_color='red', edge_color='w', edge_linewidth=0.5)
    plt.show(block=True)
    return res

def cost2(distance):
    speed = 20
    hours = (distance / 1000) / speed
    res = 1.3 * distance
    res += 800 * (hours // 24)

    if hours % 24 != 0:
        res += 800
    
    if hours > 8:
        res += 8 * 1.3
        res += 1.5 * (hours - 8)
    else:
        res += 1.3 * hours
    return res

def cost1(distance):
    speed = 10
    hours = (distance / 1000) / speed
    res = 1.1 * distance
    res += 500 * (hours // 24)
    if hours % 24 != 0:
        res += 500
    
    if hours > 8:
        res += 8 * 1.1
        res += 1.3 * (hours - 8)
    else:
        res += 1.1 * hours
    return res

def BFS(G, sources):
    lengths = getLengths(G)
    visited = set()
    res = {}
    queue = deque([(source, None, source, None) for source in sources])

    while queue:
        node, _, source, _ = queue.popleft()
        for i in G.neighbors(node):
            for j in G[node][i]:
                length = lengths[(node, i, j)]
                edge = (node, i, j)
                if edge not in visited:
                    visited.add(edge)
                    queue.append((i, node, source, j))
                    res[edge] = (color_map[sources.index(source)], length)
                    
    return res

def simulation(n, G):
    cost = 0
    time = 0
    sources = chooseSources(G, n)    
    edge_colors = BFS(G, sources)
        
    distances = []
        
    for color, length in edge_colors.values():
        i = find_color(color, distances) 
        if i != -1:
            d = distances[i][1] + (length)
            del distances[i]
            distances.append((color, d))
        else:
            distances.append((color, length))
    
    for (color, length) in distances:
        time = max((length/1000) / 10, time)
        cost += cost1(length / 1000)
        
    #pos = {node: (data['x'], data['y']) for node, data in G.nodes(data=True)}
    #draw_graph(G, pos, edge_colors)
    return (cost, time)

def simulation2(n, G):
    cost = 0
    time = 0
    sources = chooseSources(G, n)    
    edge_colors = BFS(G, sources)
        
    distances = []
        
    for color, length in edge_colors.values():
        i = find_color(color, distances) 
        if i != -1:
            d = distances[i][1] + (length)
            del distances[i]
            distances.append((color, d))
        else:
            distances.append((color, length))
    
    for (color, length) in distances:
        time = max((length/1000) / 20, time)
        cost += cost2(length / 1000)
        
    #pos = {node: (data['x'], data['y']) for node, data in G.nodes(data=True)}
    #draw_graph(G, pos, edge_colors)
    return (cost, time)

color_map = ["red", "lightpink", "gold", "orchid", "olive", "gray", "magenta", "green", "blue", "yellow"]

sectors = [
    "Outremont, Montreal, Quebec, Canada",
    "Verdun, Montreal, Quebec, Canada",
    "Anjou, Montreal, Quebec, Canada",
]
def res1():
    res = 0
    resT = 0
    for i in sectors:
        G = mapOfsector(i)
        minC = 100000000000000
        nC = 0
        minT = 100000000000000
        nT = 0
        for j in range(2,11):
            r = simulation(j, G)
            if r[1] < 7:
                print(f"cost for {j} snowplot: {r[0]:.2f}")
                print(f"time for {j} snowplot: {r[1]:.2f}")
                if r[0] < minC:
                    minC = r[0]
                    nC = j
                if r[1] < minT:
                    minT = r[1]
                    nT = j
        res+= minC
        resT = max(minT, resT)
        print(f"Optimal cost for {i.split(',')[0]} is {minC} with {nC} snowplot")
        print(f"Optimal time for {i.split(',')[0]} is {minT} with {nT} snowplot\n")

    print(f"total optimal cost: {res:.2f}")
    print(f"total optimal time for all the operations: {resT:.2f}")

def res2():
    res = 0
    resT = 0
    for i in sectors:
        G = mapOfsector(i)
        minC = 100000000000000
        nC = 0
        minT = 100000000000000
        nT = 0
        for j in range(2,11):
            r = simulation2(j, G)
            if r[1] < 7:
                print(f"cost for {j} snowplot: {r[0]:.2f}")
                print(f"time for {j} snowplot: {r[1]:.2f}")
                if r[0] < minC:
                    minC = r[0]
                    nC = j
                if r[1] < minT:
                    minT = r[1]
                    nT = j
        res+= minC
        resT = max(minT, resT)
        print(f"Optimal cost for {i.split(',')[0]} is {minC} with {nC} snowplot")
        print(f"Optimal time for {i.split(',')[0]} is {minT} with {nT} snowplot\n")

    print(f"total optimal cost: {res:.2f}")
    print(f"total optimal time for all the operations: {resT:.2f}")

res2()