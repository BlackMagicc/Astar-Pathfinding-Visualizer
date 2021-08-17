import pygame
import math
from queue import PriorityQueue

WIDTH = 800
WINDOW = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Finding Visualizer")

# Colors for our visualizer
BLUE = (0, 0, 255)  # End node
ORANGE = (255, 165, 0)  # Outlines direct path to end node
GREEN = (0, 255, 0)  # Next nodes to explore
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)  # Board
BLACK = (0, 0, 0)  # Barrier
PURPLE = (128, 0, 128)
RED = (255, 0, 0)  # Starting position
GREY = (128, 128, 128)  # Grid lines
TURQUOISE = (64, 224, 208)  # Nodes we have seen


# The color of each node tells us how we will interact with it
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

    def get_position(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == TURQUOISE

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == RED

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    # The following methods allow us to actually
    # change each node rather than just check the color
    def make_start(self):
        self.color = RED

    def make_closed(self):
        self.color = TURQUOISE

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = BLUE

    def make_path(self):
        self.color = ORANGE

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():  # Check neighbor below
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # Check neighbor above
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # Check left neighbor
            self.neighbors.append(grid[self.row][self.col - 1])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():  # Check right neighbor
            self.neighbors.append(grid[self.row][self.col + 1])

    def __lt__(self, other):
        return False


# Our heuristic function, we will use Manhattan distance
def heuristic_function(p1, p2):
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
    open_set = PriorityQueue()  # We use PriorityQueue because its efficient to get the smallest element everytime
    open_set.put((0, count, start))
    came_from = {}
    g_score = {node: float("inf") for row in grid for node in row}  # Distance from start to visiting node
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row}  # Predicted distance from visited node to end node
    f_score[start] = heuristic_function(start.get_position(), end.get_position())

    # PriorityQueue doesn't let you check whats in the queue so we created this hash
    open_set_hash = {start}

    # Even though we already have this function below, we create it again because
    # Now this algorithm takes over, and we'll need a way to exit in case something goes wrong
    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)  # Syncing the behaviors of the two

        if current == end:  # We found the shortest path
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        # Temp score comes from the fact that we're moving one node away
        # To a potential neighbor, but we update the score when necessary
        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + heuristic_function(neighbor.get_position(), end.get_position())
                if neighbor not in open_set_hash:
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()
        draw()

        # We close the node we just looked at because we found a better path
        if current != start:
            current.make_closed()

    return False


# Here we take the total rows and width of the grid
# And then we can find out the width of each cube
# to create our grid
def make_grid(rows, width):
    grid = []
    cube_width = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, cube_width, rows)
            grid[i].append(node)

    return grid


# Now we need to add gridlines so it looks like
# an actual grid
def draw_grid(window, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(window, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(window, GREY, (j * gap, 0), (j * gap, width))


# Now we can put everything together and actually draw the grid
def draw(window, grid, rows, width):
    window.fill(WHITE)

    for row in grid:
        for node in row:
            node.draw(window)

    draw_grid(window, rows, width)
    pygame.display.update()


# Tells us the position of a mouse click
def get_clicked_position(mouse_pos, rows, width):
    gap = width // rows
    y, x = mouse_pos

    row = y // gap
    col = x // gap

    return row, col


def main(window, width):
    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True
    started = False
    while run:
        draw(window, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:  # Left mouse click
                pos = pygame.mouse.get_pos()  # Grabs position of the pygame mouse
                # we pass that position to our get clicked position function
                # to find out where we just clicked
                row, col = get_clicked_position(pos, ROWS, width)
                node = grid[row][col]
                # our first two clicks will always define the start, end positions
                if not start and node != end:
                    start = node
                    start.make_start()
                elif not end and node != start:
                    end = node
                    end.make_end()
                elif node != end and node != start:
                    node.make_barrier()
            # Right mouse click - allows us to erase from the grid
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_position()
                row, col = get_clicked_position(pos, ROWS, width)
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

                    algorithm(lambda: draw(window, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)
    pygame.quit()


main(WINDOW, WIDTH)
