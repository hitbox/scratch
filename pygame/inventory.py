import itertools as it

from operator import attrgetter
from types import SimpleNamespace

import pygamelib

from pygamelib import pygame

# custom events
MOVECURSOR = pygame.event.custom_type()
GRAB = pygame.event.custom_type()
DROP = pygame.event.custom_type()
ROTATE_HOLDING = pygame.event.custom_type()

CUSTOMTYPENAMES = {
    MOVECURSOR: 'MOVECURSOR',
    GRAB: 'GRAB',
    DROP: 'DROP',
    ROTATE_HOLDING: 'ROTATE_HOLDING',
}

# pygame key id to two-tuple normalized direction vector
MOVEKEY_DELTA = {
    pygame.K_UP: (0, -1),
    pygame.K_RIGHT: (1, 0),
    pygame.K_DOWN: (0, 1),
    pygame.K_LEFT: (-1, 0),
}

class Cursor:
    "Cursor selector on grid."

    def __init__(self, rect, holding=None, hovering=None):
        self.rect = rect
        self.holding = holding
        self.hovering = hovering

    def update_hovering(self, items):
        for item in items:
            if self.rect.colliderect(pygamelib.wrap(item.body)):
                self.hovering = item
                break
        else:
            self.hovering = None


class AttributeAnimation:
    """
    Set an object's attribute from the next value of an iterable, every call.
    """

    def __init__(self, target, attr, iterable):
        self.target = target
        self.attr = attr
        self.iterable = iterable

    def __call__(self):
        value = next(self.iterable)
        setattr(self.target, self.attr, value)


class CursorRenderer:
    """
    Render cursor when it is not holding an item.
    """

    def __init__(self, items):
        self.items = items

    def __call__(self, surf, cursor):
        # nothing to draw if holding an item
        if cursor.holding:
            return
        # not holding
        if cursor.hovering:
            # is hovering
            cursor_rect = pygame.Rect(pygamelib.wrap(cursor.hovering.body))
        else:
            # not hovering
            cursor_rect = cursor.rect
        if cursor.hovering:
            # shimmer hovering item
            image = pygame.Surface(cursor_rect.size, flags=pygame.SRCALPHA)
            image.fill(cursor.fill_color)
            surf.blit(image, cursor_rect)
        pygame.draw.rect(surf, cursor.color, cursor_rect, 1)


class InventoryItemRenderer:
    """
    Render items in an order that keeps the held item on top.
    """

    def __init__(self, shadow_color=None):
        if shadow_color is None:
            shadow_color = pygamelib.get_color('green', a=255//2)
        self.shadow_color = shadow_color

    def __call__(self, surf, grid, cursor, items):
        """
        Render all inventory items onto grid.
        """
        def draw_body(item, body_rect):
            surf.blit(render_rect(body_rect, item.border, item.color), body_rect)

        for item in items:
            if item is cursor.holding:
                continue
            draw_body(item, pygame.Rect(pygamelib.wrap(item.body)))

        if cursor.holding:
            body_rect = pygame.Rect(pygamelib.wrap(cursor.holding.body))
            # draw drop shadow on top
            surf.blit(render_rect(body_rect, fill_color=self.shadow_color), body_rect)
            # draw held item to appear above the grid
            inflate_size = (min(grid.rect.size)*.05, ) * 2
            elevated_rect = grid.rect.inflate(inflate_size)
            elevated_rect.midbottom = (grid.rect.centerx, grid.rect.bottom - 4)
            # remap from grid to elevated rect
            body_rect.center = pygamelib.remap_rect(
                grid.rect,
                body_rect.center,
                elevated_rect,
            )
            draw_body(cursor.holding, body_rect)


class Grid:
    """
    Attributes of the grid to pack items into.
    """

    def __init__(self, rows, cols, cell_size):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size

    @property
    def image_size(self):
        return (
            self.cols * self.cell_size[0],
            self.rows * self.cell_size[1]
        )


class Inventory:

    def __init__(self, grid):
        self.grid = grid
        # items
        # make and move grid cells; and sort for placement later
        self.items = sorted(devel_items(self.grid.cell_size), key=item_body_area)
        # cursor
        self.cursor = Cursor(rect=pygamelib.make_rect(size=self.grid.cell_size))
        self.cursor.color = pygame.Color('yellow')
        self.cursor.fill_color = pygame.Color('yellow')
        self.cursor.renderer = CursorRenderer(self.items)

    def move_cursor(self, delta):
        """
        Move inventory cursor. Moves wrap around grid_rect. Moves take whatever
        cursor is holding with it. Cursor warps through items.
        """
        # TODO
        # - moving left, jump across object that causes wrap, makes cursor appear
        #   to move right instead
        dx, dy = delta
        if self.cursor.holding:
            # Move as if from the topleft of the holding item's body rects. The
            # cursor could be anywhere inside the thing it's holding.
            x, y = self.cursor.holding.body[0].topleft
        else:
            x, y = self.cursor.rect.topleft
        x += dx * self.cursor.rect.width
        y += dy * self.cursor.rect.height

        # fixup x, y as we go along
        if not self.cursor.holding:
            if self.cursor.hovering:
                # warping through items when not holding something
                item_rect = pygame.Rect(pygamelib.wrap(self.cursor.hovering.body))
                if dx < 0:
                    x = item_rect.left - self.cursor.rect.width
                elif dx > 0:
                    x = item_rect.right
                if dy < 0:
                    y = item_rect.top - self.cursor.rect.height
                elif dy > 0:
                    y = item_rect.bottom
                # TODO
                # - do a clamp on (x,y) here to prevent wrapping when jumping
                #   through item

        # gather up rects to move and adjust the right+bottom values for wrapping
        # this is necessary because the wrapping occurs against the topleft
        right, bottom = self.grid.rect.bottomright
        rects = [self.cursor.rect]
        if self.cursor.holding:
            # wrap for dimensions of item, not cursor
            width, height = pygame.Rect(pygamelib.wrap(self.cursor.holding.body)).size
            right -= width - self.cursor.rect.width
            bottom -= height - self.cursor.rect.height
            # add what cursor is holding to list
            rects.extend(self.cursor.holding.body)

        x = pygamelib.modo(x, right, self.grid.rect.left)
        y = pygamelib.modo(y, bottom, self.grid.rect.top)
        pygamelib.move_as_one(rects, x=x, y=y)
        self.cursor.update_hovering(self.items)


class InventoryState(pygamelib.DemoBase):
    "A simple inventory with movement like Resident Evil 4."

    def __init__(self):
        self.background = pygame.display.get_surface().copy()
        self.frame = self.background.get_rect()
        self.font = pygamelib.system_font('arial', 20)
        # help text
        self.help_ = SimpleNamespace(
            color = 'ghostwhite',
            normal_font = pygamelib.system_font('arial', 32),
            frame = self.frame.inflate((-min(self.frame.size)//32, ) * 2),
            lines = [
                'Arrow keys to move',
                'Return or Space to grab and drop',
                'Tab to rotate',
            ],
        )
        # grid
        grid = Grid(rows=7, cols=11, cell_size=(60,)*2)
        grid.image = pygame.Surface(grid.image_size, flags=pygame.SRCALPHA)
        grid.rect = grid.image.get_rect()
        draw_cells(grid.image, pygame.Rect((0,)*2, grid.cell_size), 'azure4')
        # inventory
        self.inventory = Inventory(grid)
        self.inventory.grid.rect = self.inventory.grid.image.get_rect(
            center = self.frame.center
        )
        self.inventory.cursor.rect.topleft = self.inventory.grid.rect.topleft
        # initial position items
        for item in self.inventory.items:
            pygamelib.move_as_one(
                item.body,
                topleft = self.inventory.grid.rect.topleft
            )
        # place items on grid
        items = self.inventory.items[:]
        while items:
            item = items.pop()
            place_item(item, self.inventory.grid, self.inventory.items)

        # render text images and rects
        self.help_.images = render_lines(
            self.help_.normal_font, self.help_.color, self.help_.lines
        )
        self.help_.rects = [image.get_rect() for image in self.help_.images]
        # align text rects
        self.help_.rects[0].topright = self.help_.frame.topright
        align(self.help_.rects, {'topright': 'bottomright'})
        # bake background
        for image, rect in zip(self.help_.images, self.help_.rects):
            self.background.blit(image, rect)
        self.background.blit(self.inventory.grid.image, self.inventory.grid.rect)
        self.item_renderer = InventoryItemRenderer()
        self.animations = [
            AttributeAnimation(
                self.inventory.cursor.fill_color,
                'a', # alpha
                it.cycle(
                    int(pygamelib.mix(frametime/10, 255*.25, 255*.50))
                    for time in it.chain(range(10), range(9, 0, -1))
                    for frametime in it.repeat(time, 2)
                )
            ),
        ]

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        if event.key in (pygame.K_q, ):
            # quit
            pygamelib.post_quit()
        elif event.key in MOVEKEY_DELTA:
            # key to move event
            delta = MOVEKEY_DELTA[event.key]
            post_movecursor(delta, self.inventory.grid)
        elif event.key == pygame.K_TAB:
            # rotate item cursor is holding
            post_rotate_holding(self.inventory.cursor)
        elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
            # grab/drop item
            if self.inventory.cursor.holding:
                post_event = post_drop
            else:
                post_event = post_grab
            post_event(self.inventory.cursor, self.inventory.items)

    def do_userevent(self, event):
        if event.type == MOVECURSOR:
            self.do_movecursor(event)
        elif event.type == ROTATE_HOLDING:
            self.do_rotate(event)
        elif event.type == GRAB:
            self.do_grab(event)
        elif event.type == DROP:
            self.do_drop(event)

    def do_movecursor(self, event):
        """
        Move Cursor
        """
        self.inventory.move_cursor(event.delta)

    def do_rotate(self, event):
        """
        Rotate item current held by cursor.
        """
        if self.inventory.cursor.holding:
            rotate_holding(self.inventory.cursor, self.inventory.grid.rect)

    def do_grab(self, event):
        """
        Grab Item
        """
        item = cursor_collideitem(self.inventory.cursor, self.inventory.items)
        if item:
            self.inventory.cursor.holding = item

    def do_drop(self, event):
        """
        Drop Item
        """
        was_holding = self.inventory.cursor.holding
        items = cursor_collideitem_all(
            self.inventory.cursor,
            self.inventory.items
        )
        other_colliding = [item for item in items if item is not was_holding]
        if len(other_colliding) == 1:
            # item dropped onto another, pick the other up
            self.inventory.cursor.holding = other_colliding[0]
            self.inventory.cursor.rect.clamp_ip(pygamelib.wrap(other_colliding[0].body))
        elif len(other_colliding) == 0:
            # item dropped into empty space
            self.inventory.cursor.holding = None

    def do_videoexpose(self, event):
        self.draw()

    def update(self):
        super().update()
        for animation in self.animations:
            animation()
        self.draw()

    def draw(self):
        "Draw Inventory"
        self.screen.blit(self.background, (0,)*2)
        # items
        self.item_renderer(
            self.screen,
            self.inventory.grid,
            self.inventory.cursor,
            self.inventory.items
        )
        # cursor
        self.inventory.cursor.renderer(self.screen, self.inventory.cursor)
        # item text
        item = self.inventory.cursor.hovering or self.inventory.cursor.holding
        if item:
            image = self.help_.normal_font.render(item.name, True, item.font.color)
            rect = image.get_rect(bottomleft=self.help_.frame.bottomleft)
            self.screen.blit(image, rect)
        pygame.display.flip()


def render_lines(font, color, lines, antialias=True):
    """
    Render lines of text with a font.
    """
    def render_line(line):
        "Reorganize arguments for use with map"
        return font.render(line, antialias, color)
    return list(map(render_line, lines))

def post_movecursor(delta, grid):
    event = pygame.event.Event(MOVECURSOR, delta=delta)
    pygame.event.post(event)

def post_grab(cursor, items):
    event = pygame.event.Event(GRAB, cursor=cursor, items=items)
    pygame.event.post(event)

def post_drop(cursor, items):
    event = pygame.event.Event(DROP, cursor=cursor, items=items)
    pygame.event.post(event)

def post_rotate_holding(cursor):
    event = pygame.event.Event(ROTATE_HOLDING, cursor=cursor)
    pygame.event.post(event)

def align(rects, attrmap):
    """
    Align rects in iterable order
    :param rects: list of rects.
    :param attrmap: mapping of attribute names.
    """
    # allow for many ways to give mapping but this uses dict interface
    attrmap = dict(attrmap)
    for prevrect, rect in it.pairwise(rects):
        if not rect:
            continue
        for key, prevkey in attrmap.items():
            setattr(rect, key, getattr(prevrect, prevkey))

def cursor_collideitem(cursor, items):
    if cursor.holding:
        cursor_rect = pygame.Rect(pygamelib.wrap(cursor.holding.body))
    else:
        cursor_rect = cursor.rect
    for item in items:
        if cursor_rect.colliderect(pygamelib.wrap(item.body)):
            return item

def cursor_collideitem_all(cursor, items):
    if cursor.holding:
        cursor_rect = pygame.Rect(pygamelib.wrap(cursor.holding.body))
    else:
        cursor_rect = cursor.rect
    return [item for item in items if cursor_rect.colliderect(pygamelib.wrap(item.body))]

def makegrid(rect_size, rows, columns):
    """
    Return list of rects of given size, arranged in a grid of rows and columns.
    """
    width, height = rect_size
    yield from (
        pygame.Rect(width*i, height*j, width, height)
        for i, j in it.product(range(rows), range(columns))
    )

def render_rect(
    rect,
    border_color = None,
    fill_color = None,
    width = 1,
    flags = pygame.SRCALPHA
):
    # allows "rect drawing" with alpha in color
    surf = pygame.Surface(rect.size, flags=flags)
    if fill_color:
        surf.fill(fill_color)
    if border_color:
        pygame.draw.rect(surf, border_color, rect, width)
    return surf

def draw_grid(surface, cell_size, *colors, line_width=1):
    if len(colors) != line_width:
        raise ValueError
    cell_width, cell_height = cell_size
    rect = surface.get_rect()
    offset_start = -line_width // 2
    for x in range(cell_width, rect.width, cell_width):
        for offset, color in enumerate(colors, start=offset_start):
            p1 = (x+offset, 0)
            p2 = (x+offset, rect.height)
            pygame.draw.line(surface, color, p1, p2, 1)
    for y in range(cell_height, rect.height, cell_height):
        for offset, color in enumerate(colors, start=offset_start):
            p1 = (0, y+offset)
            p2 = (rect.width, y+offset)
            pygame.draw.line(surface, color, p1, p2, 1)

def draw_cells(surface, rect, color, width=1):
    """
    Draw the grid the way the cells are displayed--next to each other.
    """
    frame = surface.get_rect()
    # save x
    x = rect.x
    while True:
        while True:
            pygame.draw.rect(surface, color, rect, width)
            rect = pygamelib.make_rect(rect, left=rect.right)
            if not frame.contains(rect):
                break
        rect = pygamelib.make_rect(rect, x=x, top=rect.bottom)
        if not frame.contains(rect):
            break

def rotate_rects(rects):
    """
    Rotate rects 90 degrees.

    Rects are grouped into rows by their y attribute, in a nested list.
    Transpose the list and use its order to reflow the rects' positions from
    topleft.
    """
    grouped = it.groupby(sorted(rects, key=gety), key=gety)
    table = (list(items) for key, items in grouped)
    #
    rotated_table = zip(*table)
    wrapped = pygame.Rect(pygamelib.wrap(rects))
    left, top = wrapped.topleft
    for row in rotated_table:
        row = sorted(row, key=getx)
        row[0].left = left
        for r1, r2 in pygamelib.nwise(row):
            r1.top = top
            if r2:
                r2.topleft = (r1.right, top)
        top = r1.bottom

def clamp_many(rects, inside):
    # XXX: is move_as_one doing too much? since we're duplicating stuff here.
    wrapped = pygame.Rect(pygamelib.wrap(rects))
    moved = wrapped.clamp(inside)
    pygamelib.move_as_one(rects, topleft=moved.topleft)

def rotate_holding(cursor, grid_rect):
    """
    Rotate the item the cursor is holding and constrain to the grid.
    """
    rects = cursor.holding.body + [cursor.rect]
    # TODO
    # - rotate can put item outside grid
    rotate_rects(rects)
    clamp_many(rects, grid_rect)
    cursor.rect.clamp_ip(pygamelib.wrap(cursor.holding.body))

def place_item(item, grid, items):
    """
    """
    item_wrap = pygame.Rect(pygamelib.wrap(item.body))
    cells = list(makegrid(grid.cell_size, grid.rows, grid.cols))
    pygamelib.move_as_one(cells, topleft=grid.rect.topleft)
    filled = [rect for item in items for rect in item.body]
    for cell_rect in cells:
        item_wrap = pygamelib.make_rect(item_wrap, topleft=cell_rect.topleft)
        if not any(item_wrap.colliderect(filled_rect) for filled_rect in filled):
            return pygamelib.move_as_one(item.body, topleft=cell_rect.topleft)

def item_body_area(item):
    """
    Area of an items entire body of rects.
    """
    wrapped = pygame.Rect(pygamelib.wrap(item.body))
    return wrapped.width * wrapped.height

def devel_items(cell_size):
    """
    Hard-coded item objects for development.
    """
    pistol = SimpleNamespace(
        name = 'Pistol',
        color = 'red',
        border = 'darkred',
        rows = 2,
        cols = 3,
        font = SimpleNamespace(
            color = 'red',
        ),
    )
    pistol.body = list(makegrid(cell_size, pistol.rows, pistol.cols))
    rotate_rects(pistol.body)

    rifle = SimpleNamespace(
        name = 'Rifle',
        color = 'burlywood4',
        border = 'burlywood',
        rows = 1,
        cols = 9,
        font = SimpleNamespace(
            color = 'burlywood4',
        ),
    )
    rifle.body = list(makegrid(cell_size, rifle.rows, rifle.cols))
    rotate_rects(rifle.body)

    grenade = SimpleNamespace(
        name = 'Grenade',
        color = 'darkgreen',
        border = 'green',
        rows = 2,
        cols = 1,
        font = SimpleNamespace(
            color = 'darkgreen',
        ),
    )
    grenade.body = list(makegrid(cell_size, grenade.rows, grenade.cols))
    rotate_rects(grenade.body)

    chicken_egg = SimpleNamespace(
        name = 'Egg',
        color = 'oldlace',
        border = 'ghostwhite',
        rows = 1,
        cols = 1,
        font = SimpleNamespace(
            color = 'oldlace',
        ),
    )
    chicken_egg.body = list(makegrid(cell_size, chicken_egg.rows, chicken_egg.cols))
    rotate_rects(chicken_egg.body)

    items = [pistol, rifle, grenade, chicken_egg]
    return items

def start(options):
    """
    Initialize and start run loop. Bridge between options and main loop.
    """
    pygame.display.set_caption('pygame - inventory')

    settings = SimpleNamespace(
        window = pygame.display.set_mode(options.display_size),
        clock = pygame.time.Clock(),
    )
    settings.background = settings.window.copy()
    settings.frame = settings.window.get_rect()

    engine = pygamelib.Engine()
    state = InventoryState()
    engine.run(state)

def main(argv=None):
    """
    Inventory
    """
    parser = pygamelib.command_line_parser()
    args = parser.parse_args()
    start(args)

getx = attrgetter('x')
gety = attrgetter('y')

if __name__ == '__main__':
    main()

# saw this:
# https://www.reddit.com/r/pygame/comments/xasi84/inventorycrafting_system/
# TODO:
# [X] Like Resident Evil 4 in 2d
# [X] grab / drop
# [ ] Auto arrange with drag+drop animations
# [X] Rotate items
# [ ] Stacking?
# [ ] Combine to new item?
# [ ] Stealing minigame. Something chases or attacks your cursor.
# [ ] Moving through items are a way of jumping, could be part of gameplay.
# [ ] `.removable` attribute to prevent dropping.
# [ ] Drop item grid to drop items.
# [ ] Inform7, dialog (https://linusakesson.net/dialog/), etc. engine to do
#     things like automatically unlock the unremovable item before dropping
#     it, if have the key.
# [ ] Another inventory for incorporeal items, like keys?
# [ ] Inner grid games inside your inventory. Like tic-tac-toe, maybe even
#     checkers or chess.
# [ ] state machine for hovering -> grabbing -> dropping...
