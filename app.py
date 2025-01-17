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

                if len(coordinates) >= 3:
                    # Extract XYZ arrays
                    coords_array = np.vstack(coordinates)
                    X, Y, Z = coords_array[:, 0], coords_array[:, 1], coords_array[:, 2]

                    # Plot the points and wireframe
                    fig.add_trace(go.Scatter3d(
                        x=X, y=Y, z=Z,
                        mode='markers+lines',
                        name=f'{zone_name} Wireframe',
                        marker=dict(size=5, color='red'),
                        line=dict(color='blue', width=2)
                    ))

                else:
                    st.warning(f"Not enough valid vertices to visualize {zone_name}. Only {len(coordinates)} valid vertices found.")
                    # Log problematic zone details
                    st.write(f"Zone: {zone_name}")
                    st.write(zone_data[['Zone name', 'Data points', 'Coordinates']])

            # Customize the plot layout
            fig.update_layout(
                scene=dict(
                    xaxis_title='X',
                    yaxis_title='Y',
                    zaxis_title='Z'
                ),
                title="All Zones Visualized Together",
                legend=dict(
                    x=1.05,  # Adjusted to move legend slightly further right
                    y=1,
                    traceorder="normal",
                    font=dict(size=10),
                    borderwidth=1
                ),
                margin=dict(r=0, l=0, b=0, t=40),
                autosize=True
            )

            # Show the interactive plot in Streamlit
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("The uploaded file does not contain the required columns ('Zone name' and 'Data points'). Please check your file.")

if __name__ == "__main__":
    main()