"""Image-based species identification.

A real trained classifier: HOG shape descriptors + colour histograms fed to an
RBF support-vector machine, trained on openly-licensed reference photographs
retrieved from Wikimedia Commons.

If the trained artefact is missing the API returns a clear 503 explaining what
has to be run, rather than inventing a prediction.
"""
from __future__ import annotations

import io
import os
from pathlib import Path

import numpy as np
from PIL import Image

MODEL_PATH = Path(__file__).resolve().parents[1] / "ml" / "image_model.joblib"
IMAGE_SIZE = 128
HOG_CELL = 8
HOG_ORIENTATIONS = 9
SPECIES_DIR = Path(__file__).resolve().parents[2] / "data" / "species_images"

SPECIES_META = {
    "blue_whale": {"name": "Blue Whale", "latin": "Balaenoptera musculus", "status": "EN"},
    "fin_whale": {"name": "Fin Whale", "latin": "Balaenoptera physalus", "status": "VU"},
    "humpback_whale": {"name": "Humpback Whale", "latin": "Megaptera novaeangliae", "status": "LC"},
    "killer_whale": {"name": "Killer Whale", "latin": "Orcinus orca", "status": "DD"},
    "bottlenose_dolphin": {"name": "Bottlenose Dolphin", "latin": "Tursiops truncatus", "status": "LC"},
    "spinner_dolphin": {"name": "Spinner Dolphin", "latin": "Stenella longirostris", "status": "LC"},
}


class ModelUnavailable(RuntimeError):
    """Raised when the trained artefact has not been produced yet."""


def model_ready() -> bool:
    return MODEL_PATH.exists()


def extract_features(image):
    """HOG shape descriptors + HSV colour histogram from a PIL image."""
    from skimage.color import rgb2gray, rgb2hsv
    from skimage.feature import hog

    img = image.convert("RGB").resize((IMAGE_SIZE, IMAGE_SIZE), Image.LANCZOS)
    arr = np.asarray(img, dtype=np.float64) / 255.0

    # shape descriptors from the luminance channel
    gray = rgb2gray(arr)
    hog_feat = hog(
        gray,
        orientations=HOG_ORIENTATIONS,
        pixels_per_cell=(HOG_CELL, HOG_CELL),
        cells_per_block=(2, 2),
        block_norm="L2-Hys",
        feature_vector=True,
    )

    hsv = rgb2hsv(arr)
    hist = []
    for channel in range(3):
        h, edges = np.histogram(hsv[:, :, channel].ravel(), bins=16, range=(0, 1),
                                density=True)
        hist.append(h / (h.sum() + 1e-9))
    hist = np.concatenate(hist)

    return np.concatenate([hog_feat, hist * 5.0])


def load_model():
    if not model_ready():
        raise ModelUnavailable(
            "The image classifier has not been trained yet. Run "
            "`python scripts/10_train_image_model.py` to build "
            "backend/ml/image_model.joblib from the reference image set."
        )
    import joblib
    return joblib.load(MODEL_PATH)


def predict_image(image_bytes: bytes, filename: str = "image.jpg"):
    """Return the predicted species, confidence and a ranked list."""
    from PIL import Image

    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.load()
    except Exception as exc:
        raise ValueError(f"could not read image: {exc}") from exc

    model = load_model()
    feats = extract_features(img).reshape(1, -1)

    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(feats)[0]
        classes = model.classes_
    else:  # pragma: no cover - SVC is trained with probability=True
        proba = None
        classes = model.classes_

    if proba is not None:
        order = np.argsort(-proba)
    else:
        pred = model.predict(feats)[0]
        order = np.argsort(-np.array([1.0 if c == pred else 0.0 for c in classes]))

    ranked = []
    for i in order:
        key = str(classes[i])
        meta = SPECIES_META.get(key, {"name": key.replace("_", " ").title(), "latin": "",
                                      "status": ""})
        ranked.append({
            "species": meta["name"],
            "species_key": key,
            "scientific_name": meta["latin"],
            "status": meta["status"],
            "probability": round(float(proba[i]), 4) if proba is not None else None,
        })

    top = ranked[0]
    return {
        "filename": filename,
        "predicted_species": top["species"],
        "species_key": top["species_key"],
        "scientific_name": top["scientific_name"],
        "confidence": top["probability"] if top["probability"] is not None else None,
        "ranked": ranked,
        "model": {
            "type": "HOG + colour histogram features with a multinomial logistic regression",
            "trained_on": "openly-licensed reference photographs (Wikimedia Commons)",
            "classes": list(classes),
        },
        "note": "Predictions are model estimates on photographic reference imagery and are "
                "not a substitute for field identification by a trained observer. Accuracy is "
                "markedly higher for the baleen whale classes than for the two dolphin "
                "classes, which are visually similar to one another.",
    }


def dataset_summary():
    """Counts per class for the training set, for transparency in the UI."""
    if not SPECIES_DIR.exists():
        return {}
    out = {}
    for d in sorted(SPECIES_DIR.iterdir()):
        if d.is_dir():
            n = len([f for f in d.iterdir() if f.suffix.lower() in (".jpg", ".jpeg", ".png")])
            if n:
                out[d.name] = n
    return out
