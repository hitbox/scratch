import pygame
import math

# Initialize pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Visualization - Hyperbolic Functions")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Camera settings
fov = 60
depth = 10

# Initial camera parameters
angle_x = 0
angle_y = 0

def project(x, y, z):
    """Project 3D coordinates onto 2D screen."""
    scale = fov / (fov + z)
    x = int(WIDTH / 2 + x * scale)
    y = int(HEIGHT / 2 + y * scale)
    return x, y

def rotate(x, y, z, angle_x, angle_y):
    """Rotate 3D coordinates around the x and y axes."""
    # Rotation around x-axis
    new_y = y * math.cos(angle_x) - z * math.sin(angle_x)
    new_z = y * math.sin(angle_x) + z * math.cos(angle_x)

    # Rotation around y-axis
    new_x = x * math.cos(angle_y) - z * math.sin(angle_y)
    new_z = x * math.sin(angle_y) + z * math.cos(angle_y)

    return new_x, new_y, new_z

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill(BLACK)

    # Get mouse position
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Calculate rotation angles based on mouse position
    angle_x = (mouse_y - HEIGHT / 2) * 0.01
    angle_y = (mouse_x - WIDTH / 2) * 0.01

    # Draw 3D points
    for x in range(-5, 6):
        for y in range(-5, 6):
            # Calculate z-coordinate using hyperbolic functions
            z_sinh = math.sinh(x) * math.cosh(y)
            z_cosh = math.cosh(x) * math.sinh(y)

            # Rotate 3D coordinates
            x_sinh, y_sinh, z_sinh = rotate(x, y, z_sinh, angle_x, angle_y)
            x_cosh, y_cosh, z_cosh = rotate(x, y, z_cosh, angle_x, angle_y)

            # Project and draw 3D coordinates onto 2D screen
            sx, sy = project(x_sinh, y_sinh, z_sinh)
            pygame.draw.circle(screen, WHITE, (sx, sy), 2)

            sx, sy = project(x_cosh, y_cosh, z_cosh)
            pygame.draw.circle(screen, WHITE, (sx, sy), 2)

    pygame.display.flip()

# Quit pygame
pygame.quit()
