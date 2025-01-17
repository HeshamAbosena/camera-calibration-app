import streamlit as st
import pandas as pd
import numpy as np
import ast
import plotly.graph_objects as go

def main():
    st.title("3D Vertex Visualizer for Camera Calibration")

    st.markdown("""**How to Use:** 1. Upload an Excel file containing XYZ coordinates for vehicle zones. 2. View the generated 3D wireframes for each zone. 3. Rotate, zoom, and inspect the geometry interactively.""")

    # File uploader
    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

    if uploaded_file:
        # Load the Excel file
        try:
            data = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Error reading the Excel file: {e}")
            return

        # Check if required columns exist
        if "Zone name" in data.columns and "Data points" in data.columns:
            st.success("File uploaded successfully!")

            # Parse and extract XYZ coordinates
            def parse_coordinates(data_point):
                try:
                    # Fixing the format of the coordinate string (space-separated to comma-separated)
                    formatted_data_point = data_point.replace(' ', ',')
                    return np.array(ast.literal_eval(formatted_data_point))
                except (ValueError, SyntaxError):
                    return np.nan

            data['Coordinates'] = data['Data points'].apply(parse_coordinates)

            # Identify rows with invalid or missing coordinates
            invalid_rows = data[data['Coordinates'].isna()]
            if not invalid_rows.empty:
                st.warning(f"Some rows have invalid or missing coordinates. Total: {len(invalid_rows)}")
                st.dataframe(invalid_rows)

            # Create a figure for all zones
            fig = go.Figure()

            # Iterate through zones and plot on the same axis
            for zone_name, zone_data in data.groupby(data['Zone name'].str.extract(r'(.*) Vertex')[0]):
                st.subheader(f"Zone: {zone_name}")

                # Filter valid coordinates
                coordinates = zone_data.dropna(subset=['Coordinates'])['Coordinates']

                if len(coordinates) == 4:  # We expect exactly 4 points for each zone
                    # Extract XYZ arrays
                    coords_array = np.vstack(coordinates)
                    X, Y, Z = coords_array[:, 0], coords_array[:, 1], coords_array[:, 2]

                    # Plot the points
                    fig.add_trace(go.Scatter3d(
                        x=X, y=Y, z=Z,
                        mode='markers',
                        name=f'{zone_name} Vertices',
                        marker=dict(size=5, color='red')
                    ))

                    # Draw wireframe (4 edges connecting the 4 points to form a closed shape)
                    # Edge 1: from point 1 to point 2
                    fig.add_trace(go.Scatter3d(
                        x=[X[0], X[1]], y=[Y[0], Y[1]], z=[Z[0], Z[1]],
                        mode='lines',
                        line=dict(color='blue', width=2),
                        name=f'{zone_name} Edge 1'
                    ))

                    # Edge 2: from point 2 to point 3
                    fig.add_trace(go.Scatter3d(
                        x=[X[1], X[2]], y=[Y[1], Y[2]], z=[Z[1], Z[2]],
                        mode='lines',
                        line=dict(color='blue', width=2),
                        name=f'{zone_name} Edge 2'
                    ))

                    # Edge 3: from point 3 to point 4
                    fig.add_trace(go.Scatter3d(
                        x=[X[2], X[3]], y=[Y[2], Y[3]], z=[Z[2], Z[3]],
                        mode='lines',
                        line=dict(color='blue', width=2),
                        name=f'{zone_name} Edge 3'
                    ))

                    # Edge 4: from point 4 to point 1 (to close the shape)
                    fig.add_trace(go.Scatter3d(
                        x=[X[3], X[0]], y=[Y[3], Y[0]], z=[Z[3], Z[0]],
                        mode='lines',
                        line=dict(color='blue', width=2),
                        name=f'{zone_name} Edge 4'
                    ))

                else:
                    st.warning(f"Not enough valid vertices to visualize {zone_name}. Only {len(coordinates)} valid vertices found.")
                    # Log problematic zone details
                    st.write(f"Zone: {zone_name}")
                    st.write(zone_data[['Zone name', 'Data points', 'Coordinates']])
