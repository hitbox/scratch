import pygame

import core
import base

class Sprite(base.Base):

    _visible = True

    _use_view_lens = None # defaults to True in __init__

    _lens_factor_x = 1.0
    _lens_factor_y = 1.0

    def __init__(self, position=None, size=None, velocity=None,
                       acceleration=None):
        super(Sprite, self).__init__()
        if position is None:
            position = (0., 0.)
        if size is None:
            size = (0., 0.)
        if velocity is None:
            velocity = (0., 0.)
        if acceleration is None:
            acceleration = (0., 0.)
        self.x, self.y = position
        self.width, self.height = size
        self.vx, self.vy = velocity
        self.ax, self.ay = acceleration
        # view stuff
        self.is_view_aligned = True
        # animation stuff
        self.animations = {}
        self._animation = None
        #
        self.use_view_lens = True

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value
        self._which_draw_to_use()

    def _which_draw_to_use(self):
        if self._animation is None or not self._visible:
            self.draw = self._no_draw
        else:
            if self._use_view_lens:
                self.draw = self._draw_lens
            else:
                self.draw = self._draw_no_lens

    def _no_draw(self):
        pass

    @property
    def use_view_lens(self):
        return self._use_view_lens

    @use_view_lens.setter
    def use_view_lens(self, value):
        self._use_view_lens = value
        self._which_draw_to_use()

    @property
    def size(self):
        return self.width, self.height

    @size.setter
    def size(self, value):
        self.width, self.height = value

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), 
                           int(self.width), int(self.height))

    @property
    def animation(self):
        return self._animation

    @animation.setter
    def animation(self, name):
        # set what animation is playing
        # maybe this would be better as a "verb" (i.e.: a method, e.g.:
        # sprite.play(name))
        self._animation = self.animations[name]
        self._which_draw_to_use()

    @property
    def image(self):
        return self._animation.image

    # trying out switching draw to point at different methods
    # probably be easier just to figure out in one draw method what rects to
    # use

    def _draw_lens(self):
        if self._animation is None:
            return
        # draw ourselves, if we should, on all of the current scene's views
        for view in core.Core.scene.views:
            if not view.lens.colliderect(self.rect):
                continue
            # we're colliding with a this view
            if view.lens.contains(self.rect):
                # simple easy case, we're all inside the view what to draw on
                # the view's surface...
                image = self.image
                # ...and where
                x = self.rect.x - view.lens.x
                y = self.rect.y - view.lens.y
            else:
                # we are only partially within the lens of the view get the
                # part of our sprite's image to draw (world-space)
                cliprect = self.rect.clip(view.lens)
                # where to draw (world-space)
                x, y = cliprect.topleft
                x -= view.lens.x
                y -= view.lens.y
                # part of our image (need image-space, hence the move)
                imagerect = cliprect.move(-self.rect.x, -self.rect.y)
                image = self.image.subsurface(imagerect)
            x *= self._lens_factor_x
            y *= self._lens_factor_y
            view.surface.blit(image, (x, y))

    def _draw_no_lens(self):
        if self._animation is None:
            return
        # draw ourselves, if we should, on all of the current scene's views
        for view in core.Core.scene.views:
            if not view.rect.colliderect(self.rect):
                continue
            # we're colliding with a this view
            if view.rect.contains(self.rect):
                # simple easy case, we're all inside the view what to draw on
                # the view's surface...
                image = self.image
                # ...and where
                x = self.rect.x - view.rect.x
                y = self.rect.y - view.rect.y
            else:
                # we are only partially within the lens of the view get the
                # part of our sprite's image to draw (world-space)
                cliprect = self.rect.clip(view.rect)
                # where to draw (world-space)
                x, y = cliprect.topleft
                x -= view.rect.x
                y -= view.rect.y
                # part of our image (need image-space, hence the move)
                imagerect = cliprect.move(-self.rect.x, -self.rect.y)
                image = self.image.subsurface(imagerect)
            view.surface.blit(image, (x, y))

    def update_motion(self):
        self.vx += self.ax
        self.vy += self.ay
        self.x += self.vx
        self.y += self.vy

    def update(self):
        if self._animation is not None:
            self._animation.update()
        self.update_motion()


