"""
Intelligent Whale & Dolphin Conservation Platform - FastAPI backend.
Run:  uvicorn app.main:app --reload   (from backend/)
"""
import json
import pickle
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app import db, security
from app.recommendations import generate_recommendations
from app.routes_analysis import router as analysis_router

ROOT = Path(__file__).resolve().parent.parent.parent  # project root
GEO_DIR = ROOT / "data" / "geojson"
META_DIR = ROOT / "data" / "processed"
ML_DIR = ROOT / "backend" / "ml"

app = FastAPI(title="Whale & Dolphin Conservation Platform", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(analysis_router)

# ---------- load ML model once at startup --------------------------------
with open(ML_DIR / "model.pkl", "rb") as f:
    _model_bundle = pickle.load(f)
MODEL = _model_bundle["model"]
FEATURES = _model_bundle["features"]
CLASSES = _model_bundle["classes"]

with open(ML_DIR / "ml_metrics.json") as f:
    METRICS = json.load(f)

with open(META_DIR / "features_metadata.json") as f:
    FEAT_META = json.load(f)

GEOJSON_FILES = {
    "risk": "risk_cells.geojson",
    "sightings": "sightings.geojson",
    "hotspots": "hotspots.geojson",
    "corridors": "corridors.geojson",
    "mpas": "mpas.geojson",
    "incidents": "incidents.geojson",
    "vessels": "vessels.geojson",
}

LAYER_CATALOG = [
    {"name": "risk", "label": "Risk zones", "url": "/api/layers/risk", "default_on": True, "kind": "polygon"},
    {"name": "sightings", "label": "Whale & dolphin sightings", "url": "/api/layers/sightings", "default_on": True, "kind": "point"},
    {"name": "vessels", "label": "Vessel traffic", "url": "/api/layers/vessels", "default_on": True, "kind": "point"},
    {"name": "incidents", "label": "Historical incidents", "url": "/api/layers/incidents", "default_on": False, "kind": "point"},
    {"name": "corridors", "label": "Predicted corridors", "url": "/api/layers/corridors", "default_on": True, "kind": "line"},
    {"name": "hotspots", "label": "Sighting hotspots", "url": "/api/layers/hotspots", "default_on": False, "kind": "point"},
    {"name": "mpas", "label": "Protected marine areas", "url": "/api/layers/mpas", "default_on": True, "kind": "polygon"},
]


# ---------- auth ----------------------------------------------------------
class LoginBody(BaseModel):
    username: str
    password: str


class RegisterBody(LoginBody):
    email: str = ""
    role: str = "researcher"


def require_auth(authorization: str = Header(None, alias="Authorization")):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing bearer token")
    try:
        return security.decode_token(authorization.split(" ", 1)[1])
    except Exception:
        raise HTTPException(401, "Invalid or expired token")


@app.get("/api/health")
def health():
    return {"status": "ok", "model": METRICS.get("f1_weighted")}


@app.post("/api/auth/register")
def register(b: RegisterBody):
    if db.fetch_one("SELECT id FROM users WHERE username=%s", (b.username,)):
        raise HTTPException(400, "Username taken")
    db.execute(
        "INSERT INTO users (username,email,password_hash,role) VALUES (%s,%s,%s,%s)",
        (b.username, b.email, security.hash_password(b.password), b.role),
    )
    return {"message": "registered"}


@app.post("/api/auth/login")
def login(b: LoginBody):
    row = db.fetch_one("SELECT * FROM users WHERE username=%s", (b.username,))
    if not row or not security.verify_password(b.password, row["password_hash"]):
        raise HTTPException(401, "Invalid credentials")
    token = security.create_token(row["id"], row["username"], row["role"])
    return {"token": token, "role": row["role"], "username": row["username"]}


# ---------- data read endpoints --------------------------------------------
@app.get("/api/species")
def species(user=Depends(require_auth)):
    return db.fetch_all("SELECT * FROM species ORDER BY common_name")


@app.get("/api/sightings")
def sightings(bbox: str = "", species_id: int = None, limit: int = 2000, user=Depends(require_auth)):
    """bbox as lat_min,lon_min,lat_max,lon_max"""
    sql = "SELECT * FROM sightings"
    params = []
    where = []
    if bbox:
        lat0, lon0, lat1, lon1 = (float(x) for x in bbox.split(","))
        where.append("lat BETWEEN %s AND %s AND lon BETWEEN %s AND %s")
        params += [lat0, lat1, lon0, lon1]
    if species_id:
        where.append("species_id=%s")
        params.append(species_id)
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY event_date DESC LIMIT %s"
    params.append(limit)
    rows = db.fetch_all(sql, params)
    feats = [{
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [r["lon"], r["lat"]]},
        "properties": {"date": str(r["event_date"]), "count": round(r["individual_count"]),
                       "source": r["source"]},
    } for r in rows]
    return {"type": "FeatureCollection", "features": feats}


@app.get("/api/layers/{name}")
def layer(name: str, user=Depends(require_auth)):
    if name not in GEOJSON_FILES:
        raise HTTPException(404, "no such layer")
    return FileResponse(GEO_DIR / GEOJSON_FILES[name], media_type="application/geo+json")


@app.get("/api/map-layers")
def map_layers(user=Depends(require_auth)):
    return LAYER_CATALOG


@app.get("/api/corridors")
def corridors(user=Depends(require_auth)):
    rows = db.fetch_all("SELECT * FROM corridors ORDER BY rank")
    return [{
        "rank": r["rank"], "from": [r["from_lat"], r["from_lon"]],
        "to": [r["to_lat"], r["to_lon"]], "mean_suitability": r["mean_suitability"],
    } for r in rows]


# ---------- risk prediction ------------------------------------------------
def nearest_cell(lat, lon):
    return db.fetch_one(
        "SELECT * FROM grid_cells ORDER BY abs(lat-%s)+abs(lon-%s) LIMIT 1",
        (float(lat), float(lon)),
    )


def predict_from_cell(c):
    x = [[c[f] for f in FEATURES]]
    proba = MODEL.predict_proba(x)[0]
    cls = CLASSES[int(proba.argmax())]
    conf = float(proba.max())
    imp = METRICS["feature_importance"]
    top = sorted(FEATURES, key=lambda f: imp.get(f, 0) * (c.get(f) or 0), reverse=True)[:3]
    return {"risk_class": cls, "confidence": round(conf, 3), "risk_score": round(float(c["risk_score"]), 4),
            "top_factors": top}


@app.get("/api/risk/predict")
def predict(lat: float = Query(...), lon: float = Query(...), save: bool = False, user=Depends(require_auth)):
    c = nearest_cell(lat, lon)
    if not c:
        raise HTTPException(404, "cell not found")
    result = predict_from_cell(c)
    if save:
        db.execute(
            "INSERT INTO risk_predictions (user_id,lat,lon,risk_score,risk_class,confidence,model_version) "
            "VALUES (%s,%s,%s,%s,%s,%s,'rf_v1')",
            (user["sub"], c["lat"], c["lon"], c["risk_score"], result["risk_class"], result["confidence"]),
        )
    return {**result, "cell": {"lat": c["lat"], "lon": c["lon"]}}


@app.get("/api/risk/summary")
def risk_summary(user=Depends(require_auth)):
    dist = db.fetch_all("SELECT risk_class, COUNT(*) n FROM grid_cells GROUP BY risk_class")
    total = sum(r["n"] for r in dist)
    return {"distribution": dist, "total_cells": total,
            "pct_high_critical": round(100 * sum(r["n"] for r in dist if r["risk_class"] in ("High", "Critical")) / total, 1)}


@app.get("/api/risk/model")
def risk_model_info(user=Depends(require_auth)):
    return {
        "f1_weighted": METRICS["f1_weighted"], "accuracy": METRICS["accuracy"],
        "roc_auc": METRICS["roc_auc_ovr"], "logistic_f1": METRICS["logistic_f1_weighted"],
        "feature_importance": METRICS["feature_importance"],
        "confusion_matrix": METRICS["confusion_matrix"], "classes": METRICS["classes"],
        "formula": FEAT_META.get("risk_formula"), "thresholds": FEAT_META.get("thresholds"),
    }


# ---------- recommendations -------------------------------------------------
class RecBody(BaseModel):
    lat: float
    lon: float


@app.get("/api/recommendations")
def get_recommendations(cls: str = "", user=Depends(require_auth)):
    sql = "SELECT * FROM recommendations"
    params = []
    if cls:
        sql += " WHERE threat=%s"
        params.append(cls)
    sql += " ORDER BY created_at DESC LIMIT 100"
    return db.fetch_all(sql, params)


@app.post("/api/recommendations")
def make_recommendation(b: RecBody, user=Depends(require_auth)):
    c = nearest_cell(b.lat, b.lon)
    if not c:
        raise HTTPException(404, "cell not found")
    pred = predict_from_cell(c)
    recs = generate_recommendations({**c, "risk_class": pred["risk_class"]}, pred["confidence"])
    out = []
    for r in recs:
        db.execute(
            "INSERT INTO recommendations (user_id,lat,lon,threat,action,reason,priority,confidence) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (user["sub"], c["lat"], c["lon"], r["threat"], r["action"], r["reason"],
             r["priority"], r["confidence"]),
        )
        out.append({**r, "lat": c["lat"], "lon": c["lon"]})
    return {"cell": {"lat": c["lat"], "lon": c["lon"]}, "predictions": pred, "advisories": out}


# ---------- dashboard -------------------------------------------------------
@app.get("/api/dashboard/summary")
def dash_summary(user=Depends(require_auth)):
    sightings = db.fetch_one("SELECT COUNT(*) n, COUNT(DISTINCT species_id) sp FROM sightings")
    incidents = db.fetch_one("SELECT COUNT(*) n, COUNT(*) FILTER (WHERE severity='fatal') fatal FROM incidents")
    recs = db.fetch_one("SELECT COUNT(*) n FROM recommendations")
    return {
        "sightings": sightings["n"], "species": sightings["sp"],
        "incidents": incidents["n"], "fatal_incidents": incidents["fatal"],
        "recommendations": recs["n"],
        "risk": db.fetch_all("SELECT risk_class, COUNT(*) n FROM grid_cells GROUP BY risk_class"),
    }


@app.get("/api/dashboard/trend")
def dash_trend(user=Depends(require_auth)):
    by_year = db.fetch_all("SELECT year, COUNT(*) n FROM sightings GROUP BY year ORDER BY year")
    by_month = db.fetch_all("SELECT month, COUNT(*) n FROM sightings GROUP BY month ORDER BY month")
    return {"by_year": by_year, "by_month": by_month}


@app.get("/api/icons")
def icons():
    return {"whale": "🐋", "dolphin": "🐬"}