import igraph as ig
import osmnx as ox
import heapq

import ograph


# Оценка расстояния от вершины до цели
def heuristic(from_node, to_node, node_list):
    return ((node_list[from_node][0] - node_list[to_node][0]) ** 2 + (
                node_list[from_node][1] - node_list[to_node][1]) ** 2) ** 0.5


def astar(graph, start, end):
    n = len(graph.node_list)

    distances = {vertex: float('infinity') for vertex in graph.edge_list}
    distances[start] = 0

    queue = [(0, start)]
    predecessors = {vertex: None for vertex in graph.edge_list}

    while queue:
        # Извлекаем вершину с наименьшим расстоянием
        current_distance, current_vertex = heapq.heappop(queue)

        # Если вершина является конечной, то завершаем поиск
        if current_vertex == end:
            # Строим путь от конечной вершины до стартовой
            path = []
            while current_vertex is not None and current_vertex in graph.edge_list:
                path.append(current_vertex)
                current_vertex = predecessors[current_vertex]
            return path[::-1], distances[end]

        if current_vertex in graph.edge_list:
            for neighbor, weight in graph.edge_list[current_vertex].items():
                # Вычисляем расстояние до соседней вершины через текущую вершину
                distance = distances[current_vertex] + weight
                if neighbor in graph.edge_list:
                    if distance < distances[neighbor]:
                        distances[neighbor] = distance
                        # Вычисляем эвристическую функцию для соседней вершины
                        priority = distance + heuristic(neighbor, end, graph.node_list)
                        heapq.heappush(queue, (priority, neighbor))
                        predecessors[neighbor] = current_vertex

    return None, float('infinity')

# g = ograph.OGraph(ox.graph_from_point((45.039546, 38.974388), dist=200, network_type="drive", retain_all=False))
# print(g.node_list[0][0])
# path = astar(g, 0, 4)

# print(path)
