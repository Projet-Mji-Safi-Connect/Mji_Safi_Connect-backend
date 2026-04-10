# Spécifications du Backend - Projet Smart Poubelle ULPGL Goma

Ce document détaille l'architecture, les modèles de données et les endpoints de l'API pour le backend du projet de gestion de déchets optimisée.

**Stack Technique :**

- **Framework :** FastAPI (Python 3.12.8)
- **Base de Données :** PostgreSQL
- **ORM / Modélisation :** SQLModel (combine SQLAlchemy et Pydantic)
- **Serveur :** Uvicorn
- **Client HTTP :** HTTPLib (pour appeler Mapbox)

---

## 1. Objectif du Backend

Le backend est le **cerveau central** du système. Il a quatre responsabilités principales :

1.  **Ingestion :** Recevoir, valider et authentifier les données de remplissage envoyées par **The Things Network (TTN)** via un Webhook.
2.  **Stockage :** Enregistrer de manière fiable et structurée toutes les lectures de capteurs (remplissage, batterie) dans la base de données PostgreSQL.
3.  **Exposition (API) :** Fournir une API RESTful sécurisée pour que le **Frontend React** puisse afficher l'état des poubelles et leur historique.
4.  **Optimisation :** Exposer un endpoint qui calcule l'**itinéraire de collecte optimal** en interrogeant l'API d'optimisation de Mapbox.

---

## 2. Modèles de Données (Base de Données SQLModel)

Nous utiliserons SQLModel pour définir nos tables et nos modèles de validation Pydantic en un seul endroit.

### Table: `Poubelle`

Stocke les informations statiques sur chaque appareil physique (vos 4 prototypes).

| Champ       | Type              | Contraintes    | Description                                      |
| :---------- | :---------------- | :------------- | :----------------------------------------------- |
| `id`        | `Optional[int]`   | Clé Primaire   | Identifiant unique de la table.                  |
| `nom`       | `str`             |                | Nom lisible (ex: "Poubelle ULPGL").              |
| `device_id` | `str`             | Unique, Indexé | ID de l'appareil sur TTN (ex: "poubelle-001").   |
| `latitude`  | `float`           |                | Coordonnée GPS (Latitude).                       |
| `longitude` | `float`           |                | Coordonnée GPS (Longitude).                      |
| `lectures`  | `List["Lecture"]` | Relation       | Lien vers toutes les lectures de cette poubelle. |

### Table: `Lecture`

Stocke chaque mesure reçue de TTN. C'est la table d'historique.

| Champ             | Type            | Contraintes       | Description                              |
| :---------------- | :-------------- | :---------------- | :--------------------------------------- |
| `id`              | `Optional[int]` | Clé Primaire      | Identifiant unique de la table.          |
| `timestamp`       | `datetime`      | `default_factory` | Date et heure de réception de la donnée. |
| `remplissage_pct` | `int`           |                   | Niveau de remplissage (0-100).           |
| `batterie_V`      | `float`         |                   | Tension de la batterie (ex: 4.1).        |
| `poubelle_id`     | `int`           | Clé Étrangère     | Lien vers la `Poubelle` correspondante.  |
| `poubelle`        | `Poubelle`      | Relation          | Lien retour vers l'objet Poubelle.       |

---

## 3. Endpoints de l'API (Contrat de Service)

Voici la liste détaillée des routes de l'API FastAPI à implémenter.

### A. Endpoint d'Ingestion (Webhook TTN)

C'est l'endpoint le plus critique pour la réception des données.

#### `POST /api/v1/webhook/ttn`

- **Objectif :** Point d'entrée unique pour le Webhook de The Things Network.
- **Logique :**
  1.  Recevoir la requête POST de TTN.
  2.  Valider le JSON entrant à l'aide d'un **modèle Pydantic** (`TTNWebhook`) qui extraira :
      - `end_device_ids.device_id` (l'ID de l'appareil).
      - `uplink_message.decoded_payload.remplissage_pct` (le remplissage).
      - `uplink_message.decoded_payload.batterie_V` (la batterie).
  3.  Rechercher dans la table `Poubelle` l'appareil correspondant au `device_id` reçu.
  4.  Si l'appareil n'est pas trouvé : lever une erreur 404 (ou 422) et la logger.
  5.  Si l'appareil est trouvé :
      - Créer une nouvelle instance du modèle `Lecture`.
      - Remplir `remplissage_pct`, `batterie_V`, et `poubelle_id`.
      - Enregistrer la nouvelle `Lecture` dans la base de données.
  6.  Retourner une réponse `{"status": "ok"}` avec un code `201 Created`. (TTN n'a pas besoin d'une réponse complexe, juste d'un succès).

### B. Endpoints pour le Frontend (Dashboard)

Ces endpoints alimenteront votre application React/TypeScript.

#### `GET /api/v1/poubelles`

- **Objectif :** Fournir au dashboard la liste de toutes les poubelles et leur **dernier état connu**.
- **Logique :**
  1.  Interroger la base de données pour obtenir la liste de toutes les `Poubelle`.
  2.  Pour chaque poubelle, effectuer un sous-requête (ou un JOIN) pour trouver la **dernière** `Lecture` (basée sur `timestamp`).
  3.  Construire une réponse JSON contenant la liste des poubelles, incluant leur dernière lecture (remplissage et batterie).
- **Modèle de Réponse :** `List[PoubelleReadWithLast]` (un modèle Pydantic personnalisé).

#### `GET /api/v1/poubelles/{poubelle_id}/historique`

- **Objectif :** Fournir l'historique complet d'une poubelle (pour les graphiques).
- **Logique :**
  1.  Recevoir `poubelle_id` en paramètre.
  2.  Interroger la table `Lecture` pour trouver toutes les lectures où `poubelle_id` correspond.
  3.  (Optionnel) Permettre des filtres (ex: `?start_date=...&end_date=...`).
- **Modèle de Réponse :** `List[LectureBase]`

### C. Endpoint d'Optimisation (Le Cerveau Logistique)

C'est le cœur de votre problématique "économie de carburant".

#### `GET /api/v1/tournee/optimale`

- **Objectif :** Calculer l'itinéraire de collecte le plus efficace en se basant sur l'état actuel des poubelles.
- **Logique :**
  1.  Définir un seuil de collecte (ex: `SEUIL_CRITIQUE = 80%`).
  2.  Définir un point de départ (Dépôt) (ex: `DEPART_GPS = [latitude, longitude]`).
  3.  Interroger la base de données (similaire à `GET /api/v1/poubelles`) pour trouver toutes les poubelles dont la **dernière lecture `remplissage_pct` >= `SEUIL_CRITIQUE`**.
  4.  Extraire les coordonnées GPS (`latitude`, `longitude`) de ces poubelles.
  5.  **Cas 1 :** Si aucune poubelle n'atteint le seuil, retourner une réponse vide (`{"route": null, "stops": []}`).
  6.  **Cas 2 :** Si des poubelles sont pleines :
      - Construire la liste des points de passage (Coordonnées du Dépôt + Coordonnées des poubelles pleines).
      - Faire un appel (ex: avec `httpx`) à l'**API Mapbox Optimization** (API de Routage).
      - Envoyer la liste des coordonnées à Mapbox.
      - Récupérer la réponse de Mapbox, qui contiendra l'ordre optimisé des arrêts et le GeoJSON du tracé de la route.
  7.  Retourner au frontend une réponse JSON propre contenant le tracé GeoJSON et la liste ordonnée des arrêts.
- **Modèle de Réponse :** `{ "route_geojson": {...}, "stops_order": [...], "total_distance_m": 15000, "total_duration_s": 3600 }`

### D. Endpoints de Gestion (CRUD - Administration)

Nécessaires pour configurer le système la première fois (enregistrer vos 4 poubelles).

#### `POST /api/v1/poubelles`

- **Objectif :** Créer une nouvelle poubelle dans le système.
- **Corps de la Requête :** `PoubelleBase` (nom, device_id, lat, lon).
- **Action :** Enregistrer la nouvelle poubelle dans la DB.

#### `GET /api/v1/poubelles/{poubelle_id}`

- **Objectif :** Obtenir les détails d'une seule poubelle.
- **Modèle de Réponse :** `PoubelleRead`
