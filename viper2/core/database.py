# Copyright 2023 The viper2 Authors. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

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
    class Meta:  # pylint: disable=too-few-public-methods
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
    parent = ForeignKeyField("self", backref="children", null=True)


class Tag(BaseModel):
    file = ForeignKeyField(File, backref="tags")
    name = CharField(unique=True)


class Note(BaseModel):
    file = ForeignKeyField(File, backref="notes")
    title = CharField()
    body = TextField()


def init_db(db_path: str) -> None:
    database_proxy.initialize(SqliteDatabase(db_path))
    database_proxy.create_tables([File, Tag, Note])
