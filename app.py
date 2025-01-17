import streamlit as st
import pandas as pd
import numpy as np
import ast
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

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

            # Group by zone name
            zones = data.groupby(data['Zone name'].str.extract(r'(.*) Vertex')[0])

            # Visualize each zone
            for zone_name, zone_data in zones:
                st.subheader(f"Zone: {zone_name}")

                # Filter valid coordinates
                coordinates = zone_data.dropna(subset=['Coordinates'])['Coordinates']

                if len(coordinates) >= 3:
                    fig = plt.figure()
                    ax = fig.add_subplot(111, projection='3d')

                    # Extract XYZ arrays
                    coords_array = np.vstack(coordinates)
                    X, Y, Z = coords_array[:, 0], coords_array[:, 1], coords_array[:, 2]

                    # Plot the points and wireframe
                    ax.scatter(X, Y, Z, c='red', label='Vertices')
                    ax.plot(X, Y, Z, c='blue', label='Wireframe')
                    ax.plot([X[-1], X[0]], [Y[-1], Y[0]], [Z[-1], Z[0]], c='blue')  # Close loop

                    ax.set_xlabel('X')
                    ax.set_ylabel('Y')
                    ax.set_zlabel('Z')
                    ax.set_title(zone_name)
                    ax.legend()

                    st.pyplot(fig)
                else:
                    st.warning(f"Not enough valid vertices to visualize {zone_name}. Only {len(coordinates)} valid vertices found.")
                    # Log problematic zone details
                    st.write(f"Zone: {zone_name}")
                    st.write(zone_data[['Zone name', 'Data points', 'Coordinates']])
        else:
            st.error("The uploaded file does not contain the required columns ('Zone name' and 'Data points'). Please check your file.")

if __name__ == "__main__":
    main()
