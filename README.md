# 🗑️ Mji Safi Connect — Backend API

<div align="center">

**Système Intelligent de Gestion des Déchets pour la Ville de Goma**

*Projet de Mémoire de Licence 3 — Génie Électrique et Informatique*

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Mapbox](https://img.shields.io/badge/Mapbox-000000?style=for-the-badge&logo=mapbox&logoColor=white)](https://www.mapbox.com/)

</div>

---

## 📋 Table des Matières

- [📖 Description du Projet](#-description-du-projet)
- [🎯 Contexte Académique](#-contexte-académique)
- [🏗️ Architecture du Système](#️-architecture-du-système)
- [⚙️ Stack Technique](#️-stack-technique)
- [📁 Structure du Projet](#-structure-du-projet)
- [🗃️ Modèles de Données](#️-modèles-de-données)
- [🔌 Endpoints de l'API](#-endpoints-de-lapi)
- [🚀 Installation et Démarrage](#-installation-et-démarrage)
- [🔧 Configuration](#-configuration)
- [📡 Intégration IoT (TTN)](#-intégration-iot-ttn)
- [🗺️ Optimisation des Tournées](#️-optimisation-des-tournées)
- [🖥️ Frontend Associé](#️-frontend-associé)
- [📄 Licence](#-licence)

---

## 📖 Description du Projet

**Mji Safi Connect** (en Swahili : *« Ville Propre Connectée »*) est une plateforme IoT complète de **gestion intelligente des déchets** conçue pour la ville de **Goma, RD Congo**. Le système utilise des **capteurs ultrasoniques** installés dans des poubelles connectées pour mesurer en temps réel le niveau de remplissage, et transmet ces données via le réseau **LoRaWAN** (The Things Network) vers ce backend.

### 🎯 Problématique

La collecte des déchets dans les villes africaines souffre de plusieurs problèmes :
- **Tournées non optimisées** : les camions suivent des itinéraires fixes sans connaître l'état réel des poubelles
- **Gaspillage de carburant** : des trajets inutiles vers des poubelles encore vides
- **Débordements** : certaines poubelles débordent car elles ne sont pas collectées à temps

### 💡 Solution Proposée

Ce backend constitue le **cerveau central** du système avec quatre responsabilités principales :

1. **🔄 Ingestion** — Réception, validation et authentification des données de remplissage envoyées par **The Things Network (TTN)** via un Webhook
2. **💾 Stockage** — Enregistrement structuré de toutes les lectures de capteurs (remplissage, batterie) dans une base de données PostgreSQL
3. **📊 Exposition (API REST)** — Fournir une API RESTful pour que le Dashboard Frontend puisse afficher l'état des poubelles et leur historique
4. **🧠 Optimisation** — Calcul de l'**itinéraire de collecte optimal** en interrogeant l'API d'optimisation de Mapbox, permettant de réduire la consommation de carburant

---

## 🎯 Contexte Académique

| Élément | Détail |
|:---|:---|
| **Niveau** | Licence 3 (L3) |
| **Filière** | Génie Électrique et Informatique |
| **Type** | Mémoire / Projet de fin d'études |
| **Thème** | Optimisation de la collecte des déchets urbains par l'IoT |
| **Lieu d'application** | Ville de Goma, République Démocratique du Congo |
| **Institution** | ULPGL Goma |

---

## 🏗️ Architecture du Système

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARCHITECTURE GLOBALE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    LoRaWAN     ┌──────────────┐              │
│  │  🗑️ Capteurs  │──────────────▶│  📡 Gateway   │              │
│  │  (Ultrason +  │               │  LoRaWAN      │              │
│  │   Arduino)    │               └──────┬───────┘              │
│  └──────────────┘                       │                      │
│                                         ▼                      │
│                              ┌──────────────────┐              │
│                              │  ☁️ The Things    │              │
│                              │  Network (TTN)   │              │
│                              └────────┬─────────┘              │
│                                       │ Webhook POST           │
│                                       ▼                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              🖥️ BACKEND (Ce Repository)                  │   │
│  │  ┌─────────────┐  ┌──────────┐  ┌──────────────────┐   │   │
│  │  │  FastAPI     │  │ SQLModel │  │ Service Mapbox   │   │   │
│  │  │  (REST API)  │──│  (ORM)   │──│  (Optimisation)  │   │   │
│  │  └─────────────┘  └────┬─────┘  └──────────────────┘   │   │
│  │                        │                                 │   │
│  │                   ┌────▼─────┐                          │   │
│  │                   │PostgreSQL│                           │   │
│  │                   │  / SQLite│                           │   │
│  │                   └──────────┘                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │ API REST                             │
│                          ▼                                     │
│             ┌──────────────────────┐                           │
│             │  🌐 FRONTEND         │                           │
│             │  React + TypeScript  │                           │
│             │  + Mapbox GL JS      │                           │
│             │  (Dashboard)         │                           │
│             └──────────────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Stack Technique

| Technologie | Rôle | Version |
|:---|:---|:---|
| **Python** | Langage de programmation | 3.12+ |
| **FastAPI** | Framework web / API REST | Dernière |
| **SQLModel** | ORM (combine SQLAlchemy + Pydantic) | Dernière |
| **PostgreSQL** | Base de données relationnelle (production) | 15+ |
| **SQLite** | Base de données locale (développement) | Intégrée |
| **Uvicorn** | Serveur ASGI haute performance | Dernière |
| **httpx** | Client HTTP asynchrone (appels Mapbox) | Dernière |
| **python-dotenv** | Gestion des variables d'environnement | Dernière |
| **psycopg2-binary** | Driver PostgreSQL pour Python | Dernière |

---

## 📁 Structure du Projet

```
Mji_Safi_Connect-backend/
├── 📄 README.md                    # Ce fichier
├── 📄 requirements.txt             # Dépendances Python
├── 📄 Guide_backend.md             # Spécifications techniques détaillées
├── 📄 .gitignore                   # Fichiers ignorés par Git
│
└── 📁 app/                         # Code source principal
    ├── 📄 __init__.py              # Initialisation du package
    ├── 📄 main.py                  # Point d'entrée de l'application FastAPI
    ├── 📄 database.py              # Configuration de la base de données
    │
    ├── 📁 models/                  # Modèles de données (SQLModel)
    │   ├── 📄 __init__.py          # Export des modèles
    │   ├── 📄 poubelle.py          # Modèle Poubelle (bin)
    │   └── 📄 lecture.py           # Modèle Lecture (sensor reading)
    │
    ├── 📁 services/                # Services externes
    │   ├── 📄 __init__.py
    │   └── 📄 mapbox.py            # Service d'optimisation Mapbox
    │
    └── 📁 api/                     # Routes de l'API
        ├── 📄 __init__.py
        └── 📁 v1/                  # Version 1 de l'API
            ├── 📄 __init__.py
            └── 📄 endpoints.py     # Tous les endpoints REST
```

---

## 🗃️ Modèles de Données

### Table `Poubelle` (Bin)

Représente chaque poubelle physique connectée au système.

| Champ | Type | Contraintes | Description |
|:---|:---|:---|:---|
| `id` | `int` | Clé Primaire, Auto-incrémenté | Identifiant unique |
| `nom` | `str` | — | Nom lisible (ex: "Poubelle ULPGL") |
| `device_id` | `str` | **Unique**, Indexé | ID de l'appareil sur TTN (ex: "poubelle-001") |
| `latitude` | `float` | — | Coordonnée GPS (Latitude) |
| `longitude` | `float` | — | Coordonnée GPS (Longitude) |
| `lectures` | `List[Lecture]` | Relation (One-to-Many) | Historique des mesures |

### Table `Lecture` (Sensor Reading)

Stocke chaque mesure reçue des capteurs via TTN.

| Champ | Type | Contraintes | Description |
|:---|:---|:---|:---|
| `id` | `int` | Clé Primaire, Auto-incrémenté | Identifiant unique |
| `timestamp` | `datetime` | Auto-généré (UTC) | Date et heure de réception |
| `remplissage_pct` | `int` | — | Niveau de remplissage (0–100%) |
| `batterie_V` | `float` | — | Tension de la batterie (ex: 4.1V) |
| `poubelle_id` | `int` | Clé Étrangère → `Poubelle.id` | Référence vers la poubelle |

### Diagramme Entité-Relation

```
┌────────────────────┐         ┌────────────────────────┐
│     POUBELLE       │         │        LECTURE          │
├────────────────────┤         ├────────────────────────┤
│ PK  id             │◄────────│ FK  poubelle_id        │
│     nom            │   1:N   │ PK  id                 │
│ UQ  device_id      │         │     timestamp           │
│     latitude       │         │     remplissage_pct     │
│     longitude      │         │     batterie_V          │
└────────────────────┘         └────────────────────────┘
```

---

## 🔌 Endpoints de l'API

L'API est versionnée (`/api/v1/`) et fournit les endpoints suivants :

### 📡 Webhook TTN (Ingestion IoT)

| Méthode | Endpoint | Description |
|:---|:---|:---|
| `POST` | `/api/v1/webhook/ttn` | Réception des données capteurs depuis The Things Network |

**Payload attendu :**
```json
{
  "end_device_ids": {
    "device_id": "poubelle-001"
  },
  "uplink_message": {
    "decoded_payload": {
      "remplissage_pct": 85,
      "batterie_V": 3.7
    }
  }
}
```

**Réponse :** `201 Created` → `{"status": "ok"}`

---

### 🗑️ CRUD Poubelles

| Méthode | Endpoint | Description |
|:---|:---|:---|
| `POST` | `/api/v1/poubelles` | Créer une nouvelle poubelle |
| `GET` | `/api/v1/poubelles` | Lister toutes les poubelles avec leur dernière lecture |
| `GET` | `/api/v1/poubelles/{id}` | Obtenir les détails d'une poubelle |
| `GET` | `/api/v1/poubelles/{id}/historique` | Historique complet des lectures d'une poubelle |

**Exemple — Créer une poubelle :**
```json
POST /api/v1/poubelles
{
  "nom": "Poubelle Marché Central",
  "device_id": "poubelle-002",
  "latitude": -1.6690,
  "longitude": 29.2284
}
```

**Exemple — Liste des poubelles (avec dernière lecture) :**
```json
GET /api/v1/poubelles
[
  {
    "id": 1,
    "nom": "Poubelle ULPGL",
    "device_id": "poubelle-001",
    "latitude": -1.6585,
    "longitude": 29.2205,
    "last_lecture": {
      "id": 42,
      "remplissage_pct": 87,
      "batterie_V": 3.9,
      "timestamp": "2026-04-11T14:30:00",
      "poubelle_id": 1
    }
  }
]
```

---

### 🧠 Optimisation des Tournées

| Méthode | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/api/v1/tournee/optimale` | Calculer l'itinéraire optimal de collecte |

**Logique :**
1. Identifie les poubelles dont le remplissage ≥ **80%** (seuil critique)
2. Construit la liste des coordonnées (Dépôt ULPGL + poubelles pleines)
3. Appelle l'**API Mapbox Optimization** pour le calcul du trajet optimal
4. Retourne le tracé GeoJSON et les statistiques de la tournée

**Réponse :**
```json
{
  "optimization_result": {
    "trips": [
      {
        "geometry": { "type": "LineString", "coordinates": [...] },
        "distance": 15200,
        "duration": 3600
      }
    ]
  },
  "poubelles_a_collecter": ["Poubelle ULPGL", "Poubelle Marché Central"]
}
```

---

### 📚 Documentation Interactive

FastAPI génère automatiquement une documentation interactive accessible à :

| URL | Type |
|:---|:---|
| `http://localhost:8000/docs` | **Swagger UI** (interface interactive) |
| `http://localhost:8000/redoc` | **ReDoc** (documentation détaillée) |

---

## 🚀 Installation et Démarrage

### Prérequis

- **Python** 3.12 ou supérieur → [Télécharger Python](https://www.python.org/downloads/)
- **PostgreSQL** 15+ (production) ou SQLite (développement) → [Télécharger PostgreSQL](https://www.postgresql.org/download/)
- **Git** → [Télécharger Git](https://git-scm.com/)
- Un compte **Mapbox** avec un token API → [Créer un compte](https://www.mapbox.com/)

### Étape 1 — Cloner le Repository

```bash
git clone https://github.com/Projet-Mji-Safi-Connect/Mji_Safi_Connect-backend.git
cd Mji_Safi_Connect-backend
```

### Étape 2 — Créer un Environnement Virtuel

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows :
venv\Scripts\activate
# Sur macOS/Linux :
source venv/bin/activate
```

### Étape 3 — Installer les Dépendances

```bash
pip install -r requirements.txt
```

### Étape 4 — Configurer les Variables d'Environnement

Créer un fichier `.env` à la racine du projet :

```env
# Base de données
# Pour SQLite (développement local) :
DATABASE_URL=sqlite:///./database.db

# Pour PostgreSQL (production) :
# DATABASE_URL=postgresql://user:password@localhost:5432/mji_safi_db

# Token Mapbox (pour l'optimisation des tournées)
MAPBOX_ACCESS_TOKEN=pk.eyJ1Ijoixxxxxxxxx
```

### Étape 5 — Lancer le Serveur

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Le serveur sera accessible à : **http://localhost:8000**

### Vérification

Ouvrez votre navigateur et accédez à :
- `http://localhost:8000` → Message de bienvenue
- `http://localhost:8000/docs` → Documentation Swagger UI interactive

---

## 🔧 Configuration

### Variables d'Environnement

| Variable | Requis | Description | Exemple |
|:---|:---|:---|:---|
| `DATABASE_URL` | ✅ | URL de connexion à la base de données | `sqlite:///./database.db` |
| `MAPBOX_ACCESS_TOKEN` | ✅ | Token d'accès API Mapbox | `pk.eyJ1Ioixxxxxxx` |

### Configuration de la Base de Données

Le système supporte deux modes :

| Mode | Base | Usage | Configuration |
|:---|:---|:---|:---|
| **Développement** | SQLite | Tests locaux, prototypage | `DATABASE_URL=sqlite:///./database.db` |
| **Production** | PostgreSQL | Déploiement, données réelles | `DATABASE_URL=postgresql://user:pass@host:5432/db` |

> **Note :** Les tables sont créées automatiquement au démarrage de l'application grâce à SQLModel.

---

## 📡 Intégration IoT (TTN)

### Chaîne Complète IoT

```
Capteur Ultrasonique → Arduino → Module LoRa → Gateway LoRaWAN → TTN → Webhook → Backend API
```

### Configuration du Webhook sur TTN

1. Connectez-vous à [The Things Network Console](https://console.thethingsnetwork.org/)
2. Sélectionnez votre application
3. Allez dans **Integrations** → **Webhooks**
4. Créez un nouveau Webhook :
   - **Format** : JSON
   - **Base URL** : `https://votre-domaine.com/api/v1/webhook/ttn`
   - **Uplink message** : ✅ Activé

### Format des Données Capteur

Le décodeur de payload TTN doit formater les données comme suit :
```javascript
function Decoder(bytes, port) {
  return {
    remplissage_pct: bytes[0],  // 0-100
    batterie_V: (bytes[1] * 256 + bytes[2]) / 100  // ex: 3.70
  };
}
```

---

## 🗺️ Optimisation des Tournées

### Comment ça fonctionne ?

1. Le système lit l'état de toutes les poubelles
2. Filtre celles dont le remplissage **≥ 80%** (seuil critique configurable)
3. Construit une liste de coordonnées GPS (point de départ = dépôt ULPGL Goma)
4. Envoie ces coordonnées à l'**API Mapbox Optimization v1**
5. Mapbox retourne le **trajet optimal** (ordre des arrêts, distance, durée)
6. Le backend renvoie ces données au frontend pour affichage sur la carte

### Point de Départ (Dépôt)

```python
DEPOT_LAT = -1.6585   # Latitude ULPGL Goma
DEPOT_LON = 29.2205   # Longitude ULPGL Goma
SEUIL_CRITIQUE = 80   # Seuil de remplissage (%)
```

---

## 🖥️ Frontend Associé

Ce backend fonctionne avec le **Dashboard Frontend** disponible dans un repository séparé :

🔗 **[Mji_Safi_Connect-frontend](https://github.com/Projet-Mji-Safi-Connect/Mji_Safi_Connect-frontend)**

### Stack Frontend

| Technologie | Rôle |
|:---|:---|
| **React 19** + **TypeScript** | Framework UI |
| **Vite** | Build tool |
| **Mapbox GL JS** (`react-map-gl`) | Cartographie interactive |
| **Mantine UI** | Bibliothèque de composants |
| **Zustand** | Gestion d'état global |
| **Axios** | Client HTTP |

### Fonctionnalités du Dashboard

- 🗺️ **Carte interactive** de Goma avec les poubelles géolocalisées
- 🔴🟠🟢 **Marqueurs colorés** selon le niveau de remplissage (rouge > 80%, orange > 50%, vert sinon)
- 📊 **Popups informatifs** avec le détail de chaque poubelle (remplissage, batterie, ID)
- 🛣️ **Tracé de l'itinéraire optimal** directement sur la carte
- 📈 **Panneau de statistiques** (distance totale, durée estimée de la tournée)
- 🔄 **Actualisation automatique** des données toutes les 30 secondes (polling)

### Communication Frontend ↔ Backend

Le frontend communique avec ce backend via un proxy Vite configuré :
```
Frontend (localhost:5173) → Proxy → Backend (localhost:8000)
```
Toutes les requêtes vers `/api/*` sont automatiquement redirigées vers le backend.

---

## 🧪 Tester l'API

### Avec cURL

**Créer une poubelle :**
```bash
curl -X POST http://localhost:8000/api/v1/poubelles \
  -H "Content-Type: application/json" \
  -d '{"nom": "Poubelle Test", "device_id": "test-001", "latitude": -1.6585, "longitude": 29.2205}'
```

**Simuler un envoi TTN :**
```bash
curl -X POST http://localhost:8000/api/v1/webhook/ttn \
  -H "Content-Type: application/json" \
  -d '{"end_device_ids": {"device_id": "test-001"}, "uplink_message": {"decoded_payload": {"remplissage_pct": 85, "batterie_V": 3.7}}}'
```

**Lister les poubelles :**
```bash
curl http://localhost:8000/api/v1/poubelles
```

**Calculer la tournée optimale :**
```bash
curl http://localhost:8000/api/v1/tournee/optimale
```

---

## 🛠️ Développement

### Lancer en mode développement

```bash
# Avec rechargement automatique
uvicorn app.main:app --reload --port 8000
```

### Initialiser la base de données avec des données de test

Vous pouvez utiliser la documentation Swagger (`/docs`) pour créer vos 4 prototypes de poubelles avec l'endpoint `POST /api/v1/poubelles`.

### Dépendances principales

```
fastapi          # Framework API web haute performance
uvicorn          # Serveur ASGI
sqlmodel         # ORM (SQLAlchemy + Pydantic)
psycopg2-binary  # Driver PostgreSQL
httpx            # Client HTTP asynchrone
python-dotenv    # Variables d'environnement
```

---

## 📄 Licence

Ce projet est développé dans le cadre d'un **mémoire de fin d'études de Licence 3** en **Génie Électrique et Informatique**. Tous droits réservés.

---

<div align="center">

**Mji Safi Connect** — *Pour une ville de Goma plus propre et connectée* 🌍♻️

*Fait avec ❤️ à Goma, RD Congo*

</div>