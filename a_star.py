import pygame
import math
from queue import PriorityQueue

#set up grid display
WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Algorithm")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (251, 255, 135)
LIGHT_BLUE = (189, 225, 255)
DARK_BLUE = (19, 84, 138)
WHITE = (255, 255, 255)
BLACK = (50, 50, 50)
GREY = (128, 128, 128)


class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    #closed: we have already looked at the node
    def is_closed(self):
        return self.color == LIGHT_BLUE

    def is_open(self):
        return self.color == DARK_BLUE

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == GREEN

    def is_end(self):
        return self.color == RED

    def reset(self):
        self.color = WHITE

    def make_closed(self):
        self.color = LIGHT_BLUE

    def make_open(self):
        self.color = DARK_BLUE

    def make_barrier(self):
        self.color = BLACK

    def make_start(self):
        self.color = GREEN

    def make_end(self):
        self.color = RED

    def make_path(self):
        self.color = YELLOW

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        # self.neighbors = [] # need?
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # down neighbor
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():                   # up neighbor
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # left neighbor
            self.neighbors.append(grid[self.row][self.col - 1])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # right neighbor
            self.neighbors.append(grid[self.row][self.col + 1])


    # compares 2 nodes together
    def less_than(self, other):
        return False

# heuristic using Manhattan Distance ("L distance")
# points p1, p2 of form (x, y)
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()      # PriorityQueue helps get the smallest element each time
    open_set.put((0, count, start)) # add start node to open set
    came_from = {}
    # g_score is current shortest distance to get from start to current
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    # f_score predicted distance of current node to end node 
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start} # tells us if node is in the queue or not

    while not open_set.empty(): # if empty, we've considered all nodes
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2] # pop the node from the open set
        open_set_hash.remove(current)  # also remove it from the hash

        if current == end:
            reconstruct_path(came_from, end, draw)
            start.make_start()
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()
        if current != start:
            current.make_closed()


# creates a 2D array of nodes
def make_grid(rows, grid_width):
    grid = []
    node_width = grid_width // rows #calculate width of a square by dividing width of entire grid by number of rows 
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, node_width, rows)
            grid[i].append(node)
    return grid

def draw_grid_lines(win, rows, grid_width):
    node_width = grid_width // rows
    for i in range(rows):
        # draws horizontal lines at each row
        # pygame.draw.line(surface, color, start_pos, end_pos)
        pygame.draw.line(win, GREY, (0, i * node_width), (grid_width, i * node_width))
        for j in range(rows):
            # draws vertical lines at each column
            pygame.draw.line(win, GREY, (j * node_width, 0), (j * node_width, grid_width))

def draw(win, grid, rows, grid_width):
    win.fill(WHITE) # fills entire screen with a color every frame

    for row in grid:
        for node in row:
            node.draw(win)

    draw_grid_lines(win, rows, grid_width)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
	gap = width // rows
	y, x = pos
	row = y // gap
	col = x // gap
	return row, col
    

def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None
    run = True
    started = False

    while run:
        draw(win, grid, ROWS, width)
        # checks all events in pygame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run == False
                pygame.quit()

            # if the mouse button was clicked (left=0, middle=1, right=2)
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                if not start and node != end:           # color node start color is there is no start
                    start = node
                    start.make_start()
                elif not end and node != start:         # color node end color is there is no end
                    end = node
                    end.make_end()
                elif node != end and node != start:
                    node.make_barrier()

            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                elif node == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()

main(WIN, WIDTH)