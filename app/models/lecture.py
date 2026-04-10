from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from .poubelle import Poubelle

class LectureBase(SQLModel):
    remplissage_pct: int
    batterie_V: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Lecture(LectureBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    poubelle_id: int = Field(foreign_key="poubelle.id")
    poubelle: Optional[Poubelle] = Relationship(back_populates="lectures")

class LectureCreate(LectureBase):
    poubelle_id: int

class LectureRead(LectureBase):
    id: int
    poubelle_id: int
