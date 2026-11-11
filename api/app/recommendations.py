"""Rule-based conservation recommendation engine.

Produces decision-support advisories (NOT legal/regulatory orders).
Each advisory has: threat, action, reason, priority, confidence, status.
Input is a grid-cell feature dictionary.
"""
THREAT_LABELS = {
    "vessel_intensity": "ship collisions",
    "fishing_intensity": "bycatch / entanglement",
    "noise_proxy": "underwater noise disturbance",
    "habitat_suit": "habitat degradation",
    "species_density": "high species presence",
}


def generate_recommendations(cell: dict, model_confidence: float = 0.7):
    """cell keys: risk_class, risk_score, vessel_intensity, fishing_intensity,
    noise_proxy, habitat_suit, species_density, in_mpa, lat, lon."""
    recs = []
    cls = cell.get("risk_class")
    v = float(cell.get("vessel_intensity", 0) or 0)
    f = float(cell.get("fishing_intensity", 0) or 0)
    n = float(cell.get("noise_proxy", 0) or 0)
    h = float(cell.get("habitat_suit", 0) or 0)
    s = float(cell.get("species_density", 0) or 0)
    mpa = int(cell.get("in_mpa", 0) or 0)
    conf = float(model_confidence or 0.7)

    high = cls in ("High", "Critical")
    if cls == "Critical" or (high and v > 0.45):
        recs.append(dict(
            threat="ship collisions",
            action="Seasonal vessel speed reduction (<=10 kn) in this cell during peak season",
            reason="Critical/High risk with high vessel intensity near known sightings",
            priority="High", confidence=round(conf * min(1.0, v + 0.3), 2),
        ))
    if high and f > 0.5:
        recs.append(dict(
            threat="bycatch / entanglement",
            action="Seasonal fishing-gear restriction / bycatch mitigation in hotspot",
            reason="High fishing intensity overlapping predicted habitat use",
            priority="High", confidence=round(conf * min(1.0, f + 0.2), 2),
        ))
    if high and n > 0.5:
        recs.append(dict(
            threat="underwater noise disturbance",
            action="Slow-steaming / noise-monitoring zone; advise reduced engine activity",
            reason="Elevated noise proxy (derived from vessel traffic)",
            priority="Medium", confidence=round(conf * min(1.0, n + 0.2), 2),
        ))
    if h > 0.4 and s > 0 and high:
        recs.append(dict(
            threat="habitat degradation",
            action="Designate or extend a seasonal protection zone here",
            reason="High habitat suitability with recorded species presence and high risk",
            priority="High", confidence=round(conf * min(1.0, h + s), 2),
        ))
    if high and not mpa:
        recs.append(dict(
            threat="habitat degradation",
            action="Evaluate extending Marine Protected Area coverage to this cell",
            reason="Unprotected cell with elevated risk",
            priority="Medium", confidence=round(conf * 0.7, 2),
        ))
    if high and s > 0:
        recs.append(dict(
            threat="ship collisions",
            action="Issue alert/advisory zone on dashboard for vessel traffic",
            reason="Species presence confirmed in high-risk cell",
            priority="High", confidence=round(conf * 0.85, 2),
        ))
    if not recs:
        recs.append(dict(
            threat="general",
            action="Maintain routine monitoring of this cell",
            reason="No dominant threat identified",
            priority="Low", confidence=0.6,
        ))
    return recs