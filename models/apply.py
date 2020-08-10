from typing import Union

from PyDrocsid.database import db
from sqlalchemy import Column, Integer, Text


class Jobs(db.Base):
    __tablename__ = "jobs"

    id: Union[Column, int] = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name: Union[Column, str] = Column(Text(collation="utf8mb4_bin"))
    description: Union[Column, str] = Column(Text(collation="utf8mb4_bin"))

    @staticmethod
    def create(name: str, description: str) -> "Jobs":
        row = Jobs(name=name, description=description)
        db.add(row)
        return row


class Questions(db.Base):
    __tablename__ = "questions"

    id: Union[Column, int] = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    job_name: Union[Column, str] = Column(Text(collation="utf8mb4_bin"))
    question: Union[Column, str] = Column(Text(collation="utf8mb4_bin"))
    order: Union[Column, int] = Column(Integer)

    @staticmethod
    def create(job_name: str, question: str, order: int) -> "Questions":
        row = Questions(job_name=job_name, question=question, order=order)
        db.add(row)
        return row
