import streamlit as st
import pandas as pd
from cab_logic import run_cab_allocation 
from database import CabDatabase
import os

# Initialize database
db = CabDatabase()

# Page Title
st.set_page_config(page_title="Events_Cab_Pooling", layout="wide")

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"

def admin_login():
    """Admin login interface"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #d63031;">🔐 Admin Login</h1>
        <p style="font-size: 1.1rem; color: #666;">Administrator access for base data upload and system management</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            st.markdown("""
            <div style="background: #f8f9fa; padding: 2rem; border-radius: 15px; border: 1px solid #dee2e6;">
            """, unsafe_allow_html=True)
            
            username = st.text_input("👤 Username", placeholder="Enter admin username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter admin password")
            
            col_login, col_back = st.columns(2)
            with col_login:
                if st.button("🔓 Login as Admin", type="primary", use_container_width=True):
                    # Simple hardcoded credentials (you can enhance this with proper authentication)
                    if username == "admin" and password == "admin123":
                        st.session_state.logged_in = True
                        st.session_state.user_type = "admin"
                        st.session_state.current_page = "admin_dashboard"
                        st.success("✅ Admin login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials")
            
            with col_back:
                if st.button("🔙 Back to Home", use_container_width=True):
                    st.session_state.current_page = "home"
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Credentials hint
            st.info("💡 **Default Credentials:** Username: `admin` | Password: `admin123`")

def poc_login():
    """POC login interface"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #00b894;">🔐 POC Login</h1>
        <p style="font-size: 1.1rem; color: #666;">Point of Contact access for cab allocation and route management</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            st.markdown("""
            <div style="background: #f8f9fa; padding: 2rem; border-radius: 15px; border: 1px solid #dee2e6;">
            """, unsafe_allow_html=True)
            
            username = st.text_input("👤 Username", placeholder="Enter POC username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter POC password")
            
            col_login, col_back = st.columns(2)
            with col_login:
                if st.button("🔓 Login as POC", type="primary", use_container_width=True):
                    # Simple hardcoded credentials (you can enhance this with proper authentication)
                    if username == "poc" and password == "poc123":
                        st.session_state.logged_in = True
                        st.session_state.user_type = "poc"
                        st.session_state.current_page = "poc_dashboard"
                        st.success("✅ POC login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials")
            
            with col_back:
                if st.button("🔙 Back to Home", use_container_width=True):
                    st.session_state.current_page = "home"
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Credentials hint
            st.info("💡 **Default Credentials:** Username: `poc` | Password: `poc123`")

def admin_dashboard():
    """Admin dashboard for base data upload"""
    st.title("🔧 Admin Dashboard - Base Data Management")
    
    if st.button("Logout", key="admin_logout"):
        st.session_state.logged_in = False
        st.session_state.user_type = None
        st.session_state.current_page = "home"
        st.rerun()
    
    st.subheader("📊 Current Database Status")
    location_count = db.get_location_count()
    st.metric("Total Locations in Database", location_count)
    
    st.subheader("📤 Upload Base Data")
    st.write("Upload CSV file with base location data (Area_Id, Area, Latitude, Longitude)")
    
    uploaded_file = st.file_uploader(
        "Choose CSV file", 
        type=["csv"],
        help="Expected format: Area_Id, Area, Latitude, Longitude"
    )
    
    if uploaded_file:
        try:
            # Read the uploaded CSV
            df = pd.read_csv(uploaded_file)
            
            # Validate required columns
            required_cols = {"Area", "Latitude", "Longitude"}
            if not required_cols.issubset(df.columns):
                st.error(f"❌ Missing required columns. Found: {df.columns.tolist()}")
                st.error(f"Required: {list(required_cols)}")
                return
            
            # Show preview
            st.subheader("📋 Data Preview")
            st.dataframe(df.head(10))
            st.write(f"Total rows: {len(df)}")
            
            # Upload button
            if st.button("💾 Save to Database", type="primary"):
                try:
                    success = db.insert_base_locations(df)
                    if success:
                        st.success(f"✅ Successfully uploaded {len(df)} locations to database!")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Error saving to database: {str(e)}")
                    
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
    
    # Show current data
    if st.checkbox("📋 View Current Database Data"):
        current_data = db.get_base_locations()
        if not current_data.empty:
            st.dataframe(current_data)
        else:
            st.info("No data in database yet.")

def enhance_user_data_with_coordinates(user_df):
    """Enhance user data with coordinates from database"""
    enhanced_data = []
    missing_locations = []
    
    for _, row in user_df.iterrows():
        area_name = row['Area']
        location_data = db.search_location_by_area(area_name)
        
        if location_data:
            enhanced_row = row.copy()
            enhanced_row['Latitude'] = location_data['Latitude']
            enhanced_row['Longitude'] = location_data['Longitude']
            enhanced_data.append(enhanced_row)
        else:
            missing_locations.append(area_name)
    
    enhanced_df = pd.DataFrame(enhanced_data)
    return enhanced_df, missing_locations

def poc_data_upload():
    """POC data upload page"""
    # Header with logout
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown("""
        <h1 style="color: #00b894;">🚕 POC Dashboard - Upload User Data</h1>
        <p style="color: #666; font-size: 1.1rem;">Upload participant data and generate optimized cab allocations</p>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("🚪 Logout", key="poc_logout", type="secondary"):
            st.session_state.logged_in = False
            st.session_state.user_type = None
            st.session_state.current_page = "home"
            st.session_state.poc_page = "upload"
            st.rerun()
    
    st.divider()
    
    st.subheader("📊 Database Status")
    location_count = db.get_location_count()
    if location_count == 0:
        st.warning("⚠️ No base location data available. Please contact admin to upload base data.")
        return
    else:
        st.success(f"✅ {location_count} locations available in database")
    
    st.subheader("📤 Upload User Data")
    st.write("Upload Excel file with user data (User ID, Name, Area)")

    # Download demo data button
    demo_path = os.path.join(os.getcwd(), "demo_user_data.xlsx")
    with open(demo_path, "rb") as f:
        st.download_button("⬇️ Download Demo Excel", f, file_name="demo_user_data.xlsx", use_container_width=True)

    # Button to use demo data directly
    use_demo = st.button("Use Demo Data", key="use_demo_data")

    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

    # Load data from upload or demo
    user_df = None
    if uploaded_file:
        user_df = pd.read_excel(uploaded_file)
    elif use_demo:
        user_df = pd.read_excel(demo_path)

    if user_df is not None:
        # Validate columns
        required_cols = {"User ID", "Name", "Area"}
        if not required_cols.issubset(user_df.columns):
            st.error(f"❌ Excel file must contain columns: {list(required_cols)}")
            return

        st.subheader("📋 User Data Preview")
        st.dataframe(user_df, use_container_width=True)

        # Enhance with coordinates (using Area)
        user_df_for_coords = user_df.rename(columns={"User ID": "User"})
        with st.spinner("🔍 Fetching coordinates from database..."):
            enhanced_df, missing_locations = enhance_user_data_with_coordinates(user_df_for_coords)

        if missing_locations:
            st.warning(f"⚠️ Could not find coordinates for {len(missing_locations)} locations:")
            for loc in missing_locations[:10]:  # Show first 10
                st.write(f"- {loc}")
            if len(missing_locations) > 10:
                st.write(f"... and {len(missing_locations) - 10} more")

        if not enhanced_df.empty:
            st.success(f"✅ Successfully found coordinates for {len(enhanced_df)} users")

            # Validate enhanced data has required columns for cab allocation
            required_cols2 = {"User", "Area", "Latitude", "Longitude"}
            if required_cols2.issubset(enhanced_df.columns):
                # Run cab allocation logic (same as original)
                with st.spinner("🚕 Calculating cab allocation..."):
                    result_df, cab_route_map_file = run_cab_allocation(enhanced_df)

                # Store results in session state
                st.session_state.cab_allocation_result = result_df
                st.session_state.cab_route_map_file = cab_route_map_file
                st.session_state.enhanced_user_data = enhanced_df

                st.success("✅ Cab Allocation Completed")

                # Show navigation buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("📊 View Cab Allocation", use_container_width=True):
                        st.session_state.poc_page = "allocation"
                        st.rerun()
                with col2:
                    if st.button("🗺️ View Route Map", use_container_width=True):
                        st.session_state.poc_page = "map"
                        st.rerun()
                with col3:
                    # Show Download Link for Excel
                    output_excel = os.path.join("Output", "cab_allocation_output.xlsx")
                    os.makedirs(os.path.dirname(output_excel), exist_ok=True)
                    result_df.to_excel(output_excel, index=False)
                    with open(output_excel, "rb") as f:
                        st.download_button("⬇️ Download Excel", f, file_name="cab_allocation.xlsx", use_container_width=True)
            else:
                st.error("❌ Could not process data - missing coordinate information")
        else:
            st.error("❌ No valid location data found")

def poc_allocation_management():
    """POC cab allocation management page"""
    st.title("📊 Cab Allocation Management")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        if st.button("📤 Back to Upload", key="back_to_upload"):
            st.session_state.poc_page = "upload"
            st.rerun()
    with col2:
        if st.button("🗺️ View Map", key="view_map"):
            st.session_state.poc_page = "map"
            st.rerun()
    with col3:
        if st.button("Logout", key="poc_logout_alloc"):
            st.session_state.logged_in = False
            st.session_state.user_type = None
            st.session_state.current_page = "home"
            st.session_state.poc_page = "upload"
            st.rerun()
    
    if 'cab_allocation_result' not in st.session_state:
        st.warning("⚠️ No cab allocation data found. Please upload user data first.")
        if st.button("Go to Upload Page"):
            st.session_state.poc_page = "upload"
            st.rerun()
        return
    
    # Get current allocation data
    if 'modified_allocation' not in st.session_state:
        st.session_state.modified_allocation = st.session_state.cab_allocation_result.copy()
    
    allocation_df = st.session_state.modified_allocation
    
    if allocation_df.empty:
        st.warning("⚠️ No allocation data available.")
        return
    
    st.subheader("🚕 Current Cab Allocation")
    
    # Display cab groups
    cab_groups = allocation_df['Cab Group'].unique()
    
    if len(cab_groups) == 0:
        st.warning("⚠️ No cab groups found.")
        return
    
    # Add new participant section
    with st.expander("➕ Add New Participant", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                new_user = st.text_input("User ID", key="new_user_id")
            with col2:
                # Get available areas from database
                available_areas = db.get_base_locations()['area'].tolist() if not db.get_base_locations().empty else []
                new_area = st.selectbox("Select Area", options=available_areas, key="new_area")
            with col3:
                new_cab = st.selectbox("Assign to Cab", options=sorted(cab_groups), key="new_cab")
            with col4:
                if st.button("Add Participant", type="primary"):
                    if new_user and new_area:
                        # Get coordinates for the selected area
                        location_data = db.search_location_by_area(new_area)
                        if location_data:
                            # Create new row
                            max_pickup_order = st.session_state.modified_allocation[
                                st.session_state.modified_allocation['Cab Group'] == new_cab
                            ]['Pickup Order'].max() if not st.session_state.modified_allocation[
                                st.session_state.modified_allocation['Cab Group'] == new_cab
                            ].empty else 0
                            
                            new_row = pd.DataFrame({
                                'User': [new_user],
                                'Area': [new_area],
                                'Latitude': [location_data['Latitude']],
                                'Longitude': [location_data['Longitude']],
                                'Cab Group': [new_cab],
                                'Pickup Order': [max_pickup_order + 1]
                            })
                            
                            # Add to allocation
                            st.session_state.modified_allocation = pd.concat([
                                st.session_state.modified_allocation, new_row
                            ], ignore_index=True)
                            
                            # Regenerate map
                            regenerate_map_with_allocation()
                            st.success(f"✅ Added {new_user} to Cab {new_cab}!")
                            st.rerun()
                        else:
                            st.error("❌ Could not find coordinates for selected area")
                    else:
                        st.error("❌ Please fill all fields")
    
    # Create new cab option
    with st.expander("🚗 Create New Cab", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Create New Cab", type="secondary"):
                    # Find next available cab number
                    max_cab = max(cab_groups) if cab_groups.size > 0 else -1
                    new_cab_number = max_cab + 1
                    
                    # Create empty cab (will show in selectboxes for future use)
                    st.success(f"✅ Cab {new_cab_number} is ready for assignments!")
                    st.info("You can now assign participants to this cab using the 'Add New Participant' section above.")
            with col2:
                st.write("**Current Cabs:**")
                for cab in sorted(cab_groups):
                    passenger_count = len(allocation_df[allocation_df['Cab Group'] == cab])
                    st.write(f"Cab {cab}: {passenger_count} passengers")
    
    # Display cab groups
    cab_groups = allocation_df['Cab Group'].unique()
    
    # Cab Statistics Summary
    st.subheader("📊 Cab Statistics")
    if len(cab_groups) > 0:
            # Display all cabs in a responsive grid
            
            # First row (up to 4 cabs)
            first_row_cabs = list(sorted(cab_groups))[:4]
            if first_row_cabs:
                cols1 = st.columns(len(first_row_cabs))
                for i, cab_group in enumerate(first_row_cabs):
                    cab_data = allocation_df[allocation_df['Cab Group'] == cab_group]
                    passenger_count = len(cab_data)
                    
                    with cols1[i]:
                        color = "🟢" if passenger_count <= 6 else "🔴"
                        st.metric(
                            f"🚗 Cab {cab_group}", 
                            f"{passenger_count}/6",
                            delta=f"{color} {'OK' if passenger_count <= 6 else 'Overcrowded'}"
                        )
            
            # Second row (remaining cabs if any)
            remaining_cabs = list(sorted(cab_groups))[4:]
            if remaining_cabs:
                cols2 = st.columns(len(remaining_cabs))
                for i, cab_group in enumerate(remaining_cabs):
                    cab_data = allocation_df[allocation_df['Cab Group'] == cab_group]
                    passenger_count = len(cab_data)
                
                with cols2[i]:
                    color = "🟢" if passenger_count <= 6 else "🔴"
                    st.metric(
                        f"🚗 Cab {cab_group}", 
                        f"{passenger_count}/6",
                        delta=f"{color} {'OK' if passenger_count <= 6 else 'Overcrowded'}"
                    )
    
    st.divider()  # Add visual separator
    
    for cab_group in sorted(cab_groups):
        with st.expander(f"🚗 Cab {cab_group} ({len(allocation_df[allocation_df['Cab Group'] == cab_group])} passengers)", expanded=True):
            cab_data = allocation_df[allocation_df['Cab Group'] == cab_group].copy()
            
            st.write("**Current Passengers:**")
            
            # Create editable table for this cab
            for idx, row in cab_data.iterrows():
                col1, col2, col3, col4, col5 = st.columns([2, 3, 1, 2, 1])
                
                with col1:
                    st.write(f"**{row['User']}**")
                with col2:
                    st.write(f"{row['Area']}")
                with col3:
                    st.write(f"Order: {row['Pickup Order']}")
                with col4:
                    # Option to move to different cab
                    new_cab = st.selectbox(
                        "Move to Cab:", 
                        options=sorted(cab_groups), 
                        index=list(sorted(cab_groups)).index(cab_group),
                        key=f"cab_select_{idx}"
                    )
                    if new_cab != cab_group:
                        if st.button("Move", key=f"move_{idx}"):
                            # Update cab group
                            st.session_state.modified_allocation.loc[idx, 'Cab Group'] = new_cab
                            # Recalculate pickup orders
                            update_pickup_orders()
                            # Auto-regenerate map with new allocation
                            regenerate_map_with_allocation()
                            st.success(f"✅ Moved {row['User']} to Cab {new_cab} and updated map!")
                            st.rerun()
                with col5:
                    # Option to remove passenger
                    if f"confirm_remove_{idx}" not in st.session_state:
                        st.session_state[f"confirm_remove_{idx}"] = False
                    
                    if not st.session_state[f"confirm_remove_{idx}"]:
                        if st.button("❌", key=f"remove_{idx}", help="Remove passenger"):
                            st.session_state[f"confirm_remove_{idx}"] = True
                            st.rerun()
                    else:
                        col_yes, col_no = st.columns(2)
                        with col_yes:
                            if st.button("✅", key=f"confirm_yes_{idx}", help="Confirm removal"):
                                st.session_state.modified_allocation = st.session_state.modified_allocation.drop(idx)
                                update_pickup_orders()
                                # Auto-regenerate map after removal
                                regenerate_map_with_allocation()
                                st.session_state[f"confirm_remove_{idx}"] = False
                                st.success(f"✅ Removed {row['User']} and updated map!")
                                st.rerun()
                        with col_no:
                            if st.button("❌", key=f"cancel_{idx}", help="Cancel removal"):
                                st.session_state[f"confirm_remove_{idx}"] = False
                                st.rerun()
            
            # Reorder pickup sequence for this cab
            st.write("**Reorder Pickup Sequence:**")
            cab_passengers = allocation_df[allocation_df['Cab Group'] == cab_group]['User'].tolist()
            
            if len(cab_passengers) > 1:
                new_order = st.multiselect(
                    f"Drag to reorder pickup sequence for Cab {cab_group}:",
                    options=cab_passengers,
                    default=cab_passengers,
                    key=f"reorder_{cab_group}"
                )
                
                if len(new_order) == len(cab_passengers) and new_order != cab_passengers:
                    if st.button(f"Apply New Order for Cab {cab_group}", key=f"apply_order_{cab_group}"):
                        # Update pickup orders
                        for i, user in enumerate(new_order):
                            mask = (st.session_state.modified_allocation['Cab Group'] == cab_group) & \
                                   (st.session_state.modified_allocation['User'] == user)
                            st.session_state.modified_allocation.loc[mask, 'Pickup Order'] = i + 1
                        # Auto-regenerate map with new pickup order
                        regenerate_map_with_allocation()
                        st.success(f"✅ Updated pickup order for Cab {cab_group} and updated map!")
                        st.rerun()
    
    # Save Changes section - moved outside the cab_group loop
    st.subheader("💾 Save Changes")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save & Regenerate Map", type="primary", key="save_regenerate_main"):
            # Regenerate the map with new allocation
            regenerate_map_with_allocation()
            st.success("✅ Changes saved and map regenerated!")
    
    with col2:
        # Download updated allocation
        output_excel = os.path.join("Output", "updated_cab_allocation.xlsx")
        os.makedirs(os.path.dirname(output_excel), exist_ok=True)
        st.session_state.modified_allocation.to_excel(output_excel, index=False)
        with open(output_excel, "rb") as f:
            st.download_button("⬇️ Download Updated Allocation", f, file_name="updated_cab_allocation.xlsx")

def update_pickup_orders():
    """Update pickup orders after changes"""
    cab_groups = st.session_state.modified_allocation['Cab Group'].unique()
    for cab_group in cab_groups:
        mask = st.session_state.modified_allocation['Cab Group'] == cab_group
        cab_data = st.session_state.modified_allocation[mask]
        # Reset pickup order based on current sequence
        for i, idx in enumerate(cab_data.index):
            st.session_state.modified_allocation.loc[idx, 'Pickup Order'] = i + 1

def regenerate_map_with_allocation():
    """Regenerate map with modified allocation"""
    try:
        import folium
        
        DESTINATION = (13.171354, 80.026655)  # Same as in cab_logic
        
        # Get modified allocation data
        allocation_df = st.session_state.modified_allocation
        
        # Create map with pickup order visualization
        cab_colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen']
        m = folium.Map(location=DESTINATION, zoom_start=12)
        
        # Add destination marker
        folium.Marker(location=DESTINATION, tooltip='Destination', icon=folium.Icon(color='black')).add_to(m)
        
        # Loop over each cab group
        for cab_group, members in allocation_df.groupby('Cab Group'):
            color = cab_colors[hash(f"Cab {cab_group}") % len(cab_colors)]
            
            # Sort by pickup order and add markers with original cab icons
            for _, row in members.sort_values('Pickup Order').iterrows():
                folium.Marker(
                    location=[row['Latitude'], row['Longitude']],
                    tooltip=f"Pickup {row['Pickup Order']}: {row['User']} (Cab {cab_group}) - {row['Area']}",
                    icon=folium.Icon(color=color, icon='user')
                ).add_to(m)
        
        # Save the updated map
        updated_map_file = os.path.join("Output", "updated_cab_routes.html")
        os.makedirs(os.path.dirname(updated_map_file), exist_ok=True)
        m.save(updated_map_file)
        
        # Update session state
        st.session_state.cab_route_map_file = updated_map_file
        st.session_state.cab_allocation_result = allocation_df.copy()
        
    except Exception as e:
        st.error(f"Error regenerating map: {str(e)}")

def poc_map_view():
    """POC route map view page"""
    st.title("🗺️ Route Map View")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        if st.button("📤 Back to Upload", key="back_to_upload_map"):
            st.session_state.poc_page = "upload"
            st.rerun()
    with col2:
        if st.button("📊 Manage Allocation", key="manage_alloc"):
            st.session_state.poc_page = "allocation"
            st.rerun()
    with col3:
        if st.button("Logout", key="poc_logout_map"):
            st.session_state.logged_in = False
            st.session_state.user_type = None
            st.session_state.current_page = "home"
            st.session_state.poc_page = "upload"
            st.rerun()
    
    if 'cab_route_map_file' not in st.session_state:
        st.warning("⚠️ No route map found. Please upload user data and generate allocation first.")
        if st.button("Go to Upload Page"):
            st.session_state.poc_page = "upload"
            st.rerun()
        return
    
    try:
        st.subheader("🗺️ Pickup Route Map")
        with open(st.session_state.cab_route_map_file, "r", encoding="utf-8") as f:
            html_data = f.read()
            st.components.v1.html(html_data, height=600, scrolling=True)
    except Exception as e:
        st.error(f"❌ Error loading map: {str(e)}")

def poc_dashboard():
    """POC dashboard with multiple pages"""
    # Initialize POC page state
    if 'poc_page' not in st.session_state:
        st.session_state.poc_page = "upload"
    
    # Route to appropriate page
    if st.session_state.poc_page == "upload":
        poc_data_upload()
    elif st.session_state.poc_page == "allocation":
        poc_allocation_management()
    elif st.session_state.poc_page == "map":
        poc_map_view()

def main():
    """Main application logic with page routing"""
    
    # Route to different pages based on current_page state
    if st.session_state.current_page == "home":
        show_home_page()
    elif st.session_state.current_page == "admin_login":
        admin_login()
    elif st.session_state.current_page == "poc_login":
        poc_login()
    elif st.session_state.current_page == "admin_dashboard":
        if st.session_state.logged_in and st.session_state.user_type == "admin":
            admin_dashboard()
        else:
            st.session_state.current_page = "home"
            st.rerun()
    elif st.session_state.current_page == "poc_dashboard":
        if st.session_state.logged_in and st.session_state.user_type == "poc":
            poc_dashboard()
        else:
            st.session_state.current_page = "home"
            st.rerun()

def show_home_page():
    """Display the home page with login options"""
    # Reset POC page state when on home
    if 'poc_page' in st.session_state:
        del st.session_state.poc_page
    
    # Hero Section
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #1f77b4; font-size: 3rem; margin-bottom: 0.5rem;">🚕 Events Cab Pooling</h1>
        <p style="font-size: 1.2rem; color: #666; margin-bottom: 2rem;">Smart cab allocation and route optimization system</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features Overview
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; margin: 2rem 0; color: white;">
        <h3 style="text-align: center; margin-bottom: 1.5rem;">🌟 System Features</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
            <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px;">
                <h4>🔧 Admin Portal</h4>
                <p>• Upload base location data<br>• Manage central database<br>• Monitor system statistics</p>
            </div>
            <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px;">
                <h4>👤 POC Dashboard</h4>
                <p>• Upload participant data<br>• Smart cab allocation<br>• Interactive route management</p>
            </div>
            <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px;">
                <h4>🗺️ Smart Mapping</h4>
                <p>• Real-time route visualization<br>• Optimized pickup orders<br>• Distance calculations</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Login Cards
    st.markdown("### 🔐 Choose Your Access Level")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Admin Login Card
        with st.container():
            st.markdown("""
            <div style="border: 2px solid #ff6b6b; border-radius: 15px; padding: 1.5rem; margin: 1rem 0; 
                       background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);">
                <h4 style="color: #d63031; text-align: center; margin-bottom: 1rem;">🔧 Administrator Access</h4>
                <p style="text-align: center; margin-bottom: 1rem;">Manage base location data and system configuration</p>
            """, unsafe_allow_html=True)
            
            if st.button("🔧 Admin Login", use_container_width=True, type="primary"):
                st.session_state.current_page = "admin_login"
                st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # POC Login Card  
        with st.container():
            st.markdown("""
            <div style="border: 2px solid #4ecdc4; border-radius: 15px; padding: 1.5rem; margin: 1rem 0; 
                       background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);">
                <h4 style="color: #00b894; text-align: center; margin-bottom: 1rem;">👤 POC Access</h4>
                <p style="text-align: center; margin-bottom: 1rem;">Upload participant data and manage cab allocations</p>
            """, unsafe_allow_html=True)
            
            if st.button("👤 POC Login", use_container_width=True, type="secondary"):
                st.session_state.current_page = "poc_login"
                st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Quick Stats
    if db.get_location_count() > 0:
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📍 Locations in Database", db.get_location_count())
        with col2:
            st.metric("🗂️ System Status", "Active", delta="Running")
        with col3:
            st.metric("📊 Database", "SQLite", delta="Ready")

if __name__ == "__main__":
    main()