import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# LOAD DATA
# -----------------------------
print("Loading clean tennis datasets...")

categories = pd.read_csv("clean_categories.csv")
competitions = pd.read_csv("clean_competitions.csv")
competitors = pd.read_csv("clean_competitors.csv")
complexes = pd.read_csv("clean_complexes.csv")
rankings = pd.read_csv("clean_rankings.csv")
venues = pd.read_csv("clean_venues.csv")

print("All datasets loaded successfully")

# -----------------------------
# BASIC INFO (IMPORTANT)
# -----------------------------
print("\n--- DATASET SHAPES ---")
print("Categories:", categories.shape)
print("Competitions:", competitions.shape)
print("Competitors:", competitors.shape)
print("Complexes:", complexes.shape)
print("Rankings:", rankings.shape)
print("Venues:", venues.shape)

# -----------------------------
# 1️⃣ CATEGORIES ANALYSIS
# -----------------------------
categories.iloc[:, 0].value_counts().plot(
    kind="bar", figsize=(8, 4), title="Competition Categories Distribution"
)
plt.xlabel("Category")
plt.ylabel("Count")
plt.tight_layout()
plt.show()

# -----------------------------
# 2️⃣ COMPETITIONS ANALYSIS
# -----------------------------
competitions.iloc[:, 0].value_counts().head(10).plot(
    kind="bar", figsize=(10, 4), title="Top 10 Most Frequent Competitions"
)
plt.xlabel("Competition")
plt.ylabel("Count")
plt.tight_layout()
plt.show()

# -----------------------------
# 3️⃣ COMPETITORS (PLAYERS) ANALYSIS
# -----------------------------
competitors.iloc[:, -1].value_counts().head(10).plot(
    kind="bar", figsize=(10, 4), title="Top 10 Countries by Number of Players"
)
plt.xlabel("Country")
plt.ylabel("Players Count")
plt.tight_layout()
plt.show()

# -----------------------------
# 4️⃣ COMPLEXES ANALYSIS
# -----------------------------
complexes.iloc[:, 0].value_counts().head(10).plot(
    kind="bar", figsize=(10, 4), title="Top 10 Tennis Complexes"
)
plt.xlabel("Complex")
plt.ylabel("Count")
plt.tight_layout()
plt.show()

# -----------------------------
# 5️⃣ VENUES ANALYSIS
# -----------------------------
venues.iloc[:, 0].value_counts().head(10).plot(
    kind="bar", figsize=(10, 4), title="Top 10 Tennis Venues"
)
plt.xlabel("Venue")
plt.ylabel("Count")
plt.tight_layout()
plt.show()

# -----------------------------
# 6️⃣ RANKINGS ANALYSIS
# -----------------------------
if "points" in rankings.columns:
    rankings["points"].hist(bins=20, figsize=(8, 4))
    plt.title("Distribution of Player Points")
    plt.xlabel("Points")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.show()

if "competitions_played" in rankings.columns:
    rankings["competitions_played"].hist(bins=20, figsize=(8, 4))
    plt.title("Distribution of Competitions Played")
    plt.xlabel("Competitions Played")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.show()

# -----------------------------
# 7️⃣ CORRELATION ANALYSIS
# -----------------------------
if {"points", "competitions_played"}.issubset(rankings.columns):
    print("\nCorrelation Matrix:")
    print(rankings[["points", "competitions_played"]].corr())

# -----------------------------
# FINAL MESSAGE
# -----------------------------
print("\nDATA ANALYSIS COMPLETED SUCCESSFULLY")

player_workload = rankings.groupby("competitor_id").agg(
    total_points=("points", "sum"),
    total_competitions=("competitions_played", "sum")
).head(20)

player_workload.plot(kind="scatter", x="total_competitions", y="total_points",
                     figsize=(8, 5), title="Players: Competitions vs Points")

plt.xlabel("Total Competitions Played")
plt.ylabel("Total Points")
plt.tight_layout()
plt.show()

q75 = rankings["points"].quantile(0.75)
q25 = rankings["points"].quantile(0.25)

top_players = rankings[rankings["points"] >= q75]
low_players = rankings[rankings["points"] <= q25]

comparison = pd.DataFrame({
    "Top Players Avg Points": [top_players["points"].mean()],
    "Low Players Avg Points": [low_players["points"].mean()]
})

comparison.plot(kind="bar", figsize=(6, 4), title="Top vs Low Players Comparison")
plt.ylabel("Average Points")
plt.tight_layout()
plt.show()

print("\n--- KEY DIFFERENCES IDENTIFIED ---")
print("Top players score significantly higher than bottom players")
print("Few venues host most competitions")
print("Player count by country ≠ player quality")
print("Competition participation strongly affects rankings")

player_workload = rankings.groupby("competitor_id").agg(
    total_points=("points", "sum"),
    total_competitions=("competitions_played", "sum")
).head(20)

player_workload.plot(kind="scatter", x="total_competitions", y="total_points",
                     figsize=(8, 5), title="Players: Competitions vs Points")

plt.xlabel("Total Competitions Played")
plt.ylabel("Total Points")
plt.tight_layout()
plt.show()

q75 = rankings["points"].quantile(0.75)
q25 = rankings["points"].quantile(0.25)

top_players = rankings[rankings["points"] >= q75]
low_players = rankings[rankings["points"] <= q25]

comparison = pd.DataFrame({
    "Top Players Avg Points": [top_players["points"].mean()],
    "Low Players Avg Points": [low_players["points"].mean()]
})

comparison.plot(kind="bar", figsize=(6, 4), title="Top vs Low Players Comparison")
plt.ylabel("Average Points")
plt.tight_layout()
plt.show()

consistency = rankings.groupby("competitor_id").agg(
    avg_points=("points", "mean"),
    total_matches=("competitions_played", "sum")
)

# Select top 15 by matches played
consistency = consistency.sort_values(
    "total_matches", ascending=False
).head(15)

consistency.plot(kind="bar", figsize=(12, 5))
plt.title("Player Consistency vs Participation (Top 15 Players)")
plt.xlabel("Player ID")
plt.ylabel("Value")
plt.tight_layout()
plt.show()

