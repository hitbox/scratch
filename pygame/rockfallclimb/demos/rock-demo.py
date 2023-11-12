import bleeding_eagle

class Rock(bleeding_eagle.Sprite):

    def __init__(self):
        super(Rock, self).__init__(size=(16,16))
        fname = "rock1.png"
        self.animations["falling"] = Core.assets.animation(fname,
                                                           repeat=True, 
                                                           duration=250)
        self.animations["idle"] = Animation([self.animations["falling"].frames[0]])
        self.animation = "idle"


class FallingRocksDemo(Scene):
    "I'm 'a make it rain rocks down on you!"

    def __init__(self):
        super(FallingRocksDemo, self).__init__()
        # =====================================================================
        # Demo will start when S is pressed
        Core.callbacks.append(
                ((KEYDOWN, {"key":K_s}), self.on_keydown_s))
        self.rocks = []
        self.started = False
        self.elapsed = 0
        self.rock_wait = 100
        # =====================================================================
        # testing "little" views
        for view in self.views:
            view.rect_color = pygame.Color(255,0,0)
            #
            view.lens.width /= 2
            view.lens.height /= 2
            #
            view.rect.width /= 2
            view.rect.height /= 2
            view.rect.center = Core.get_apparent_screen_rect().center
            #
            view.surface = pygame.Surface(view.lens.size)
        # =====================================================================
        # Some stars for your background
        # testing scroll factors here
        self.stars = stars = Sprite()
        stars.animations["idle"] = Animation([Frame(Core.assets.image("stars-bg-1.png"))])
        stars.animation = "idle"
        stars.size = stars.image.get_rect().size
        stars._lens_factor_x = 0.25
        stars._lens_factor_y = 0.25
        # center the stars
        r = self.views[0].lens
        stars.x = r.centerx - stars.width / 2
        stars.y = r.centery - stars.height / 2
        self.members.append(stars)
        # =====================================================================
        # Some trees for your foreground
        # testing scroll factors here
        self.trees = trees = Sprite()
        trees.animations["idle"] = Animation([Frame(Core.assets.image("trees-1.png"))])
        trees.animation = "idle"
        trees._lens_factor_x = 1.75
        trees._lens_factor_y = 1.75
        trees.size = trees.image.get_rect().size
        trees.x = stars.x
        trees.y = stars.y + stars.height - trees.height
        self.members.append(trees)
        # =====================================================================
        # Some info for the user
        self.info = info = Sprite()
        # this should make the sprite always appear in the same place inside
        # the view
        info.use_view_lens = False
        info.animations["idle"] = Animation([Frame(Core.assets.image("falling-rocks-demo-1-info.png"))])
        info.animation = "idle"
        info.size = info.image.get_rect().size
        # center the info inside the view
        # NOTE: using rect instead of lens
        r = self.views[0].rect
        info.x = r.centerx - info.width / 2
        info.y = r.centery - info.height / 2
        self.members.append(info)
        # trying this dict thing to keep from "polluting" this scene's
        # attribute space
        self.viewattrs = dict(angle=0, distance=25)
        #
        self.banner = Sprite()
        self.banner.animations["idle"] = Animation(
                [Frame(Core.assets.image("falling-rocks-demo-1-banner.png"))])
        # XXX: set last added animation to current?
        self.banner.animation = "idle"
        self.banner.size = self.banner.image.get_rect().size
        # XXX: better way to report from Core the correct screen size?
        #      or should I get it from the views?
        #      and if so, which view?
        #      How does one center oneself?
        r = self.views[0].lens
        self.banner.x = r.centerx - self.banner.width / 2
        self.banner.y = r.centery - self.banner.height / 2
        self.members.append(self.banner)

    def on_keydown_s(self):
        self.started = True
        self.banner.visible = False

    def update(self):
        self.elapsed += Core.elapsed
        # should not use Core.screen! it's not necessarily the "screen"

        # move the view(s) around a little
        self.viewattrs["angle"] = (self.viewattrs["angle"] + 1) % 360
        for view in self.views:
            a = math.radians(self.viewattrs["angle"])
            view.x = math.cos(a) * self.viewattrs["distance"]
            view.y = math.sin(a) * self.viewattrs["distance"]

        spawn_rock_rect = self.views[0].lens

        if (self.started and len(self.rocks) < 100 and 
                self.elapsed >= self.rock_wait):
            self.elapsed -= self.rock_wait
            rock = Rock()
            rock.x = random.choice(range(-rock.width, 
                                         spawn_rock_rect.width))
            rock.y = random.choice(range(spawn_rock_rect.top - rock.height * 8, 
                                         spawn_rock_rect.top - rock.height))
            # random gravity, hmmm...
            rock.ay = 0.09
            rock.animation = "falling"
            self.rocks.append(rock)
            self.members.append(rock)

        remove_rocks = []

        for rock in self.rocks:
            if rock.rect.top > spawn_rock_rect.bottom:
                remove_rocks.append(rock)

        for rock in remove_rocks:
            self.rocks.remove(rock)
            self.members.remove(rock)

        # trees in front of stars
        self.members.remove(self.trees)
        self.members.append(self.trees)

        # keep info always-on-top
        self.members.remove(self.info)
        self.members.append(self.info)

        super(FallingRocksDemo, self).update()


def main():
    Core.init((256,240), scale=2)
    Core.view_frame_color = (255,0,0)

    scene = FallingRocksDemo()
    Core.start(scene)

if __name__ == "__main__":
    main()

