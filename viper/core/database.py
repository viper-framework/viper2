import logging
import os
from datetime import datetime
from typing import Optional, Union

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
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


# pylint: disable=too-many-instance-attributes
class File(Base):
    __tablename__ = "file"

    id = Column(Integer(), primary_key=True)
    name = Column(String(255), nullable=True)
    size = Column(Integer(), nullable=False)
    magic = Column(Text(), nullable=True)
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
        return f"<File ('{self.id}','{self.sha1}')>"

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        md5: str,
        crc32: str,
        sha1: str,
        sha256: str,
        sha512: str,
        size: int,
        magic: Optional[str] = None,
        mime: Optional[str] = None,
        ssdeep: Optional[str] = None,
        name: Optional[str] = None,
        parent=None,
    ) -> None:
        self.md5 = md5
        self.sha1 = sha1
        self.crc32 = crc32
        self.sha256 = sha256
        self.sha512 = sha512
        self.size = size
        self.magic = magic
        self.mime = mime
        self.ssdeep = ssdeep
        self.name = name
        self.parent = parent


class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer(), primary_key=True)
    tag = Column(String(255), nullable=False, unique=True, index=True)

    def to_dict(self) -> dict:
        row = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            row[column.name] = value

        return row

    def __repr__(self) -> str:
        return f"<Tag ('{self.id}','{self.tag}')>"

    def __init__(self, tag: str) -> None:
        self.tag = tag


class Note(Base):
    __tablename__ = "note"

    id = Column(Integer(), primary_key=True)
    title = Column(String(255), nullable=True)
    body = Column(Text(), nullable=False)

    def to_dict(self) -> dict:
        row = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            row[column.name] = value

        return row

    def __repr__(self) -> str:
        return f"<Note ('{self.id}','{self.title}')>"

    def __init__(self, title: str, body: str) -> None:
        self.title = title
        self.body = body


# pylint: disable=too-few-public-methods
class BaseManager:
    def __init__(self, session):
        self.session = session


class FileManager(BaseManager):
    def add(
        self,
        file_object: FileObject,
        name: Optional[str] = None,
        parent_sha: Optional[str] = None,
    ) -> bool:
        if not name:
            name = file_object.name

        if parent_sha:
            parent_sha = (
                self.session.query(File).filter(File.sha256 == parent_sha).first()
            )

        if isinstance(file_object, FileObject):
            try:
                file_entry = File(
                    md5=file_object.md5,
                    crc32=file_object.crc32,
                    sha1=file_object.sha1,
                    sha256=file_object.sha256,
                    sha512=file_object.sha512,
                    size=file_object.size,
                    magic=file_object.magic,
                    mime=file_object.mime,
                    ssdeep=file_object.ssdeep,
                    name=name,
                    parent=parent_sha,
                )
                self.session.add(file_entry)
                self.session.commit()
            except IntegrityError:
                self.session.rollback()
                file_entry = (
                    self.session.query(File).filter(File.md5 == file_object.md5).first()
                )
            except SQLAlchemyError as exc:
                log.error("Unable to store file: %s", exc)
                self.session.rollback()
                return False

        return True

    def delete_file(self, id: int) -> bool:
        try:
            file = self.session.query(File).get(id)
            if not file:
                log.error(
                    "The open file doesn't appear to be in the database, have you stored it yet?"
                )
                return False

            self.session.delete(file)
            self.session.commit()
        except SQLAlchemyError as exc:
            log.error("Unable to delete file: %s", exc)
            self.session.rollback()
            return False
        finally:
            self.session.close()

        return True

    def get_latest_files(self, limit: int = 5, offset: int = 0) -> list:
        try:
            limit = int(limit)
        except ValueError:
            log.error("You need to specify a valid number as a limit for your query")
            return []

        rows = (
            self.session.query(File)
            .order_by(File.id.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

        return rows

    def get_files_by_name_pattern(self, name_pattern: str) -> list:
        if not name_pattern:
            log.error(
                "You need to specify a valid file name pattern (you can use wildcards)"
            )
            return []

        if "*" in name_pattern:
            name_pattern = name_pattern.replace("*", "%")
        else:
            name_pattern = f"%{name_pattern}%"

        rows = self.session.query(File).filter(File.name.like(name_pattern)).all()
        return rows

    def get_files_by_note_pattern(
        self, pattern: str, offset: Optional[int] = 0, limit: Optional[int] = None
    ) -> list:
        offset = int(offset)
        limit = limit or 10
        pattern = f"%{pattern}%"

        rows = (
            self.session.query(File)
            .options(subqueryload(File.note))
            .join(Note)
            .filter(Note.body.like(pattern))
            .order_by(File.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return rows

    def find(
        self, key: str, value: Optional[str] = None, offset: Optional[int] = 0
    ) -> list:
        queries = {
            "all": self.session.query(File).options(subqueryload(File.tag)).all(),
            "ssdeep": self.session.query(File)
            .filter(File.ssdeep.contains(str(value)))
            .all(),
            "any": self.session.query(File)
            .filter(
                File.name.startswith(str(value))
                | File.md5.startswith(str(value))
                | File.sha1.startswith(str(value))
                | File.sha256.startswith(str(value))
                | File.magic.contains(str(value))
                | File.mime.contains(str(value))
            )
            .all(),
            "latest": self.get_latest_files(value, offset),
            "md5": self.session.query(File).filter(File.md5 == value).all(),
            "sha1": self.session.query(File).filter(File.sha1 == value).all(),
            "sha256": self.session.query(File).filter(File.sha256 == value).all(),
            "name": self.get_files_by_name_pattern(value),
            "note": self.get_files_by_note_pattern(value),
            "magic": self.session.query(File).filter(File.magic.like(f"%{value}%")).all(),
            "mime": self.session.query(File).filter(File.mime.like(f"%{value}%")).all(),
        }

        rows = queries.get(key)
        if rows is None:
            log.error("No valid term specified")
            return []

        return rows

    def add_parent(self, file_sha256: str, parent_sha256: str) -> None:
        try:
            file = self.session.query(File).filter(File.sha256 == file_sha256).first()
            file.parent = (
                self.session.query(File).filter(File.sha256 == parent_sha256).first()
            )
            self.session.commit()
        except SQLAlchemyError as exc:
            log.error("Unable to add parent: %s", exc)
            self.session.rollback()
        finally:
            self.session.close()

    def delete_parent(self, file_sha256: str) -> None:
        try:
            file = self.session.query(File).filter(File.sha256 == file_sha256).first()
            file.parent = None
            self.session.commit()
        except SQLAlchemyError as exc:
            log.error("Unable to delete parent: %s", exc)
            self.session.rollback()
        finally:
            self.session.close()

    def get_parent(self, file_id: int) -> File:
        file = self.session.query(File).get(file_id)
        if not file.parent_id:
            return None

        parent = self.session.query(File).get(file.parent_id)
        return parent

    def get_children(self, parent_id: int) -> str:
        children = self.session.query(File).filter(File.parent_id == parent_id).all()
        child_samples = ""
        for child in children:
            child_samples += f"{child.sha256},"

        return child_samples

    def list_children(self, parent_id: str) -> list:
        children = self.session.query(File).filter(File.parent_id == parent_id).all()
        return children


class TagManager(BaseManager):
    def add_tags(self, sha256: str, tags: Union[str, list]):
        file_entry = self.session.query(File).filter(File.sha256 == sha256).first()
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
                self.session.commit()
            except IntegrityError:
                self.session.rollback()
                try:
                    file_entry.tag.append(
                        self.session.query(Tag).filter(Tag.tag == tag).first()
                    )
                    self.session.commit()
                except SQLAlchemyError:
                    self.session.rollback()

    def list_tags(self) -> list:
        rows = self.session.query(Tag).all()
        return rows

    def list_tags_for_file(self, sha256: str) -> list:
        file = (
            self.session.query(File)
            .options(subqueryload(File.tag))
            .filter(File.sha256 == sha256)
            .first()
        )
        return file.tag

    def delete_tag(self, tag_name: str, sha256: str) -> None:
        try:
            # First remove the tag from the sample
            file_entry = self.session.query(File).filter(File.sha256 == sha256).first()
            tag = self.session.query(Tag).filter(Tag.tag == tag_name).first()
            try:
                file_entry = (
                    self.session.query(File).filter(File.sha256 == sha256).first()
                )
                file_entry.tag.remove(tag)
                self.session.commit()
            except Exception:
                log.error("Tag %s does not exist for this sample", tag_name)

            # If tag has no entries drop it.
            count = len(self.find("tag", tag_name))
            if count == 0:
                self.session.delete(tag)
                self.session.commit()
        except SQLAlchemyError as exc:
            log.error("Unable to delete tag: %s", exc)
            self.session.rollback()
        finally:
            self.session.close()


class NoteManager(BaseManager):
    def list_notes(self) -> list:
        rows = self.session.query(Note).all()
        return rows

    def add_note(self, sha256: str, title: str, body: str) -> None:
        if sha256 is not None:
            file_entry = self.session.query(File).filter(File.sha256 == sha256).first()
            if not file_entry:
                return

        try:
            new_note = Note(title, body)
            if sha256 is not None:
                file_entry.note.append(new_note)
            else:
                self.session.add(new_note)

            self.session.commit()
        except SQLAlchemyError as exc:
            log.error("Unable to add note: %s", exc)
            self.session.rollback()
        finally:
            self.session.close()

    def get_note(self, note_id: int) -> Note:
        return self.session.query(Note).get(note_id)

    def edit_note(self, note_id: int, body: str) -> None:
        try:
            self.session.query(Note).get(note_id).body = body
            self.session.commit()
        except SQLAlchemyError as exc:
            log.error("Unable to update note: %s", exc)
            self.session.rollback()
        finally:
            self.session.close()

    def delete_note(self, note_id: int) -> None:
        try:
            note = self.session.query(Note).get(note_id)
            self.session.delete(note)
            self.session.commit()
        except SQLAlchemyError as exc:
            log.error("Unable to delete note: %s", exc)
            self.session.rollback()
        finally:
            self.session.close()


# pylint: disable=too-few-public-methods
class Database:
    def __init__(self) -> None:
        self.db_path = os.path.join(projects.current.path, "viper.db")
        engine = create_engine(f"sqlite:///{self.db_path}", poolclass=NullPool)
        engine.echo = False
        engine.pool_timeout = 60

        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)  # pylint: disable=invalid-name
        self.session = Session()

        self.files = FileManager(self.session)
        self.tags = TagManager(self.session)
        self.notes = NoteManager(self.session)

    def __repr__(self):
        return f"<{self.__class__.__name__}>"
