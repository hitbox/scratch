class EntityDatabase:

    def __init__(self):
        self.entities = {}

    def new(self, with_components=None):
        if with_components is None:
            with_components = {}
        if self.entities:
            id_ = max(self.entities) + 1
        else:
            id_ = 0

        self.entities[id_] = with_components
        return id_

    def get(self, id_):
        return self.entities.get(id_)

    def select(self, *components):
        for entity_id, _components in self.entities.items():
            keys = set(components).issubset(_components)
            if not keys:
                continue
            if len(components) > 1:
                yield tuple(_components[key] for key in components)
            else:
                yield _components[components[0]]

    def one(self, *components):
        iterable = self.select(*components)
        try:
            entity = next(iterable)
        except StopIteration:
            raise ValueError('no entity for one')
        else:
            try:
                next(iterable)
            except StopIteration:
                # good
                pass
            else:
                raise ValueError('more than one result for one')


def ecs_database():
    db = EntityDatabase()
    db.new(
        with_components = dict(
            id = 'meter',
            shape = dict(
                rect = (0, 0, 100, 10),
            ),
        )
    )
    return db

def run(display_size, framerate):
    db = ecs_database()
    meter_id = db.one('id')
