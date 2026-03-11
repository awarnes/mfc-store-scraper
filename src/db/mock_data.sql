-- ============================================================================
-- MOCK DATA FOR COOP DATABASE
-- Run after coop_schema.sql
-- ============================================================================

-- ============================================================================
-- CONTACTS
-- ============================================================================

INSERT INTO public.contacts (contact_type, name, display_name, email, phone, address_line1, city, state, postal_code)
VALUES
    -- Vendor contacts
    ('entity', 'Azure Standard', NULL, 'orders@azurestandard.com', '541-467-2230', '79709 Dufur Valley Rd', 'Dufur', 'OR', '97021')
    , ('entity', 'Hummingbird Wholesale', NULL, 'sales@hummingbirdwholesale.com', '541-687-0990', '150 Shelton McMurphey Blvd', 'Eugene', 'OR', '97401')
    , ('entity', 'Quiche Me', 'Quiche Me Bakery', 'orders@quicheme.local', '555-867-5309', '123 Baker St', 'Portland', 'OR', '97201')
    -- Member contacts
    , ('individual', 'Jane Smith', NULL, 'jane.smith@email.com', '555-111-2222', '456 Oak Ave', 'Portland', 'OR', '97202')
    , ('individual', 'Bob Johnson', NULL, 'bob.j@email.com', '555-333-4444', '789 Pine St', 'Portland', 'OR', '97203')
    , ('individual', 'Alice Chen', NULL, 'alice.chen@email.com', '555-555-6666', '321 Elm Blvd', 'Beaverton', 'OR', '97005')
;

-- ============================================================================
-- VENDORS
-- ============================================================================

INSERT INTO public.vendors (contacts_id, name, slug, description, minimum_order_amount, minimum_order_notes, ordering_process, lead_time_days)
VALUES
    (
        (SELECT contacts_id FROM public.contacts WHERE name = 'Azure Standard')
        , 'Azure Standard'
        , 'azure'
        , '{"about": "Organic and natural foods distributor", "certifications": ["USDA Organic", "Non-GMO"]}'::jsonb
        , 50.00
        , 'Orders under $50 incur $10 handling fee'
        , '{"method": "api", "frequency": "weekly", "cutoff": "Monday 5pm", "delivery": "Thursday"}'::jsonb
        , 3
    )
    , (
        (SELECT contacts_id FROM public.contacts WHERE name = 'Hummingbird Wholesale')
        , 'Hummingbird Wholesale'
        , 'hummingbird'
        , '{"about": "Natural foods distributor serving the Pacific Northwest", "certifications": ["B-Corp"]}'::jsonb
        , 200.00
        , 'Minimum $200 per order, $500 for free delivery'
        , '{"method": "email", "frequency": "monthly", "catalog": "PDF updated quarterly"}'::jsonb
        , 7
    )
    , (
        (SELECT contacts_id FROM public.contacts WHERE name = 'Quiche Me')
        , 'Quiche Me'
        , 'quiche-me'
        , '{"about": "Local artisan bakery specializing in savory pastries", "specialties": ["quiche", "sourdough", "pastries"]}'::jsonb
        , 100.00
        , 'Minimum $100 per order, 48 hours notice required'
        , '{"method": "phone", "frequency": "weekly", "delivery": "Wednesday and Saturday"}'::jsonb
        , 2
    )
;

-- ============================================================================
-- USERS (for member accounts)
-- ============================================================================

INSERT INTO public.users (contacts_id, email, is_active, email_verified_at)
VALUES
    ((SELECT contacts_id FROM public.contacts WHERE name = 'Jane Smith'), 'jane.smith@email.com', TRUE, now())
    , ((SELECT contacts_id FROM public.contacts WHERE name = 'Bob Johnson'), 'bob.j@email.com', TRUE, now())
    , ((SELECT contacts_id FROM public.contacts WHERE name = 'Alice Chen'), 'alice.chen@email.com', TRUE, NULL)
;

-- ============================================================================
-- MEMBERS
-- ============================================================================

INSERT INTO public.members (contacts_id, users_id, member_number, standing, dues_paid_through, member_dollars, joined_at)
VALUES
    (
        (SELECT contacts_id FROM public.contacts WHERE name = 'Jane Smith')
        , (SELECT users_id FROM public.users WHERE email = 'jane.smith@email.com')
        , 'M001'
        , 'good'
        , '2025-12-31'
        , 15.00
        , '2024-01-15'
    )
    , (
        (SELECT contacts_id FROM public.contacts WHERE name = 'Bob Johnson')
        , (SELECT users_id FROM public.users WHERE email = 'bob.j@email.com')
        , 'M002'
        , 'good'
        , '2025-06-30'
        , 0.00
        , '2024-06-01'
    )
    , (
        (SELECT contacts_id FROM public.contacts WHERE name = 'Alice Chen')
        , (SELECT users_id FROM public.users WHERE email = 'alice.chen@email.com')
        , 'M003'
        , 'dues_owed'
        , '2024-12-31'
        , 5.50
        , '2023-03-10'
    )
;

-- ============================================================================
-- PRODUCTS (Canonical catalog)
-- ============================================================================

INSERT INTO public.products (name, slug, short_description, description, brand, category, subcategory)
VALUES
    -- Grains
    ('Organic Rolled Oats', 'organic-rolled-oats', 'Whole grain rolled oats', '{"nutrition": {"servings_per_container": 30, "calories": 150}, "allergens": ["wheat_facility"]}'::jsonb, 'Azure Market', 'Grains', 'Oats')
    , ('Organic Quinoa', 'organic-quinoa', 'White quinoa, pre-rinsed', '{"nutrition": {"servings_per_container": 12, "calories": 170}, "origin": "Peru"}'::jsonb, 'Lundberg', 'Grains', 'Ancient Grains')
    , ('Organic All-Purpose Flour', 'organic-ap-flour', 'Unbleached all-purpose flour', '{"nutrition": {"servings_per_container": 38, "calories": 110}}'::jsonb, 'Azure Market', 'Grains', 'Flour')

    -- Baked Goods
    , ('Spinach Quiche', 'spinach-quiche', 'Fresh spinach and gruyere quiche', '{"ingredients": ["eggs", "cream", "spinach", "gruyere", "pie crust"], "allergens": ["eggs", "dairy", "wheat"]}'::jsonb, 'Quiche Me', 'Baked Goods', 'Quiche')
    , ('Mushroom Quiche', 'mushroom-quiche', 'Wild mushroom and fontina quiche', '{"ingredients": ["eggs", "cream", "mushrooms", "fontina", "thyme", "pie crust"], "allergens": ["eggs", "dairy", "wheat"]}'::jsonb, 'Quiche Me', 'Baked Goods', 'Quiche')
    , ('Sourdough Bread', 'sourdough-bread', 'Traditional sourdough loaf', '{"ingredients": ["flour", "water", "salt", "starter"], "shelf_life_days": 5}'::jsonb, 'Quiche Me', 'Baked Goods', 'Bread')

    -- Bulk Dry Goods
    , ('Raw Almonds', 'raw-almonds', 'Whole raw almonds', '{"nutrition": {"servings_per_container": 16, "calories": 170}, "origin": "California"}'::jsonb, NULL, 'Bulk', 'Nuts')
    , ('Organic Pinto Beans', 'organic-pinto-beans', 'Dried pinto beans', '{"nutrition": {"servings_per_container": 13, "calories": 120}}'::jsonb, 'Azure Market', 'Bulk', 'Beans')
;

-- ============================================================================
-- VENDOR_PRODUCTS (What vendors offer)
-- ============================================================================

-- Azure Standard products
INSERT INTO public.vendor_products (vendors_id, products_id, vendor_sku, vendor_name, size, weight, wholesale_price, retail_price, unit_price, price_unit, stock_status, last_synced_at)
VALUES
    (
        (SELECT vendors_id FROM public.vendors WHERE slug = 'azure')
        , (SELECT products_id FROM public.products WHERE slug = 'organic-rolled-oats')
        , 'AZ-12345'
        , 'Rolled Oats, Organic'
        , '5 lb'
        , '{"value": 5, "unit": "lb"}'::jsonb
        , 8.50
        , 10.99
        , 1.70
        , 'lb'
        , 'in_stock'
        , now()
    )
    , (
        (SELECT vendors_id FROM public.vendors WHERE slug = 'azure')
        , (SELECT products_id FROM public.products WHERE slug = 'organic-rolled-oats')
        , 'AZ-12346'
        , 'Rolled Oats, Organic'
        , '25 lb'
        , '{"value": 25, "unit": "lb"}'::jsonb
        , 32.00
        , 42.99
        , 1.28
        , 'lb'
        , 'in_stock'
        , now()
    )
    , (
        (SELECT vendors_id FROM public.vendors WHERE slug = 'azure')
        , (SELECT products_id FROM public.products WHERE slug = 'raw-almonds')
        , 'AZ-88001'
        , 'Almonds, Raw, Whole'
        , '1 lb'
        , '{"value": 1, "unit": "lb"}'::jsonb
        , 8.00
        , 10.99
        , 8.00
        , 'lb'
        , 'in_stock'
        , now()
    )
    , (
        (SELECT vendors_id FROM public.vendors WHERE slug = 'azure')
        , (SELECT products_id FROM public.products WHERE slug = 'organic-ap-flour')
        , 'AZ-FL500'
        , 'All Purpose Flour, Organic, Unbleached'
        , '5 lb'
        , '{"value": 5, "unit": "lb"}'::jsonb
        , 6.25
        , 8.49
        , 1.25
        , 'lb'
        , 'in_stock'
        , now()
    )
    , (
        (SELECT vendors_id FROM public.vendors WHERE slug = 'azure')
        , (SELECT products_id FROM public.products WHERE slug = 'organic-pinto-beans')
        , 'AZ-BN100'
        , 'Pinto Beans, Organic'
        , '5 lb'
        , '{"value": 5, "unit": "lb"}'::jsonb
        , 9.75
        , 12.99
        , 1.95
        , 'lb'
        , 'in_stock'
        , now()
    )
;

-- Hummingbird Wholesale products
INSERT INTO public.vendor_products (vendors_id, products_id, vendor_sku, vendor_name, size, weight, wholesale_price, retail_price, unit_price, price_unit, stock_status, last_synced_at)
VALUES
    (
        (SELECT vendors_id FROM public.vendors WHERE slug = 'hummingbird')
        , (SELECT products_id FROM public.products WHERE slug = 'organic-quinoa')
        , 'HB-Q100'
        , 'Quinoa, White, Organic'
        , '2 lb'
        , '{"value": 2, "unit": "lb"}'::jsonb
        , 7.25
        , 9.99
        , 3.63
        , 'lb'
        , 'in_stock'
        , now() - interval '3 days'
    )
    , (
        (SELECT vendors_id FROM public.vendors WHERE slug = 'hummingbird')
        , (SELECT products_id FROM public.products WHERE slug = 'raw-almonds')
        , 'HB-A200'
        , 'Raw Almonds, California'
        , '1 lb'
        , '{"value": 1, "unit": "lb"}'::jsonb
        , 8.75
        , 11.49
        , 8.75
        , 'lb'
        , 'in_stock'
        , now() - interval '3 days'
    )
    , (
        (SELECT vendors_id FROM public.vendors WHERE slug = 'hummingbird')
        , (SELECT products_id FROM public.products WHERE slug = 'organic-pinto-beans')
        , 'HB-PB500'
        , 'Organic Pinto Beans'
        , '25 lb'
        , '{"value": 25, "unit": "lb"}'::jsonb
        , 42.50
        , 54.99
        , 1.70
        , 'lb'
        , 'in_stock'
        , now() - interval '3 days'
    )
;

-- Quiche Me products
INSERT INTO public.vendor_products (vendors_id, products_id, vendor_sku, vendor_name, size, weight, wholesale_price, retail_price, unit_price, price_unit, stock_status, last_synced_at)
VALUES
    (
        (SELECT vendors_id FROM public.vendors WHERE slug = 'quiche-me')
        , (SELECT products_id FROM public.products WHERE slug = 'spinach-quiche')
        , 'QM-SPN-9'
        , 'Spinach & Gruyere Quiche'
        , '9 inch'
        , '{"value": 32, "unit": "oz"}'::jsonb
        , 12.00
        , NULL
        , NULL
        , NULL
        , 'available'
        , now()
    )
    , (
        (SELECT vendors_id FROM public.vendors WHERE slug = 'quiche-me')
        , (SELECT products_id FROM public.products WHERE slug = 'mushroom-quiche')
        , 'QM-MSH-9'
        , 'Wild Mushroom & Fontina Quiche'
        , '9 inch'
        , '{"value": 32, "unit": "oz"}'::jsonb
        , 14.00
        , NULL
        , NULL
        , NULL
        , 'available'
        , now()
    )
    , (
        (SELECT vendors_id FROM public.vendors WHERE slug = 'quiche-me')
        , (SELECT products_id FROM public.products WHERE slug = 'sourdough-bread')
        , 'QM-SD-LF'
        , 'Sourdough Loaf'
        , 'loaf'
        , '{"value": 24, "unit": "oz"}'::jsonb
        , 5.50
        , NULL
        , NULL
        , NULL
        , 'available'
        , now()
    )
;

-- ============================================================================
-- OUR_SKUS (What we sell)
-- ============================================================================

INSERT INTO public.our_skus (products_id, sku, name, size, weight, wholesale_price, member_price, nonmember_price, processing_cost, is_listed)
VALUES
    -- Grains
    (
        (SELECT products_id FROM public.products WHERE slug = 'organic-rolled-oats')
        , 'OAT-5LB'
        , 'Organic Rolled Oats - 5 lb'
        , '5 lb'
        , '{"value": 5, "unit": "lb"}'::jsonb
        , 8.50
        , 10.99
        , 12.99
        , 0.50
        , TRUE
    )
    , (
        (SELECT products_id FROM public.products WHERE slug = 'organic-rolled-oats')
        , 'OAT-25LB'
        , 'Organic Rolled Oats - 25 lb'
        , '25 lb'
        , '{"value": 25, "unit": "lb"}'::jsonb
        , 32.00
        , 39.99
        , 44.99
        , 1.00
        , TRUE
    )
    , (
        (SELECT products_id FROM public.products WHERE slug = 'organic-quinoa')
        , 'QUI-2LB'
        , 'Organic White Quinoa - 2 lb'
        , '2 lb'
        , '{"value": 2, "unit": "lb"}'::jsonb
        , 7.25
        , 9.49
        , 10.99
        , 0.25
        , TRUE
    )
    , (
        (SELECT products_id FROM public.products WHERE slug = 'organic-ap-flour')
        , 'FLOUR-5LB'
        , 'Organic All-Purpose Flour - 5 lb'
        , '5 lb'
        , '{"value": 5, "unit": "lb"}'::jsonb
        , 6.25
        , 7.99
        , 9.49
        , 0.25
        , TRUE
    )

    -- Baked Goods
    , (
        (SELECT products_id FROM public.products WHERE slug = 'spinach-quiche')
        , 'QUICHE-SP'
        , 'Spinach & Gruyere Quiche - 9"'
        , '9 inch'
        , '{"value": 32, "unit": "oz"}'::jsonb
        , 12.00
        , 15.99
        , 18.99
        , 0.00
        , TRUE
    )
    , (
        (SELECT products_id FROM public.products WHERE slug = 'mushroom-quiche')
        , 'QUICHE-MS'
        , 'Wild Mushroom Quiche - 9"'
        , '9 inch'
        , '{"value": 32, "unit": "oz"}'::jsonb
        , 14.00
        , 17.99
        , 20.99
        , 0.00
        , TRUE
    )
    , (
        (SELECT products_id FROM public.products WHERE slug = 'sourdough-bread')
        , 'BREAD-SD'
        , 'Sourdough Bread Loaf'
        , 'loaf'
        , '{"value": 24, "unit": "oz"}'::jsonb
        , 5.50
        , 7.49
        , 8.99
        , 0.00
        , TRUE
    )

    -- Bulk Dry Goods
    , (
        (SELECT products_id FROM public.products WHERE slug = 'raw-almonds')
        , 'ALM-1LB'
        , 'Raw Almonds - 1 lb'
        , '1 lb'
        , '{"value": 1, "unit": "lb"}'::jsonb
        , 8.00
        , 10.49
        , 12.49
        , 0.50
        , TRUE
    )
    , (
        (SELECT products_id FROM public.products WHERE slug = 'organic-pinto-beans')
        , 'BEANS-5LB'
        , 'Organic Pinto Beans - 5 lb'
        , '5 lb'
        , '{"value": 5, "unit": "lb"}'::jsonb
        , 9.75
        , 12.49
        , 14.99
        , 0.50
        , TRUE
    )
;

-- ============================================================================
-- SKU_SOURCING (Link our SKUs to vendor products)
-- ============================================================================

INSERT INTO public.sku_sourcing (our_skus_id, vendor_products_id, is_preferred, conversion_factor, notes)
VALUES
    -- Oats from Azure
    (
        (SELECT our_skus_id FROM public.our_skus WHERE sku = 'OAT-5LB')
        , (SELECT vendor_products_id FROM public.vendor_products WHERE vendor_sku = 'AZ-12345')
        , TRUE
        , 1.0
        , NULL
    )
    , (
        (SELECT our_skus_id FROM public.our_skus WHERE sku = 'OAT-25LB')
        , (SELECT vendor_products_id FROM public.vendor_products WHERE vendor_sku = 'AZ-12346')
        , TRUE
        , 1.0
        , NULL
    )

    -- Quinoa from Hummingbird
    , (
        (SELECT our_skus_id FROM public.our_skus WHERE sku = 'QUI-2LB')
        , (SELECT vendor_products_id FROM public.vendor_products WHERE vendor_sku = 'HB-Q100')
        , TRUE
        , 1.0
        , NULL
    )

    -- Flour from Azure
    , (
        (SELECT our_skus_id FROM public.our_skus WHERE sku = 'FLOUR-5LB')
        , (SELECT vendor_products_id FROM public.vendor_products WHERE vendor_sku = 'AZ-FL500')
        , TRUE
        , 1.0
        , NULL
    )

    -- Quiche from Quiche Me
    , (
        (SELECT our_skus_id FROM public.our_skus WHERE sku = 'QUICHE-SP')
        , (SELECT vendor_products_id FROM public.vendor_products WHERE vendor_sku = 'QM-SPN-9')
        , TRUE
        , 1.0
        , NULL
    )
    , (
        (SELECT our_skus_id FROM public.our_skus WHERE sku = 'QUICHE-MS')
        , (SELECT vendor_products_id FROM public.vendor_products WHERE vendor_sku = 'QM-MSH-9')
        , TRUE
        , 1.0
        , NULL
    )
    , (
        (SELECT our_skus_id FROM public.our_skus WHERE sku = 'BREAD-SD')
        , (SELECT vendor_products_id FROM public.vendor_products WHERE vendor_sku = 'QM-SD-LF')
        , TRUE
        , 1.0
        , NULL
    )

    -- Almonds from Azure (preferred) and Hummingbird (backup)
    , (
        (SELECT our_skus_id FROM public.our_skus WHERE sku = 'ALM-1LB')
        , (SELECT vendor_products_id FROM public.vendor_products WHERE vendor_sku = 'AZ-88001')
        , TRUE
        , 1.0
        , 'Primary source - better price'
    )
    , (
        (SELECT our_skus_id FROM public.our_skus WHERE sku = 'ALM-1LB')
        , (SELECT vendor_products_id FROM public.vendor_products WHERE vendor_sku = 'HB-A200')
        , FALSE
        , 1.0
        , 'Backup source when Azure out of stock'
    )

    -- Pinto beans from Azure
    , (
        (SELECT our_skus_id FROM public.our_skus WHERE sku = 'BEANS-5LB')
        , (SELECT vendor_products_id FROM public.vendor_products WHERE vendor_sku = 'AZ-BN100')
        , TRUE
        , 1.0
        , NULL
    )
;

-- ============================================================================
-- LOCATIONS
-- ============================================================================

INSERT INTO public.locations (name, slug, description)
VALUES
    ('Main Storage', 'main-storage', '{"type": "warehouse", "address": "123 Coop Way", "conditions": {"temperature": "ambient", "humidity": "controlled"}}'::jsonb)
    , ('Refrigerated Storage', 'refrigerated', '{"type": "cold storage", "conditions": {"temperature": "35-40F"}}'::jsonb)
;

-- ============================================================================
-- INVENTORY
-- ============================================================================

INSERT INTO public.inventory (our_skus_id, locations_id, quantity_on_hand, quantity_reserved, reorder_point)
VALUES
    -- Grains at main storage
    (
        (SELECT our_skus_id FROM public.our_skus WHERE sku = 'OAT-5LB')
        , (SELECT locations_id FROM public.locations WHERE slug = 'main-storage')
        , 12
        , 2
        , 5
    )
    , (
        (SELECT our_skus_id FROM public.our_skus WHERE sku = 'OAT-25LB')
        , (SELECT locations_id FROM public.locations WHERE slug = 'main-storage')
        , 3
        , 0
        , 2
    )
    , (
        (SELECT our_skus_id FROM public.our_skus WHERE sku = 'QUI-2LB')
        , (SELECT locations_id FROM public.locations WHERE slug = 'main-storage')
        , 8
        , 0
        , 4
    )
    , (
        (SELECT our_skus_id FROM public.our_skus WHERE sku = 'FLOUR-5LB')
        , (SELECT locations_id FROM public.locations WHERE slug = 'main-storage')
        , 15
        , 3
        , 5
    )

    -- Baked goods - quiches at 0 (made to order), bread in stock
    , (
        (SELECT our_skus_id FROM public.our_skus WHERE sku = 'QUICHE-SP')
        , (SELECT locations_id FROM public.locations WHERE slug = 'refrigerated')
        , 0
        , 0
        , NULL
    )
    , (
        (SELECT our_skus_id FROM public.our_skus WHERE sku = 'QUICHE-MS')
        , (SELECT locations_id FROM public.locations WHERE slug = 'refrigerated')
        , 0
        , 0
        , NULL
    )
    , (
        (SELECT our_skus_id FROM public.our_skus WHERE sku = 'BREAD-SD')
        , (SELECT locations_id FROM public.locations WHERE slug = 'main-storage')
        , 8
        , 1
        , 4
    )

    -- Bulk dry goods
    , (
        (SELECT our_skus_id FROM public.our_skus WHERE sku = 'ALM-1LB')
        , (SELECT locations_id FROM public.locations WHERE slug = 'main-storage')
        , 20
        , 0
        , 10
    )
    , (
        (SELECT our_skus_id FROM public.our_skus WHERE sku = 'BEANS-5LB')
        , (SELECT locations_id FROM public.locations WHERE slug = 'main-storage')
        , 6
        , 1
        , 3
    )
;

-- ============================================================================
-- VENDOR_ORDERS (Our purchases from vendors)
-- ============================================================================

INSERT INTO public.vendor_orders (vendors_id, order_number, status, order_date, expected_delivery_date, subtotal, shipping_cost, total, notes)
VALUES
    -- Completed Azure order
    (
        (SELECT vendors_id FROM public.vendors WHERE slug = 'azure')
        , 'VO-2025-001'
        , 'received'
        , '2025-01-15'
        , '2025-01-18'
        , 125.00
        , 0.00
        , 125.00
        , 'Weekly restock order'
    )
    -- Pending Azure order (in draft)
    , (
        (SELECT vendors_id FROM public.vendors WHERE slug = 'azure')
        , 'VO-2025-002'
        , 'draft'
        , NULL
        , NULL
        , NULL
        , NULL
        , NULL
        , 'Building order for next week'
    )
    -- Submitted Quiche Me order
    , (
        (SELECT vendors_id FROM public.vendors WHERE slug = 'quiche-me')
        , 'VO-2025-003'
        , 'confirmed'
        , '2025-02-12'
        , '2025-02-15'
        , 108.00
        , 0.00
        , 108.00
        , 'Special order for Saturday market'
    )
;

-- ============================================================================
-- VENDOR_ORDER_LINES
-- ============================================================================

INSERT INTO public.vendor_order_lines (vendor_orders_id, vendor_products_id, quantity, unit_price, quantity_received)
VALUES
    -- VO-2025-001 (received Azure order)
    (
        (SELECT vendor_orders_id FROM public.vendor_orders WHERE order_number = 'VO-2025-001')
        , (SELECT vendor_products_id FROM public.vendor_products WHERE vendor_sku = 'AZ-12345')
        , 10
        , 8.50
        , 10
    )
    , (
        (SELECT vendor_orders_id FROM public.vendor_orders WHERE order_number = 'VO-2025-001')
        , (SELECT vendor_products_id FROM public.vendor_products WHERE vendor_sku = 'AZ-88001')
        , 5
        , 8.00
        , 5
    )
    -- VO-2025-002 (draft Azure order)
    , (
        (SELECT vendor_orders_id FROM public.vendor_orders WHERE order_number = 'VO-2025-002')
        , (SELECT vendor_products_id FROM public.vendor_products WHERE vendor_sku = 'AZ-12346')
        , 2
        , 32.00
        , NULL
    )
    -- VO-2025-003 (confirmed Quiche Me order)
    , (
        (SELECT vendor_orders_id FROM public.vendor_orders WHERE order_number = 'VO-2025-003')
        , (SELECT vendor_products_id FROM public.vendor_products WHERE vendor_sku = 'QM-SPN-9')
        , 4
        , 12.00
        , NULL
    )
    , (
        (SELECT vendor_orders_id FROM public.vendor_orders WHERE order_number = 'VO-2025-003')
        , (SELECT vendor_products_id FROM public.vendor_products WHERE vendor_sku = 'QM-MSH-9')
        , 3
        , 14.00
        , NULL
    )
    , (
        (SELECT vendor_orders_id FROM public.vendor_orders WHERE order_number = 'VO-2025-003')
        , (SELECT vendor_products_id FROM public.vendor_products WHERE vendor_sku = 'QM-SD-LF')
        , 6
        , 5.50
        , NULL
    )
;

-- ============================================================================
-- MEMBER_ORDERS
-- ============================================================================

INSERT INTO public.member_orders (members_id, order_number, status, fulfillment_type, order_date, ready_date, completed_date, subtotal, member_dollars_applied, tax, total, amount_paid)
VALUES
    -- Jane's completed order
    (
        (SELECT members_id FROM public.members WHERE member_number = 'M001')
        , 'MO-2025-001'
        , 'picked_up'
        , 'pickup'
        , '2025-02-01 10:30:00'
        , '2025-02-01 14:00:00'
        , '2025-02-01 16:45:00'
        , 38.47
        , 5.00
        , 0.00
        , 33.47
        , 33.47
    )
    -- Bob's pending order
    , (
        (SELECT members_id FROM public.members WHERE member_number = 'M002')
        , 'MO-2025-002'
        , 'confirmed'
        , 'pickup'
        , '2025-02-14 09:15:00'
        , NULL
        , NULL
        , 28.97
        , 0.00
        , 0.00
        , 28.97
        , 0.00
    )
    -- Alice's cart (not yet submitted)
    , (
        (SELECT members_id FROM public.members WHERE member_number = 'M003')
        , NULL
        , 'cart'
        , NULL
        , NULL
        , NULL
        , NULL
        , NULL
        , NULL
        , NULL
        , NULL
        , NULL
    )
;

-- ============================================================================
-- MEMBER_ORDER_LINES
-- ============================================================================

INSERT INTO public.member_order_lines (member_orders_id, our_skus_id, quantity, unit_price, price_tier)
VALUES
    -- Jane's order (MO-2025-001)
    (
        (SELECT member_orders_id FROM public.member_orders WHERE order_number = 'MO-2025-001')
        , (SELECT our_skus_id FROM public.our_skus WHERE sku = 'OAT-5LB')
        , 2
        , 10.99
        , 'member'
    )
    , (
        (SELECT member_orders_id FROM public.member_orders WHERE order_number = 'MO-2025-001')
        , (SELECT our_skus_id FROM public.our_skus WHERE sku = 'BREAD-SD')
        , 1
        , 7.49
        , 'member'
    )
    , (
        (SELECT member_orders_id FROM public.member_orders WHERE order_number = 'MO-2025-001')
        , (SELECT our_skus_id FROM public.our_skus WHERE sku = 'ALM-1LB')
        , 1
        , 10.49
        , 'member'
    )
    -- Bob's order (MO-2025-002)
    , (
        (SELECT member_orders_id FROM public.member_orders WHERE order_number = 'MO-2025-002')
        , (SELECT our_skus_id FROM public.our_skus WHERE sku = 'QUICHE-SP')
        , 1
        , 15.99
        , 'member'
    )
    , (
        (SELECT member_orders_id FROM public.member_orders WHERE order_number = 'MO-2025-002')
        , (SELECT our_skus_id FROM public.our_skus WHERE sku = 'QUI-2LB')
        , 1
        , 9.49
        , 'member'
    )
    -- Alice's cart (items she's considering)
    , (
        (SELECT member_orders_id FROM public.member_orders WHERE order_number IS NULL AND status = 'cart')
        , (SELECT our_skus_id FROM public.our_skus WHERE sku = 'FLOUR-5LB')
        , 2
        , 7.99
        , 'member'
    )
;

-- ============================================================================
-- PAYMENTS
-- ============================================================================

INSERT INTO public.payments (member_orders_id, members_id, amount, payment_method, status, reference_number, payment_date)
VALUES
    -- Jane paid for her order with card
    (
        (SELECT member_orders_id FROM public.member_orders WHERE order_number = 'MO-2025-001')
        , (SELECT members_id FROM public.members WHERE member_number = 'M001')
        , 33.47
        , 'card'
        , 'completed'
        , 'ch_abc123xyz'
        , '2025-02-01 16:45:00'
    )
    -- Jane also used $5 member dollars (tracked separately)
    , (
        (SELECT member_orders_id FROM public.member_orders WHERE order_number = 'MO-2025-001')
        , (SELECT members_id FROM public.members WHERE member_number = 'M001')
        , 5.00
        , 'member_dollars'
        , 'completed'
        , NULL
        , '2025-02-01 16:45:00'
    )
;

-- ============================================================================
-- VERIFY DATA
-- ============================================================================

SELECT 'Vendors' AS entity, COUNT(*) AS count FROM public.vendors
UNION ALL
SELECT 'Members', COUNT(*) FROM public.members
UNION ALL
SELECT 'Products', COUNT(*) FROM public.products
UNION ALL
SELECT 'Vendor Products', COUNT(*) FROM public.vendor_products
UNION ALL
SELECT 'Our SKUs', COUNT(*) FROM public.our_skus
UNION ALL
SELECT 'SKU Sourcing Links', COUNT(*) FROM public.sku_sourcing
UNION ALL
SELECT 'Inventory Records', COUNT(*) FROM public.inventory
UNION ALL
SELECT 'Vendor Orders', COUNT(*) FROM public.vendor_orders
UNION ALL
SELECT 'Vendor Order Lines', COUNT(*) FROM public.vendor_order_lines
UNION ALL
SELECT 'Member Orders', COUNT(*) FROM public.member_orders
UNION ALL
SELECT 'Member Order Lines', COUNT(*) FROM public.member_order_lines
UNION ALL
SELECT 'Payments', COUNT(*) FROM public.payments
;
