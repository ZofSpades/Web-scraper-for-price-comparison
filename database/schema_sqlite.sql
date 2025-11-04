-- SQLite-compatible schema for Web Scraper Search History

CREATE TABLE IF NOT EXISTS searches (
    search_id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    search_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER,
    total_results INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'completed',
    search_duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_searches_timestamp ON searches(search_timestamp);
CREATE INDEX IF NOT EXISTS idx_searches_user ON searches(user_id);

CREATE TABLE IF NOT EXISTS sites (
    site_id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_name VARCHAR(100) NOT NULL UNIQUE,
    site_url TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_scraped TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sites_name ON sites(site_name);

CREATE TABLE IF NOT EXISTS search_results (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    FOREIGN KEY (site_id) REFERENCES sites(site_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_results_search ON search_results(search_id);
CREATE INDEX IF NOT EXISTS idx_results_site ON search_results(site_id);
CREATE INDEX IF NOT EXISTS idx_results_price ON search_results(price);
CREATE INDEX IF NOT EXISTS idx_results_scraped ON search_results(scraped_at);

CREATE TABLE IF NOT EXISTS search_metadata (
    metadata_id INTEGER PRIMARY KEY AUTOINCREMENT,
    search_id INTEGER NOT NULL,
    metadata_key VARCHAR(100) NOT NULL,
    metadata_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (search_id) REFERENCES searches(search_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_metadata_search ON search_metadata(search_id, metadata_key);

CREATE TABLE IF NOT EXISTS export_history (
    export_id INTEGER PRIMARY KEY AUTOINCREMENT,
    search_id INTEGER NOT NULL,
    export_format VARCHAR(20) NOT NULL,
    export_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    result_count INTEGER,
    file_path TEXT,
    FOREIGN KEY (search_id) REFERENCES searches(search_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_export_search ON export_history(search_id);
CREATE INDEX IF NOT EXISTS idx_export_timestamp ON export_history(export_timestamp);

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

CREATE VIEW IF NOT EXISTS popular_queries AS
SELECT 
    query,
    COUNT(*) as search_count,
    MAX(search_timestamp) as last_searched,
    AVG(total_results) as avg_results
FROM searches
GROUP BY query
ORDER BY search_count DESC;

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
