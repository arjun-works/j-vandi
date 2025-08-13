"""
Test script to verify the application components work correctly
"""

def test_database():
    """Test database functionality"""
    print("Testing database functionality...")
    
    try:
        from database import CabDatabase
        
        # Initialize database
        db = CabDatabase()
        print("✅ Database initialized successfully")
        
        # Get location count
        count = db.get_location_count()
        print(f"✅ Database contains {count} locations")
        
        # Test search functionality
        test_search = db.search_location_by_area("Karapakkam")
        if test_search:
            print(f"✅ Search test successful: {test_search}")
        else:
            print("⚠️ Search test returned no results")
            
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")

def test_imports():
    """Test all required imports"""
    print("\nTesting imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported")
        
        import pandas as pd
        print("✅ Pandas imported")
        
        from cab_logic import run_cab_allocation
        print("✅ Cab logic imported")
        
        from database import CabDatabase
        print("✅ Database module imported")
        
        import folium
        print("✅ Folium imported")
        
        import sqlite3
        print("✅ SQLite3 imported")
        
    except Exception as e:
        print(f"❌ Import test failed: {str(e)}")

def main():
    print("🧪 Running application tests...\n")
    
    test_imports()
    test_database()
    
    print("\n🎉 Tests completed!")

if __name__ == "__main__":
    main()
