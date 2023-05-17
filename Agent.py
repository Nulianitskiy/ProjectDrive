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

        self.expected_way = 0
        self.way_log = []

    def __init__(self, graph):
        self.start = 0
        self.goal = 0
        self.cur_pos = 1
        self.cur_edge = None
        self.move_time = 0
        self.start_time = 0
        self.g = graph
        self.way = []
        self.in_move = False
        self.done_way = False

        self.expected_way = 0
        self.way_log = []
        self.real_way = []
        self.results = []
        self.cur_res = 0
        self.waiting = 0
        self.generate()

    def find_way(self):
        return Astar.astar(self.g, self.start, self.goal)

    def generate(self):
        n = len(self.g.node_list)
        # print(n)
        while True:
            self.start = ra.randrange(n)
            self.goal = ra.randrange(n)
            self.way, self.expected_way = self.find_way()
            self.start_time = ra.randrange(0,3600)
            if self.way != None and len(self.way) >=3:
                break

    def update_way_log(self):
        self.way_log.append(self.move_time)
        self.real_way.append(self.cur_edge.weight)
        self.move_time = 0
        self.cur_pos += 1

    def time_shift(self):
        while True:
            t = self.start_time + ra.randint(0, 600) - 300
            if t > 0 and t < 3600:
                self.start_time = t
                break

    def way_shift(self):
        for i in range(len(self.way_log)):
            self.g.edge_list[self.way[i]][self.way[i + 1]] += (self.way_log[i] - self.g.edge_list[self.way[i]][self.way[i + 1]]) / 2

        self.way, self.expected_way = self.find_way()

    def calc_result(self):
        self.results.append(sum(self.way_log) - self.expected_way + self.waiting)
        self.cur_res = self.results[-1]
        #if self.cur_res < -900:
        #print(self.way_log, " = ", sum(self.way_log),"|", self.real_way, " exp - ", self.expected_way, "\n")
        self.way_log.clear()

    def evolve(self):
        match ra.randint(0, 2):
            case 0:
                self.time_shift()
                self.way_shift()
            case 1:
                self.time_shift()
            case 2:
                self.way_shift()

    def re_run(self):
        self.cur_pos = 1
        self.cur_edge = None
        self.move_time = 0
        self.in_move = False
        self.done_way = False
        self.waiting = 0
