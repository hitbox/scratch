import math

from bleeding_eagle.core import Core
from bleeding_eagle.scene import Scene
from bleeding_eagle.frame import Frame
from bleeding_eagle.sprite import Sprite
from bleeding_eagle.animation import Animation

class TitleSprite(Sprite):
    "The one and only sprite for this little demo"
    def __init__(self):
        super(TitleSprite, self).__init__()
        # NOTES: * this is ugly
        #        * does everything have to be an animation?
        #        * maybe assets shouldn't be in the Core?
        #        * because sprite-demo's assets should probably be in the same
        #          directory as sprite-demo.py
        idle_images = [Core.assets.image("sprite-demo", "title.png")]
        idle_anim = Animation([Frame(img) for img in idle_images])
        self.animations["idle"] = idle_anim
        self.animation = "idle"
        self.size = self.image.get_rect().size

class SpriteDemo(Scene):

    def __init__(self):
        super(SpriteDemo, self).__init__()
        self.title = title = TitleSprite()
        self.members.append(title)
        # we're going to move the title around with these
        self.angle = 0
        self.dangle = math.radians(2)
        self.dist = 75

    @property
    def view(self):
        # shortcut to the one and only view
        return self.views[0]

    def update(self):
        self.angle = (self.angle + self.dangle) % (2 * math.pi)
        # NOTES: * This is ugly as sin.
        #        * Really really need sprites to have a rect attribute.
        #        * Except that we really need floats for positions too.
        #        * ...or maybe decimal.Decimals but anyway something besides
        #          ints
        x, y = self.view.lens.center
        self.title.x = (x + math.cos(self.angle) * self.dist) - (self.title.width / 2)
        self.title.y = (y + math.sin(self.angle) * self.dist) - (self.title.height / 2)
        super(SpriteDemo, self).update()


def main():
    Core.init((256,240), scale=2)
    Core.start(SpriteDemo())

if __name__ == "__main__":
    main()

