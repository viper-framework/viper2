import logging
import os
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    and_,
    create_engine,
)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship, sessionmaker, subqueryload
from sqlalchemy.pool import NullPool

from viper.common.file import FileObject
from viper.core.projects import projects

log = logging.getLogger("viper")

Base = declarative_base()

association_table = Table(
    "association",
    Base.metadata,
    Column("tag_id", Integer, ForeignKey("tag.id")),
    Column("note_id", Integer, ForeignKey("note.id")),
    Column("file_id", Integer, ForeignKey("file.id")),
)


class File(Base):
    __tablename__ = "file"

    id = Column(Integer(), primary_key=True)
    name = Column(String(255), nullable=True)
    size = Column(Integer(), nullable=False)
    type = Column(Text(), nullable=True)
    mime = Column(String(255), nullable=True)
    md5 = Column(String(32), nullable=False, index=True)
    crc32 = Column(String(8), nullable=False)
    sha1 = Column(String(40), nullable=False)
    sha256 = Column(String(64), nullable=False, index=True)
    sha512 = Column(String(128), nullable=False)
    ssdeep = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=False), default=datetime.now, nullable=False)
    parent_id = Column(Integer(), ForeignKey("file.id"))
    parent = relationship("File", lazy="subquery", remote_side=[id])
    tag = relationship("Tag", secondary=association_table, backref=backref("file"))
    note = relationship(
        "Note",
        cascade="all, delete",
        secondary=association_table,
        backref=backref("file"),
    )
    __table_args__ = (
        Index("hash_index", "md5", "crc32", "sha1", "sha256", "sha512", unique=True),
    )

    def to_dict(self):
        row = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            row[column.name] = value

        return row

    def __repr__(self):
        return "<File ('{0}','{1}')>".format(self.id, self.md5)

    def __init__(
        self,
        md5,
        crc32,
        sha1,
        sha256,
        sha512,
        size,
        type=None,
        mime=None,
        ssdeep=None,
        name=None,
        parent=None,
    ):
        self.md5 = md5
        self.sha1 = sha1
        self.crc32 = crc32
        self.sha256 = sha256
        self.sha512 = sha512
        self.size = size
        self.type = type
        self.mime = mime
        self.ssdeep = ssdeep
        self.name = name
        self.parent = parent


class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer(), primary_key=True)
    tag = Column(String(255), nullable=False, unique=True, index=True)

    def to_dict(self):
        row = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            row[column.name] = value

        return row

    def __repr__(self):
        return "<Tag ('{0}','{1}')>".format(self.id, self.tag)

    def __init__(self, tag):
        self.tag = tag


class Note(Base):
    __tablename__ = "note"

    id = Column(Integer(), primary_key=True)
    title = Column(String(255), nullable=True)
    body = Column(Text(), nullable=False)

    def to_dict(self):
        row = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            row[column.name] = value

        return row

    def __repr__(self):
        return "<Note ('{0}','{1}')>".format(self.id, self.title)

    def __init__(self, title, body):
        self.title = title
        self.body = body


class Database:
    def __init__(self) -> None:
        self.db_path = os.path.join(projects.current.path, "viper.db")
        self.engine = create_engine(f"sqlite:///{self.db_path}", poolclass=NullPool)
        self.engine.echo = False
        self.engine.pool_timeout = 60

        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        self.added_ids = {}

    def __repr__(self):
        return "<{}>".format(self.__class__.__name__)

    def add_tags(self, sha256, tags):
        session = self.Session()

        file_entry = session.query(File).filter(File.sha256 == sha256).first()
        if not file_entry:
            return

        # The tags argument might be a list, a single tag, or a
        # comma-separated list of tags.
        if isinstance(tags, str):
            tags = tags.strip()
            if "," in tags:
                tags = tags.split(",")
            else:
                tags = tags.split()

        for tag in tags:
            tag = tag.strip().lower()
            if tag == "":
                continue

            try:
                new_tag = Tag(tag)
                file_entry.tag.append(new_tag)
                session.commit()
                self.added_ids.setdefault("tag", []).append(new_tag.id)
            except IntegrityError:
                session.rollback()
                try:
                    file_entry.tag.append(
                        session.query(Tag).filter(Tag.tag == tag).first()
                    )
                    session.commit()
                except SQLAlchemyError:
                    session.rollback()

    def list_tags(self):
        session = self.Session()
        rows = session.query(Tag).all()
        return rows

    def list_tags_for_file(self, sha256):
        session = self.Session()
        file = (
            session.query(File)
            .options(subqueryload(File.tag))
            .filter(File.sha256 == sha256)
            .first()
        )
        return file.tag

    def delete_tag(self, tag_name, sha256):
        session = self.Session()

        try:
            # First remove the tag from the sample
            file_entry = session.query(File).filter(File.sha256 == sha256).first()
            tag = session.query(Tag).filter(Tag.tag == tag_name).first()
            try:
                file_entry = session.query(File).filter(File.sha256 == sha256).first()
                file_entry.tag.remove(tag)
                session.commit()
            except Exception:
                log.error("Tag {0} does not exist for this sample".format(tag_name))

            # If tag has no entries drop it
            count = len(self.find("tag", tag_name))
            if count == 0:
                session.delete(tag)
                session.commit()
                log.warning(
                    "Tag {0} has no additional entries dropping from Database".format(
                        tag_name
                    )
                )
        except SQLAlchemyError as e:
            log.error("Unable to delete tag: {0}".format(e))
            session.rollback()
        finally:
            session.close()

    def list_notes(self):
        session = self.Session()
        rows = session.query(Note).all()
        return rows

    def add_note(self, sha256, title, body):
        session = self.Session()

        if sha256 is not None:
            file_entry = session.query(File).filter(File.sha256 == sha256).first()
            if not file_entry:
                return

        try:
            new_note = Note(title, body)
            if sha256 is not None:
                file_entry.note.append(new_note)
            else:
                session.add(new_note)

            session.commit()
            self.added_ids.setdefault("note", []).append(new_note.id)
        except SQLAlchemyError as e:
            log.error("Unable to add note: {0}".format(e))
            session.rollback()
        finally:
            session.close()

    def get_note(self, note_id):
        session = self.Session()
        note = session.query(Note).get(note_id)

        return note

    def edit_note(self, note_id, body):
        session = self.Session()

        try:
            session.query(Note).get(note_id).body = body
            session.commit()
        except SQLAlchemyError as e:
            log.error("Unable to update note: {0}".format(e))
            session.rollback()
        finally:
            session.close()

    def delete_note(self, note_id):
        session = self.Session()

        try:
            note = session.query(Note).get(note_id)
            session.delete(note)
            session.commit()
        except SQLAlchemyError as e:
            log.error("Unable to delete note: {0}".format(e))
            session.rollback()
        finally:
            session.close()

    def add(
        self,
        file_object,
        name=None,
        tags=None,
        parent_sha=None,
        notes_body=None,
        notes_title=None,
    ):
        session = self.Session()

        if not name:
            name = file_object.name

        if parent_sha:
            parent_sha = session.query(File).filter(File.sha256 == parent_sha).first()

        if isinstance(file_object, FileObject):
            try:
                file_entry = File(
                    md5=file_object.md5,
                    crc32=file_object.crc32,
                    sha1=file_object.sha1,
                    sha256=file_object.sha256,
                    sha512=file_object.sha512,
                    size=file_object.size,
                    type=file_object.type,
                    mime=file_object.mime,
                    ssdeep=file_object.ssdeep,
                    name=name,
                    parent=parent_sha,
                )
                session.add(file_entry)
                session.commit()
                self.added_ids.setdefault("file", []).append(file_entry.id)
            except IntegrityError:
                session.rollback()
                file_entry = (
                    session.query(File).filter(File.md5 == file_object.md5).first()
                )
            except SQLAlchemyError as e:
                log.error("Unable to store file: {0}".format(e))
                session.rollback()
                return False

        if tags:
            self.add_tags(sha256=file_object.sha256, tags=tags)

        if notes_body and notes_title:
            self.add_note(sha256=file_object.sha256, title=notes_title, body=notes_body)

        return True

    def delete_file(self, id):
        session = self.Session()

        try:
            file = session.query(File).get(id)
            if not file:
                log.error(
                    "The open file doesn't appear to be in the database, have you stored it yet?"
                )
                return False

            session.delete(file)
            session.commit()
        except SQLAlchemyError as e:
            log.error("Unable to delete file: {0}".format(e))
            session.rollback()
            return False
        finally:
            session.close()

        return True

    def find(self, key, value=None, offset=0):
        session = self.Session()
        offset = int(offset)
        rows = None

        if key == "all":
            rows = session.query(File).options(subqueryload(File.tag)).all()
        elif key == "ssdeep":
            ssdeep_val = str(value)
            rows = session.query(File).filter(File.ssdeep.contains(ssdeep_val)).all()
        elif key == "any":
            prefix_val = str(value)
            rows = (
                session.query(File)
                .filter(
                    File.name.startswith(prefix_val)
                    | File.md5.startswith(prefix_val)
                    | File.sha1.startswith(prefix_val)
                    | File.sha256.startswith(prefix_val)
                    | File.type.contains(prefix_val)
                    | File.mime.contains(prefix_val)
                )
                .all()
            )
        elif key == "latest":
            if value:
                try:
                    value = int(value)
                except ValueError:
                    log.error(
                        "You need to specify a valid number as a limit for your query"
                    )
                    return None
            else:
                value = 5

            rows = (
                session.query(File).order_by(File.id.desc()).limit(value).offset(offset)
            )
        elif key == "md5":
            rows = session.query(File).filter(File.md5 == value).all()
        elif key == "sha1":
            rows = session.query(File).filter(File.sha1 == value).all()
        elif key == "sha256":
            rows = session.query(File).filter(File.sha256 == value).all()
        elif key == "tag":
            rows = session.query(File).filter(self.tag_filter(value)).all()
        elif key == "name":
            if not value:
                log.error(
                    "You need to specify a valid file name pattern (you can use wildcards)"
                )
                return None

            if "*" in value:
                value = value.replace("*", "%")
            else:
                value = "%{0}%".format(value)

            rows = session.query(File).filter(File.name.like(value)).all()
        elif key == "note":
            value = "%{0}%".format(value)
            rows = (
                session.query(File).filter(File.note.any(Note.body.like(value))).all()
            )
        elif key == "type":
            rows = (
                session.query(File).filter(File.type.like("%{0}%".format(value))).all()
            )
        elif key == "mime":
            rows = (
                session.query(File).filter(File.mime.like("%{0}%".format(value))).all()
            )
        else:
            log.error("No valid term specified")

        return rows

    def add_parent(self, file_sha256, parent_sha256):
        session = self.Session()

        try:
            file = session.query(File).filter(File.sha256 == file_sha256).first()
            file.parent = (
                session.query(File).filter(File.sha256 == parent_sha256).first()
            )
            session.commit()
        except SQLAlchemyError as e:
            log.error("Unable to add parent: {0}".format(e))
            session.rollback()
        finally:
            session.close()

    def delete_parent(self, file_sha256):
        session = self.Session()

        try:
            file = session.query(File).filter(File.sha256 == file_sha256).first()
            file.parent = None
            session.commit()
        except SQLAlchemyError as e:
            log.error("Unable to delete parent: {0}".format(e))
            session.rollback()
        finally:
            session.close()

    def get_parent(self, file_id):
        session = self.Session()
        file = session.query(File).get(file_id)
        if not file.parent_id:
            return None
        else:
            parent = session.query(File).get(file.parent_id)
            return parent

    def get_children(self, parent_id):
        session = self.Session()
        children = session.query(File).filter(File.parent_id == parent_id).all()
        child_samples = ""
        for child in children:
            child_samples += "{0},".format(child.sha256)
        return child_samples

    def list_children(self, parent_id):
        session = self.Session()
        children = session.query(File).filter(File.parent_id == parent_id).all()
        return children