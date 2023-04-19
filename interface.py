import pygame
import math
import osmnx as ox
import random as ra
from abc import ABCMeta

import ograph
import Astar
import Agent
 
 
def render_text(text, family, size, color=(0, 0, 0), aa=False):
    font = pygame.font.SysFont(family, size)
    return font.render(text, aa, color)
 
 
def near(p, center, radius):
    d2 = (p[0] - center[0])**2 + (p[1] - center[1])**2
    return d2 <= radius**2

def set_agent(agent, graph, time):
    if(agent.move_time == time):
        ed = graph.find_node(agent.way[0], agent.way[1])
        ed.add_agent(agent)
        agent.cur_edge = ed
        agent.in_move = True
    #print(ed.weight, ed.capacity)

def move_agent(agent, graph):
    if agent.in_move:
        if len(agent.way) > agent.cur_pos+1:
            if agent.move_time >= agent.cur_edge.weight and not graph.verticies[agent.way[agent.cur_pos + 1]].light_stop:
                nnode = graph.find_node(agent.way[agent.cur_pos],agent.way[agent.cur_pos + 1])
                if nnode.check_road:
                    agent.cur_edge.del_agent()
                    nnode.add_agent(agent)
                    agent.cur_edge = nnode
                    agent.move_time = 0
                    agent.cur_pos += 1
            else:
                agent.move_time += 5
        else:
            agent.cur_edge.del_agent()
            agent.in_move = False

 
class GraphObject (metaclass=ABCMeta):
    def draw(self, surface):
        pass
 
    def update(self):
        pass
 
    def get_event(self, ev):
        pass
 
 
class Vertex (GraphObject):
    def __init__(self, name, x, y, size=15, color=(0, 0, 0), width=1):
        self.__name, self.__name_surface = "", None
        self.set_name(name)
        self.x, self.y = x, y
        self.size, self.width, self.color = size, width, color
        self.__edges = []
        self.selected = False
        self.selection_color = (255, 0, 0)

        self.light = False
        self.light_stop = False
        self.light_time = 0
        self.light_cur_time = 0

    @property
    def edges(self):
        return self.__edges
 
    @property
    def name(self):
        return self.__name
 
    @property
    def pos(self):
        return self.x, self.y
 
    def set_name(self, name):
        self.__name = name
        self.__name_surface = render_text(name, "Arial", 16)
 
    def get_event(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and near(self.pos, ev.pos, self.size):
            self.select()
        elif ev.type == pygame.MOUSEMOTION and self.selected:
            self.x, self.y = ev.pos
        elif ev.type == pygame.MOUSEBUTTONUP and self.selected:
            self.deselect()
 
    def select(self, color=(255, 0, 0)):
        self.selected = True
        self.selection_color = color
 
    def deselect(self):
        self.selected = False
 
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.pos, self.size, self.width)  # Нарисовать вершину
        #if self.__name_surface:  # draw name
        #    x, y, w, h = self.__name_surface.get_rect()
        #    surface.blit(self.__name_surface, (self.x-w//2, self.y-h//2))
        if self.selected:  # Нарисовать выбранную вершину
            pygame.draw.circle(surface, self.selection_color, self.pos, self.size-self.width)

    def update_traffic_light(self):
        if self.light_cur_time >= self.light_time:
            self.light_cur_time = 0
            self.light_stop = not self.light_stop

        self.color = (0, 255, 0) if not self.light_stop else (255, 0, 0)
        self.light_cur_time += 1
 
 
class Edge (GraphObject):
    def __init__(self, v1, v2, weight=0, color=(0, 0, 0), width=1):
        self.v1, self.v2 = v1, v2
        self.__weight, self.__weight_surface = 0, None
        self.set_weight(weight)
        self.width, self.color = width, color

        self.capacity = 0
        if weight // 5 >=1 : # 5 - средняя длина автомобиля
            self.capacity = weight // 5
        else:
            self.capacity = 1 

        self.road = []
 
    @property
    def weight(self):
        return self.__weight
 
    def set_weight(self, weight):
        self.__weight = weight
        self.__weight_surface = render_text(str(weight), "Arial", 16)
 
    @property
    def pos1(self):
        return self.v1.pos
 
    @property
    def pos2(self):
        return self.v2.pos
    
    def add_agent(self, agent):
        self.road.append(agent)

    def del_agent(self):
        self.road.pop(0)
    
    def check_road(self):
        return len(self.road) + 1 >= self.capacity
    
    def check_capacity(self):
        if len(self.road) == 0:
            self.color = (0, 0, 0)
        elif len(self.road) / self.capacity >= 0.7:
            self.color = (255, 0, 0)
        elif len(self.road) / self.capacity >= 0.35:
            self.color = (255, 255, 0)
        else:
            self.color = (0,255,0)

    def draw(self, surface):
        self.check_capacity()
        pygame.draw.line(surface, self.color, self.pos1, self.pos2, self.width)  # Нарисовать ребро
        '''
        if self.__weight_surface:  # Нарисоваь вес ребра
            x1, y1 = self.pos1
            x2, y2 = self.pos2
            pos = (x2-x1)//2 + x1, (y2-y1)//2 + y1
            surface.blit(self.__weight_surface, pos)
        '''
 
 
class Graph:
    def __init__(self, matrix, verticies, edges, tr_lights):
        self.matrix = matrix
        self.verticies = verticies
        self.edges = edges
        self.tr_light = tr_lights
        self.objects = self.edges + self.verticies

        #for ed in edges:
        #    print(ed.v1.name)
        #    print(ed.v2.name, "\n")
 
    def __len__(self):
        return len(self.verticies)
 
    def draw(self, surface):
        [obj.draw(surface) for obj in self.objects]
 
    def update(self):
        [obj.update() for obj in self.objects]
 
    def get_event(self, ev):
        [obj.get_event(ev) for obj in self.objects]
 
    def set_width(self, width):
        [setattr(obj, "width", width) for obj in self.objects]
    
    @classmethod
    def from_ograph(cls, graph, vsize=5, width=1, color=(0, 0, 0)):
        n = len(graph.node_list)
        matrix = [[0]*n for _ in range(n)]
        verticies = []
        edges = []
        tr_lights = []

        for i in range(n):
            # Нормализация/центрирование
            x = (graph.node_list[i][0] - graph.minx)/(graph.maxx - graph.minx) * (SIZE[0]-100) + 50
            y = SIZE[1] - ((graph.node_list[i][1] - graph.miny)/(graph.maxy - graph.miny) * (SIZE[1]-100) + 50)
            verticies.append(Vertex(str(i),x,y, vsize, color, width))

        for j in range(n-1):
            if graph.get_node_deg(j) >= 3 and ra.random() <= 0.3:
                verticies[j].light = True
                verticies[j].light_time = 30
                verticies[j].light_cur_time = ra.randrange(61)
                tr_lights.append(verticies[j])
        
        for x, value in graph.edge_list.items():
            for y, l in value.items():
                matrix[x][y] = matrix[y][x]= l
                edges.append(Edge(verticies[x],verticies[y],l,color,5))
        
        return cls(matrix,verticies, edges, tr_lights)
    
    def find_node(self, a, b):
        for ed in self.edges:
            if ed.v1.name == str(a) and ed.v2.name == str(b):
                return ed

 
FPS = 30
SIZE = (1200, 900)

pygame.init()
screen = pygame.display.set_mode(SIZE, pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE)
pygame.display.set_caption("ProjectDrive")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 100)
 
#g = Graph.random(300, 300, 8)
# Галерея
graph = ograph.OGraph(ox.graph_from_point((45.039546, 38.974388), dist=3000, network_type="drive", retain_all=False))
# Кубик
#graph = ograph.OGraph(ox.graph_from_point((45.019667, 39.027768), dist=1000, network_type="drive", retain_all=False))


g = Graph.from_ograph(graph)

#print(graph.edge_list)
#print(g.find_node(40,26))

agents_n = 10000
agents = []

for i in range(agents_n):
    agents.append(Agent.Agent(graph,0))
 
h = m = s = 0
text = font.render(str(s), True, (0, 128, 0))

time_delay = 100
timer_event = pygame.USEREVENT+1
pygame.time.set_timer(timer_event, time_delay)
 
running = True
while running:
    clock.tick(FPS)
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        elif ev.type == timer_event:
            for i in range(agents_n):
                set_agent(agents[i], g, h*3600+m*60+s)
                move_agent(agents[i],g)
            for j in g.tr_light:
                j.update_traffic_light()

            s += 1
            if s >= 60: s -= 60; m += 1
            if m >= 60: m -= 60; h += 1
            text = font.render('%d:%d:%d' % (h % 24, m, s), True, (0, 128, 0))
        
        g.get_event(ev)
 
    screen.fill((255, 255, 255))
    text_rect = text.get_rect(topleft = screen.get_rect().topleft)

    screen.blit(text, text_rect)
 
    g.update()
    g.draw(screen)
 
    pygame.display.flip()
 
 
pygame.quit()