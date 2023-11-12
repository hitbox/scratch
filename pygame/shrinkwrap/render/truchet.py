import rectop

from lib.external import pygame

DEBUGCOLOR = (200,30,200)

CURVE_CONNECTIONS = {
    ('midtop', 'midright'): 'topright',
    ('midright', 'midbottom'): 'bottomright',
    ('midbottom', 'midleft'): 'bottomleft',
    ('midleft', 'midtop'): 'topleft',
}

def tile(midpoints_radius, corners_radius, connections):
    """
    Render truchet tile.
    :param connections: 2-tuples of midpoint names to connect.
    """
    frame_bg_color = (30,) * 3
    tile_bg_color = (60,) * 3
    midpoint_color = (20,) * 3

    # NOTES
    # * maybe the little dots should not be "connectors" they should be "terminators".
    # * transparent "outside the tile" so that the overlapping works.

    small_diameter = midpoints_radius * 2
    big_diameter = corners_radius * 2

    frame_side_length = big_diameter * 2 + small_diameter
    frame_rect = pygame.Rect((0, )*2, (frame_side_length,)*2)

    surf = pygame.Surface(frame_rect.size)
    surf.fill(frame_bg_color)

    sidelen = big_diameter + small_diameter
    tile_rect = rectop.get.new(
        size = (sidelen, ) * 2,
        center = frame_rect.center,
    )

    # fill inner tile area
    pygame.draw.rect(surf, tile_bg_color, tile_rect)

    # separate curves and straight connectors so they can be draw in an order.
    curve_radius = tile_rect.width // 2 + midpoints_radius
    dots = []
    connrects = []
    curves = []
    for attrs in connections:
        attr1, attr2 = attrs
        if attr1 is None:
            dots.append(attr2)
        elif attr2 is None:
            dots.append(attr1)
        elif rectop.get.opposite_midpoint(attr1) == attr2:
            # rect
            point1 = getattr(tile_rect, attr1)
            point2 = getattr(tile_rect, attr2)
            # sort top-bottom, left-right
            point1, point2 = sorted([point1, point2], key=lambda p: (p[1], p[0]))
            if (
                # already confirmed a mid point
                ('top' in attr1 or 'bottom' in attr1)
                and
                ('top' in attr2 or 'bottom' in attr2)
            ):
                # top-bottom
                x = tile_rect.centerx - midpoints_radius
                y = tile_rect.top
                width = small_diameter
                height = tile_rect.height
            else:
                # left-right
                x = tile_rect.left
                y = tile_rect.centery - midpoints_radius
                height = small_diameter
                width = tile_rect.width
            connrect = pygame.Rect(x,y,width,height)
            connrects.append((midpoint_color, connrect, 0))
        else:
            # curve
            # find the corner to put a big circle in for the "curve"
            for ATTRS, pointattr in CURVE_CONNECTIONS.items():
                if set(ATTRS) == set(attrs):
                    break
            else:
                raise ValueError
            corner_point = getattr(tile_rect, pointattr)
            curves.append((midpoint_color, corner_point, curve_radius, 0))
            curves.append((tile_bg_color, corner_point, corners_radius, 0))

    # draw "curves"
    for color, center, radius, width in curves:
        pygame.draw.circle(surf, color, center, radius, width)

    # "clear" the big curve circles from the outside of the tile
    # NOTE: maybe do this with a separate surface, letting clipping do the work?
    for outside_rect in rectop.cut.with_knife(tile_rect, frame_rect):
        pygame.draw.rect(surf, frame_bg_color, outside_rect, 0)

    # draw debugging big circles on corners
    for point in rectop.get.corners(tile_rect):
        pygame.draw.circle(surf, DEBUGCOLOR, point, corners_radius, 1)

    # draw straight horizontal and vertical connectors
    for color, rect, width in connrects:
        pygame.draw.rect(surf, color, rect, width)

    # draw little "connector" circles in midpoints
    for attr in dots:
        point = getattr(tile_rect, attr)
        pygame.draw.circle(surf, midpoint_color, point, midpoints_radius, 0)

    # draw the tile frame
    pygame.draw.rect(surf, DEBUGCOLOR, tile_rect, 1)

    return surf
