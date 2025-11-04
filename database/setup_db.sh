#!/bin/bash
# Quick setup script for local development database

echo "=========================================="
echo "Web Scraper Database Setup"
echo "=========================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is required but not installed."
    exit 1
fi

# Install required dependencies
echo "Installing required Python packages..."
pip3 install mysql-connector-python

# Ask user for database type
echo ""
echo "Which database would you like to use?"
echo "1) SQLite (recommended for local development)"
echo "2) MySQL"
read -p "Enter choice [1-2]: " db_choice

if [ "$db_choice" == "1" ]; then
    # SQLite setup
    echo ""
    read -p "Database file name [scraper_history.db]: " db_file
    db_file=${db_file:-scraper_history.db}
    
    echo ""
    echo "Initializing SQLite database: $db_file"
    python3 migrate.py init-sqlite --db "$db_file"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ Setup complete!"
        echo ""
        echo "Your database is ready at: $db_file"
        echo ""
        echo "To use it in your application, add this to your code:"
        echo "  from database import create_sqlite_db"
        echo "  db = create_sqlite_db('$db_file')"
    fi
    
elif [ "$db_choice" == "2" ]; then
    # MySQL setup
    echo ""
    echo "MySQL Database Configuration"
    read -p "Host [localhost]: " mysql_host
    mysql_host=${mysql_host:-localhost}
    
    read -p "User [root]: " mysql_user
    mysql_user=${mysql_user:-root}
    
    read -sp "Password: " mysql_password
    echo ""
    
    read -p "Database name [scraper_history]: " mysql_db
    mysql_db=${mysql_db:-scraper_history}
    
    echo ""
    echo "Initializing MySQL database: $mysql_db on $mysql_host"
    python3 migrate.py init-mysql \
        --host "$mysql_host" \
        --user "$mysql_user" \
        --password "$mysql_password" \
        --database "$mysql_db"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ Setup complete!"
        echo ""
        echo "To use it in your application, add this to your code:"
        echo "  from database import create_mysql_db"
        echo "  db = create_mysql_db("
        echo "      host='$mysql_host',"
        echo "      user='$mysql_user',"
        echo "      password='YOUR_PASSWORD',"
        echo "      database='$mysql_db'"
        echo "  )"
    fi
else
    echo "Invalid choice. Exiting."
    exit 1
fi

echo ""
echo "=========================================="
echo "Next steps:"
echo "1. Update app.py to use the database"
echo "2. Run: python3 app.py"
echo "=========================================="
