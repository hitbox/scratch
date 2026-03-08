# Source - https://stackoverflow.com/a
# Posted by Fnord, modified by community. See post 'Timeline' for change history
# Retrieved 2026-01-17, License - CC BY-SA 4.0
import argparse
import math

import matplotlib.pyplot as plt

from mpl_toolkits.mplot3d import Axes3D

def fibonacci_sphere(samples=1000):
    phi = math.pi * (math.sqrt(5.) - 1.)  # golden angle in radians

    for i in range(samples):
        y = 1 - (i / float(samples - 1)) * 2  # y goes from 1 to -1
        radius = math.sqrt(1 - y * y)  # radius at y

        theta = phi * i  # golden angle increment

        x = math.cos(theta) * radius
        z = math.sin(theta) * radius

        yield (x, y, z)

def export_ply(filename, points):
    points = list(points)
    with open(filename, "w") as f:
        f.write("ply\n")
        f.write("format ascii 1.0\n")
        f.write(f"element vertex {len(points)}\n")
        f.write("property float x\n")
        f.write("property float y\n")
        f.write("property float z\n")
        f.write("end_header\n")
        for x, y, z in points:
            f.write(f"{x:.6f} {y:.6f} {z:.6f}\n")

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--samples', type=int, default=500)
    parser.add_argument('--ply')
    args = parser.parse_args(argv)

    points = fibonacci_sphere(args.samples)  # your function

    if args.ply:
        export_ply(args.ply, points)
    else:
        xs, ys, zs = zip(*points)

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(xs, ys, zs, s=10, c='blue')
        ax.set_box_aspect([1,1,1])  # keep aspect ratio 1:1:1
        plt.show()

if __name__ == '__main__':
    main()
