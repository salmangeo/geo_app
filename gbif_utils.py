import time
import pandas as pd
from pygbif import occurrences

def get_gbif_genus_occurrences(genus, lat_min, lat_max, lon_min, lon_max, limit=300):
    geometry = (
        f"POLYGON(({lon_min} {lat_min}, "
        f"{lon_min} {lat_max}, "
        f"{lon_max} {lat_max}, "
        f"{lon_max} {lat_min}, "
        f"{lon_min} {lat_min}))"
    )

    res = occurrences.search(
        scientificName=genus,
        hasCoordinate=True,
        geometry=geometry,
        limit=limit
    )

    if 'results' not in res:
        return pd.DataFrame()

    data = [
        {
            "genus": genus,
            "lat": r.get("decimalLatitude"),
            "lon": r.get("decimalLongitude"),
            "species": r.get("species"),
            "elevation": r.get("elevation"),
            "country": r.get("country"),
            "eventDate": r.get("eventDate")
        }
        for r in res['results']
        if r.get("decimalLatitude") and r.get("decimalLongitude")
    ]

    return pd.DataFrame(data)

def fetch_all_genera_occurrences(genera_list, lat_min, lat_max, lon_min, lon_max, limit_per_genus=200):
    all_occurrences = pd.DataFrame()
    for genus in genera_list:
        occ_df = get_gbif_genus_occurrences(genus, lat_min, lat_max, lon_min, lon_max, limit=limit_per_genus)
        all_occurrences = pd.concat([all_occurrences, occ_df], ignore_index=True)
        print(f"Collected {len(occ_df)} records for {genus}")
        time.sleep(1)  # To respect API rate limits
    print(f"Total records collected: {len(all_occurrences)}")
    return all_occurrences
