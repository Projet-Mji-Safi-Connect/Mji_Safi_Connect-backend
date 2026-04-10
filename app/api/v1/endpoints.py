from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.database import get_session
from app.models.poubelle import Poubelle, PoubelleCreate, PoubelleRead
from app.models.lecture import Lecture, LectureCreate, LectureRead
from app.services.mapbox import get_optimized_route

router = APIRouter()


# --- Schemas pour TTN Webhook ---
class TTNDeviceIds(BaseModel):
    device_id: str


class TTNDecodedPayload(BaseModel):
    remplissage_pct: int
    batterie_V: float


class TTNUplinkMessage(BaseModel):
    decoded_payload: TTNDecodedPayload


class TTNWebhook(BaseModel):
    end_device_ids: TTNDeviceIds
    uplink_message: TTNUplinkMessage


# --- Schemas de Réponse Personnalisés ---
class PoubelleReadWithLast(PoubelleRead):
    last_lecture: Optional[LectureRead] = None


# --- Endpoints ---


@router.post("/webhook/ttn", status_code=status.HTTP_201_CREATED)
def ttn_webhook(payload: TTNWebhook, session: Session = Depends(get_session)):
    device_id = payload.end_device_ids.device_id
    remplissage = payload.uplink_message.decoded_payload.remplissage_pct
    batterie = payload.uplink_message.decoded_payload.batterie_V

    # Trouver la poubelle
    statement = select(Poubelle).where(Poubelle.device_id == device_id)
    poubelle = session.exec(statement).first()

    if not poubelle:
        # On pourrait créer la poubelle automatiquement ou rejeter.
        # Pour l'instant, on rejette si elle n'existe pas.
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

    # Créer la lecture
    lecture = Lecture(
        remplissage_pct=remplissage, batterie_V=batterie, poubelle_id=poubelle.id
    )
    session.add(lecture)
    session.commit()
    return {"status": "ok"}


@router.post("/poubelles", response_model=PoubelleRead)
def create_poubelle(poubelle: PoubelleCreate, session: Session = Depends(get_session)):
    db_poubelle = Poubelle.from_orm(poubelle)
    session.add(db_poubelle)
    session.commit()
    session.refresh(db_poubelle)
    return db_poubelle


@router.get("/poubelles", response_model=List[PoubelleReadWithLast])
def read_poubelles(session: Session = Depends(get_session)):
    poubelles = session.exec(select(Poubelle)).all()
    results = []
    for p in poubelles:
        # Obtenir la dernière lecture
        # Optimisation possible: faire une seule requête complexe, mais ici on fait simple (N+1 query problem, acceptable pour 4 poubelles)
        last_lecture = session.exec(
            select(Lecture)
            .where(Lecture.poubelle_id == p.id)
            .order_by(Lecture.timestamp.desc())
            .limit(1)
        ).first()

        p_with_last = PoubelleReadWithLast.from_orm(p)
        if last_lecture:
            p_with_last.last_lecture = LectureRead.from_orm(last_lecture)
        results.append(p_with_last)
    return results


@router.get("/poubelles/{poubelle_id}", response_model=PoubelleRead)
def read_poubelle(poubelle_id: int, session: Session = Depends(get_session)):
    poubelle = session.get(Poubelle, poubelle_id)
    if not poubelle:
        raise HTTPException(status_code=404, detail="Poubelle not found")
    return poubelle


@router.get("/poubelles/{poubelle_id}/historique", response_model=List[LectureRead])
def read_historique(poubelle_id: int, session: Session = Depends(get_session)):
    lectures = session.exec(
        select(Lecture)
        .where(Lecture.poubelle_id == poubelle_id)
        .order_by(Lecture.timestamp.desc())
    ).all()
    return lectures


@router.get("/tournee/optimale")
async def get_tournee_optimale(session: Session = Depends(get_session)):
    SEUIL_CRITIQUE = 80
    # Coordonnées du dépôt (Exemple: ULPGL Goma)
    DEPOT_LAT = -1.6585
    DEPOT_LON = 29.2205

    # Trouver les poubelles pleines
    # Note: Pour simplifier, on prend la dernière lecture de chaque poubelle et on vérifie le seuil.
    poubelles = session.exec(select(Poubelle)).all()
    poubelles_pleines = []

    for p in poubelles:
        last_lecture = session.exec(
            select(Lecture)
            .where(Lecture.poubelle_id == p.id)
            .order_by(Lecture.timestamp.desc())
            .limit(1)
        ).first()

        if last_lecture and last_lecture.remplissage_pct >= SEUIL_CRITIQUE:
            poubelles_pleines.append(p)

    if not poubelles_pleines:
        return {"route": None, "stops": []}

    # Construire la liste des coordonnées: [Depot, P1, P2, ..., Depot]
    # Mapbox Optimization API gère l'ordre, on lui donne juste les points.
    # Le premier point est le départ.

    coordinates = [[DEPOT_LAT, DEPOT_LON]]
    stops_map = {0: "Depot"}  # Index -> Nom/ID

    for i, p in enumerate(poubelles_pleines):
        coordinates.append([p.latitude, p.longitude])
        stops_map[i + 1] = p.nom

    # Appel Mapbox
    try:
        optimization_result = await get_optimized_route(coordinates)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "optimization_result": optimization_result,
        "poubelles_a_collecter": [p.nom for p in poubelles_pleines],
    }
