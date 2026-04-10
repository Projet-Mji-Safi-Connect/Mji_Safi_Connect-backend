from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .lecture import Lecture

class PoubelleBase(SQLModel):
    nom: str
    device_id: str = Field(unique=True, index=True)
    latitude: float
    longitude: float

class Poubelle(PoubelleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    lectures: List["Lecture"] = Relationship(back_populates="poubelle")

class PoubelleRead(PoubelleBase):
    id: int

class PoubelleCreate(PoubelleBase):
    pass
