import pandas as pd
import geopandas as gpd
import folium

def create_folium_map(df_occurrences, center=[34.1, 74.6], zoom_start=8):
    m = folium.Map(location=center, zoom_start=zoom_start, tiles="CartoDB positron")
    # Ensure lat/lon are numeric and drop missing
    df_occurrences['lat'] = pd.to_numeric(df_occurrences['lat'], errors='coerce')
    df_occurrences['lon'] = pd.to_numeric(df_occurrences['lon'], errors='coerce')
    valid_df = df_occurrences.dropna(subset=['lat', 'lon'])

    for _, row in valid_df.iterrows():
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=4,
            color='green',
            fill=True,
            fill_opacity=0.6,
            popup=f"Genus: {row.get('genus', 'NA')}, Species: {row.get('species', 'NA')}"
        ).add_to(m)

    return m

def folium_map_to_html(m):
    return m.get_root().render()

def save_gdf(df_occurrences, filename="data/gbif_occurrences.gpkg"):
    gdf = gpd.GeoDataFrame(
        df_occurrences,
        geometry=gpd.points_from_xy(df_occurrences["lon"], df_occurrences["lat"]),
        crs="EPSG:4326"
    )
    gdf.to_file(filename, driver="GPKG")
