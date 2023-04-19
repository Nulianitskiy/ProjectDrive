import networkx as nx
import osmnx as ox
import igraph as ig


# G_nx = ox.graph_from_point((45.039546, 38.974388), dist=200, network_type="drive", retain_all=False)


class OGraph:
    def __init__(self, graph):
        self.node_list, self.edge_list = self.transform_graph(graph)
        self.minx = min(x[0] for x in self.node_list)
        self.miny = min(x[1] for x in self.node_list)
        self.maxx = max(x[0] for x in self.node_list)
        self.maxy = max(x[1] for x in self.node_list)
    

    def transform_graph(self, G_nx):
        osmids = list(G_nx.nodes)
        G_nx = nx.relabel.convert_node_labels_to_integers(G_nx)
        # выдаем каждому узлу его osmid
        osmid_values = {k: v for k, v in zip(G_nx.nodes, osmids)}
        nx.set_node_attributes(G_nx, osmid_values, "osmid")

        # переводим networkx граф в igraph
        G_ig = ig.Graph(directed=True)
        G_ig.add_vertices(G_nx.nodes) # Передается y, x, highway, street_count, osmid
        G_ig.add_edges(G_nx.edges())
        #G_ig.vs["osmid"] = osmids
        we = list(nx.get_edge_attributes(G_nx, "length").values()) # length

        for i in range(len(we)):
            we[i] = round(we[i])
        G_ig.es["length"] = we

        nodes = []
        for i in range(len(G_ig.vs)):
            nodes.append([G_ig.vs["name"][i]["x"],G_ig.vs["name"][i]["y"],osmids[i]])

        edges = {}
        inner_dict = {}
        n = 0
        p = 0
        for i in G_nx.edges():
            if(i[0]==n):
                inner_dict[i[1]] = G_ig.es["length"][p]
            else:
                a = inner_dict.copy()
                edges[n] = a
                inner_dict.clear()
                inner_dict[i[1]] = G_ig.es["length"][p]
                n+=1
            p+=1

        return nodes, edges

    def get_node_deg(self, node):
        return len(self.edge_list[node])