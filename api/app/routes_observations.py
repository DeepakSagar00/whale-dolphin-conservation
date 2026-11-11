"""Observation collection and dashboard aggregation.

Observations submitted through the GIS workflow are stored in PostgreSQL and
become part of the platform record immediately. Every aggregate in this module
is computed from the database - nothing is hard-coded.
"""
from __future__ import annotations

import json
import math
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from app import db, security

router = APIRouter()

MAX_LAT, MAX_LON = 90.0, 180.0


def _uid(user) -> Optional[int]:
    try:
        return int(user.get("sub"))
    except Exception:
        return None


def current_user(authorization: str = Header(None, alias="Authorization")):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing bearer token")
    try:
        return security.decode_token(authorization.split(" ", 1)[1])
    except Exception:
        raise HTTPException(401, "Invalid or expired token")


def optional_user(authorization: str = Header(None, alias="Authorization")):
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        return security.decode_token(authorization.split(" ", 1)[1])
    except Exception:
        return None


class ObservationBody(BaseModel):
    species: str = Field(..., description="Common name of the observed species")
    scientific_name: Optional[str] = None
    lat: float
    lon: float
    observed_at: str = Field(..., description="ISO date, YYYY-MM-DD")
    individuals: int = Field(1, ge=1, le=5000)
    notes: str = ""
    media_type: str = Field("", description="'photo' | 'audio' | '' ")
    media_filename: str = ""
    source: str = Field("platform submission")
    count_confirmed: bool = True


@router.post("/api/observations")
def create_observation(body: ObservationBody, user=Depends(current_user)):
    """Store a new observation submitted through the GIS map workflow."""
    if not (-MAX_LAT <= body.lat <= MAX_LAT):
        raise HTTPException(400, "Latitude must be between -90 and 90")
    if not (-MAX_LON <= body.lon <= MAX_LON):
        raise HTTPException(400, "Longitude must be between -180 and 180")
    if not body.species.strip():
        raise HTTPException(400, "Species is required")
    try:
        import datetime as _dt
        _dt.date.fromisoformat(body.observed_at)
    except Exception:
        raise HTTPException(400, "observed_at must be an ISO date (YYYY-MM-DD)")

    # match the species against the reference table where possible
    sp = db.safe_fetch_one(
        "SELECT id, scientific_name FROM species WHERE lower(common_name) = lower(%s)",
        (body.species.strip(),))
    species_id = sp["id"] if sp else None
    sci = body.scientific_name or (sp["scientific_name"] if sp else None)

    ok = db.safe_execute(
        "INSERT INTO observations (user_id, species_id, common_name, scientific_name, lat, lon, "
        "observed_at, individuals, notes, media_type, media_filename, source, count_confirmed) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
        (_uid(user), species_id, body.species.strip(), sci, body.lat, body.lon,
         body.observed_at, body.individuals, body.notes.strip(), body.media_type,
         body.media_filename, body.source, body.count_confirmed))
    if not ok:
        raise HTTPException(503, "The database is not reachable, so this observation could not "
                                 "be stored. Please try again shortly.")

    row = db.safe_fetch_one(
        "SELECT id, user_id, species_id, common_name, scientific_name, lat, lon, observed_at, "
        "individuals, notes, media_type, media_filename, source, created_at "
        "FROM observations ORDER BY id DESC LIMIT 1")
    return {"status": "stored", "observation": dict(row) if row else None}


@router.get("/api/observations")
def list_observations(limit: int = 200, species: str = "", region: str = "",
                      date_from: str = "", date_to: str = ""):
    where = []
    params = []
    if species:
        where.append("lower(common_name) = lower(%s)")
        params.append(species)
    if date_from:
        where.append("observed_at >= %s")
        params.append(date_from)
    if date_to:
        where.append("observed_at <= %s")
        params.append(date_to)
    sql = ("SELECT id, user_id, species_id, common_name, scientific_name, lat, lon, observed_at, "
           "individuals, notes, media_type, media_filename, source, count_confirmed, created_at "
           "FROM observations")
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY observed_at DESC, id DESC LIMIT %s"
    params.append(min(int(limit), 2000))
    rows = db.safe_fetch_all(sql, tuple(params))
    return {"count": len(rows), "observations": [dict(r) for r in rows]}


@router.delete("/api/observations/{observation_id}")
def delete_observation(observation_id: int, user=Depends(current_user)):
    ok = db.safe_execute("DELETE FROM observations WHERE id=%s AND user_id=%s",
                         (observation_id, _uid(user)))
    if not ok:
        raise HTTPException(503, "The database is not reachable")
    return {"deleted": observation_id}


@router.get("/api/dashboard/overview")
def dashboard_overview():
    """Aggregated figures for the professional dashboard - all from the database."""
    def scalar(sql, params=()):
        row = db.safe_fetch_one(sql, params)
        return list(row.values())[0] if row else 0

    sightings = scalar("SELECT count(*) AS c FROM sightings")
    incidents = scalar("SELECT count(*) AS c FROM incidents")
    grid_cells = scalar("SELECT count(*) AS c FROM grid_cells")
    protected = scalar("SELECT count(*) AS c FROM protected_areas")
    species_rows = db.safe_fetch_all(
        "SELECT common_name, scientific_name, iucn_category, conservation_note FROM species "
        "ORDER BY common_name")
    observations = scalar("SELECT count(*) AS c FROM observations")

    by_severity = db.safe_fetch_all(
        "SELECT severity, count(*) AS c FROM incidents GROUP BY severity ORDER BY c DESC")
    by_cause = db.safe_fetch_all(
        "SELECT cause, count(*) AS c FROM incidents GROUP BY cause ORDER BY c DESC LIMIT 6")
    by_year = db.safe_fetch_all(
        "SELECT year, count(*) AS c FROM sightings WHERE year IS NOT NULL GROUP BY year ORDER BY year")
    risk = db.safe_fetch_all(
        "SELECT risk_class, count(*) AS c FROM grid_cells GROUP BY risk_class")
    recent_incidents = db.safe_fetch_all(
        "SELECT i.id, i.event_date, i.lat, i.lon, i.cause, i.severity, sp.common_name "
        "FROM incidents i LEFT JOIN species sp ON sp.id = i.species_id "
        "ORDER BY i.event_date DESC, i.id DESC LIMIT 8")
    recent_sightings = db.safe_fetch_all(
        "SELECT s.id, s.event_date, s.lat, s.lon, s.individual_count, sp.common_name, "
        "sp.scientific_name FROM sightings s LEFT JOIN species sp ON sp.id = s.species_id "
        "ORDER BY s.event_date DESC, s.id DESC LIMIT 8")
    top_species = db.safe_fetch_all(
        "SELECT sp.common_name, count(*) AS c FROM sightings s "
        "JOIN species sp ON sp.id = s.species_id GROUP BY sp.common_name ORDER BY c DESC")

    # alerts derived from real records
    alerts = []
    fatal = scalar("SELECT count(*) AS c FROM incidents WHERE severity = 'fatal'")
    severe = scalar("SELECT count(*) AS c FROM incidents WHERE severity = 'severe'")
    if fatal:
        alerts.append({
            "level": "critical", "title": "Fatality records present",
            "detail": f"{fatal} fatal incidents are recorded in the platform database.",
            "source": "incidents table",
        })
    if severe:
        alerts.append({
            "level": "warning", "title": "Severe incidents recorded",
            "detail": f"{severe} incidents are classified as severe.",
            "source": "incidents table",
        })
    critical = 0
    for r in risk:
        if r["risk_class"] == "Critical":
            critical = r["c"]
    if critical:
        alerts.append({
            "level": "critical", "title": "Critical risk cells",
            "detail": f"{critical} of {grid_cells} modelled ocean cells are in the Critical "
                      f"conservation risk class.",
            "source": "grid_cells risk model",
        })
    endangered = [s for s in species_rows if (s["iucn_category"] or "").upper() in ("EN", "VU")]
    if endangered:
        alerts.append({
            "level": "warning", "title": "Species under threat",
            "detail": ", ".join(f"{s['common_name']} ({s['iucn_category']})" for s in endangered),
            "source": "species reference table",
        })

    return {
        "totals": {
            "sightings": sightings,
            "incidents": incidents,
            "observations": observations,
            "grid_cells": grid_cells,
            "protected_areas": protected,
            "species": len(species_rows),
        },
        "species": [dict(s) for s in species_rows],
        "incidents_by_severity": [dict(r) for r in by_severity],
        "incidents_by_cause": [dict(r) for r in by_cause],
        "sightings_by_year": [dict(r) for r in by_year],
        "risk_classes": [dict(r) for r in risk],
        "recent_incidents": [dict(r) for r in recent_incidents],
        "recent_sightings": [dict(r) for r in recent_sightings],
        "top_species": [dict(r) for r in top_species],
        "alerts": alerts,
        "database_connected": db.database_available(),
    }
