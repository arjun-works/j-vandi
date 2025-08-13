# Cab Nodal Points Application

A Streamlit application for managing cab pooling with admin and POC login functionality.

## Features

### 🔧 Admin Login
- **Username:** `admin`
- **Password:** `admin123`
- Upload base location data (CSV format with Area_Id, Area, Latitude, Longitude)
- Manage central location database
- View database statistics

### 👤 POC Login
- **Username:** `poc`
- **Password:** `poc123`
- Upload user data (Excel format with User, Area columns)
- Automatic coordinate fetching from database
- Multi-page interface:
  - **Upload Page:** Data upload and processing
  - **Allocation Management Page:** Edit cab assignments and pickup order
  - **Map View Page:** Visualize routes and pickup locations

## POC Dashboard Pages

### 1. Upload Page
- Upload Excel files with user data
- System automatically matches areas with base data
- Generate initial cab allocation

### 2. Allocation Management Page
- View current cab assignments
- Move users between cabs
- Reorder pickup sequences
- Remove users from allocation
- Save changes and regenerate map

### 3. Map View Page
- Interactive map showing pickup routes
- Color-coded by cab groups
- Numbered pickup order markers

## Setup Instructions

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize Database:**
   ```bash
   python populate_db.py
   ```

3. **Run Application:**
   ```bash
   streamlit run app.py
   ```

## File Structure

- `app.py` - Main Streamlit application
- `database.py` - SQLite database management
- `cab_logic.py` - Cab allocation algorithms
- `populate_db.py` - Database initialization script
- `cab_nodal_points_lat_&_long_08.07.25.csv` - Base location data
- `sample_poc_data.xlsx` - Sample POC data for testing

## Database

The application uses SQLite database (`cab_nodal_points.db`) to store:
- Base location data (Area_Id, Area, Latitude, Longitude)
- Persistent storage accessible from anywhere

## Testing

Run the test script to verify functionality:
```bash
python test_app.py
```

## Notes

- The application maintains the original cab allocation logic
- UI for cab allocation and mapping remains unchanged for the core functionality
- Admin can only upload base data - no other options available
- POC has full access to cab allocation and management features
- All changes are saved and can be downloaded as Excel files
