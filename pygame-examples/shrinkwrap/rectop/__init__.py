from . import cut
from . import get
from . import handle
from . import is_
from . import join
from . import query
from . import resize
from .constants import CORNERS
from .constants import LINES
from .constants import MIDPOINTS
from .constants import POINTS
from .constants import SIDES

def update(rect, **kwargs):
    for key, val in kwargs.items():
        setattr(rect, key, val)
