import requests
import pandas as pd

def fetch_inat_genus_occurrences(genus, lat_min, lat_max, lon_min, lon_max, max_records=200):

    base_url = "https://api.inaturalist.org/v1/observations"

    params = {
        "taxon_name": genus,
        "swlat": lat_min,
        "swlng": lon_min,
        "nelat": lat_max,
        "nelng": lon_max,
        "quality_grade": "research",
        "per_page": 200,
        "page": 1
    }

    results = []

    while len(results) < max_records:
        response = requests.get(base_url, params=params)
        data = response.json()

        if not data.get("results"):
            break

        for obs in data["results"]:
            if obs.get("geojson") and obs.get("taxon"):
                results.append({
                    "genus": genus,
                    "lat": obs["geojson"]["coordinates"][1],
                    "lon": obs["geojson"]["coordinates"][0],
                    "species": obs["taxon"]["name"],
                    "elevation": None,
                    "country": None,
                    "eventDate": obs.get("observed_on"),
                    "source": "iNaturalist"
                })

        params["page"] += 1

    return pd.DataFrame(results)


def fetch_all_inat_occurrences(genera_list, lat_min, lat_max, lon_min, lon_max, limit_per_genus=200):
    all_occurrences = pd.DataFrame()

    for genus in genera_list:
        occ_df = fetch_inat_genus_occurrences(
            genus, lat_min, lat_max, lon_min, lon_max, limit_per_genus
        )
        all_occurrences = pd.concat([all_occurrences, occ_df], ignore_index=True)
        print(f"Collected {len(occ_df)} iNaturalist records for {genus}")

    print(f"Total iNaturalist records: {len(all_occurrences)}")
    return all_occurrences
