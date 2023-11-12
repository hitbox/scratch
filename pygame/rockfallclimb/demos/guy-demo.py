import pygame

from bleeding_eagle.sprite import Sprite
from bleeding_eagle.core import Core
from bleeding_eagle.scene import Scene
from bleeding_eagle.animation import Animation
from bleeding_eagle.frame import Frame

class Guy(Sprite):

    def __init__(self):
        super(Guy, self).__init__()
        #
        image = Core.assets.image("guy-1.png")
        tiles = Core.utils.row_wise_tiles(image, pygame.Rect(0,0,16,16))
        (idle_tiles, yawn_tiles, run_tiles, jump_tiles) = tiles
        self.animations["idle"] = Animation([Frame(idle_tiles[0])])

        self.animations["yawn"] = Animation(
                [Frame(tile, duration=200) 
                 for tile in yawn_tiles[:7]],
                repeat=False)

        self.animations["run_right"] = Animation(
                [Frame(tile, duration=100) for tile in run_tiles],
                repeat=True)

        self.animations["run_left"] = Animation(
                [Frame(pygame.transform.flip(tile, True, False), 
                       duration=100) 
                 for tile in run_tiles],
                repeat=True)

        self.animations["jump"] = Animation(
                [Frame(tile, duration=50) for tile in jump_tiles[:4]],
                repeat=False)
        self.animation = "idle"
        # guy's size
        self.size = self.image.get_rect().size
        #
        self.idle_elapsed = 0
        self.yawn_time = 1000 # ms
        #

    def update(self):

        if Core.keys.pressed(pygame.K_LEFT):
            self.animation = "run_left"
        elif Core.keys.pressed(pygame.K_RIGHT):
            self.animation = "run_right"
        elif Core.keys.pressed(pygame.K_UP):
            self.animation = "jump"
        else:
            self.animation = "idle"

        if self.animation is not self.animations["jump"]:
            self.animations["jump"].reset()

        super(Guy, self).update()


class GuyDemo(Scene):

    def __init__(self):
        super(GuyDemo, self).__init__()
        # =====================================================================
        # The Guy (you)
        self.guy = guy = Guy()
        # guy's position
        guy.x = self.views[0].lens.centerx
        guy.y = self.views[0].lens.centery
        self.members.append(guy)
        # =====================================================================
        self.info = info = Sprite()
        frames = [Frame(Core.assets.image("guy-demo-info-1.png"))]
        info.animations["idle"] = Animation(frames)
        info.animation = "idle"
        self.members.append(info)

def main():
    Core.init((256,240), scale=2)
    Core.start(GuyDemo())

if __name__ == "__main__":
    main()

