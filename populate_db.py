"""
Script to populate the database with existing CSV data
Run this once to initialize the database with base location data
"""

import pandas as pd
from database import CabDatabase

def populate_database():
    """Populate database with existing CSV data"""
    # Initialize database
    db = CabDatabase()
    
    # Read the existing CSV file
    csv_file = "cab_nodal_points_lat_&_long_08.07.25.csv"
    
    try:
        df = pd.read_csv(csv_file)
        print(f"Read {len(df)} rows from {csv_file}")
        print("Columns:", df.columns.tolist())
        
        # Insert data into database
        success = db.insert_base_locations(df)
        
        if success:
            print(f"✅ Successfully populated database with {len(df)} locations!")
            
            # Verify the data
            count = db.get_location_count()
            print(f"📊 Database now contains {count} locations")
            
        else:
            print("❌ Failed to populate database")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    populate_database()
