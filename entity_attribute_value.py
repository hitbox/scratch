import argparse
import sqlalchemy as sa

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):

    @sa.orm.declared_attr.directive
    def __tablename__(cls):
        return cls.__name__.lower()


class Entity(Base):

    id = sa.Column(
        sa.Integer,
        primary_key = True,
    )

    name = sa.Column(
        sa.String,
        nullable = False,
    )

    entity_attribute_values = sa.orm.relationship(
        'EntityAttributeValue',
        back_populates = 'entity',
    )

    attributes = association_proxy(
        'entity_attribute_values',
        'attribute',
    )


class Attribute(Base):

    id = sa.Column(
        sa.Integer,
        primary_key = True,
    )

    name = sa.Column(
        sa.String,
        nullable = False,
    )

    data_type = sa.Column(
        sa.String,
        nullable = False,
    )

    entity_attribute_values = sa.orm.relationship(
        'EntityAttributeValue',
        back_populates = 'attribute',
    )


class EntityAttributeValue(Base):

    __table_args__ = (
        sa.PrimaryKeyConstraint(
            'entity_id',
            'attribute_id',
        ),
    )

    entity_id = sa.Column(
        sa.ForeignKey(
            'entity.id',
        ),
        nullable = False,
    )

    attribute_id = sa.Column(
        sa.ForeignKey(
            'attribute.id',
        ),
        nullable = False,
    )

    value = sa.Column(
        sa.String,
        nullable = False,
    )

    entity = sa.orm.relationship(
        'Entity',
        back_populates = 'entity_attribute_values',
    )

    attribute = sa.orm.relationship(
        'Attribute',
        back_populates = 'entity_attribute_values',
    )


def color(value):
    return str(value)

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

if __name__ == '__main__':
    main()
