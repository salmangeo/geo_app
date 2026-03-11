import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry


# -----------------------------------------
# Setup API client
# -----------------------------------------

cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)

openmeteo = openmeteo_requests.Client(session=retry_session)


# -----------------------------------------
# Query climate for ONE coordinate
# -----------------------------------------

def get_climate_for_point(lat, lon):

    url = "https://seasonal-api.open-meteo.com/v1/seasonal"

    params = {
        "latitude": lat,
        "longitude": lon,
        "monthly": [
            "temperature_max24h_2m_mean",
            "temperature_min24h_2m_mean",
            "precipitation_mean"
        ],
    }

    responses = openmeteo.weather_api(url, params=params)

    response = responses[0]

    monthly = response.Monthly()

    temp_max = monthly.Variables(0).ValuesAsNumpy()
    temp_min = monthly.Variables(1).ValuesAsNumpy()
    precip = monthly.Variables(2).ValuesAsNumpy()

    monthly_data = {
        "temp_max": temp_max,
        "temp_min": temp_min,
        "precip": precip
    }

    df = pd.DataFrame(monthly_data)

    return df.to_string()


# -----------------------------------------
# Apply to dataframe
# -----------------------------------------

def calculate_climate_dataframe(df):

    results = []

    df = df.head(5)   # only first 5 points

    for _, row in df.iterrows():

        lat = row["lat"]
        lon = row["lon"]
        species = row.get("species", "NA")

        try:

            climate_text = get_climate_for_point(lat, lon)

            print("------ CLIMATE RESULT ------")
            print(lat, lon)
            print(climate_text)

            results.append({
                "lat": lat,
                "lon": lon,
                "species": species,
                "result": climate_text
            })

        except Exception as e:

            results.append({
                "lat": lat,
                "lon": lon,
                "species": species,
                "result": str(e)
            })

    return pd.DataFrame(results)