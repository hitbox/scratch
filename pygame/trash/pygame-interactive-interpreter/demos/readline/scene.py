from codeop import CommandCompiler

from engine.engine import stopengine
from lib.external import pygame
from lib.screen import Screen
from scenes.base import BaseScene

from lib.readline import Readline

from .mapping import pygame2readline
from .renderer import ReadlineRenderer

class ReadlineScene(BaseScene):
    """
    Read a single line in a pygame gui.
    """
    readline_renderer_class = ReadlineRenderer

    def enter(self):
        pass

    def exit(self):
        pass

    def __init__(self, screen_size):
        if screen_size is None:
            screen_size = (800, 600)
        self.screen = Screen(screen_size)
        self.ui_frame = self.screen.rect.inflate(*(-50,)*2)
        pygame.font.init()
        # XXX:
        # * don't know what to do about pygame.font
        # * would like it to be more nicely abstracted like Screen
        self.font = pygame.font.SysFont('monospace', 30)
        self.readline = Readline()
        self.readline.send('dir()')
        self.readline_renderer = self.readline_renderer_class(self.font)
        self.help = self.font.render('Return to commit to stdout and clear.', True, (200,)*3)
        self.compile = CommandCompiler()

    def on_event(self, event):
        """
        Dispatch event to handler.
        """
        if event.type == pygame.QUIT:
            # NOTE: had a thought: maybe a "root" scene that stops the engine
            #       on `enter`.
            stopengine()
        elif event.type == pygame.KEYDOWN:
            self.on_keydown(event)

    def on_keydown(self, event):
        # XXX:
        # * seems like an awful lot going on in here
        # * another object to map from pygame keys, mods, etc. to `Readline.method`?

        if (event.key == pygame.K_ESCAPE):
            self.quit()
        # commit on return
        elif (event.key == pygame.K_RETURN):
            # TODO:
            # * how to communicate that we've received a line, to something else?
            # * initialize/accept a file-like to write to?
            # * use the lib.readline object for communication? should pass in then.
            source = self.readline.get_line()
            self.readline.reset()
        else:
            callback, args = pygame2readline(event, self.readline)
            if callback:
                callback(*args)

    def quit(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def runsource(self, source, filename='<input>', symbol='single'):
        try:
            code = self.compile(source)
        except (OverflowError, SyntaxError, ValueError):
            #
            self.showsyntaxerror(filename)
            return False

        if code is None:
            # need more lines
            return True

        self.runcode(code)
        return False

    def runcode(self, code):
        try:
            exec(code, self.locals)
        except SystemExit:
            self.quit()
        except:
            self.showtraceback()

    def showsyntaxerror(filename):
        # TODO: subclass code.InteractiveInterpreter and implement `write`
        pass

    def showtraceback(self):
        pass

    def render_cursor_split(self, readline):
        s = str(readline.cursor_split())
        image = self.font.render(s, True, (200,)*3)
        return image

    def update(self, events):
        # events
        for event in events:
            self.on_event(event)
        # draw
        self.screen.clear()
        inside = self.screen.rect.inflate(-50, -50)
        pygame.draw.rect(self.screen.surface, (200,10,10), inside, 1)
        image = self.readline_renderer.render(self.readline, inside)
        self.screen.blit(image, image.get_rect(midleft=inside.midleft))
        self.screen.blit(self.help, self.help.get_rect(midtop=self.screen.rect.midtop))
        self.screen.update()
