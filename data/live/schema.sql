PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS venues (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  area TEXT,
  address TEXT,
  lat REAL,
  lng REAL
);

CREATE TABLE IF NOT EXISTS events (
  id TEXT PRIMARY KEY,
  date TEXT NOT NULL,
  start_at TEXT,
  end_at TEXT,
  title TEXT NOT NULL,
  venue_id TEXT,
  admission_price INTEGER,
  drink_price INTEGER,
  total_price INTEGER,
  budget_status TEXT NOT NULL DEFAULT 'unknown' CHECK (budget_status IN ('under','unknown','over')),
  reservation_required INTEGER NOT NULL DEFAULT 0,
  note TEXT,
  source_url TEXT,
  fetched_at TEXT,
  FOREIGN KEY (venue_id) REFERENCES venues(id)
);

CREATE TABLE IF NOT EXISTS artists (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS event_artists (
  event_id TEXT NOT NULL,
  artist_id TEXT NOT NULL,
  PRIMARY KEY (event_id, artist_id),
  FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
  FOREIGN KEY (artist_id) REFERENCES artists(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS sources (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id TEXT NOT NULL,
  url TEXT NOT NULL,
  source_type TEXT,
  checked_at TEXT,
  confidence TEXT,
  UNIQUE(event_id, url),
  FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_events_date ON events(date);
CREATE INDEX IF NOT EXISTS idx_events_budget ON events(budget_status, total_price);
CREATE INDEX IF NOT EXISTS idx_events_venue ON events(venue_id);
CREATE INDEX IF NOT EXISTS idx_sources_event ON sources(event_id);
