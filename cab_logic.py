import pandas as pd
import os
from sklearn.cluster import DBSCAN
from geopy.distance import great_circle
from geopy import Point
import folium
import math
 
def run_cab_allocation(df):
    # Clustering + pickup + map code
    # -------------------------------
    # CONFIGURATION
    # -------------------------------
    EXCEL_FILE = r"C:\Users\2322594\OneDrive - Cognizant\Outreach\Cab_Nodal_Points\sample_data.xlsx"  # Replace with your file name
    DESTINATION = (13.171354, 80.026655)  # Kilakondaiyur
    DISTANCE_THRESHOLD_METERS = 4000  # Cluster max distance: 4 km
    MAX_PEOPLE_PER_CAB = 6
    
    # -------------------------------
    # HELPER: Haversine Distance in meters
    # -------------------------------
    def haversine(coord1, coord2):
        return great_circle(coord1, coord2).meters
    
    # -------------------------------
    # STEP 1: Read Data
    # -------------------------------
    #df = pd.read_excel(EXCEL_FILE)
    locations = list(zip(df['Latitude'], df['Longitude']))
    
    # -------------------------------
    # STEP 2: Create Distance Matrix
    # -------------------------------
    distance_matrix = []
    for loc1 in locations:
        row = []
        for loc2 in locations:
            row.append(haversine(loc1, loc2))
        distance_matrix.append(row)
    
    # -------------------------------
    # STEP 3: Clustering with DBSCAN
    # -------------------------------
    kms_per_radian = 6371000.0  # Earth's radius in meters
    db = DBSCAN(eps=DISTANCE_THRESHOLD_METERS, min_samples=1, metric='precomputed')
    labels = db.fit_predict(distance_matrix)
    df['Cab Group'] = labels
    
    # -------------------------------
    # STEP 4: Split groups exceeding cab capacity
    # -------------------------------
    final_allocations = []
    for group in df['Cab Group'].unique():
        group_df = df[df['Cab Group'] == group].reset_index(drop=True)
        
        # If group size is OK, assign directly
        if len(group_df) <= MAX_PEOPLE_PER_CAB:
            group_df['Cab Group'] = group  # Keep original group number if within capacity
            final_allocations.append(group_df)
        else:
            # Split into subgroups and assign new cab group numbers
            num_cabs = math.ceil(len(group_df) / MAX_PEOPLE_PER_CAB)
            max_existing_group = df['Cab Group'].max()
            for i in range(num_cabs):
                sub_df = group_df.iloc[i * MAX_PEOPLE_PER_CAB: (i + 1) * MAX_PEOPLE_PER_CAB].copy()
                # Assign new unique cab group number for split groups
                sub_df['Cab Group'] = max_existing_group + 1 + i
                final_allocations.append(sub_df)
    
    # Combine all
    result_df = pd.concat(final_allocations, ignore_index=True)
    
    # -------------------------------
    # STEP 5: Output Cab Assignments
    # -------------------------------
    cab_groups = result_df.groupby('Cab Group')
    for cab, members in cab_groups:
        print(f"\n🚕 Cab {cab}:")
        for _, row in members.iterrows():
            print(f"   {row['User']} - {row['Area']}")
    
    # -------------------------------
    # STEP 6: Optional Map Visualization
    # -------------------------------
    cab_colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen']
    m = folium.Map(location=DESTINATION, zoom_start=12)
    
    # Add destination marker
    folium.Marker(location=DESTINATION, tooltip='Destination', icon=folium.Icon(color='black')).add_to(m)
    
    # Add user locations
    for cab, members in cab_groups:
        color = cab_colors[hash(f"Cab {cab}") % len(cab_colors)]
        for _, row in members.iterrows():
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                tooltip=f"{row['User']} (Cab {cab})",
                icon=folium.Icon(color=color)
            ).add_to(m)

    # -------------------------------
    # STEP 6: Optional Map Visualization
    # -------------------------------
    cab_colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen']
    m = folium.Map(location=DESTINATION, zoom_start=12)
    
    # Add destination marker
    folium.Marker(location=DESTINATION, tooltip='Destination', icon=folium.Icon(color='black')).add_to(m)
    
    # Group users by exact Lat & Long
    grouped = result_df.groupby(['Latitude', 'Longitude'])
    
    # Add combined markers for users in the same location
    for (lat, lon), group in grouped:
        first_cab = group['Cab Group'].iloc[0]  # Get the cab for color coding
        color = cab_colors[hash(f"Cab {first_cab}") % len(cab_colors)]
    
        tooltip_text = "\n".join(
            f"{row['User']} (Cab {row['Cab Group']}) - {row['Area']}" for _, row in group.iterrows()
        )
    
        folium.Marker(
            location=[lat, lon],
            tooltip=tooltip_text,
            icon=folium.Icon(color=color)
        ).add_to(m)
    
    # Save to HTML
    os.makedirs("Output", exist_ok=True)
    m.save(os.path.join("Output", "cab_routes.html"))
    print("\n✅ Map saved as cab_routes.html")

    # -------------------------------
    # STEP 7: Optimize Pickup Order
    # -------------------------------
    
    def sort_pickup_order(group_df, destination_coords):
        unvisited = group_df.copy()
        pickup_order = []
    
        # Start from the user farthest from destination
        unvisited['DistToDest'] = unvisited.apply(lambda row: haversine((row['Latitude'], row['Longitude']), destination_coords), axis=1)
        current = unvisited.sort_values('DistToDest', ascending=False).iloc[0]
        pickup_order.append(current)
        unvisited = unvisited[unvisited['User'] != current['User']]
    
        # Visit nearest person next
        while not unvisited.empty:
            last_point = (current['Latitude'], current['Longitude'])
            unvisited['DistToLast'] = unvisited.apply(lambda row: haversine((row['Latitude'], row['Longitude']), last_point), axis=1)
            current = unvisited.sort_values('DistToLast').iloc[0]
            pickup_order.append(current)
            unvisited = unvisited[unvisited['User'] != current['User']]
    
        # Return the ordered DataFrame
        return pd.DataFrame(pickup_order)
    
    # Apply optimization for each cab group
    optimized_routes = []
    
    for cab, members in result_df.groupby('Cab Group'):
        ordered_df = sort_pickup_order(members, DESTINATION)
        ordered_df['Pickup Order'] = range(1, len(ordered_df) + 1)
        ordered_df['Cab Group'] = cab
        optimized_routes.append(ordered_df)
    
    # Combine all optimized pickup orders
    final_route_df = pd.concat(optimized_routes, ignore_index=True)
    
    # -------------------------------
    # STEP 8: Display Optimized Routes
    # -------------------------------
    
    cab_groups = final_route_df.groupby('Cab Group')
    for cab, members in cab_groups:
        print(f"\n🚕 Cab {cab} Pickup Order:")
        for _, row in members.sort_values('Pickup Order').iterrows():
            print(f"   {row['Pickup Order']}: {row['User']} - {row['Area']}")

    # -------------------------------
    # STEP 9: Export to Excel
    # -------------------------------
    
    output_file = os.path.join("Output", "cab_allocation_output.xlsx")
    os.makedirs("Output", exist_ok=True)
    final_route_df.to_excel(output_file, index=False)
    
    print(f"\n✅ Cab allocation and pickup order exported to {output_file}")

    # -------------------------------
    # STEP 10: Visualize Pickup Order on Map
    # -------------------------------
    
    # Create base map
    m = folium.Map(location=DESTINATION, zoom_start=12)
    
    # Add destination marker
    folium.Marker(location=DESTINATION, tooltip='Destination', icon=folium.Icon(color='black')).add_to(m)
    
    # Loop over each cab group
    for cab, members in final_route_df.groupby('Cab Group'):
        color = cab_colors[hash(f"Cab {cab}") % len(cab_colors)]
    
        # Sort by pickup order
        for _, row in members.sort_values('Pickup Order').iterrows():
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                tooltip=f"Pickup {row['Pickup Order']}: {row['User']} (Cab {cab}) - {row['Area']}",
                icon=folium.Icon(color=color, icon='user')
            ).add_to(m)
    
    # Save the map
    m.save(os.path.join("Output", "cab_routes_with_order.html"))
    print("\n✅ Map saved as cab_routes_with_order.html")

    return final_route_df, os.path.join("Output", "cab_routes.html")
