-- Web Scraper Search History Database Schema
-- Supports both SQLite and MySQL with minor adjustments

-- Table: searches
-- Stores search query metadata
CREATE TABLE IF NOT EXISTS searches (
    search_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Use AUTO_INCREMENT for MySQL
    query TEXT NOT NULL,
    search_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER,  -- Optional: for multi-user support
    total_results INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'completed',  -- completed, failed, in_progress
    search_duration_ms INTEGER,  -- Search execution time in milliseconds
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_query (query(255)),  -- Remove (255) for SQLite
    INDEX idx_timestamp (search_timestamp),
    INDEX idx_user (user_id)
);

-- Table: sites
-- Stores information about scraped websites
CREATE TABLE IF NOT EXISTS sites (
    site_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Use AUTO_INCREMENT for MySQL
    site_name VARCHAR(100) NOT NULL UNIQUE,
    site_url TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_scraped TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_site_name (site_name)
);

-- Table: search_results
-- Stores individual product results for each search
CREATE TABLE IF NOT EXISTS search_results (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Use AUTO_INCREMENT for MySQL
    search_id INTEGER NOT NULL,
    site_id INTEGER NOT NULL,
    product_name TEXT NOT NULL,
    price DECIMAL(10, 2),
    original_price DECIMAL(10, 2),
    discount_percentage DECIMAL(5, 2),
    rating DECIMAL(3, 2),
    reviews_count INTEGER,
    availability VARCHAR(50),
    seller TEXT,
    product_url TEXT,
    image_url TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (search_id) REFERENCES searches(search_id) ON DELETE CASCADE,
    FOREIGN KEY (site_id) REFERENCES sites(site_id) ON DELETE CASCADE,
    INDEX idx_search_id (search_id),
    INDEX idx_site_id (site_id),
    INDEX idx_price (price),
    INDEX idx_scraped_at (scraped_at)
);

-- Table: search_metadata
-- Stores additional metadata about searches (e.g., filters applied, export history)
CREATE TABLE IF NOT EXISTS search_metadata (
    metadata_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Use AUTO_INCREMENT for MySQL
    search_id INTEGER NOT NULL,
    metadata_key VARCHAR(100) NOT NULL,
    metadata_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (search_id) REFERENCES searches(search_id) ON DELETE CASCADE,
    INDEX idx_search_meta (search_id, metadata_key)
);

-- Table: export_history
-- Tracks when searches were exported and in what format
CREATE TABLE IF NOT EXISTS export_history (
    export_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Use AUTO_INCREMENT for MySQL
    search_id INTEGER NOT NULL,
    export_format VARCHAR(20) NOT NULL,  -- csv, pdf, json
    export_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    result_count INTEGER,
    file_path TEXT,
    FOREIGN KEY (search_id) REFERENCES searches(search_id) ON DELETE CASCADE,
    INDEX idx_export_search (search_id),
    INDEX idx_export_timestamp (export_timestamp)
);

-- Views for common queries

-- View: recent_searches
-- Shows recent searches with result counts
CREATE VIEW IF NOT EXISTS recent_searches AS
SELECT 
    s.search_id,
    s.query,
    s.search_timestamp,
    s.total_results,
    s.status,
    s.search_duration_ms,
    COUNT(DISTINCT sr.site_id) as sites_searched
FROM searches s
LEFT JOIN search_results sr ON s.search_id = sr.search_id
GROUP BY s.search_id, s.query, s.search_timestamp, s.total_results, s.status, s.search_duration_ms
ORDER BY s.search_timestamp DESC;

-- View: popular_queries
-- Shows most frequently searched queries
CREATE VIEW IF NOT EXISTS popular_queries AS
SELECT 
    query,
    COUNT(*) as search_count,
    MAX(search_timestamp) as last_searched,
    AVG(total_results) as avg_results
FROM searches
GROUP BY query
ORDER BY search_count DESC;

-- View: site_statistics
-- Shows statistics for each site
CREATE VIEW IF NOT EXISTS site_statistics AS
SELECT 
    st.site_id,
    st.site_name,
    st.site_url,
    COUNT(DISTINCT sr.search_id) as total_searches,
    COUNT(sr.result_id) as total_products_found,
    AVG(sr.price) as avg_price,
    MIN(sr.price) as min_price,
    MAX(sr.price) as max_price,
    st.last_scraped
FROM sites st
LEFT JOIN search_results sr ON st.site_id = sr.site_id
GROUP BY st.site_id, st.site_name, st.site_url, st.last_scraped
ORDER BY total_products_found DESC;
