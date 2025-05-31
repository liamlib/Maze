from pydoc import locate
from turtledemo import clock
from collections import deque
import json
import pygame
import sys
import heapq
from pygame.draw import rect
from pygame.examples import grid

WIDTH = 600
HEIGHT = 600
ROWS = 30
RGB = (215, 245, 245)
GRAY = (120, 120, 120)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
RUNNING = False

pygame.display.set_caption("Pathfinding game")

def make_grid(rows, width):
    grid = []
    cell_size = int(width / rows)
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, cell_size, rows)
            grid[i].append(node)

    return grid




def draw_grid(screen, rows, width):

    global run
    cell_size = int(width / rows)
    cell_size1 = int(HEIGHT/ rows)
    pos = pygame.mouse.get_pos()
    RUN = False

    for i in range(rows):
        pygame.draw.line(screen, GRAY, (0, i * cell_size), (width, i * cell_size))  # 600/20 = 30 --> 0 , 0*30 0 , 1*30

        for j in range(rows):
            pygame.draw.line(screen, GRAY, (j * cell_size, 0), (j * cell_size, width))


def draw(screen, rows, width, grid, buttons = []):
    screen.fill(RGB)

    for row in grid:
        for node in row:
            node.draw(screen)

    draw_grid(screen, rows, width)
    for button in buttons:
        button.draw(screen)
    pygame.display.update()



def get_clicked_pos(pos, ROWS, width):
    size = int(width / ROWS)
    y, x = pos
    row = int(y / size)
    col = int(x / size)

    return row, col


class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = RGB
        self.width = width
        self.total_rows = total_rows
        self.neighbors = []

    def to_dict(self):
        return {
            "row": self.row,
            "col": self.col,
            "color": self.color
        }

    def from_dict(self, data):
        self.row = data["row"]
        self.col = data["col"]
        self.color = tuple(data["color"])


    def get_pos(self):
        return self.row, self.col

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == PURPLE

    def make_start(self):
        self.color = ORANGE

    def make_end(self):
        self.color = PURPLE

    def reset(self):
        self.color = RGB

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():  # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():  # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])
        # if self.row > 0 and self.col > 0 and not grid[self.row -1][self.col -1].is_barrier():
        #     self.neighbors.append(grid[self.row - 1][self.col - 1])
        # if self.row < 0 and self.col < 0 and not grid[self.row +1][self.col  +1].is_barrier():
        #     self.neighbors.append(grid[self.row + 1][self.col + 1])
        # if self.row < 0 and self.col < 0 and not grid[self.row + 1][self.col + 1].is_barrier():
        #     self.neighbors.append(grid[self.row + 1][self.col + 1])

        # check the diagonals

    def is_barrier(self):
        return self.color == BLACK

    def __lt__(self, other):
        return False

class Button:
    def __init__(self, x, y, width, height, text, color, action = None):
        self.rect = pygame.Rect(x,y,width,height)
        self.color = color
        self.text = text
        self.action = action
        self.font = pygame.font.SysFont("Arial", 20)

    def draw(self, surface):
        pygame.draw.rect(surface,self.color,self.rect)
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center = self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)






def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.color = (0, 0, 255)  # Path color (blue)
        draw()
def save_maze(grid, filename="maze.json"):
    maze_data = [[node.to_dict() for node in row] for row in grid]
    with open(filename, "w") as f:
        json.dump(maze_data, f, indent=4)


def load_maze(grid, filename="maze.json"):
    with open(filename, "r") as f:
        maze_data = json.load(f)
    for row in range(len(grid)):
        for col in range(len(grid[row])):
            grid[row][col].from_dict(maze_data[row][col])

def bfs(draw, grid, start, end):
    queue = deque([start])
    came_from = {}
    visited = {start}

    while queue:
        current = queue.popleft()

        # If we've reached the end, reconstruct the path
        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            start.make_start()

            return True

        # Check all neighbors
        for neighbor in current.neighbors:
            if neighbor not in visited and not neighbor.is_barrier():
                visited.add(neighbor)
                came_from[neighbor] = current
                queue.append(neighbor)
                neighbor.color = (0, 255, 0)  # Open set color
                draw()

            # Mark the node as closed
        if current != start and current != end:
            current.color = (255, 0, 0)  # Closed set color
            draw()

    return False


def dijkstra(draw, grid, start, end):
    count = 0
    open_set = []
    heapq.heappush(open_set, (0, count, start))
    came_from = {}

    # Distance from start to each node; start has distance 0
    distance = {node: float("inf") for row in grid for node in row}
    distance[start] = 0

    visited = set()

    while open_set:
        current_distance, _, current = heapq.heappop(open_set)

        if current in visited:
            continue
        visited.add(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            start.make_start()
            return True

        for neighbor in current.neighbors:
            temp_distance = distance[current] + 1  # All edges cost 1
            if temp_distance < distance[neighbor]:
                distance[neighbor] = temp_distance
                came_from[neighbor] = current
                heapq.heappush(open_set, (temp_distance, count, neighbor))
                count += 1
                neighbor.color = (0, 255, 0)  # Open set color
                draw()

        if current != start and current != end:
            current.color = (255, 0, 0)  # Closed set color
            draw()

    return False

def dfs(draw, grid, start, end):
    stack = [start]
    came_from = {}
    visited = {start}

    while stack:
        current = stack.pop()

        # If we've reached the end, reconstruct the path
        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            start.make_start()

            return True

        # Check all neighbors
        for neighbor in current.neighbors:
            if neighbor not in visited and not neighbor.is_barrier():
                visited.add(neighbor)
                came_from[neighbor] = current
                stack.append(neighbor)
                neighbor.color = (0, 255, 0)  # Open set color
                draw()

            # Mark the node as closed
        if current != start and current != end:
            current.color = (255, 0, 0)  # Closed set color
            draw()

    return False

def main(screen, width, RUNNING):
    global pos
    grid = make_grid(ROWS, width)
    start = None
    end = None

    button_width = 100
    button_height = 40
    margin = 10
    button_y = HEIGHT - button_height - margin

    buttons = [
        Button(margin, button_y, button_width, button_height, "save", (255, 130, 0), lambda: save_maze(grid)),
        Button(margin * 2 + button_width, button_y, button_width, button_height, 'load', (0, 255, 247), lambda: load_maze(grid)),
        Button(margin * 3 + button_width * 2, button_y, button_width, button_height, 'cancel', (255, 50, 38), lambda: reset_grid()),
        Button(margin * 4 + button_width * 3, button_y, button_width, button_height, 'run', (118, 255, 94), lambda: run_algorithm())
    ]

    def reset_grid():
        nonlocal grid, start, end
        start = None
        end = None
        grid = make_grid(ROWS, width)

    def run_algorithm():
        if start and end:
            for row in grid:
                for node in row:
                    node.update_neighbors(grid)
            dfs(lambda: draw(screen, ROWS, width, grid, buttons), grid, start, end)
            # dijkstra(lambda: draw(screen, ROWS, width, grid, buttons), grid, start, end)

    run = True
    while run:
        draw(screen, ROWS, width, grid, buttons)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                if event.button == 1:
                    # Left click - first check buttons
                    for button in buttons:
                        if button.is_clicked(pos):
                            button.action()
                            break
                    else:
                        # No button clicked, handle grid click
                        row, col = get_clicked_pos(pos, ROWS, width)
                        node = grid[row][col]

                        if not start and node != end:
                            start = node
                            start.make_start()
                        elif not end and node != start:
                            end = node
                            end.make_end()
                        elif node != start and node != end:
                            node.color = BLACK

                elif event.button == 3:
                    # Right click - reset node
                    pos = pygame.mouse.get_pos()
                    row, col = get_clicked_pos(pos, ROWS, width)
                    node = grid[row][col]
                    node.reset()
                    if node == start:
                        start = None
                    elif node == end:
                        end = None

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    save_maze(grid)
                if event.key == pygame.K_l:
                    load_maze(grid)
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    dfs(lambda: draw(screen, ROWS, width, grid, buttons), grid, start, end)
                    # dijkstra(lambda: draw(screen, ROWS, width, grid, buttons), grid, start, end)

                if event.key == pygame.K_c:
                    reset_grid()




main(SCREEN, WIDTH, RUNNING)



# [
# [
# [
# [
# [
