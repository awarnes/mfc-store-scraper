-- TABLE DEFINITIONS
-- Patch History Table
CREATE TABLE IF NOT EXISTS public.patch_history (
    filename TEXT PRIMARY KEY,
    created TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Set updated_at during updates
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE SCHEMA IF NOT EXISTS azure;

CREATE TABLE IF NOT EXISTS azure.products (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT,
    short_description TEXT,
    description TEXT,
    slug TEXT,
    storage_climate TEXT,
    unshippable_regions JSONB,
    brand JSONB,
    substitutions JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE OR REPLACE TRIGGER set_timestamp_update_products
BEFORE UPDATE ON azure.products
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

CREATE TABLE IF NOT EXISTS azure.packaging (
    id SERIAL,
    products_id INTEGER NOT NULL,
    code TEXT,
    size TEXT,
    weight JSONB,
    stock INTEGER DEFAULT 0,
    images JSONB,
    rewards_enabled BOOLEAN DEFAULT FALSE,
    freight_handling_required BOOLEAN DEFAULT FALSE,
    tags JSONB,
    primary_category INTEGER,
    favorites INTEGER,
    next_purchase_arrival TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(products_id, code)
);

CREATE OR REPLACE TRIGGER set_timestamp_update_packaging
BEFORE UPDATE ON azure.packaging
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

CREATE TABLE IF NOT EXISTS azure.prices (
    id SERIAL,
    packaging_code TEXT NOT NULL,
    retail_dollars REAL,
    retail_unit TEXT,
    wholesale_dollars REAL,
    wholesale_unit TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE OR REPLACE TRIGGER set_timestamp_update_prices
BEFORE UPDATE ON azure.prices
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();
