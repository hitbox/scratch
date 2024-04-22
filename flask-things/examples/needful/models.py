import sqlalchemy as sa

from .extensions import db

class Book(db.Model):

    isbn = sa.Column(
        sa.Integer,
        primary_key = True,
        comment = 'International Standard Book Number',
    )

    authors_assocs = sa.orm.relationship(
        'BookAuthor',
        back_populates = 'book',
    )


class BookAuthor(db.Model):

    book_isbn = sa.Column(
        sa.ForeignKey('book.isbn'),
        primary_key = True,
    )

    author_id = sa.Column(
        sa.ForeignKey('author.id'),
        primary_key = True,
    )

    book = sa.orm.relationship(
        'Book',
        back_populates = 'authors_assocs',
    )

    author = sa.orm.relationship(
        'Author',
        back_populates = 'books_assocs',
    )


class Author(db.Model):

    id = sa.Column(
        sa.Integer,
        primary_key = True,
    )

    books_assocs = sa.orm.relationship(
        'BookAuthor',
        back_populates = 'author',
    )
