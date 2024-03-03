from collections import deque
import pygame
from time import sleep
import numpy as np
from random import randint
pygame.init()
SCREEN = pygame.display.set_mode((1000, 900))
pygame.display.set_caption('Hello World!')
pygame.font.init() 
square_size = 45
offset = 25
my_font = pygame.font.SysFont('Arial', int(square_size*0.7))
mouse = pygame.image.load("mouse.png")
mouse = pygame.transform.scale(mouse, (int(square_size * 0.8), square_size))
mouse_rect = mouse.get_rect()

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
      pygame.draw.rect(SCREEN, fill_color,
                       (x * square_size + offset_x, y * square_size + offset_y,
                        square_size - 1, square_size - 1))
points = []
def draw_window(mouse_x, mouse_y):
  SCREEN.fill((255, 255, 255))
  draw_maze(map, offset, offset, square_size)
  draw_maze(collected_maze, 100,
            square_size * len(map) + 40, square_size / 2.5)
  mouse_rect.x = mouse_x * square_size + offset+2
  mouse_rect.y = mouse_y * square_size + offset+2
  for point in range(len(stack)):
    xpos = int((stack[point][1]+1)*square_size)
    ypos = int((stack[point][0]+1)*square_size)
    text_surface = my_font.render(str(point), False, (0, 0, 0))
    pygame.draw.circle(SCREEN, (111,101,30), (xpos, ypos), int(square_size*0.5), int(square_size*0.5))
    SCREEN.blit(text_surface, (xpos-square_size/4+3,ypos-square_size/4))
  for point in visited:
    xpos = int((point[1]+1)*square_size)
    ypos = int((point[0]+1)*square_size)
    pygame.draw.circle(SCREEN, (181,101,30), (int(xpos), int(ypos)), int(square_size*0.2), int(square_size*0.2))
  
  xpos = int((end_pos[1]+1)*square_size)
  ypos = int((end_pos[0]+1)*square_size)
  text_surface = my_font.render("END", False, (0, 0, 0))
  pygame.draw.circle(SCREEN, (0,255,0), (xpos, ypos), int(square_size*0.8), int(square_size*0.8))
  SCREEN.blit(text_surface, (xpos-square_size/2-10,ypos-square_size/2+10))  
  SCREEN.blit(mouse, mouse_rect)
  pygame.display.update()


map = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0],
                [0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0],
                [0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0],
                [0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0],
                [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0],
                [0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                [0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                [0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0],
                [0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                [0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]],
               dtype='int8')

collected_maze = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]], dtype='int8')
#stack
def colect_maze(x, y):
  global collected_maze
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

direction = 0

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

turn_to(2)

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
    neighbouring_nodes = [[1, 0], [-1, 0], [0, 1], [0, -1]]
    for i in neighbouring_nodes:
      x = visiting[1] + i[1]
      y = visiting[0] + i[0]
      if [y, x] in bfs_visited:
        continue
      if not maze[y][x]:
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
start_pos = [1, 1]
end_pos = [9, 18]
stack = [start_pos]
neighbors = [[0, 1], [0, -1], [1, 0], [-1, 0]]
mouse_pos = start_pos
while len(stack) > 0:
  current = stack.pop()
  y = current[0]
  x = current[1]
  
  visited = np.append(visited, [[y, x]], axis=0)
  for pos in bfs(mouse_pos, current, collected_maze):
    sleep(0.25)
    xpos = pos[1]
    ypos = pos[0]
    turn_to(go_to(mouse_pos, [ypos, xpos]))
    mouse_pos = [ypos, xpos]
    if mouse_pos in stack:
      visited = np.append(visited, [mouse_pos], axis=0)
      stack.remove(mouse_pos)
    draw_window(mouse_pos[1], mouse_pos[0])
  for i in neighbors:
    new_y = y + i[0]
    new_x = x + i[1]
    if map[new_y][new_x] and not check_in(new_y, new_x, visited) and [new_y,new_x] not in stack:
      stack.append([new_y, new_x])
      original_dir = direction
      direction = go_to(mouse_pos, [new_y, new_x])
      colect_maze(new_x, new_y)
      direction = original_dir

print("The collected maze:")
print(collected_maze)

turn_to(go_to(mouse_pos, start_pos))
draw_window(mouse_pos[1],mouse_pos[0])
mouse_pos = start_pos
sleep(0.5)
turn_to(1)
draw_window(mouse_pos[1],mouse_pos[0])
sleep(2.5)

for pos in bfs(start_pos, end_pos, collected_maze):
  sleep(0.1)
  xpos = pos[1]
  ypos = pos[0]
  turn_to(go_to(mouse_pos, [ypos, xpos]))
  mouse_pos = [ypos, xpos]
  draw_window(mouse_pos[1], mouse_pos[0])
