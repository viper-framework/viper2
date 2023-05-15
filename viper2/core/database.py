import datetime

from peewee import (
    CharField,
    DatabaseProxy,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    Model,
    SqliteDatabase,
    TextField,
)

database_proxy = DatabaseProxy()


class BaseModel(Model):
    # pylint disable=too-few-public-methods
    class Meta:
        database = database_proxy


class File(BaseModel):
    name = CharField()
    size = IntegerField()
    magic = CharField()
    mime = CharField()
    md5 = CharField()
    crc32 = CharField()
    sha1 = CharField()
    sha256 = CharField()
    sha512 = CharField()
    ssdeep = CharField()
    created_date = DateTimeField(default=datetime.datetime.now)
    # parent = ForeignKeyField(File)


class Tag(BaseModel):
    file = ForeignKeyField(File)
    name = CharField(unique=True)


class Note(BaseModel):
    file = ForeignKeyField(File)
    title = CharField()
    body = TextField()


def init_db(db_path: str) -> None:
    database_proxy.initialize(SqliteDatabase(db_path))
    database_proxy.create_tables([File, Tag, Note])
