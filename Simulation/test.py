# Import necessary libraries
import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the screen
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 900
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Lawn Mower Simulation')

square_size = 45
# Define colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# Load the mouse image
mouse = pygame.image.load("mouse.png")
mouse = pygame.transform.scale(mouse, (int(square_size * 0.8), square_size))
mouse_rect = mouse.get_rect()

# Set initial position for the mouse
mouse_x, mouse_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

# Set the initial direction (1 for right, -1 for left)
direction = 1

# Set the step to the side
side_step = 20

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Update mouse position (back-and-forth motion)
    mouse_x += direction * 5  # Adjust the speed as needed

    # Reverse direction when reaching screen edges
    if mouse_x <= 0 or mouse_x >= SCREEN_WIDTH:
        direction *= -1
        mouse_y += side_step  # Take one step to the side

    # Draw the screen
    SCREEN.fill(WHITE)
    SCREEN.blit(mouse, (mouse_x, mouse_y))

    # Update the display
    pygame.display.flip()

    # Add a small delay to control frame rate
    pygame.time.delay(50)

# Clean up and exit
pygame.quit()
sys.exit()