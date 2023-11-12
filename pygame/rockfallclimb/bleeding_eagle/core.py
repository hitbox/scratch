import pygame
from pygame.locals import *
import os

ASSET_DIR = 'assets/'

class Core:

    # list of tuples of ((event type, event dict), callback) pairs
    callbacks = []

    class screen:
        surface = None
        rect = None

        background = pygame.Color(0,0,0)

        @classmethod
        def init(cls, size):
            os.environ["SDL_VIDEO_CENTERED"] = "1"
            cls.surface = pygame.display.set_mode(size)
            cls.rect = cls.surface.get_rect()

        @classmethod
        def clear(cls):
            cls.surface.fill(cls.background)

        @staticmethod
        def update():
            pygame.display.flip()


    class keys:
        last = None
        _pressed = None

        callbacks = []

        @classmethod
        def pressed(cls, key):
            return cls._pressed[key]

        @classmethod
        def just_pressed(cls, key):
            return cls._pressed[key] and not cls.last[key]

        @classmethod
        def update(cls):
            cls.last = cls._pressed
            cls._pressed = pygame.key.get_pressed()


    class assets:

        @staticmethod
        def image(*path):
            return pygame.image.load(os.path.join(ASSET_DIR, *path))

        @staticmethod
        def animation(sheetfilename, repeat=None, duration=None):
            image = Core.assets.image(sheetfilename)
            return Core.utils.get_animation(image, repeat, duration)


    class utils:

        @staticmethod
        def row_wise_tiles(image, subrect):
            rect = image.get_rect()
            for y in range(0, rect.height, subrect.height):
                row = []
                for x in range(0, rect.width, subrect.width):
                    row.append(image.subsurface(subrect.move(x, y)))
                yield row

        @staticmethod
        def get_tiles(image, subrect):
            rect = image.get_rect()
            for y in range(0, rect.height, subrect.height):
                for x in range(0, rect.width, subrect.width):
                    yield image.subsurface(subrect.move(x, y))

        @staticmethod
        def get_animation(image, repeat=None, duration=None):
            rect = image.get_rect()
            rect.width = rect.height
            tiles = [Frame(tile, duration) 
                     for tile in Core.utils.get_tiles(image, rect)]
            return Animation(tiles, repeat)


    @classmethod
    def init(cls, size, framerate=None, scale=None):
        if framerate is None:
            framerate = 30
        if scale is None:
            scale = 1
        pygame.display.init()
        #
        cls.scale = scale
        cls.screen.init([x * scale for x in size])
        cls._drawbuffer = pygame.Surface(size)
        #
        cls.clock = pygame.time.Clock()
        cls.framerate = framerate
        #
        if cls.scale > 1:
            cls.draw = cls.scaled_draw
        else:
            cls.draw = cls.straight_draw
        # default key bindings
        cls.callbacks.append(
                ((KEYDOWN, {"key" : K_q}), cls.post_quit)
            )

    @classmethod
    def get_apparent_screen_rect(cls):
        if cls.scale == 1:
            return cls.screen.rect.copy()
        else:
            return cls._drawbuffer.get_rect()

    @classmethod
    def straight_draw(cls, scene):
        cls.screen.clear()
        for view in scene.views:
            view.draw(cls.screen.surface)

    @classmethod
    def scaled_draw(cls, scene):
        cls._drawbuffer.fill(cls.screen.background)
        for view in scene.views:
            view.draw(cls._drawbuffer)
        pygame.transform.scale(cls._drawbuffer, 
                               cls.screen.rect.size, 
                               cls.screen.surface)

    @staticmethod
    def post_quit():
        pygame.event.post(pygame.event.Event(QUIT))

    @classmethod
    def start(cls, scene):
        #NOTE: scene is "kept twice" so that other things can change it but it
        #      will only get switched out at a specific time in the loop
        cls.scene = scene
        running = True
        while running:
            scene = cls.scene
            cls.elapsed = cls.clock.tick(cls.framerate)
            # =================================================================
            # update section...
            # NOTE: with callbacks, object's might change their state before
            #       their update method is called
            cls.keys.update()
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                else:
                    for ((etype, edict), callback) in cls.callbacks:
                        # only match the against the binding's "event members"
                        # (as pygame calls 'em)
                        if (etype == event.type and 
                                all(getattr(event, key) == val 
                                    for key, val in edict.items())):
                            callback()
            scene.update()
            scene.draw()
            cls.draw(scene)
            cls.screen.update()


