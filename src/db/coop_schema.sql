-- ============================================================================
-- COOP DATABASE SCHEMA
-- Food Coop/Buyers Club - Multi-vendor support
-- ============================================================================

-- Migration tracking
CREATE TABLE IF NOT EXISTS public.patch_history (
    filename TEXT PRIMARY KEY
    , created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- UTILITY FUNCTIONS
-- ============================================================================

-- Get or create a system user based on connection info
-- Used as fallback when application doesn't provide user context
CREATE OR REPLACE FUNCTION get_or_create_connection_user()
RETURNS INTEGER AS $$
DECLARE
    v_email TEXT;
    v_user_id INTEGER;
BEGIN
    -- Build identifier from connection info
    SELECT format('%s@%s', usename, COALESCE(NULLIF(application_name, ''), 'unknown'))
    INTO v_email
    FROM pg_stat_activity
    WHERE pid = pg_backend_pid();

    -- Look for existing user
    SELECT users_id INTO v_user_id
    FROM public.users
    WHERE email = v_email
    LIMIT 1;

    -- Create if not found
    IF v_user_id IS NULL THEN
        INSERT INTO public.users (email, is_system_user, is_active)
        VALUES (v_email, TRUE, TRUE)
        RETURNING users_id INTO v_user_id;
    END IF;

    RETURN v_user_id;
END;
$$ LANGUAGE plpgsql;

-- Get current user ID: checks session variable first, falls back to connection user
-- Application can SET LOCAL app.current_user_id = 123 to specify user
CREATE OR REPLACE FUNCTION get_current_user_id()
RETURNS INTEGER AS $$
DECLARE
    v_user_id INTEGER;
BEGIN
    -- Try session variable first (set by application)
    BEGIN
        v_user_id := NULLIF(current_setting('app.current_user_id', true), '')::INTEGER;
    EXCEPTION WHEN OTHERS THEN
        v_user_id := NULL;
    END;

    -- Fall back to connection-based user
    IF v_user_id IS NULL THEN
        v_user_id := get_or_create_connection_user();
    END IF;

    RETURN v_user_id;
END;
$$ LANGUAGE plpgsql;


-- Unified trigger function for audit fields (created_at/by, updated_at/by)
-- Works for tables with or without _by columns
CREATE OR REPLACE FUNCTION trigger_set_audit()
RETURNS TRIGGER AS $$
DECLARE
    v_new_json JSONB;
BEGIN
    v_new_json := to_jsonb(NEW);

    IF TG_OP = 'INSERT' THEN
        NEW.created_at = COALESCE(NEW.created_at, now());
        IF v_new_json ? 'created_by' THEN
            NEW.created_by = COALESCE(NEW.created_by, get_current_user_id());
        END IF;
    ELSIF TG_OP = 'UPDATE' THEN
        NEW.updated_at = now();
        IF v_new_json ? 'updated_by' THEN
            NEW.updated_by = COALESCE(NEW.updated_by, get_current_user_id());
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Archive vendor price on change
CREATE OR REPLACE FUNCTION trigger_archive_vendor_price()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.wholesale_price IS DISTINCT FROM NEW.wholesale_price
       OR OLD.retail_price IS DISTINCT FROM NEW.retail_price
       OR OLD.unit_price IS DISTINCT FROM NEW.unit_price THEN
        INSERT INTO public.vendor_price_history (
            vendor_products_id
            , wholesale_price
            , retail_price
            , unit_price
            , price_unit
            , effective_at
            , recorded_at
        ) VALUES (
            OLD.vendor_products_id
            , OLD.wholesale_price
            , OLD.retail_price
            , OLD.unit_price
            , OLD.price_unit
            , OLD.updated_at
            , now()
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Archive our SKU price on change
CREATE OR REPLACE FUNCTION trigger_archive_our_price()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.wholesale_price IS DISTINCT FROM NEW.wholesale_price
       OR OLD.member_price IS DISTINCT FROM NEW.member_price
       OR OLD.nonmember_price IS DISTINCT FROM NEW.nonmember_price
       OR OLD.processing_cost IS DISTINCT FROM NEW.processing_cost THEN
        INSERT INTO public.our_price_history (
            our_skus_id
            , wholesale_price
            , member_price
            , nonmember_price
            , processing_cost
            , effective_at
            , recorded_at
        ) VALUES (
            OLD.our_skus_id
            , OLD.wholesale_price
            , OLD.member_price
            , OLD.nonmember_price
            , OLD.processing_cost
            , OLD.updated_at
            , now()
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- ENUMS
-- ============================================================================

DO $$ BEGIN
    CREATE TYPE contact_type AS ENUM ('individual', 'entity');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE member_standing AS ENUM ('good', 'dues_owed', 'suspended', 'inactive');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

-- ============================================================================
-- CONTACTS (Unified contact management)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.contacts (
    contacts_id SERIAL PRIMARY KEY
    , contact_type contact_type NOT NULL DEFAULT 'individual'
    , name TEXT NOT NULL
    , display_name TEXT
    , email TEXT
    , phone TEXT
    , address_line1 TEXT
    , address_line2 TEXT
    , city TEXT
    , state TEXT
    , postal_code TEXT
    , country TEXT DEFAULT 'US'
    , metadata JSONB
    , is_active BOOLEAN NOT NULL DEFAULT TRUE
    , created_at TIMESTAMPTZ DEFAULT now()
    , created_by INTEGER
    , updated_at TIMESTAMPTZ
    , updated_by INTEGER
);

CREATE INDEX IF NOT EXISTS idx_contacts_email ON public.contacts(email);
CREATE INDEX IF NOT EXISTS idx_contacts_name ON public.contacts(name);
CREATE INDEX IF NOT EXISTS idx_contacts_active ON public.contacts(is_active) WHERE is_active = TRUE;

DROP TRIGGER IF EXISTS set_timestamp_contacts ON public.contacts;
DROP TRIGGER IF EXISTS set_created_contacts ON public.contacts;
DROP TRIGGER IF EXISTS set_updated_contacts ON public.contacts;
DROP TRIGGER IF EXISTS set_audit_contacts ON public.contacts;
CREATE TRIGGER set_audit_contacts
BEFORE INSERT OR UPDATE ON public.contacts
FOR EACH ROW EXECUTE PROCEDURE trigger_set_audit();

-- ============================================================================
-- USERS (System users, extends contacts)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.users (
    users_id SERIAL PRIMARY KEY
    , contacts_id INTEGER REFERENCES public.contacts(contacts_id) ON DELETE RESTRICT
    , email TEXT UNIQUE NOT NULL
    , password_hash TEXT
    , is_system_user BOOLEAN NOT NULL DEFAULT FALSE
    , is_active BOOLEAN NOT NULL DEFAULT TRUE
    , last_login_at TIMESTAMPTZ
    , email_verified_at TIMESTAMPTZ
    , created_at TIMESTAMPTZ DEFAULT now()
    , updated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_users_contacts ON public.users(contacts_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);

DROP TRIGGER IF EXISTS set_timestamp_users ON public.users;
DROP TRIGGER IF EXISTS set_created_users ON public.users;
DROP TRIGGER IF EXISTS set_updated_users ON public.users;
DROP TRIGGER IF EXISTS set_audit_users ON public.users;
CREATE TRIGGER set_audit_users
BEFORE INSERT OR UPDATE ON public.users
FOR EACH ROW EXECUTE PROCEDURE trigger_set_audit();

-- ============================================================================
-- VENDORS (Suppliers we buy from)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.vendors (
    vendors_id SERIAL PRIMARY KEY
    , contacts_id INTEGER REFERENCES public.contacts(contacts_id) ON DELETE SET NULL
    , name TEXT NOT NULL
    , slug TEXT UNIQUE NOT NULL
    , description JSONB
    , minimum_order_amount DECIMAL(10,2)
    , minimum_order_notes TEXT
    , ordering_process JSONB
    , lead_time_days INTEGER
    , is_active BOOLEAN NOT NULL DEFAULT TRUE
    , metadata JSONB
    , created_at TIMESTAMPTZ DEFAULT now()
    , created_by INTEGER
    , updated_at TIMESTAMPTZ
    , updated_by INTEGER
);

CREATE INDEX IF NOT EXISTS idx_vendors_slug ON public.vendors(slug);
CREATE INDEX IF NOT EXISTS idx_vendors_active ON public.vendors(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_vendors_contacts ON public.vendors(contacts_id);

DROP TRIGGER IF EXISTS set_timestamp_vendors ON public.vendors;
DROP TRIGGER IF EXISTS set_created_vendors ON public.vendors;
DROP TRIGGER IF EXISTS set_updated_vendors ON public.vendors;
DROP TRIGGER IF EXISTS set_audit_vendors ON public.vendors;
CREATE TRIGGER set_audit_vendors
BEFORE INSERT OR UPDATE ON public.vendors
FOR EACH ROW EXECUTE PROCEDURE trigger_set_audit();

-- ============================================================================
-- MEMBERS (Buyers club members)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.members (
    members_id SERIAL PRIMARY KEY
    , contacts_id INTEGER NOT NULL REFERENCES public.contacts(contacts_id) ON DELETE RESTRICT
    , users_id INTEGER REFERENCES public.users(users_id) ON DELETE SET NULL
    , member_number TEXT UNIQUE
    , standing member_standing NOT NULL DEFAULT 'good'
    , dues_paid_through DATE
    , member_dollars DECIMAL(10,2) NOT NULL DEFAULT 0
    , notes TEXT
    , joined_at DATE NOT NULL DEFAULT CURRENT_DATE
    , is_active BOOLEAN NOT NULL DEFAULT TRUE
    , metadata JSONB
    , created_at TIMESTAMPTZ DEFAULT now()
    , created_by INTEGER
    , updated_at TIMESTAMPTZ
    , updated_by INTEGER
);

CREATE INDEX IF NOT EXISTS idx_members_contacts ON public.members(contacts_id);
CREATE INDEX IF NOT EXISTS idx_members_users ON public.members(users_id);
CREATE INDEX IF NOT EXISTS idx_members_standing ON public.members(standing);
CREATE INDEX IF NOT EXISTS idx_members_active ON public.members(is_active) WHERE is_active = TRUE;

DROP TRIGGER IF EXISTS set_timestamp_members ON public.members;
DROP TRIGGER IF EXISTS set_created_members ON public.members;
DROP TRIGGER IF EXISTS set_updated_members ON public.members;
DROP TRIGGER IF EXISTS set_audit_members ON public.members;
CREATE TRIGGER set_audit_members
BEFORE INSERT OR UPDATE ON public.members
FOR EACH ROW EXECUTE PROCEDURE trigger_set_audit();

-- ============================================================================
-- PRODUCTS (Canonical product list)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.products (
    products_id SERIAL PRIMARY KEY
    , name TEXT NOT NULL
    , slug TEXT UNIQUE
    , short_description TEXT
    , description JSONB
    , brand TEXT
    , category TEXT
    , subcategory TEXT
    , is_active BOOLEAN NOT NULL DEFAULT TRUE
    , metadata JSONB
    , created_at TIMESTAMPTZ DEFAULT now()
    , created_by INTEGER
    , updated_at TIMESTAMPTZ
    , updated_by INTEGER
);

CREATE INDEX IF NOT EXISTS idx_products_slug ON public.products(slug);
CREATE INDEX IF NOT EXISTS idx_products_name ON public.products(name);
CREATE INDEX IF NOT EXISTS idx_products_category ON public.products(category);
CREATE INDEX IF NOT EXISTS idx_products_brand ON public.products(brand);
CREATE INDEX IF NOT EXISTS idx_products_active ON public.products(is_active) WHERE is_active = TRUE;

DROP TRIGGER IF EXISTS set_timestamp_products ON public.products;
DROP TRIGGER IF EXISTS set_created_products ON public.products;
DROP TRIGGER IF EXISTS set_updated_products ON public.products;
DROP TRIGGER IF EXISTS set_audit_products ON public.products;
CREATE TRIGGER set_audit_products
BEFORE INSERT OR UPDATE ON public.products
FOR EACH ROW EXECUTE PROCEDURE trigger_set_audit();

-- ============================================================================
-- VENDOR_PRODUCTS (What vendors offer)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.vendor_products (
    vendor_products_id SERIAL PRIMARY KEY
    , vendors_id INTEGER NOT NULL REFERENCES public.vendors(vendors_id) ON DELETE CASCADE
    , products_id INTEGER REFERENCES public.products(products_id) ON DELETE SET NULL
    , vendor_sku TEXT NOT NULL
    , vendor_name TEXT NOT NULL
    , size TEXT
    , weight JSONB
    , wholesale_price DECIMAL(10,2)
    , retail_price DECIMAL(10,2)
    , unit_price DECIMAL(10,4)
    , price_unit TEXT
    , stock_status TEXT
    , vendor_data JSONB
    , is_active BOOLEAN NOT NULL DEFAULT TRUE
    , last_synced_at TIMESTAMPTZ
    , created_at TIMESTAMPTZ DEFAULT now()
    , created_by INTEGER
    , updated_at TIMESTAMPTZ
    , updated_by INTEGER
    , UNIQUE(vendors_id, vendor_sku)
);

CREATE INDEX IF NOT EXISTS idx_vendor_products_vendor ON public.vendor_products(vendors_id);
CREATE INDEX IF NOT EXISTS idx_vendor_products_product ON public.vendor_products(products_id);
CREATE INDEX IF NOT EXISTS idx_vendor_products_sku ON public.vendor_products(vendor_sku);
CREATE INDEX IF NOT EXISTS idx_vendor_products_active ON public.vendor_products(is_active) WHERE is_active = TRUE;

DROP TRIGGER IF EXISTS set_timestamp_vendor_products ON public.vendor_products;
DROP TRIGGER IF EXISTS set_created_vendor_products ON public.vendor_products;
DROP TRIGGER IF EXISTS set_updated_vendor_products ON public.vendor_products;
DROP TRIGGER IF EXISTS set_audit_vendor_products ON public.vendor_products;
CREATE TRIGGER set_audit_vendor_products
BEFORE INSERT OR UPDATE ON public.vendor_products
FOR EACH ROW EXECUTE PROCEDURE trigger_set_audit();

-- ============================================================================
-- VENDOR_PRICE_HISTORY (Historical vendor prices)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.vendor_price_history (
    vendor_price_history_id SERIAL PRIMARY KEY
    , vendor_products_id INTEGER NOT NULL REFERENCES public.vendor_products(vendor_products_id) ON DELETE CASCADE
    , wholesale_price DECIMAL(10,2)
    , retail_price DECIMAL(10,2)
    , unit_price DECIMAL(10,4)
    , price_unit TEXT
    , effective_at TIMESTAMPTZ NOT NULL
    , recorded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_vendor_price_history_product ON public.vendor_price_history(vendor_products_id);
CREATE INDEX IF NOT EXISTS idx_vendor_price_history_effective ON public.vendor_price_history(effective_at);

-- Add price archive trigger after history table exists
DROP TRIGGER IF EXISTS archive_vendor_price_on_update ON public.vendor_products;
CREATE TRIGGER archive_vendor_price_on_update
BEFORE UPDATE ON public.vendor_products
FOR EACH ROW EXECUTE PROCEDURE trigger_archive_vendor_price();

-- ============================================================================
-- OUR_SKUS (What we sell)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.our_skus (
    our_skus_id SERIAL PRIMARY KEY
    , products_id INTEGER NOT NULL REFERENCES public.products(products_id) ON DELETE RESTRICT
    , sku TEXT UNIQUE NOT NULL
    , name TEXT NOT NULL
    , size TEXT
    , weight JSONB
    , wholesale_price DECIMAL(10,2)
    , member_price DECIMAL(10,2)
    , nonmember_price DECIMAL(10,2)
    , processing_cost DECIMAL(10,2) DEFAULT 0
    , is_listed BOOLEAN NOT NULL DEFAULT TRUE
    , is_active BOOLEAN NOT NULL DEFAULT TRUE
    , sort_order INTEGER DEFAULT 0
    , metadata JSONB
    , created_at TIMESTAMPTZ DEFAULT now()
    , created_by INTEGER
    , updated_at TIMESTAMPTZ
    , updated_by INTEGER
);

CREATE INDEX IF NOT EXISTS idx_our_skus_product ON public.our_skus(products_id);
CREATE INDEX IF NOT EXISTS idx_our_skus_sku ON public.our_skus(sku);
CREATE INDEX IF NOT EXISTS idx_our_skus_listed ON public.our_skus(is_listed) WHERE is_listed = TRUE;
CREATE INDEX IF NOT EXISTS idx_our_skus_active ON public.our_skus(is_active) WHERE is_active = TRUE;

DROP TRIGGER IF EXISTS set_timestamp_our_skus ON public.our_skus;
DROP TRIGGER IF EXISTS set_created_our_skus ON public.our_skus;
DROP TRIGGER IF EXISTS set_updated_our_skus ON public.our_skus;
DROP TRIGGER IF EXISTS set_audit_our_skus ON public.our_skus;
CREATE TRIGGER set_audit_our_skus
BEFORE INSERT OR UPDATE ON public.our_skus
FOR EACH ROW EXECUTE PROCEDURE trigger_set_audit();

-- ============================================================================
-- OUR_PRICE_HISTORY (Historical selling prices)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.our_price_history (
    our_price_history_id SERIAL PRIMARY KEY
    , our_skus_id INTEGER NOT NULL REFERENCES public.our_skus(our_skus_id) ON DELETE CASCADE
    , wholesale_price DECIMAL(10,2)
    , member_price DECIMAL(10,2)
    , nonmember_price DECIMAL(10,2)
    , processing_cost DECIMAL(10,2)
    , effective_at TIMESTAMPTZ NOT NULL
    , recorded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_our_price_history_sku ON public.our_price_history(our_skus_id);
CREATE INDEX IF NOT EXISTS idx_our_price_history_effective ON public.our_price_history(effective_at);

-- Add price archive trigger after history table exists
DROP TRIGGER IF EXISTS archive_our_price_on_update ON public.our_skus;
CREATE TRIGGER archive_our_price_on_update
BEFORE UPDATE ON public.our_skus
FOR EACH ROW EXECUTE PROCEDURE trigger_archive_our_price();

-- ============================================================================
-- SKU_SOURCING (Links our SKUs to vendor products)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.sku_sourcing (
    sku_sourcing_id SERIAL PRIMARY KEY
    , our_skus_id INTEGER NOT NULL REFERENCES public.our_skus(our_skus_id) ON DELETE CASCADE
    , vendor_products_id INTEGER NOT NULL REFERENCES public.vendor_products(vendor_products_id) ON DELETE CASCADE
    , is_preferred BOOLEAN NOT NULL DEFAULT FALSE
    , conversion_factor DECIMAL(10,4) DEFAULT 1
    , notes TEXT
    , created_at TIMESTAMPTZ DEFAULT now()
    , created_by INTEGER
    , updated_at TIMESTAMPTZ
    , updated_by INTEGER
    , UNIQUE(our_skus_id, vendor_products_id)
);

CREATE INDEX IF NOT EXISTS idx_sku_sourcing_our_sku ON public.sku_sourcing(our_skus_id);
CREATE INDEX IF NOT EXISTS idx_sku_sourcing_vendor_product ON public.sku_sourcing(vendor_products_id);
CREATE INDEX IF NOT EXISTS idx_sku_sourcing_preferred ON public.sku_sourcing(is_preferred) WHERE is_preferred = TRUE;

DROP TRIGGER IF EXISTS set_created_sku_sourcing ON public.sku_sourcing;
DROP TRIGGER IF EXISTS set_updated_sku_sourcing ON public.sku_sourcing;
DROP TRIGGER IF EXISTS set_audit_sku_sourcing ON public.sku_sourcing;
CREATE TRIGGER set_audit_sku_sourcing
BEFORE INSERT OR UPDATE ON public.sku_sourcing
FOR EACH ROW EXECUTE PROCEDURE trigger_set_audit();

-- ============================================================================
-- LOCATIONS (Where we store inventory)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.locations (
    locations_id SERIAL PRIMARY KEY
    , name TEXT NOT NULL
    , slug TEXT UNIQUE NOT NULL
    , description JSONB
    , is_active BOOLEAN NOT NULL DEFAULT TRUE
    , created_at TIMESTAMPTZ DEFAULT now()
    , created_by INTEGER
    , updated_at TIMESTAMPTZ
    , updated_by INTEGER
);

DROP TRIGGER IF EXISTS set_timestamp_locations ON public.locations;
DROP TRIGGER IF EXISTS set_created_locations ON public.locations;
DROP TRIGGER IF EXISTS set_updated_locations ON public.locations;
DROP TRIGGER IF EXISTS set_audit_locations ON public.locations;
CREATE TRIGGER set_audit_locations
BEFORE INSERT OR UPDATE ON public.locations
FOR EACH ROW EXECUTE PROCEDURE trigger_set_audit();

-- ============================================================================
-- INVENTORY (What we have on hand)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.inventory (
    inventory_id SERIAL PRIMARY KEY
    , our_skus_id INTEGER NOT NULL REFERENCES public.our_skus(our_skus_id) ON DELETE CASCADE
    , locations_id INTEGER NOT NULL REFERENCES public.locations(locations_id) ON DELETE CASCADE
    , quantity_on_hand DECIMAL(10,2) NOT NULL DEFAULT 0
    , quantity_reserved DECIMAL(10,2) NOT NULL DEFAULT 0
    , reorder_point DECIMAL(10,2)
    , notes TEXT
    , created_at TIMESTAMPTZ DEFAULT now()
    , created_by INTEGER
    , updated_at TIMESTAMPTZ
    , updated_by INTEGER
    , UNIQUE(our_skus_id, locations_id)
);

CREATE INDEX IF NOT EXISTS idx_inventory_sku ON public.inventory(our_skus_id);
CREATE INDEX IF NOT EXISTS idx_inventory_location ON public.inventory(locations_id);

DROP TRIGGER IF EXISTS set_timestamp_inventory ON public.inventory;
DROP TRIGGER IF EXISTS set_created_inventory ON public.inventory;
DROP TRIGGER IF EXISTS set_updated_inventory ON public.inventory;
DROP TRIGGER IF EXISTS set_audit_inventory ON public.inventory;
CREATE TRIGGER set_audit_inventory
BEFORE INSERT OR UPDATE ON public.inventory
FOR EACH ROW EXECUTE PROCEDURE trigger_set_audit();

-- ============================================================================
-- VENDOR_ORDERS (Our purchases from vendors)
-- ============================================================================

DO $$ BEGIN
    CREATE TYPE order_status AS ENUM ('draft', 'submitted', 'confirmed', 'shipped', 'received', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS public.vendor_orders (
    vendor_orders_id SERIAL PRIMARY KEY
    , vendors_id INTEGER NOT NULL REFERENCES public.vendors(vendors_id) ON DELETE RESTRICT
    , order_number TEXT UNIQUE
    , status order_status NOT NULL DEFAULT 'draft'
    , order_date DATE
    , expected_delivery_date DATE
    , actual_delivery_date DATE
    , subtotal DECIMAL(10,2)
    , shipping_cost DECIMAL(10,2) DEFAULT 0
    , tax DECIMAL(10,2) DEFAULT 0
    , total DECIMAL(10,2)
    , notes TEXT
    , metadata JSONB
    , created_at TIMESTAMPTZ DEFAULT now()
    , created_by INTEGER
    , updated_at TIMESTAMPTZ
    , updated_by INTEGER
);

CREATE INDEX IF NOT EXISTS idx_vendor_orders_vendor ON public.vendor_orders(vendors_id);
CREATE INDEX IF NOT EXISTS idx_vendor_orders_status ON public.vendor_orders(status);
CREATE INDEX IF NOT EXISTS idx_vendor_orders_date ON public.vendor_orders(order_date);

DROP TRIGGER IF EXISTS set_timestamp_vendor_orders ON public.vendor_orders;
DROP TRIGGER IF EXISTS set_created_vendor_orders ON public.vendor_orders;
DROP TRIGGER IF EXISTS set_updated_vendor_orders ON public.vendor_orders;
DROP TRIGGER IF EXISTS set_audit_vendor_orders ON public.vendor_orders;
CREATE TRIGGER set_audit_vendor_orders
BEFORE INSERT OR UPDATE ON public.vendor_orders
FOR EACH ROW EXECUTE PROCEDURE trigger_set_audit();

-- ============================================================================
-- VENDOR_ORDER_LINES (Line items on vendor orders)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.vendor_order_lines (
    vendor_order_lines_id SERIAL PRIMARY KEY
    , vendor_orders_id INTEGER NOT NULL REFERENCES public.vendor_orders(vendor_orders_id) ON DELETE CASCADE
    , vendor_products_id INTEGER NOT NULL REFERENCES public.vendor_products(vendor_products_id) ON DELETE RESTRICT
    , quantity DECIMAL(10,2) NOT NULL
    , unit_price DECIMAL(10,2) NOT NULL
    , line_total DECIMAL(10,2) GENERATED ALWAYS AS (quantity * unit_price) STORED
    , quantity_received DECIMAL(10,2)
    , notes TEXT
    , created_at TIMESTAMPTZ DEFAULT now()
    , created_by INTEGER
    , updated_at TIMESTAMPTZ
    , updated_by INTEGER
);

CREATE INDEX IF NOT EXISTS idx_vendor_order_lines_order ON public.vendor_order_lines(vendor_orders_id);
CREATE INDEX IF NOT EXISTS idx_vendor_order_lines_product ON public.vendor_order_lines(vendor_products_id);

DROP TRIGGER IF EXISTS set_timestamp_vendor_order_lines ON public.vendor_order_lines;
DROP TRIGGER IF EXISTS set_created_vendor_order_lines ON public.vendor_order_lines;
DROP TRIGGER IF EXISTS set_updated_vendor_order_lines ON public.vendor_order_lines;
DROP TRIGGER IF EXISTS set_audit_vendor_order_lines ON public.vendor_order_lines;
CREATE TRIGGER set_audit_vendor_order_lines
BEFORE INSERT OR UPDATE ON public.vendor_order_lines
FOR EACH ROW EXECUTE PROCEDURE trigger_set_audit();

-- ============================================================================
-- MEMBER_ORDERS (Member purchases from us)
-- ============================================================================

DO $$ BEGIN
    CREATE TYPE member_order_status AS ENUM ('cart', 'pending', 'confirmed', 'ready', 'picked_up', 'delivered', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE fulfillment_type AS ENUM ('pickup', 'delivery');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS public.member_orders (
    member_orders_id SERIAL PRIMARY KEY
    , members_id INTEGER NOT NULL REFERENCES public.members(members_id) ON DELETE RESTRICT
    , order_number TEXT UNIQUE
    , status member_order_status NOT NULL DEFAULT 'cart'
    , fulfillment_type fulfillment_type
    , order_date TIMESTAMPTZ
    , ready_date TIMESTAMPTZ
    , completed_date TIMESTAMPTZ
    , subtotal DECIMAL(10,2)
    , member_dollars_applied DECIMAL(10,2) DEFAULT 0
    , tax DECIMAL(10,2) DEFAULT 0
    , total DECIMAL(10,2)
    , amount_paid DECIMAL(10,2) DEFAULT 0
    , notes TEXT
    , metadata JSONB
    , created_at TIMESTAMPTZ DEFAULT now()
    , created_by INTEGER
    , updated_at TIMESTAMPTZ
    , updated_by INTEGER
);

CREATE INDEX IF NOT EXISTS idx_member_orders_member ON public.member_orders(members_id);
CREATE INDEX IF NOT EXISTS idx_member_orders_status ON public.member_orders(status);
CREATE INDEX IF NOT EXISTS idx_member_orders_date ON public.member_orders(order_date);

DROP TRIGGER IF EXISTS set_timestamp_member_orders ON public.member_orders;
DROP TRIGGER IF EXISTS set_created_member_orders ON public.member_orders;
DROP TRIGGER IF EXISTS set_updated_member_orders ON public.member_orders;
DROP TRIGGER IF EXISTS set_audit_member_orders ON public.member_orders;
CREATE TRIGGER set_audit_member_orders
BEFORE INSERT OR UPDATE ON public.member_orders
FOR EACH ROW EXECUTE PROCEDURE trigger_set_audit();

-- ============================================================================
-- MEMBER_ORDER_LINES (Line items on member orders)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.member_order_lines (
    member_order_lines_id SERIAL PRIMARY KEY
    , member_orders_id INTEGER NOT NULL REFERENCES public.member_orders(member_orders_id) ON DELETE CASCADE
    , our_skus_id INTEGER NOT NULL REFERENCES public.our_skus(our_skus_id) ON DELETE RESTRICT
    , quantity DECIMAL(10,2) NOT NULL
    , unit_price DECIMAL(10,2) NOT NULL
    , line_total DECIMAL(10,2) GENERATED ALWAYS AS (quantity * unit_price) STORED
    , price_tier TEXT
    , notes TEXT
    , created_at TIMESTAMPTZ DEFAULT now()
    , created_by INTEGER
    , updated_at TIMESTAMPTZ
    , updated_by INTEGER
);

CREATE INDEX IF NOT EXISTS idx_member_order_lines_order ON public.member_order_lines(member_orders_id);
CREATE INDEX IF NOT EXISTS idx_member_order_lines_sku ON public.member_order_lines(our_skus_id);

DROP TRIGGER IF EXISTS set_timestamp_member_order_lines ON public.member_order_lines;
DROP TRIGGER IF EXISTS set_created_member_order_lines ON public.member_order_lines;
DROP TRIGGER IF EXISTS set_updated_member_order_lines ON public.member_order_lines;
DROP TRIGGER IF EXISTS set_audit_member_order_lines ON public.member_order_lines;
CREATE TRIGGER set_audit_member_order_lines
BEFORE INSERT OR UPDATE ON public.member_order_lines
FOR EACH ROW EXECUTE PROCEDURE trigger_set_audit();

-- ============================================================================
-- PAYMENTS (Tracks payments on member orders)
-- ============================================================================

DO $$ BEGIN
    CREATE TYPE payment_method AS ENUM ('cash', 'check', 'card', 'eft', 'venmo', 'member_dollars', 'other');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE payment_status AS ENUM ('pending', 'completed', 'failed', 'refunded');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS public.payments (
    payments_id SERIAL PRIMARY KEY
    , member_orders_id INTEGER REFERENCES public.member_orders(member_orders_id) ON DELETE RESTRICT
    , members_id INTEGER NOT NULL REFERENCES public.members(members_id) ON DELETE RESTRICT
    , amount DECIMAL(10,2) NOT NULL
    , payment_method payment_method NOT NULL
    , status payment_status NOT NULL DEFAULT 'pending'
    , reference_number TEXT
    , notes TEXT
    , metadata JSONB
    , payment_date TIMESTAMPTZ DEFAULT now()
    , created_at TIMESTAMPTZ DEFAULT now()
    , created_by INTEGER
    , updated_at TIMESTAMPTZ
    , updated_by INTEGER
);

CREATE INDEX IF NOT EXISTS idx_payments_order ON public.payments(member_orders_id);
CREATE INDEX IF NOT EXISTS idx_payments_member ON public.payments(members_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON public.payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_date ON public.payments(payment_date);

DROP TRIGGER IF EXISTS set_timestamp_payments ON public.payments;
DROP TRIGGER IF EXISTS set_created_payments ON public.payments;
DROP TRIGGER IF EXISTS set_updated_payments ON public.payments;
DROP TRIGGER IF EXISTS set_audit_payments ON public.payments;
CREATE TRIGGER set_audit_payments
BEFORE INSERT OR UPDATE ON public.payments
FOR EACH ROW EXECUTE PROCEDURE trigger_set_audit();

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Product listing view with availability
CREATE OR REPLACE VIEW public.v_store_products AS
SELECT
    os.our_skus_id
    , os.sku
    , os.name AS sku_name
    , p.products_id
    , p.name AS product_name
    , p.brand
    , p.category
    , p.subcategory
    , p.short_description
    , p.description AS product_description
    , os.size
    , os.weight
    , os.wholesale_price
    , os.member_price
    , os.nonmember_price
    , os.processing_cost
    , os.is_listed
    , COALESCE(SUM(i.quantity_on_hand - i.quantity_reserved), 0) AS available_quantity
    , CASE
        WHEN COALESCE(SUM(i.quantity_on_hand - i.quantity_reserved), 0) > 0 THEN 'in_stock'
        WHEN os.is_listed THEN 'available_to_order'
        ELSE 'out_of_stock'
      END AS availability_status
    , os.metadata
FROM public.our_skus os
JOIN public.products p ON os.products_id = p.products_id
LEFT JOIN public.inventory i ON os.our_skus_id = i.our_skus_id
WHERE os.is_active = TRUE
  AND p.is_active = TRUE
GROUP BY
    os.our_skus_id
    , os.sku
    , os.name
    , p.products_id
    , p.name
    , p.brand
    , p.category
    , p.subcategory
    , p.short_description
    , p.description
    , os.size
    , os.weight
    , os.wholesale_price
    , os.member_price
    , os.nonmember_price
    , os.processing_cost
    , os.is_listed
    , os.metadata
ORDER BY p.category, p.name, os.sort_order;

-- Price comparison view
CREATE OR REPLACE VIEW public.v_price_comparison AS
SELECT
    os.our_skus_id
    , os.sku AS our_sku
    , os.name AS our_name
    , os.wholesale_price AS our_wholesale
    , os.member_price AS our_member_price
    , os.nonmember_price AS our_nonmember_price
    , v.vendors_id
    , v.name AS vendor_name
    , vp.vendor_sku
    , vp.vendor_name AS vendor_product_name
    , vp.wholesale_price AS vendor_wholesale
    , vp.retail_price AS vendor_retail
    , ss.is_preferred AS is_preferred_source
    , ss.conversion_factor
    , CASE
        WHEN os.wholesale_price > 0 AND vp.wholesale_price > 0
        THEN ROUND(((os.wholesale_price - vp.wholesale_price * COALESCE(ss.conversion_factor, 1))
                    / (vp.wholesale_price * COALESCE(ss.conversion_factor, 1))) * 100, 2)
        ELSE NULL
      END AS margin_percent
FROM public.our_skus os
JOIN public.sku_sourcing ss ON os.our_skus_id = ss.our_skus_id
JOIN public.vendor_products vp ON ss.vendor_products_id = vp.vendor_products_id
JOIN public.vendors v ON vp.vendors_id = v.vendors_id
WHERE os.is_active = TRUE
  AND vp.is_active = TRUE
ORDER BY os.sku, ss.is_preferred DESC, v.name;

-- Vendor product catalog view
CREATE OR REPLACE VIEW public.v_vendor_catalog AS
SELECT
    v.vendors_id
    , v.name AS vendor_name
    , v.slug AS vendor_slug
    , vp.vendor_products_id
    , vp.vendor_sku
    , vp.vendor_name AS product_name
    , vp.size
    , vp.wholesale_price
    , vp.retail_price
    , vp.unit_price
    , vp.price_unit
    , vp.stock_status
    , p.products_id AS linked_product_id
    , p.name AS linked_product_name
    , CASE WHEN ss.sku_sourcing_id IS NOT NULL THEN TRUE ELSE FALSE END AS is_sourced
    , vp.last_synced_at
FROM public.vendor_products vp
JOIN public.vendors v ON vp.vendors_id = v.vendors_id
LEFT JOIN public.products p ON vp.products_id = p.products_id
LEFT JOIN public.sku_sourcing ss ON vp.vendor_products_id = ss.vendor_products_id
WHERE vp.is_active = TRUE
  AND v.is_active = TRUE
ORDER BY v.name, vp.vendor_name;

-- Inventory summary view
CREATE OR REPLACE VIEW public.v_inventory_summary AS
SELECT
    l.locations_id
    , l.name AS location_name
    , os.our_skus_id
    , os.sku
    , os.name AS sku_name
    , p.name AS product_name
    , i.quantity_on_hand
    , i.quantity_reserved
    , (i.quantity_on_hand - i.quantity_reserved) AS available
    , i.reorder_point
    , CASE
        WHEN i.reorder_point IS NOT NULL
             AND (i.quantity_on_hand - i.quantity_reserved) <= i.reorder_point
        THEN TRUE
        ELSE FALSE
      END AS needs_reorder
    , i.updated_at AS last_updated
FROM public.inventory i
JOIN public.our_skus os ON i.our_skus_id = os.our_skus_id
JOIN public.products p ON os.products_id = p.products_id
JOIN public.locations l ON i.locations_id = l.locations_id
WHERE os.is_active = TRUE
ORDER BY l.name, p.name, os.sku;

-- Members view with contact info
CREATE OR REPLACE VIEW public.v_members AS
SELECT
    m.members_id
    , m.member_number
    , c.name AS member_name
    , c.email
    , c.phone
    , format('%s, %s %s', c.city, c.state, c.postal_code) AS location
    , m.standing
    , m.dues_paid_through
    , m.member_dollars
    , m.joined_at
    , m.is_active
FROM public.members m
JOIN public.contacts c ON m.contacts_id = c.contacts_id
ORDER BY c.name;

-- Vendor orders with totals
CREATE OR REPLACE VIEW public.v_vendor_orders AS
SELECT
    vo.vendor_orders_id
    , vo.order_number
    , v.vendors_id
    , v.name AS vendor_name
    , vo.status
    , vo.order_date
    , vo.expected_delivery_date
    , vo.actual_delivery_date
    , COUNT(vol.vendor_order_lines_id) AS line_count
    , COALESCE(SUM(vol.line_total), 0) AS calculated_subtotal
    , vo.shipping_cost
    , vo.tax
    , vo.total
    , v.minimum_order_amount
    , CASE
        WHEN COALESCE(SUM(vol.line_total), 0) >= COALESCE(v.minimum_order_amount, 0)
        THEN TRUE
        ELSE FALSE
      END AS meets_minimum
    , vo.created_at
FROM public.vendor_orders vo
JOIN public.vendors v ON vo.vendors_id = v.vendors_id
LEFT JOIN public.vendor_order_lines vol ON vo.vendor_orders_id = vol.vendor_orders_id
GROUP BY
    vo.vendor_orders_id
    , vo.order_number
    , v.vendors_id
    , v.name
    , vo.status
    , vo.order_date
    , vo.expected_delivery_date
    , vo.actual_delivery_date
    , vo.shipping_cost
    , vo.tax
    , vo.total
    , v.minimum_order_amount
    , vo.created_at
ORDER BY vo.order_date DESC NULLS LAST, vo.created_at DESC;

-- Member orders with payment status
CREATE OR REPLACE VIEW public.v_member_orders AS
SELECT
    mo.member_orders_id
    , mo.order_number
    , m.members_id
    , m.member_number
    , c.name AS member_name
    , mo.status
    , mo.fulfillment_type
    , mo.order_date
    , mo.ready_date
    , mo.completed_date
    , COUNT(mol.member_order_lines_id) AS line_count
    , COALESCE(SUM(mol.line_total), 0) AS calculated_subtotal
    , mo.member_dollars_applied
    , mo.tax
    , mo.total
    , mo.amount_paid
    , (COALESCE(mo.total, 0) - COALESCE(mo.amount_paid, 0)) AS balance_due
    , mo.created_at
FROM public.member_orders mo
JOIN public.members m ON mo.members_id = m.members_id
JOIN public.contacts c ON m.contacts_id = c.contacts_id
LEFT JOIN public.member_order_lines mol ON mo.member_orders_id = mol.member_orders_id
GROUP BY
    mo.member_orders_id
    , mo.order_number
    , m.members_id
    , m.member_number
    , c.name
    , mo.status
    , mo.fulfillment_type
    , mo.order_date
    , mo.ready_date
    , mo.completed_date
    , mo.member_dollars_applied
    , mo.tax
    , mo.total
    , mo.amount_paid
    , mo.created_at
ORDER BY mo.order_date DESC NULLS LAST, mo.created_at DESC;

-- Order line details for member orders
CREATE OR REPLACE VIEW public.v_member_order_details AS
SELECT
    mo.member_orders_id
    , mo.order_number
    , c.name AS member_name
    , mol.member_order_lines_id
    , os.sku
    , os.name AS sku_name
    , p.name AS product_name
    , mol.quantity
    , mol.unit_price
    , mol.line_total
    , mol.price_tier
    , mo.status AS order_status
FROM public.member_orders mo
JOIN public.members m ON mo.members_id = m.members_id
JOIN public.contacts c ON m.contacts_id = c.contacts_id
JOIN public.member_order_lines mol ON mo.member_orders_id = mol.member_orders_id
JOIN public.our_skus os ON mol.our_skus_id = os.our_skus_id
JOIN public.products p ON os.products_id = p.products_id
ORDER BY mo.order_number, mol.member_order_lines_id;
