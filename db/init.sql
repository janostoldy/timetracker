CREATE TABLE focus_sessions (
    id SERIAL PRIMARY KEY,
    focus_name TEXT NOT NULL,
    device TEXT,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ
);
