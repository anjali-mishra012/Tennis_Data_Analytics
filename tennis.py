#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import altair as alt


# =========================
# LOAD CSV DATA 
# =========================
@st.cache_data
def load_data():
    competitors = pd.read_csv("competitors.csv")
    rankings = pd.read_csv("competitor_rankings.csv")
    competitions = pd.read_csv("competitions.csv")
    categories = pd.read_csv("categories.csv")
    venues = pd.read_csv("venues.csv")
    return competitors, rankings, competitions, categories, venues

competitors, rankings, competitions, categories, venues = load_data()

def execute_query(query, params=None):
    with engine.connect() as conn:
        return pd.read_sql(query, conn, params=params)

# =========================
# PAGE CONFIG (UI ONLY)
# =========================
st.set_page_config(
    page_title="Tennis Data Explorer",
    page_icon="🎾",
    layout="wide"
)

# =========================
# SIDEBAR (ENHANCED)
# =========================
st.sidebar.title("🎾 Tennis Data Explorer")

page = st.sidebar.selectbox(
    "📌 Navigate",
    [
        "🏠 Home Page",
        "🔍 Search Competitors",
        "🧑 Player Details",
        "🌍 Country Analysis",
        "🏆 Leaderboards"
    ]
)

st.sidebar.markdown("## 🎛️ Insight Controls")

# 1️⃣ Player Performance Tier
performance_tier = st.sidebar.selectbox(
    "🏅 Player Performance Tier",
    ["All Players", "Elite (Top 10)", "Strong (Top 50)", "Rising (Top 100)"]
)

# 2️⃣ Competition Level
competition_level = st.sidebar.multiselect(
    "🏟️ Competition Level",
    ["ITF Men", "ITF Women", "Challenger"],
    default=["ITF Men", "ITF Women"]
)

# 3️⃣ Ranking Movement
ranking_movement = st.sidebar.radio(
    "📈 Ranking Movement",
    ["All", "Improving ⬆️", "Declining ⬇️", "Stable ➖"]
)

# 4️⃣ Data View Mode
data_view = st.sidebar.selectbox(
    "🧠 View Mode",
    ["Summary View", "Detailed View", "Analyst View"]
)


# =========================
# HOME PAGE (FIXED + IMAGE)
# =========================

if page == "🏠 Home Page":

    # HEADER WITH IMAGE + TITLE
    col_img, col_title = st.columns([1, 5])

    with col_img:
        st.image("tennis_banner.jpeg", width=200)

    with col_title:
        st.markdown(
            "<h1 style='margin-bottom:0;'>Tennis Analytics Dashboard</h1>",
            unsafe_allow_html=True
        )
        st.caption("Interactive insights powered by SQL & Streamlit")

    st.markdown("---")

    # KPI CARDS  ✅ (THIS LINE WAS WRONG BEFORE)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_competitors = execute_query(
            "SELECT COUNT(*) AS total FROM Competitors"
        )["total"].iloc[0]
        st.metric("🎾 Competitors", total_competitors)

    with col2:
        countries = execute_query(
            "SELECT COUNT(DISTINCT country) AS num FROM Competitors"
        )["num"].iloc[0]
        st.metric("🌍 Countries", countries)

    with col3:
        max_points = execute_query(
            "SELECT MAX(points) AS maxp FROM Competitor_Rankings"
        )["maxp"].iloc[0]
        st.metric("🔥 Highest Points", max_points)

    with col4:
        total_venues = execute_query(
            "SELECT COUNT(*) AS v FROM Venues"
        )["v"].iloc[0]
        st.metric("🏟️ Venues", total_venues)

    st.markdown("---")

    st.subheader("📌 Top 3 Most Active Categories")
    most_active_categories = execute_query("""
        SELECT v.category_name AS Category,
               COUNT(competition_id) as Competitions
        FROM categories v
        JOIN competitions c
        ON v.category_id = c.category_id
        GROUP BY category_name
        ORDER BY COUNT(competition_id) DESC
        LIMIT 3
    """)
    st.dataframe(most_active_categories, use_container_width=True)

    st.subheader("🏅 Top 10 Players by Points")
    top_percent = execute_query("""
        SELECT c.name AS Competitor, 
               cr.Rank, 
               cr.Points
        FROM Competitors c
        JOIN Competitor_Rankings cr 
        ON c.competitor_id = cr.competitor_id
        ORDER BY cr.Points DESC
        LIMIT 10
    """)
    st.dataframe(top_percent, use_container_width=True)

    st.subheader("📊 Player Count by Category")
    category_df = execute_query("""
        SELECT cat.category_name AS Category, COUNT(*) AS Players
        FROM Competitions comp
        JOIN Categories cat ON comp.category_id = cat.category_id
        JOIN Competitor_Rankings cr ON cr.competitor_id IS NOT NULL
        GROUP BY cat.category_name
    """)

    chart = alt.Chart(category_df).mark_bar().encode(
        x='Category',
        y='Players',
        tooltip=['Category', 'Players'],
        color='Category'
    )
    st.altair_chart(chart, use_container_width=True)

elif page == "🔍 Search Competitors":
    st.title("🔍 Search Competitors")

    # --- Fetch dropdown values ---
    player_df = execute_query("SELECT DISTINCT name FROM Competitors ORDER BY name")
    country_df = execute_query("SELECT DISTINCT country FROM Competitors ORDER BY country")

    player_list = ["All"] + player_df["name"].tolist()
    country_list = ["All"] + country_df["country"].dropna().tolist()

    # --- Filters UI ---
    col1, col2 = st.columns(2)

    with col1:
        selected_player = st.selectbox("🧑 Player Name", player_list)

    with col2:
        selected_country = st.selectbox("🌍 Country", country_list)

    rank_range = st.slider("🏅 Rank Range", 1, 1000, (1, 100))
    min_points = st.number_input("🔥 Minimum Points", value=0)

    # --- Base query ---
    query = """
        SELECT c.Name, c.Country, cr.Rank, cr.Points
        FROM Competitors c
        JOIN Competitor_Rankings cr 
            ON c.competitor_id = cr.competitor_id
        WHERE cr.rank BETWEEN %s AND %s
          AND cr.points >= %s
    """
    params = [rank_range[0], rank_range[1], min_points]

    # --- Conditional filters ---
    if selected_player != "All":
        query += " AND c.name = %s"
        params.append(selected_player)

    if selected_country != "All":
        query += " AND c.country = %s"
        params.append(selected_country)

    query += " ORDER BY cr.Points DESC, cr.Rank ASC"

    df = execute_query(query, tuple(params))

    st.subheader(f"📋 Results ({len(df)} players found)")
    st.dataframe(df, use_container_width=True)



# =========================
# COMPETITOR DETAILS
# =========================
elif page == "🧑 Player Details":
    st.title("🧑 Player Details")

    competitors = execute_query(
        "SELECT name FROM Competitors ORDER BY name"
    )
    selected_name = st.selectbox(
        "🎾 Select Player",
        competitors['name'].tolist()
    )

    query = """
        SELECT c.Name, c.Country, cr.Rank, cr.Movement, cr.Points,
               cr.Competitions_played AS Competitions
        FROM Competitors c
        JOIN Competitor_Rankings cr 
        ON c.competitor_id = cr.competitor_id
        WHERE c.name = %s
    """
    df = execute_query(query, (selected_name,))
    st.table(df)

# =========================
# COUNTRY ANALYSIS
# =========================
elif page == "🌍 Country Analysis":
    st.title("🌍 Country-Wise Analysis")

    query = """
        SELECT c.Country, 
               COUNT(*) AS Competitors,
               AVG(cr.points) AS AvgPoints
        FROM Competitors c
        JOIN Competitor_Rankings cr 
        ON c.competitor_id = cr.competitor_id
        GROUP BY c.Country
        ORDER BY Competitors DESC
    """
    df = execute_query(query)
    st.dataframe(df, use_container_width=True)

# =========================
# LEADERBOARDS
# =========================
elif page == "🏆 Leaderboards":
    st.title("🏆 Leaderboards")

    st.subheader("🥇 Top Ranked Competitors")
    top_ranked = execute_query("""
        SELECT c.Name, c.Country, cr.Rank
        FROM Competitor_Rankings cr
        JOIN Competitors c 
        ON cr.competitor_id = c.competitor_id
        ORDER BY cr.rank ASC
        LIMIT 10
    """)
    st.table(top_ranked)

    st.subheader("🔥 Highest Point Scorers")
    top_points = execute_query("""
        SELECT c.Name, c.Country, cr.Points
        FROM Competitor_Rankings cr
        JOIN Competitors c 
        ON cr.competitor_id = c.competitor_id
        ORDER BY cr.points DESC
        LIMIT 10
    """)
    st.dataframe(top_points, use_container_width=True)

    st.subheader("🎯 Categories with Highest Matches")
    category_counts = execute_query("""
        SELECT cat.category_name AS Category, 
               COUNT(*) AS Matches
        FROM Competitions comp
        JOIN Categories cat 
        ON comp.category_id = cat.category_id
        GROUP BY cat.category_name
        ORDER BY Matches DESC
    """)
    st.dataframe(category_counts, use_container_width=True)

    st.subheader("🌍 Countries with Most Competitors")
    competitors = execute_query("""
        SELECT c.Country, 
               COUNT(c.competitor_id) AS Competitors
        FROM Competitors c
        GROUP BY c.Country
        ORDER BY COUNT(c.competitor_id) DESC
    """)
    st.dataframe(competitors, use_container_width=True)

