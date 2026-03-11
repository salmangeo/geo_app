from flask import Flask, request, jsonify, render_template, session, send_from_directory
import os
import pandas as pd
from gbif_utils import fetch_all_genera_occurrences
from map_utils import create_folium_map, folium_map_to_html, save_gdf
from inat_utils import fetch_all_inat_occurrences
from climate_utils import calculate_climate_dataframe

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with a strong secret key

# Folder to save uploaded files and outputs
DATA_FOLDER = os.path.join(os.getcwd(), 'data')
os.makedirs(DATA_FOLDER, exist_ok=True)

# Store occurrences globally for demo (use DB in production)
stored_occurrences = pd.DataFrame()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    global stored_occurrences
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    try:
        df = pd.read_csv(file)
        genera = df['species'].dropna().unique().tolist()
        session['genera'] = genera
        stored_occurrences = pd.DataFrame()  # Clear old data on upload
        return jsonify({'status': 'File uploaded', 'genera_count': len(genera)})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/fetch_gbif', methods=['POST'])
def fetch_gbif():
    global stored_occurrences

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Bounding box not provided'})

    lat_min = data.get('lat_min')
    lat_max = data.get('lat_max')
    lon_min = data.get('lon_min')
    lon_max = data.get('lon_max')

    if None in [lat_min, lat_max, lon_min, lon_max]:
        return jsonify({'error': 'Invalid bounding box values'})

    limit = 200
    genera = session.get('genera', [])
    if not genera:
        return jsonify({'error': 'No genera found. Upload a CSV first.'})

    # Fetch GBIF
    gbif_df = fetch_all_genera_occurrences(
        genera, lat_min, lat_max, lon_min, lon_max, limit
    )
    gbif_df["source"] = "GBIF"

    # Fetch iNaturalist
    inat_df = fetch_all_inat_occurrences(
        genera, lat_min, lat_max, lon_min, lon_max, limit
    )

    # Combine
    combined_df = pd.concat([gbif_df, inat_df], ignore_index=True)

    # Remove duplicates
    combined_df.drop_duplicates(subset=["lat", "lon", "species"], inplace=True)

    stored_occurrences = combined_df

    return jsonify({'status': f'Fetched {len(stored_occurrences)} total records (GBIF + iNat)'})

@app.route('/save_csv', methods=['POST'])
def save_csv():
    global stored_occurrences
    if stored_occurrences is None or stored_occurrences.empty:
        return jsonify({'error': 'No data to save'})
    try:
        filepath = os.path.join(DATA_FOLDER, 'gbif_data_output.csv')
        stored_occurrences.to_csv(filepath, index=False)
        return jsonify({'status': 'CSV saved successfully', 'file': filepath})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/map')
def map_view():
    global stored_occurrences
    if stored_occurrences is None or stored_occurrences.empty:
        return "No data to display on map."
    m = create_folium_map(stored_occurrences)
    return folium_map_to_html(m)

@app.route('/data/<path:filename>')
def data_files(filename):
    return send_from_directory(DATA_FOLDER, filename, as_attachment=True)

@app.route('/get_points')
def get_points():
    global stored_occurrences
    if stored_occurrences is None or stored_occurrences.empty:
        return jsonify([])

    # Ensure clean numeric values
    df = stored_occurrences.copy()
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
    df = df.dropna(subset=['lat', 'lon'])

    points = df[['lat', 'lon', 'genus', 'species', 'source']].to_dict(orient='records')
    return jsonify(points)

@app.route("/calculate_climate")
def calculate_climate():

    global stored_occurrences

    if stored_occurrences is None:
        return jsonify([])

    df = stored_occurrences.copy()

    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")

    df = df.dropna(subset=["lat","lon"])

    climate_df = calculate_climate_dataframe(df.head(50))

    return jsonify(climate_df.to_dict(orient="records"))


if __name__ == '__main__':
    app.run()
