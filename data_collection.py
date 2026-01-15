import requests
import pandas as pd
import os
import time
import json

# CONFIGURATION

API_KEY = os.getenv("SPORTRADAR_API_KEY")
if not API_KEY:
    raise RuntimeError("❌ SPORTRADAR_API_KEY not set in environment variables")

BASE_URL = "https://api.sportradar.com/tennis/trial/v3/en"

DATA_DIR = "data"
MOCK_DIR = os.path.join(DATA_DIR, "sample_api")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MOCK_DIR, exist_ok=True)

HEADERS = {"accept": "application/json"}

# API REQUEST FUNCTION (SAFE)

def fetch_api_data(endpoint):
    url = f"{BASE_URL}/{endpoint}"
    params = {"api_key": API_KEY}

    response = requests.get(url, headers=HEADERS, params=params, timeout=15)

    # Route not available (trial API limitation)
    if response.status_code == 404:
        return None

    if response.status_code != 200:
        raise RuntimeError(
            f"❌ API failed for {endpoint} | "
            f"Status: {response.status_code} | Response: {response.text}"
        )

    return response.json()

# COMPETITIONS & CATEGORIES

def collect_competitions():
    print("📥 Fetching Competitions Data...")
    data = fetch_api_data("competitions.json")

    if not data or "competitions" not in data:
        raise RuntimeError("❌ Competitions data not available from API")

    categories_map = {}
    competitions = []

    for comp in data["competitions"]:
        category = comp.get("category", {})

        if category:
            categories_map[category["id"]] = {
                "category_id": category["id"],
                "category_name": category["name"]
            }

        competitions.append({
            "competition_id": comp.get("id"),
            "competition_name": comp.get("name"),
            "parent_id": comp.get("parent_id"),
            "type": comp.get("type"),
            "gender": comp.get("gender"),
            "category_id": category.get("id") if category else None
        })

    return (
        pd.DataFrame(categories_map.values()),
        pd.DataFrame(competitions)
    )

# COMPLEXES & VENUES

def collect_complexes_and_venues():
    print("📥 Fetching Complexes & Venues Data...")
    data = fetch_api_data("complexes.json")

    if not data or "complexes" not in data:
        raise RuntimeError("❌ Complexes data not available from API")

    complexes = []
    venues = []

    for complex_item in data["complexes"]:
        complexes.append({
            "complex_id": complex_item.get("id"),
            "complex_name": complex_item.get("name")
        })

        for venue in complex_item.get("venues", []):
            venues.append({
                "venue_id": venue.get("id"),
                "venue_name": venue.get("name"),
                "city_name": venue.get("city_name"),
                "country_name": venue.get("country_name"),
                "country_code": venue.get("country_code"),
                "timezone": venue.get("timezone"),
                "complex_id": complex_item.get("id")
            })

    return pd.DataFrame(complexes), pd.DataFrame(venues)

# DOUBLES COMPETITOR RANKINGS (HYBRID)

def collect_doubles_rankings():
    print("📥 Fetching Doubles Competitor Rankings...")

    data = fetch_api_data("doubles-competitor-rankings.json")

    if data is None:
        print("⚠ API route not available. Using mock doubles rankings data.")
        with open(os.path.join(MOCK_DIR, "doubles_rankings.json"), "r", encoding="utf-8") as f:
            data = json.load(f)

    competitors = []
    rankings = []

    for rank in data.get("rankings", []):
        competitor = rank.get("competitor", {})

        competitors.append({
            "competitor_id": competitor.get("id"),
            "name": competitor.get("name"),
            "country": competitor.get("country"),
            "country_code": competitor.get("country_code"),
            "abbreviation": competitor.get("abbreviation")
        })

        rankings.append({
            "rank": rank.get("rank"),
            "movement": rank.get("movement"),
            "points": rank.get("points"),
            "competitions_played": rank.get("competitions_played"),
            "competitor_id": competitor.get("id")
        })

    return pd.DataFrame(competitors), pd.DataFrame(rankings)

# DATA CLEANING FUNCTION ✅ (FIXED)

def clean_dataframe(df):
    if df is not None:
        df.drop_duplicates(inplace=True)
        df.fillna("NA", inplace=True)
    return df

# MAIN EXECUTION

def main():
    print("\n🚀 STARTING STEP 3: DATA COLLECTION\n")

    df_categories, df_competitions = collect_competitions()
    time.sleep(1)

    df_complexes, df_venues = collect_complexes_and_venues()
    time.sleep(1)

    df_competitors, df_rankings = collect_doubles_rankings()

    datasets = {
        "categories": df_categories,
        "competitions": df_competitions,
        "complexes": df_complexes,
        "venues": df_venues,
        "competitors": df_competitors,
        "rankings": df_rankings
    }

    for name, df in datasets.items():
        df = clean_dataframe(df)
        df.to_csv(os.path.join(DATA_DIR, f"{name}.csv"), index=False)
        print(f"✅ Saved {name}.csv | Rows: {len(df)}")

    print("\n🎯 COMPLETED SUCCESSFULLY")

# RUN

if __name__ == "__main__":
    main()
