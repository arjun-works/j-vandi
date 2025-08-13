import sqlite3
import pandas as pd

class CabDatabase:
    def __init__(self, db_path="cab_nodal_points.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create base_locations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS base_locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                area_id TEXT,
                area TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_base_locations(self, df):
        """Insert base locations data from DataFrame"""
        conn = sqlite3.connect(self.db_path)
        
        # Clear existing data
        cursor = conn.cursor()
        cursor.execute('DELETE FROM base_locations')
        
        # Insert new data
        for _, row in df.iterrows():
            cursor.execute('''
                INSERT INTO base_locations (area_id, area, latitude, longitude)
                VALUES (?, ?, ?, ?)
            ''', (row.get('Area_Id'), row['Area'], row['Latitude'], row['Longitude']))
        
        conn.commit()
        conn.close()
        return True
    
    def get_base_locations(self):
        """Get all base locations as DataFrame"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('SELECT * FROM base_locations', conn)
        conn.close()
        return df
    
    def search_location_by_area(self, area_name):
        """Search for location by area name (fuzzy match)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Use LIKE for fuzzy matching
        cursor.execute('''
            SELECT area, latitude, longitude 
            FROM base_locations 
            WHERE LOWER(area) LIKE LOWER(?)
            LIMIT 1
        ''', (f'%{area_name}%',))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {'Area': result[0], 'Latitude': result[1], 'Longitude': result[2]}
        return None
    
    def get_location_count(self):
        """Get total count of locations in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM base_locations')
        count = cursor.fetchone()[0]
        conn.close()
        return count
