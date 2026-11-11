"""API routes for the bioacoustics, image-identification and simulator modules."""
from __future__ import annotations

import json
from typing import Optional

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app import db, security
from app import bioacoustics, imageid, simulator

router = APIRouter()

MAX_AUDIO_BYTES = 25 * 1024 * 1024   # 25 MB
MAX_IMAGE_BYTES = 8 * 1024 * 1024    # 8 MB
ALLOWED_AUDIO = {".wav", ".flac", ".ogg", ".oga", ".mp3", ".aiff", ".aif", ".au", ".w64"}
ALLOWED_IMAGE = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tif", ".tiff"}


# ------------------------------------------------------------------ auth dep
def current_user(authorization: str = Header(None, alias="Authorization")):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing bearer token")
    try:
        return security.decode_token(authorization.split(" ", 1)[1])
    except Exception:
        raise HTTPException(401, "Invalid or expired token")


def optional_user(authorization: str = Header(None, alias="Authorization")):
    """Identity when a valid token is supplied, otherwise None.

    Analysis endpoints are open so the platform can be explored without an
    account; results are only persisted for a signed-in researcher.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        return security.decode_token(authorization.split(" ", 1)[1])
    except Exception:
        return None


def _uid(user) -> Optional[int]:
    try:
        return int(user.get("sub"))
    except Exception:
        return None


def _ext(filename: str) -> str:
    return ("." + filename.rsplit(".", 1)[-1].lower()) if "." in filename else ""


# =========================================================== BIOACOUSTICS
@router.post("/api/audio/analyze")
async def analyze_audio(file: UploadFile = File(...), user=Depends(optional_user)):
    """Full analysis of an uploaded recording: features, spectrogram, waveform,
    species classification and acoustic-pattern interpretation."""
    name = file.filename or "recording"
    ext = _ext(name)
    if ext not in ALLOWED_AUDIO:
        raise HTTPException(415, f"Unsupported audio format '{ext}'. Accepted: "
                                 + ", ".join(sorted(ALLOWED_AUDIO)))
    data = await file.read()
    if len(data) > MAX_AUDIO_BYTES:
        raise HTTPException(413, "File is larger than the 25 MB limit")
    if not data:
        raise HTTPException(400, "The uploaded file is empty")

    try:
        result = bioacoustics.analyse(data, name, user_id=_uid(user))
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(503, f"Model artefact missing: {exc}")

    # persist
    uid = _uid(user)
    rec_id = None
    if uid is not None:
        try:
            db.execute(
                "INSERT INTO recordings (user_id, filename, duration_seconds, sample_rate) "
                "VALUES (%s,%s,%s,%s) RETURNING id",
                (uid, name, result["duration_seconds"], result["sample_rate"]),
            )
            row = db.fetch_one(
                "SELECT id FROM recordings WHERE user_id=%s AND filename=%s "
                "ORDER BY id DESC LIMIT 1", (uid, name))
            rec_id = row["id"] if row else None
            db.execute(
                "INSERT INTO audio_analyses (recording_id, user_id, detected_species, confidence, "
                "call_pattern, dominant_frequency_hz, snr_db, details) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (rec_id, uid, result["detected_species"], result["confidence"],
                 result["pattern"]["pattern"], result["pattern"]["dominant_frequency_hz"],
                 result["snr_db"], json.dumps({
                     "probabilities": result["probabilities"],
                     "pattern": result["pattern"],
                     "filename": name,
                 })),
            )
        except Exception:
            pass

    result["recording_id"] = rec_id
    return result


@router.post("/api/audio/classify")
async def classify_audio(file: UploadFile = File(...), user=Depends(optional_user)):
    """Classify a raw little-endian float32 PCM stream (decoded in the browser).

    This path supports MP3 and other containers that libsndfile cannot read by
    letting the browser decode the file first.
    """
    data = await file.read()
    if not data:
        raise HTTPException(400, "Empty audio payload")
    if len(data) > MAX_AUDIO_BYTES:
        raise HTTPException(413, "Audio payload exceeds the 25 MB limit")
    try:
        import numpy as np
        samples = np.frombuffer(data, dtype="<f4")
    except Exception as exc:
        raise HTTPException(400, f"Could not decode PCM payload: {exc}")

    if samples.size < 1024:
        raise HTTPException(400, "Audio payload is too short to analyse")

    sr = 16000
    try:
        window = samples[: int(16000 * 5.0)]
        if window.size < 1024:
            window = samples[:1024]
        feats = bioacoustics.mel_features(window, 16000)
        ranked = bioacoustics.classify(feats)
        pattern = bioacoustics.analyse_pattern(window, 16000, ranked[0][0])
        mel, freqs = bioacoustics.spectrogram(window, 16000, n_mels=48, max_frames=260)
        mins, maxs = bioacoustics.waveform_envelope(window)
        energy = mel.mean(axis=1)
        snr = float(10 * np.log10((np.percentile(energy, 95) + 1e-9)
                                  / (np.percentile(energy, 10) + 1e-9)))
        return {
            "detected_species": ranked[0][0].replace("_", " "),
            "confidence": round(ranked[0][1], 4),
            "probabilities": [{"species": c.replace("_", " "), "probability": round(p, 4)}
                              for c, p in ranked],
            "pattern": pattern.__dict__,
            "snr_db": round(snr, 2),
            "duration_seconds": round(len(samples) / 16000.0, 3),
            "sample_rate": 16000,
            "spectrogram": {
                "mels": [[round(float(v), 3) for v in row] for row in mel],
                "frequencies_hz": [round(float(v), 1) for v in freqs],
                "frames": int(mel.shape[1]),
            },
            "waveform": {"min": [round(v, 4) for v in mins], "max": [round(v, 4) for v in maxs]},
        }
    except FileNotFoundError as exc:
        raise HTTPException(503, f"Model artefact missing: {exc}")


@router.get("/api/audio/history")
def audio_history(limit: int = 50, user=Depends(current_user)):
    uid = _uid(user)
    rows = db.safe_fetch_all(
        "SELECT a.id, a.recording_id, a.detected_species, a.confidence, a.call_pattern, "
        "a.dominant_frequency_hz, a.snr_db, a.created_at, r.filename, r.duration_seconds "
        "FROM audio_analyses a LEFT JOIN recordings r ON r.id = a.recording_id "
        "WHERE a.user_id = %s ORDER BY a.id DESC LIMIT %s", (uid, min(int(limit), 200)))
    return {"count": len(rows), "analyses": [dict(r) for r in rows]}


@router.delete("/api/audio/history/{analysis_id}")
def delete_audio_history(analysis_id: int, user=Depends(current_user)):
    uid = _uid(user)
    ok = db.safe_execute("DELETE FROM audio_analyses WHERE id=%s AND user_id=%s", (analysis_id, uid))
    if not ok:
        raise HTTPException(503, "Database unavailable")
    return {"deleted": analysis_id}


# =========================================================== IMAGE IDENTIFICATION
@router.post("/api/image/identify")
async def identify_image(file: UploadFile = File(...), user=Depends(optional_user)):
    name = file.filename or "image.jpg"
    ext = _ext(name)
    if ext and ext not in ALLOWED_IMAGE:
        raise HTTPException(415, f"Unsupported image format '{ext}'. Accepted: "
                                 + ", ".join(sorted(ALLOWED_IMAGE)))
    data = await file.read()
    if not data:
        raise HTTPException(400, "The uploaded file is empty")
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(413, "Image is larger than the 8 MB limit")

    try:
        result = imageid.predict_image(data, name)
    except imageid.ModelUnavailable as exc:
        raise HTTPException(503, str(exc))
    except ValueError as exc:
        raise HTTPException(400, str(exc))

    uid = _uid(user)
    if uid is not None:
        try:
            db.execute(
                "INSERT INTO image_predictions (user_id, filename, predicted_species, confidence, "
                "details) VALUES (%s,%s,%s,%s,%s)",
                (uid, name, result["predicted_species"], result["confidence"],
                 json.dumps({"ranked": result["ranked"]})),
            )
        except Exception:
            pass
    return result


@router.get("/api/image/history")
def image_history(limit: int = 50, user=Depends(current_user)):
    uid = _uid(user)
    rows = db.safe_fetch_all(
        "SELECT id, filename, predicted_species, confidence, created_at "
        "FROM image_predictions WHERE user_id=%s ORDER BY id DESC LIMIT %s",
        (uid, min(int(limit), 200)))
    return {"count": len(rows), "predictions": [dict(r) for r in rows]}


# =========================================================== SIMULATOR
class SimulationBody(BaseModel):
    group: str = Field(..., description="'whale' or 'dolphin'")
    species: Optional[str] = None
    turns: int = 6


@router.post("/api/simulator/conversation")
def simulate_conversation(body: SimulationBody, user=Depends(optional_user)):
    try:
        result = simulator.simulate(body.group, body.species, body.turns)
    except ValueError as exc:
        raise HTTPException(400, str(exc))

    uid = _uid(user)
    if uid is not None:
        try:
            db.execute(
                "INSERT INTO simulations (user_id, group_name, species, turns) VALUES (%s,%s,%s,%s)",
                (uid, result["group"], result["species"], len(result["utterances"])),
            )
        except Exception:
            pass
    return result


@router.get("/api/simulator/species")
def simulator_species():
    out = []
    for group, species in simulator.SPECIES_PARAMS.items():
        for key, params in species.items():
            out.append({
                "group": group,
                "species": key,
                "name": params["name"],
                "scientific_name": params["latin"],
                "call_band_hz": list(params["call_band_hz"]),
                "pulse_rate_hz": params["pulse_rate_hz"],
            })
    return {"species": out}


# =========================================================== PUBLIC DIRECTORY
SPECIES_DIRECTORY = [
    {
        "id": "blue-whale", "name": "Blue Whale", "latin": "Balaenoptera musculus",
        "group": "Whale", "status": "EN", "status_label": "Endangered",
        "population": "~10,000–25,000", "length": "Up to 30 m", "weight": "Up to 180 tonnes",
        "diet": "Krill",
        "habitat": "Open ocean, from polar to tropical waters",
        "distribution": "Worldwide except the Arctic; migrates between feeding and breeding grounds",
        "description": "The largest animal known to have lived on Earth. Its calls are among the "
                       "loudest sounds made by any animal and can travel hundreds of kilometres "
                       "underwater.",
        "call_band_hz": [10, 40], "call_type": "Low-frequency swept call",
        "facts": [
            "Blue whale calls can reach 188 decibels, louder than a jet engine.",
            "A feeding blue whale can engulf up to 4 tonnes of krill in a single gulp.",
            "The species was protected from commercial whaling in 1966 under a near-global ban.",
        ],
    },
    {
        "id": "fin-whale", "name": "Fin Whale", "latin": "Balaenoptera physalus",
        "group": "Whale", "status": "VU", "status_label": "Vulnerable",
        "population": "~100,000", "length": "Up to 26 m", "weight": "Up to 80 tonnes",
        "diet": "Krill, small schooling fish",
        "habitat": "Offshore and open ocean, deep waters",
        "distribution": "Worldwide in all major oceans, mostly temperate to polar zones",
        "description": "The second-largest animal on Earth and one of the fastest swimming great "
                       "whales, reaching speeds of up to 40 km/h.",
        "call_band_hz": [15, 100], "call_type": "20 Hz downsweep call",
        "facts": [
            "The fin whale call at 20 Hz is the lowest-frequency reliably detected call of any whale.",
            "Fin whales travel widely, and individuals have been recorded across entire ocean basins.",
            "Populations continue to recover slowly after the commercial whaling era.",
        ],
    },
    {
        "id": "humpback-whale", "name": "Humpback Whale", "latin": "Megaptera novaeangliae",
        "group": "Whale", "status": "LC", "status_label": "Least Concern",
        "population": "~80,000", "length": "Up to 16 m", "weight": "Up to 40 tonnes",
        "diet": "Krill, small schooling fish",
        "habitat": "Coastal and open ocean; shelf and shelf-edge waters",
        "distribution": "Worldwide; long migrations between polar feeding grounds and tropical "
                       "breeding areas",
        "description": "Humpback whales are known for their complex songs, long pectoral fins and "
                       "spectacular breaching, and are among the most studied great whales.",
        "call_band_hz": [80, 4000], "call_type": "Phrase-based song",
        "facts": [
            "Humpback song changes progressively through the breeding season and is heard over "
            "hundreds of kilometres.",
            "Pectoral fins can be up to one third of the animal's body length.",
            "They are the focus of the sighting records held in this platform's database.",
        ],
    },
    {
        "id": "killer-whale", "name": "Killer Whale", "latin": "Orcinus orca",
        "group": "Whale", "status": "DD", "status_label": "Data Deficient",
        "population": "~50,000", "length": "Up to 9 m", "weight": "Up to 6 tonnes",
        "diet": "Fish, seals, other cetaceans (varies by population)",
        "habitat": "All oceans, from tropical seas to polar waters",
        "distribution": "Worldwide, in both coastal and offshore waters",
        "description": "The killer whale, or orca, is the largest member of the dolphin family. "
                       "Different populations have distinct cultures, diets and vocal dialects.",
        "call_band_hz": [100, 5000], "call_type": "Discrete signature call",
        "facts": [
            "Each resident population has a stable vocal dialect that calves inherit.",
            "Orcas are the largest members of the dolphin family, not true whales.",
            "Differences in diet and culture between populations are the reason the species is "
            "listed as Data Deficient.",
        ],
    },
    {
        "id": "bottlenose-dolphin", "name": "Bottlenose Dolphin", "latin": "Tursiops truncatus",
        "group": "Dolphin", "status": "LC", "status_label": "Least Concern",
        "population": "~600,000", "length": "Up to 4 m", "weight": "Up to 650 kg",
        "diet": "Fish, squid, crustaceans",
        "habitat": "Temperate and tropical seas, coastal and offshore",
        "distribution": "Worldwide in warm-temperate and tropical waters",
        "description": "The bottlenose dolphin is one of the best-known cetaceans, recognised for "
                       "its intelligence, curiosity and frequent presence near coasts and vessels.",
        "call_band_hz": [2000, 20000], "call_type": "Signature whistle",
        "facts": [
            "Each individual develops a signature whistle that others learn to associate with it.",
            "Dolphins use echolocation clicks with resolution comparable to a medical ultrasound.",
            "They routinely travel in pods of two to fifteen and occasionally much larger groups.",
        ],
    },
    {
        "id": "spinner-dolphin", "name": "Spinner Dolphin", "latin": "Stenella longirostris",
        "group": "Dolphin", "status": "LC", "status_label": "Least Concern",
        "population": "~1,000,000", "length": "Up to 2.4 m", "weight": "Up to 79 kg",
        "diet": "Small fish, squid",
        "habitat": "Tropical and subtropical pelagic waters",
        "distribution": "Worldwide in tropical and warm-temperate oceans",
        "description": "The spinner dolphin is named for its acrobatic spinning leaps. It rests in "
                       "sheltered bays during the day and feeds offshore at night.",
        "call_band_hz": [5000, 25000], "call_type": "High-frequency click train",
        "facts": [
            "Spinner dolphins rest in sheltered coastal bays by day and feed offshore at night.",
            "Their echolocation click rates rise sharply during deep off-shore foraging.",
            "They are the species with the largest published sighting dataset in this platform.",
        ],
    },
]


@router.get("/api/species/directory")
def species_directory():
    """Public species reference used by the Species Explorer page."""
    return {"count": len(SPECIES_DIRECTORY), "species": SPECIES_DIRECTORY}


@router.get("/api/public/stats")
def public_stats():
    """Headline figures computed from the platform database."""
    def scalar(sql, params=()):
        row = db.safe_fetch_one(sql, params)
        if not row:
            return None
        return list(row.values())[0]

    return {
        "sightings": scalar("SELECT count(*) AS c FROM sightings"),
        "incidents": scalar("SELECT count(*) AS c FROM incidents"),
        "grid_cells": scalar("SELECT count(*) AS c FROM grid_cells"),
        "protected_areas": scalar("SELECT count(*) AS c FROM protected_areas"),
        "corridors": scalar("SELECT count(*) AS c FROM corridors"),
        "species": scalar("SELECT count(*) AS c FROM species"),
        "database": "PostgreSQL",
        "database_connected": db.database_available(),
    }


@router.get("/api/public/sightings")
def public_sightings(limit: int = 2000, species_id: int = None, bbox: str = ""):
    """Public sighting records for the GIS explorer."""
    params = []
    where = []
    if species_id:
        where.append("s.species_id = %s")
        params.append(species_id)
    if bbox:
        try:
            lat_min, lat_max, lon_min, lon_max = [float(v) for v in bbox.split(",")]
            where.append("s.lat BETWEEN %s AND %s AND s.lon BETWEEN %s AND %s")
            params += [lat_min, lat_max, lon_min, lon_max]
        except Exception:
            raise HTTPException(400, "bbox must be 'lat_min,lat_max,lon_min,lon_max'")
    sql = ("SELECT s.id, s.species_id, sp.common_name, sp.scientific_name, s.event_date, "
           "s.lat, s.lon, s.individual_count, s.source "
           "FROM sightings s LEFT JOIN species sp ON sp.id = s.species_id")
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY s.event_date DESC LIMIT %s"
    params.append(min(int(limit), 10000))
    rows = db.safe_fetch_all(sql, tuple(params))
    return {"count": len(rows), "sightings": [dict(r) for r in rows]}


@router.get("/api/models/status")
def models_status():
    """Which trained artefacts are actually available on this deployment."""
    audio_ok = False
    try:
        bioacoustics._model()
        audio_ok = True
    except Exception:
        audio_ok = False
    image_ok = imageid.model_ready()
    return {
        "audio_classifier": {
            "available": audio_ok,
            "type": "logistic regression over 64 mel bands (mean + std)",
            "classes": ["blue_whale", "fin_whale", "humpback_whale", "killer_whale",
                        "bottlenose_dolphin", "background"],
        },
        "image_classifier": {
            "available": image_ok,
            "type": "HOG + colour histogram with multinomial logistic regression",
        },
        "grid_risk_model": {"available": True,
                            "type": "random forest over ocean grid features"},
        "database": {"connected": db.database_available()},
    }
