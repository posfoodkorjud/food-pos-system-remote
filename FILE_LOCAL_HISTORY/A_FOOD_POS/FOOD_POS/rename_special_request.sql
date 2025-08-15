-- Script to rename special_request column to customer_request
-- This will be executed step by step

-- Step 1: Add new customer_request column
ALTER TABLE order_items ADD COLUMN customer_request TEXT;

-- Step 2: Copy data from special_request to customer_request
UPDATE order_items SET customer_request = special_request;

-- Step 3: Drop the old special_request column (SQLite doesn't support DROP COLUMN directly)
-- We need to recreate the table

-- Create new table with customer_request
CREATE TABLE order_items_new (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    item_id INTEGER,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    total_price REAL NOT NULL,
    customer_request TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders (order_id),
    FOREIGN KEY (item_id) REFERENCES menu_items (item_id)
);

-- Copy data to new table
INSERT INTO order_items_new 
    (order_item_id, order_id, item_id, quantity, unit_price, total_price, customer_request, status, created_at)
SELECT 
    order_item_id, order_id, item_id, quantity, unit_price, total_price, special_request, status, created_at
FROM order_items;

-- Drop old table
DROP TABLE order_items;

-- Rename new table
ALTER TABLE order_items_new RENAME TO order_items;

-- Also update order_history_items table if it exists
CREATE TABLE order_history_items_new (
    history_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    menu_item_id INTEGER,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    customer_request TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Copy data if order_history_items exists
INSERT INTO order_history_items_new 
    (history_item_id, order_id, menu_item_id, quantity, price, customer_request, created_at)
SELECT 
    history_item_id, order_id, menu_item_id, quantity, price, special_request, created_at
FROM order_history_items
WHERE EXISTS (SELECT 1 FROM sqlite_master WHERE type='table' AND name='order_history_items');

-- Drop old table if exists
DROP TABLE IF EXISTS order_history_items;

-- Rename new table
ALTER TABLE order_history_items_new RENAME TO order_history_items;