#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import pandas as pd
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

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Tennis Data Explorer",
    page_icon="🎾",
    layout="wide"
)

# =========================
# SIDEBAR
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
# HOME PAGE
# =========================
if page == "🏠 Home Page":

    col_img, col_title = st.columns([1, 5])

    with col_img:
        st.image("tennis_banner.jpeg", width=200)

    with col_title:
        st.markdown("<h1>Tennis Analytics Dashboard</h1>", unsafe_allow_html=True)
        st.caption("Interactive insights powered by Streamlit")

    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("🎾 Competitors", competitors.shape[0])
    c2.metric("🌍 Countries", competitors["country"].nunique())
    c3.metric("🔥 Highest Points", rankings["points"].max())
    c4.metric("🏟️ Venues", venues.shape[0])

    st.subheader("📌 Top 3 Most Active Categories")

    merged = competitions.merge(categories, on="category_id")
    top_cat = merged.groupby("category_name").size().reset_index(name="Competitions") \
                    .sort_values("Competitions", ascending=False).head(3)

    st.dataframe(top_cat, use_container_width=True)

    st.subheader("🏅 Top 10 Players by Points")

    top_players = competitors.merge(rankings, on="competitor_id") \
                             .sort_values("points", ascending=False).head(10)

    st.dataframe(top_players[["name", "rank", "points"]], use_container_width=True)

    st.subheader("📊 Player Count by Category")

    cat_players = merged.groupby("category_name").size().reset_index(name="Players")

    chart = alt.Chart(cat_players).mark_bar().encode(
        x="category_name",
        y="Players",
        tooltip=["category_name", "Players"],
        color="category_name"
    )

    st.altair_chart(chart, use_container_width=True)

# =========================
# SEARCH COMPETITORS
# =========================
elif page == "🔍 Search Competitors":

    players = ["All"] + sorted(competitors["name"].unique())
    countries = ["All"] + sorted(competitors["country"].dropna().unique())

    col1, col2 = st.columns(2)
    selected_player = col1.selectbox("🧑 Player", players)
    selected_country = col2.selectbox("🌍 Country", countries)

    rank_range = st.slider("🏅 Rank Range", 1, int(rankings["rank"].max()), (1, 100))
    min_points = st.number_input("🔥 Minimum Points", value=0)

    df = competitors.merge(rankings, on="competitor_id")

    if selected_player != "All":
        df = df[df["name"] == selected_player]

    if selected_country != "All":
        df = df[df["country"] == selected_country]

    df = df[
        (df["rank"].between(rank_range[0], rank_range[1])) &
        (df["points"] >= min_points)
    ]

    st.dataframe(df[["name", "country", "rank", "points"]], use_container_width=True)

# =========================
# PLAYER DETAILS
# =========================
elif page == "🧑 Player Details":

    player = st.selectbox("🎾 Select Player", sorted(competitors["name"].unique()))

    df = competitors.merge(rankings, on="competitor_id")
    df = df[df["name"] == player]

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

