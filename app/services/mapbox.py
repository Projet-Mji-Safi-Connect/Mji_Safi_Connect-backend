import httpx
import os
from typing import List, Dict, Any

MAPBOX_ACCESS_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN")


async def get_optimized_route(coordinates: List[List[float]]) -> Dict[str, Any]:
    """
    Appelle l'API Mapbox Optimization.
    coordinates: Liste de [longitude, latitude]. Le premier est le départ/arrivée.
    """
    if not MAPBOX_ACCESS_TOKEN:
        raise Exception("MAPBOX_ACCESS_TOKEN is not set")

    # Mapbox attend "lon,lat;lon,lat;..."
    coords_string = ";".join(
        [f"{lon},{lat}" for lat, lon in coordinates]
    )  # Attention: Mapbox prend lon,lat mais nos modèles ont lat,lon.
    # Wait, my model has lat, lon. Mapbox expects lon, lat.
    # Let's double check the input format.
    # The function signature says coordinates: List[List[float]].
    # I will assume the input list is [[lat, lon], [lat, lon], ...] based on the previous step description.
    # So I need to swap them for the string.

    # Correction: Let's be explicit.
    # Input: [[lat, lon], [lat, lon]]
    # Mapbox: "lon,lat;lon,lat"

    coords_string = ";".join([f"{c[1]},{c[0]}" for c in coordinates])

    url = f"https://api.mapbox.com/optimized-trips/v1/mapbox/driving/{coords_string}"

    params = {
        "access_token": MAPBOX_ACCESS_TOKEN,
        "geometries": "geojson",
        "overview": "full",
        "source": "first",
        "destination": "last",  # Ou 'any' si on revient au dépôt ? Le user dit "Tournée", donc retour au dépôt ?
        # "roundtrip": "true" # Default is true.
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()
