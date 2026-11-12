-- database/schema.sql
-- Core tables for the Whale & Dolphin Conservation Platform.
-- NOTE: portable build uses numeric lat/lon; PostGIS geometry columns are the
-- production upgrade (ST_* functions). The schema is PostGIS-ready.

CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    username      TEXT UNIQUE NOT NULL,
    email         TEXT,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL DEFAULT 'researcher',
    created_at    TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS species (
    id                 SERIAL PRIMARY KEY,
    scientific_name    TEXT UNIQUE NOT NULL,
    common_name        TEXT NOT NULL,
    iucn_category      TEXT,
    conservation_note  TEXT
);

CREATE TABLE IF NOT EXISTS sightings (
    id               SERIAL PRIMARY KEY,
    species_id       INTEGER REFERENCES species(id),
    event_date       DATE,
    year             INTEGER,
    month            INTEGER,
    lat              DOUBLE PRECISION NOT NULL,
    lon              DOUBLE PRECISION NOT NULL,
    individual_count DOUBLE PRECISION DEFAULT 1,
    n_records        INTEGER DEFAULT 1,
    n_datasets       INTEGER DEFAULT 1,
    source           TEXT DEFAULT 'OBIS'
);

CREATE TABLE IF NOT EXISTS grid_cells (
    id               SERIAL PRIMARY KEY,
    lat              DOUBLE PRECISION NOT NULL,
    lon              DOUBLE PRECISION NOT NULL,
    depth_m          DOUBLE PRECISION,
    sst              DOUBLE PRECISION,
    hump_events      INTEGER DEFAULT 0,
    hump_inds        DOUBLE PRECISION DEFAULT 0,
    spin_events      INTEGER DEFAULT 0,
    spin_inds        DOUBLE PRECISION DEFAULT 0,
    vessel_intensity DOUBLE PRECISION,
    fishing_intensity DOUBLE PRECISION,
    noise_proxy      DOUBLE PRECISION,
    in_mpa           INTEGER DEFAULT 0,
    hump_suit        DOUBLE PRECISION,
    spin_suit        DOUBLE PRECISION,
    habitat_suit     DOUBLE PRECISION,
    species_density  DOUBLE PRECISION,
    risk_score       DOUBLE PRECISION,
    risk_class       TEXT
);

CREATE TABLE IF NOT EXISTS incidents (
    id         SERIAL PRIMARY KEY,
    species_id INTEGER REFERENCES species(id),
    event_date DATE,
    lat        DOUBLE PRECISION NOT NULL,
    lon        DOUBLE PRECISION NOT NULL,
    cause      TEXT,
    severity   TEXT
);

CREATE TABLE IF NOT EXISTS protected_areas (
    id           SERIAL PRIMARY KEY,
    name         TEXT NOT NULL,
    lat_center   DOUBLE PRECISION NOT NULL,
    lon_center   DOUBLE PRECISION NOT NULL,
    radius_deg   DOUBLE PRECISION,
    note         TEXT
);

CREATE TABLE IF NOT EXISTS corridors (
    id               SERIAL PRIMARY KEY,
    rank             INTEGER,
    from_lat         DOUBLE PRECISION,
    from_lon         DOUBLE PRECISION,
    to_lat           DOUBLE PRECISION,
    to_lon           DOUBLE PRECISION,
    mean_suitability DOUBLE PRECISION,
    nodes_json       TEXT
);

CREATE TABLE IF NOT EXISTS risk_predictions (
    id           SERIAL PRIMARY KEY,
    user_id      INTEGER REFERENCES users(id),
    lat          DOUBLE PRECISION NOT NULL,
    lon          DOUBLE PRECISION NOT NULL,
    risk_score   DOUBLE PRECISION,
    risk_class   TEXT,
    confidence   DOUBLE PRECISION,
    model_version TEXT DEFAULT 'rf_v1',
    created_at   TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS recommendations (
    id           SERIAL PRIMARY KEY,
    user_id      INTEGER REFERENCES users(id),
    lat          DOUBLE PRECISION NOT NULL,
    lon          DOUBLE PRECISION NOT NULL,
    threat       TEXT,
    action       TEXT,
    reason       TEXT,
    priority     TEXT,
    confidence   DOUBLE PRECISION,
    status       TEXT DEFAULT 'open',
    created_at   TIMESTAMP DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_sightings_ll ON sightings (lat, lon);
CREATE INDEX IF NOT EXISTS idx_grid_ll      ON grid_cells (lat, lon);
CREATE INDEX IF NOT EXISTS idx_corridors_r  ON corridors (rank);

-- ---------------------------------------------------------------------------
-- Bioacoustics, image identification and simulator records
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS recordings (
    id               SERIAL PRIMARY KEY,
    user_id          INTEGER REFERENCES users(id),
    filename         TEXT NOT NULL,
    duration_seconds DOUBLE PRECISION,
    sample_rate      INTEGER,
    created_at       TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS audio_analyses (
    id                    SERIAL PRIMARY KEY,
    recording_id          INTEGER REFERENCES recordings(id) ON DELETE SET NULL,
    user_id               INTEGER REFERENCES users(id),
    detected_species      TEXT,
    confidence            DOUBLE PRECISION,
    call_pattern          TEXT,
    dominant_frequency_hz DOUBLE PRECISION,
    snr_db                DOUBLE PRECISION,
    details               TEXT,
    created_at            TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS image_predictions (
    id               SERIAL PRIMARY KEY,
    user_id          INTEGER REFERENCES users(id),
    filename         TEXT NOT NULL,
    predicted_species TEXT,
    confidence       DOUBLE PRECISION,
    details          TEXT,
    created_at       TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS simulations (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER REFERENCES users(id),
    group_name TEXT,
    species    TEXT,
    turns      INTEGER,
    created_at TIMESTAMP DEFAULT now()
);

-- Observations submitted through the GIS collection workflow.
-- count_confirmed = FALSE marks a record the platform holds but has not
-- independently verified, so demonstration data is never shown as verified.
CREATE TABLE IF NOT EXISTS observations (
    id               SERIAL PRIMARY KEY,
    user_id          INTEGER REFERENCES users(id),
    species_id       INTEGER REFERENCES species(id),
    common_name      TEXT NOT NULL,
    scientific_name  TEXT,
    lat              DOUBLE PRECISION NOT NULL,
    lon              DOUBLE PRECISION NOT NULL,
    observed_at      DATE NOT NULL,
    individuals      INTEGER DEFAULT 1,
    notes            TEXT,
    media_type       TEXT,
    media_filename   TEXT,
    source           TEXT DEFAULT 'platform submission',
    count_confirmed  BOOLEAN DEFAULT TRUE,
    created_at       TIMESTAMP DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_obs_ll    ON observations (lat, lon);
CREATE INDEX IF NOT EXISTS idx_obs_date  ON observations (observed_at DESC);
CREATE INDEX IF NOT EXISTS idx_obs_user  ON observations (user_id, id DESC);

CREATE INDEX IF NOT EXISTS idx_audio_user  ON audio_analyses (user_id, id DESC);
CREATE INDEX IF NOT EXISTS idx_image_user  ON image_predictions (user_id, id DESC);
CREATE INDEX IF NOT EXISTS idx_rec_user    ON recordings (user_id, id DESC);