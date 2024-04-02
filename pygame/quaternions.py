import argparse
import math

from collections import namedtuple

class Quaternion(namedtuple('Quaternion', 'w x y z')):

    def __mul__(q1, q2):
        w1, x1, y1, z1 = q1
        w2, x2, y2, z2 = q2
        w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
        x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
        y = w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2
        z = w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2
        return Quaternion(w, x, y, z)

    @classmethod
    def from_euler(cls, euler):
        yaw, pitch, roll = euler
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)

        w = cy * cp * cr + sy * sp * sr
        x = cy * cp * sr - sy * sp * cr
        y = sy * cp * sr + cy * sp * cr
        z = sy * cp * cr - cy * sp * sr

        return cls(w, x, y, z)

    def normalize(self):
        norm = math.sqrt(sum(value*value for value in self))
        w, x, y, z = (value / norm for value in self)
        return Quaternion(w, x, y, z)

    def slerp_to(self, other, time):
        w1, x1, y1, z1 = self.normalize()
        w2, x2, y2, z2 = other.normalize()

        dot = w1 * w2 + x1 * x2 + y1 * y2 + z1 * z2

        # ensure shortest path
        if dot < 0:
            dot = -dot
            w2 = -w2
            x2 = -x2
            y2 = -y2
            z2 = -z2

        if dot > 0.9995:
            result = q1 + time * (q2 - q1)
            result.normalize()
            return result

        theta_0 = math.acos(dot)
        theta = theta_0 * time
        sin_theta = math.sin(theta)
        sin_theta_0 = math.sin(theta_0)

        s0 = math.cos(theta) - dot * sin_theta / sin_theta_0
        s1 = sin_theta / sin_theta_0

        return Quaternion(
            s0 * w1 + s1 * w2,
            s0 * x1 + s1 * x2,
            s0 * y1 + s1 * y2,
            s0 * z1 + s1 * z2,
        )

    def as_euler(self):
        norm = math.sqrt(sum(q * q for q in self))
        w, x, y, z = (q / norm for q in self)

        roll = math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
        pitch = math.asin(2 * (w * y - z * x))
        yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))

        return (roll, pitch, yaw)


def quaternion_multiply(q1, q2):
    """
    Multiplies two quaternions.
    """
    w = q1.w * q2.w - q1.x * q2.x - q1.y * q2.y - q1.z * q2.z
    x = q1.w * q2.x + q1.x * q2.w + q1.y * q2.z - q1.z * q2.y
    y = q1.w * q2.y - q1.x * q2.z + q1.y * q2.w + q1.z * q2.x
    z = q1.w * q2.z + q1.x * q2.y - q1.y * q2.x + q1.z * q2.w
    return Quaternion(w, x, y, z)

def normalize(quaternion):
    """
    Normalizes a quaternion.
    """
    norm = math.sqrt(quaternion.w**2 + quaternion.x**2 + quaternion.y**2 + quaternion.z**2)
    return Quaternion(quaternion.w / norm, quaternion.x / norm, quaternion.y / norm, quaternion.z / norm)

def main():
    # Example usage:
    # Identity quaternion
    q1 = Quaternion(1, 0, 0, 0)
    # Quaternion representing 45 degree rotation around y-axis
    q2 = Quaternion(math.cos(math.pi/4), 0, math.sin(math.pi/4), 0)

    print("Quaternion 1:", q1)
    print("Quaternion 2:", q2)

    # Quaternion multiplication
    result = quaternion_multiply(q1, q2)  # Multiply q1 by q2
    print("Result of quaternion multiplication:", result)

    # Normalization
    result = normalize(result)
    print("Normalized result:", result)

if __name__ == '__main__':
    main()

# 2024-04-01 Mon.
# - prompted chatgpt with "quaternions" and asked for an example in Python
