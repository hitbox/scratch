import tkinter as tk
import math

WIDTH = 800
HEIGHT = 800
CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT // 2
RADIUS_INCREMENT = 5
MAX_RADIUS = min(WIDTH, HEIGHT) // 2
SHOCKWAVE_COUNT = 2
SHOCKWAVE_GAP = 20

class CircleEdge:
    """
    Inside or outside of circle shockwave. Really just a circle. Need to have animation.
    """

    def __init__(self):
        pass


class CircleShockwave:

    def __init__(self, circle_edge1, circle_edge2):
        pass


class CircleAnimation:

    def __init__(self, canvas):
        self.canvas = canvas
        self.radius = 0
        self.shockwave_radii = [0] * SHOCKWAVE_COUNT

    def update(self):
        self.canvas.delete("all")

        # Update main circle radius
        self.radius += RADIUS_INCREMENT
        if self.radius > MAX_RADIUS:
            self.radius = 0

        # Draw main circle
        self.draw_circle(CENTER_X, CENTER_Y, self.radius)

        # Update and draw shockwave circles
        for i in range(SHOCKWAVE_COUNT):
            shockwave_radius = self.radius - i * SHOCKWAVE_GAP
            if shockwave_radius > 0:
                self.draw_circle(CENTER_X, CENTER_Y, shockwave_radius)

        # Schedule the next update
        self.canvas.after(50, self.update)

    def draw_circle(self, x, y, radius):
        self.canvas.create_oval(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            outline="white",
        )


def main():
    root = tk.Tk()

    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="black")
    canvas.pack()

    animation = CircleAnimation(canvas)
    animation.update()
    root.mainloop()

if __name__ == "__main__":
    main()
