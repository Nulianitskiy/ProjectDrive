import Astar
import random as ra

class Agent:
    def __init__(self, graph, start, goal, start_time):
        self.start = start
        self.goal = goal
        self.cur_pos = 0
        self.cur_edge = None
        self.move_time = 0
        self.start_time = start_time
        self.g = graph
        self.way = self.find_way()
        self.in_move = True
    
    def __init__(self, graph, start_time):
        self.start = 0
        self.goal = 0
        self.cur_pos = 0
        self.cur_edge = None
        self.move_time = 0
        self.start_time = start_time
        self.g = graph
        self.way = []
        self.in_move = True
        self.generate()
    
    def find_way(self):
        return Astar.astar(self.g, self.start, self.goal)
    
    def generate(self):
        n = len(self.g.node_list) - 1
        #print(n)
        while True:
            self.start = ra.randrange(n)
            self.goal = ra.randrange(n)
            self.way = self.find_way()
            if self.way != None and self.start != self.goal:
                break
