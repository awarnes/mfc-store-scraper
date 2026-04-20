-- TABLE DEFINITIONS

-- Patch History Table
CREATE TABLE IF NOT EXISTS public.patch_history (
    filename TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Set updated_at during updates
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Insert old price into history when price changes
CREATE OR REPLACE FUNCTION trigger_archive_price()
RETURNS TRIGGER AS $$
BEGIN
  IF OLD.current_price_dollars IS DISTINCT FROM NEW.current_price_dollars
     OR OLD.current_price_unit IS DISTINCT FROM NEW.current_price_unit THEN
    INSERT INTO public.price_history (
        skus_id,
        price_dollars,
        price_unit,
        stock,
        recorded_at
    ) VALUES (
        OLD.skus_id,
        OLD.current_price_dollars,
        OLD.current_price_unit,
        OLD.stock,
        OLD.updated_at
    );
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Vendors Table
CREATE TABLE IF NOT EXISTS public.vendors (
    vendors_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TRIGGER set_timestamp_update_vendors
BEFORE UPDATE ON public.vendors
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

-- Products Table
CREATE TABLE IF NOT EXISTS public.products (
    products_id SERIAL PRIMARY KEY,
    vendors_id INTEGER NOT NULL REFERENCES public.vendors(vendors_id) ON DELETE CASCADE,
    canonical_products_id INTEGER REFERENCES public.products(products_id) ON DELETE SET NULL,
    vendor_product_id TEXT,
    name TEXT NOT NULL,
    short_description TEXT,
    description TEXT,
    slug TEXT,
    vendor_data JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(vendors_id, vendor_product_id)
);

CREATE INDEX idx_products_vendor ON public.products(vendors_id);
CREATE INDEX idx_products_canonical ON public.products(canonical_products_id);

CREATE TRIGGER set_timestamp_update_products
BEFORE UPDATE ON public.products
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

-- SKUs Table
CREATE TABLE IF NOT EXISTS public.skus (
    skus_id SERIAL PRIMARY KEY,
    products_id INTEGER NOT NULL REFERENCES public.products(products_id) ON DELETE CASCADE,
    vendors_id INTEGER NOT NULL REFERENCES public.vendors(vendors_id) ON DELETE CASCADE,
    code TEXT,
    size TEXT,
    weight JSONB,
    current_price_dollars DECIMAL(10,2),
    current_price_unit TEXT,
    stock INTEGER DEFAULT 0,
    vendor_sku_data JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(vendors_id, code)
);

CREATE INDEX idx_skus_product ON public.skus(products_id);
CREATE INDEX idx_skus_vendor ON public.skus(vendors_id);

CREATE TRIGGER set_timestamp_update_skus
BEFORE UPDATE ON public.skus
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

CREATE TRIGGER archive_price_on_update
BEFORE UPDATE ON public.skus
FOR EACH ROW
EXECUTE PROCEDURE trigger_archive_price();

-- Price History Table
CREATE TABLE IF NOT EXISTS public.price_history (
    price_history_id SERIAL PRIMARY KEY,
    skus_id INTEGER NOT NULL REFERENCES public.skus(skus_id) ON DELETE CASCADE,
    price_dollars DECIMAL(10,2),
    price_unit TEXT,
    stock INTEGER,
    recorded_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX idx_price_history_sku ON public.price_history(skus_id);
CREATE INDEX idx_price_history_recorded ON public.price_history(recorded_at);
