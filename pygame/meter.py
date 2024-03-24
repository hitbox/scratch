import string

from collections import UserDict

import pygamelib

from pygamelib import pygame

class Animation:

    def __init__(self, target, attrname, value1, value2, duration, time=0):
        self.target = target
        self.attrname = attrname
        self.value1 = value1
        self.value2 = value2
        self.time = time
        self.duration = duration

    @property
    def is_complete(self):
        return self.time >= self.duration

    def update(self, elapsed):
        if (self.time + elapsed >= self.duration):
            self.time = self.duration
        else:
            self.time += elapsed
        t = self.time / self.duration
        time_value = pygamelib.mix(t, self.value1, self.value2)
        setattr(self.target, self.attrname, time_value)


class AnimationManager:

    def __init__(self):
        self.animations = []

    def update(self, elapsed):
        for animation in self.animations:
            if animation.is_complete:
                animation.commit()


class Meter:

    def __init__(self, total, current=0):
        self.total = total
        self.current = current
        self.final = self.current

    @property
    def current_portion(self):
        return self.current / self.total

    @property
    def change_amount(self):
        return self.final - self.current

    @property
    def change_portion(self):
        return self.change_amount / self.total

    @property
    def is_changing(self):
        return self.current != self.final

    @property
    def final_portion(self):
        return self.final / self.total


class MeterShape:

    def __init__(self, rect):
        self.rect = rect
        self.current_rect = self.rect.copy()
        self.final_rect = self.rect.copy()
        self.changing_rect = self.rect.copy()

    def __call__(self, meter):
        current_portion_width = self.rect.width * meter.current_portion
        self.current_rect.size = (current_portion_width, self.rect.height)
        self.current_rect.topleft = self.rect.topleft

        final_portion_width = self.rect.width * meter.final_portion
        self.final_rect.size = (final_portion_width, self.rect.height)
        self.final_rect.topleft = self.rect.topleft

        if not meter.is_changing:
            self.changing_rect.size = (0, 0)
        else:
            change_portion_width = self.rect.width * meter.change_portion
            pos = self.current_rect.topright
            size = (
                change_portion_width,
                self.rect.height
            )
            self.changing_rect.size = size
            self.changing_rect.topleft = pos
            if meter.change_amount < 0:
                self.changing_rect.normalize()
                self.changing_rect.right = self.current_rect.right
        return self


class MeterRenderer:

    def __init__(
        self,
        shaper,
        font,
        background,
        foreground,
        negchange,
        poschange,
        border = None,
    ):
        self.shaper = shaper
        self.font = font
        self.background = background
        self.foreground = foreground
        self.negchange = negchange
        self.poschange = poschange
        self.border = border

    def __call__(self, screen, meter, rect):
        shape = self.shaper(meter)
        if self.border:
            pygame.draw.rect(screen, self.border, shape.rect, 1)
        fill = 0
        pygame.draw.rect(screen, self.foreground, shape.current_rect, fill)
        if shape.changing_rect:
            if meter.change_amount > 0:
                color = self.poschange
            else:
                color = self.negchange
            pygame.draw.rect(screen, color, shape.changing_rect, fill)


def run(display_size, framerate):
    font = pygamelib.monospace_font(20)

    meter = Meter(total=100, current=50)

    window = pygame.Rect((0,0), display_size)
    ui_rect = window.inflate(-100,-100)

    meter_rect = pygame.Rect(0, 0, window.width * .5, 50)
    meter_rect.center = window.center

    shaper = MeterShape(meter_rect)
    renderer = MeterRenderer(
        shaper,
        font,
        background = 'grey10',
        foreground = 'forestgreen',

        negchange = 'brown',
        poschange = 'gold3',

        border = 'linen',
    )
    animation_manager = AnimationManager()

    interactive = False
    input_line = 'meter.current -= 10'

    clock = pygame.time.Clock()
    elapsed = 0
    running = True
    screen = pygame.display.set_mode(display_size)
    pygame.key.set_repeat(150)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygamelib.post_quit()
                if interactive:
                    if event.key == pygame.K_BACKSPACE:
                        input_line = input_line[:-1]
                    elif event.key == pygame.K_RETURN:
                        eval(compile(input_line, __file__, 'single'))
                        input_line = ''
                    else:
                        input_line += event.unicode
                else:
                    if event.key in (pygame.K_UP, pygame.K_DOWN):
                        if event.key == pygame.K_UP:
                            delta = +20
                        else:
                            delta = -20
                        animation_manager.animations.append(
                            Animation(
                                meter,
                                'current',
                                value1 = meter.current,
                                value2 = meter.current + delta,
                                duration = 200,
                            )
                        )

        screen.fill('black')
        renderer(screen, meter, meter_rect)

        if interactive:
            if input_line is not None:
                image = font.render(input_line, True, 'white')
                input_rect = image.get_rect(midbottom=ui_rect.midbottom)
                screen.blit(image, input_rect)
            else:
                input_rect = pygame.Rect(ui_rect.midbottom, 0, 0)

            # underline prompt
            p1, p2 = pygamelib.bottomline(ui_rect)
            pygame.draw.line(screen, 'white', p1, p2, 1)

            # render prompt
            image = font.render('>', True, 'white')
            screen.blit(image, image.get_rect(bottomright=input_rect.bottomleft))

        pygame.display.flip()

        # update
        elapsed = clock.tick(framerate)
        animation_manager.update(elapsed)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    args = parser.parse_args(argv)
    run(args.display_size, args.framerate)

if __name__ == '__main__':
    main()

# 2024-03-24 Sun.
# - sick of doing work on weekend
# - watching MATN play Revengence
# - talking to chatgpt about animated meter bars
# - here we are
