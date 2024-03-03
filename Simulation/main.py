from collections import deque
import pygame
from time import sleep
import numpy as np
from random import randint
import sys
from pygame.locals import *


pygame.init()
SCREEN = pygame.display.set_mode((1700, 900))
pygame.display.set_caption('Hello World!')
pygame.font.init()
square_size = 30
offset = 25
my_font = pygame.font.SysFont('Arial', int(square_size * 0.7))
mouse = pygame.image.load("mouse.png")
mouse = pygame.transform.scale(mouse, (int(square_size * 0.8), square_size))
mouse_rect = mouse.get_rect()
pictures = {"rock":pygame.transform.scale(pygame.image.load("rock.png"), (int(square_size*1.2), square_size*1.2)),
            "bush":pygame.transform.scale(pygame.image.load("bush.png"), (int(square_size*1.2), square_size*1.2)),
            "tree":pygame.transform.scale(pygame.image.load("tree.png"), (int(square_size*1.2), square_size*1.2)),
            "fenceleftside":pygame.transform.scale(pygame.image.load("fenceleftside.png"), (int(square_size), square_size*1.1)),
            "fencerightside":pygame.transform.scale(pygame.image.load("fencerightside.png"), (int(square_size), square_size*1.1)),
            "fencetop":pygame.transform.scale(pygame.image.load("fencetop.png"), (int(square_size), square_size))}

visited = np.array([[0, 0]])
start_pos = [1, 1]
def check_in(x, y, map):
    for i in map:
        if x == i[0] and y == i[1]:
            return True
    return False


def draw_maze(maze_map, offset_x, offset_y, square_size):
    for y in range(len(maze_map)):
        for x in range(len(maze_map[y])):
            if maze_map[y][x]:
                fill_color = (255, 255, 255)
            else:
                fill_color = (0, 0, 0)
            #if y > 0 and x > 0 and y < len(maze_map) - 1 and x < len(maze_map[0]) - 1 and maze_map[y][x] ==0:
            #    fill_color = (66, 105, 47)
            pygame.draw.rect(SCREEN, fill_color,(x * square_size + offset_x, y * square_size + offset_y,square_size - 1, square_size - 1))
            if maze_map[y][x] == 2:
                SCREEN.blit(pictures["rock"], (x * square_size + offset_x, y * square_size + offset_y,square_size - 1, square_size - 1))
            if maze_map[y][x] == 3:
                SCREEN.blit(pictures["bush"], (x * square_size + offset_x, y * square_size + offset_y,square_size - 1, square_size - 1))
            if maze_map[y][x] == 4:
                SCREEN.blit(pictures["tree"], (x * square_size + offset_x, y * square_size + offset_y,square_size - 1, square_size - 1))
            if maze_map[y][x] == 5:
                SCREEN.blit(pictures["fencetop"], (x * square_size + offset_x, y * square_size + offset_y,square_size - 1, square_size - 1))
            if maze_map[y][x] == 6:
                SCREEN.blit(pictures["fenceleftside"], (x * square_size + offset_x, y * square_size + offset_y,square_size - 1, square_size - 1))
            if maze_map[y][x] == 7:
                SCREEN.blit(pictures["fencerightside"], (x * square_size + offset_x, y * square_size + offset_y,square_size - 1, square_size - 1))

points = []


def draw_window(mouse_x, mouse_y):
    global run
    if not run:
        return

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            run = False
            return
    if pygame.mouse.get_pressed(num_buttons=3)[0]:
        xpos, ypos = pygame.mouse.get_pos()
        ypos = round((ypos-offset)/square_size)
        xpos = round((xpos-offset)/square_size)
        if ypos>0 and ypos <len(map)-1 and xpos>0 and xpos<len(map[0])-1:
            map[ypos][xpos] = 2
    SCREEN.fill((255, 255, 255))

    draw_maze(map, offset, offset, square_size)
    draw_maze(collected_maze, 1250, 30, 10)
    mouse_rect.x = mouse_x * square_size + offset + 2
    mouse_rect.y = mouse_y * square_size + offset + 2
    for point in range(len(visited)):
        xpos = int((visited[point][1] + 2) * square_size)
        ypos = int((visited[point][0] + 2) * square_size)
        if map[visited[point][0], visited[point][1]] ==1:
            pygame.draw.rect(SCREEN, (220,220,220),(visited[point][1] * square_size + offset, visited[point][0] * square_size + offset,square_size - 1, square_size - 1))

    SCREEN.blit(mouse, mouse_rect)
    pygame.display.update()

map = np.array([
                [6, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 7],
                [6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 7],
                [6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 7],
                [6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 7],
                [6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 7],
                [6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 7],
                [6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1, 1, 1, 1, 1, 1, 7],
                [6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1, 1, 1, 1, 1, 1, 7],
                [6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1, 1, 1, 1, 1, 1, 7],
                [6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 4, 4, 1, 1, 1, 1, 1, 1, 7],
                [6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 7],
                [6, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 7],
                [6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 7],
                [6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 7],
                [6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 7],
                [6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 7],
                [6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 7],
                [6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 3, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 1, 3, 3, 3, 7],
                [6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 3, 3, 3, 3, 3, 3, 7],
                [6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 3, 1, 1, 1, 3, 3, 1, 1, 7],
                [6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 7],
                [6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 1, 1, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 7],
                [6, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 3, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 7],
                [6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 7],
                [6, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 7]],
    dtype='int8')

collected_maze = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]], dtype='int8')
collected_maze = map.copy()
for i in range(len(collected_maze)):
    for j in range(len(collected_maze[0])):
        if collected_maze[i][j] != 1:
            collected_maze[i][j] = 0

mouse_pos = {"x": 1,"y": 1}
def check_neighbors(x, y):
    return map

#stack
def colect_maze(x, y):
    global collected_maze
    if map[y][x] == 1:
        add_row = np.zeros((1, len(collected_maze[0])), dtype='int8')
        add_column = np.zeros((1, len(collected_maze)), dtype='int8')
        if direction == 0 and y == 0:
            collected_maze = np.insert(collected_maze, 1, add_row, axis=0)
        elif direction == 2 and y == len(collected_maze) - 1:
            collected_maze = np.insert(collected_maze, -1, add_row, axis=0)
        elif direction == 1 and x == len(collected_maze[0]) - 1:
            collected_maze = np.insert(collected_maze, -1, add_column, axis=1)
        elif direction == 3 and x == 0:
            collected_maze = np.insert(collected_maze, 1, add_column, axis=1)
        collected_maze[y][x] = 1
    else:
        collected_maze[y][x] = 0


direction = 0


def go_to(start, end):
    y1 = start[0]
    x1 = start[1]
    y2 = end[0]
    x2 = end[1]
    if x2 == x1:
        if y2 == y1:
            return direction
        elif y2 > y1:
            return 2
        else:
            return 0
    else:
        if x2 > x1:
            return 1
        else:
            return 3

def turn_to(destination):
    global mouse, direction
    num_turns = abs(direction - destination)
    if direction > destination:
        mouse = pygame.transform.rotate(mouse, 90 * num_turns)
    elif direction < destination:
        mouse = pygame.transform.rotate(mouse, -90 * num_turns)
    else:
        pass
    direction = destination

turn_to(0)

"""
points = []
def calculate_points():
    for y in range(len(map)):
        for x in range(len(map[0])):
            if map[y][x] == 0:
                if len(map[0]) > x+1:
                    if map[y,x+1] == 1:
                        points.append([y,x+1])
                if (x-1)>=0:
                    if map[y,x-1] == 1:
                        points.append([y,x-1])
                if len(map) > y+1:
                    if map[y+1,x] == 1:
                        points.append([y+1,x])
                if (y-1)>=0:
                    if map[y-1,x] == 1:
                        points.append([y-1,x])
#calculate_points()
"""

def bfs(start, end, maze):
    bfs_visited = []
    bfs_queue = []
    bfs_visited.append(start)
    bfs_queue.append(start)
    path = []
    while len(bfs_queue) > 0:
        if bfs_queue[0] == end:
            break
        visiting = bfs_queue.pop(0)
        neighbouring_nodes = [[1, 0],[-1, 0],[0, -1],[0, 1]]
        for i in neighbouring_nodes:
            x = visiting[1] + i[1]
            y = visiting[0] + i[0]
            if [y, x] in bfs_visited:
                continue
            if maze[y][x] != 1:
                continue
            bfs_visited.append([y, x])
            bfs_queue.append([y, x])
            path.append([[y, x], visiting])
    global shortest_path
    shortest_path = [end]

    find_queue = deque((),3000)
    find_queue.append(end)
    while len(find_queue)!=0:
        find = find_queue.popleft()
        for i in path:
            if i[0] == find:
                shortest_path.insert(0, i[0])
                find_queue.append(i[1])
    return shortest_path

visited = np.array([[0, 0]])
stack = [start_pos]
double_points = []
#stack=points
#stack.insert(-1,start_pos)
neighbors = [[1, 0],[-1, 0], [0, 1],[0, -1] ]

mouse_pos = start_pos
mouse_visited = []
run = True
while len(stack) > 0 and run:
    sleep(0.01)
    current = stack.pop()
    y = current[0]
    x = current[1]

    if check_in(y,x, visited):
        continue
    visited = np.append(visited, [[y, x]], axis=0)

    path = bfs(mouse_pos, current, collected_maze)
    for pos in path:
        if len(path)> 3:
            sleep(0.1)
        xpos = pos[1]
        ypos = pos[0]
        if map[ypos][xpos] != 1:
            current = mouse_pos
            break
        turn_to(go_to(mouse_pos, [ypos, xpos]))
        mouse_pos = [ypos, xpos]
        if mouse_pos in stack:
            visited = np.append(visited, [mouse_pos], axis=0)
            stack.remove(mouse_pos)
        colect_maze(xpos, ypos)
        draw_window(mouse_pos[1], mouse_pos[0])

    for i in neighbors:
        new_y = y+i[0]
        new_x = x+i[1]

        #original_dir = direction
        #direction = go_to(mouse_pos, [new_y, new_x])
        colect_maze(new_x, new_y)
        #direction = original_dir
        if map[new_y][new_x]==1 and not check_in(new_y, new_x, visited) :
            stack.append([new_y, new_x])
"""
while len(stack) > 0:
    if len(collected_maze[0]) ==  len(map[0]) and len(collected_maze) == len(map):
        compare = collected_maze== map
        if compare.all():
            break
    current = stack.pop()

    y = current[0]
    x = current[1]

    #if [y, x] in double_points:
     #   continue

    for pos in bfs(mouse_pos, current, collected_maze):
        sleep(0.02)
        xpos = pos[1]
        ypos = pos[0]
        turn_to(go_to(mouse_pos, [ypos, xpos]))
        mouse_pos = [ypos, xpos]
        if mouse_pos in stack:
            visited = np.append(visited, [mouse_pos], axis=0)
            stack.remove(mouse_pos)
        mouse_visited.append([mouse_pos[1],mouse_pos[0]])
        draw_window(mouse_pos[1], mouse_pos[0])

    for i in neighbors:
        new_y = y + i[0]
        new_x = x + i[1]
        #if [new_y, new_x] in points:
         #   double_points.append([new_y, new_x])

        #points.append([new_y, new_x])
        if map[new_y][new_x] == 1 and not check_in(new_y, new_x, visited) and [new_y, new_x] not in stack :
            if i == [-1,0]:
                stack.insert(-2,[new_y, new_x])
            else:
                stack.append([new_y, new_x])
            stack.append([new_y, new_x])
            original_dir = direction
            direction = go_to(mouse_pos, [new_y, new_x])
            colect_maze(new_x, new_y)
            direction = original_dir
"""


"""
while True:
    draw_window(mouse_pos["x"], mouse_pos["y"])
"""










"""
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    draw_window(mouse_pos["x"],mouse_pos["y"])
    if map[mouse_pos["y"], mouse_pos["x"]+1]:
        turn_to(go_to([mouse_pos["y"],mouse_pos["x"]], [mouse_pos["y"], mouse_pos["x"]+1]))
        mouse_pos["x"] +=1
    else:
        turn_to(go_to([mouse_pos["y"],mouse_pos["x"]], [mouse_pos["y"]+1, mouse_pos["x"]]))
        mouse_pos["y"] += 1
    colect_maze(mouse_pos["x"], mouse_pos["y"])
    draw_maze(collected_maze, 100, square_size * len(map) + 40, square_size / 2.5)
    sleep(0.1)
"""
