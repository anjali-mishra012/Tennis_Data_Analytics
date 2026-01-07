#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import pandas as pd
import altair as alt
from pandasql import sqldf

# =========================
# LOAD CSV DATA (NO CHANGE IN DATA)
# =========================
@st.cache_data
def load_data():
    Competitors = pd.read_csv("competitors.csv")
    Competitor_Rankings = pd.read_csv("competitor_rankings.csv")
    Competitions = pd.read_csv("competitions.csv")
    Categories = pd.read_csv("categories.csv")
    Venues = pd.read_csv("venues.csv")
    return Competitors, Competitor_Rankings, Competitions, Categories, Venues

Competitors, Competitor_Rankings, Competitions, Categories, Venues = load_data()

# SQL executor (keeps ALL your SQL unchanged)
def execute_query(query, params=None):
    return sqldf(query, globals())

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

performance_tier = st.sidebar.selectbox(
    "🏅 Player Performance Tier",
    ["All Players", "Elite (Top 10)", "Strong (Top 50)", "Rising (Top 100)"]
)

competition_level = st.sidebar.multiselect(
    "🏟️ Competition Level",
    ["ITF Men", "ITF Women", "Challenger"],
    default=["ITF Men", "ITF Women"]
)

ranking_movement = st.sidebar.radio(
    "📈 Ranking Movement",
    ["All", "Improving ⬆️", "Declining ⬇️", "Stable ➖"]
)

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
        st.markdown("<h1 style='margin-bottom:0;'>Tennis Analytics Dashboard</h1>", unsafe_allow_html=True)
        st.caption("Interactive insights powered by CSV & Streamlit")

    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🎾 Competitors", len(Competitors))

    with col2:
        st.metric("🌍 Countries", Competitors["country"].nunique())

    with col3:
        st.metric("🔥 Highest Points", Competitor_Rankings["points"].max())

    with col4:
        st.metric("🏟️ Venues", len(Venues))

    st.markdown("---")

    st.subheader("📌 Top 3 Most Active Categories")
    most_active_categories = execute_query("""
        SELECT c.category_name AS Category, COUNT(*) AS Competitions
        FROM Competitions comp
        JOIN Categories c ON comp.category_id = c.category_id
        GROUP BY c.category_name
        ORDER BY COUNT(*) DESC
        LIMIT 3
    """)
    st.dataframe(most_active_categories, use_container_width=True)

    st.subheader("🏅 Top 10 Players by Points")
    top_players = execute_query("""
        SELECT c.name AS Competitor, r.rank, r.points
        FROM Competitors c
        JOIN Competitor_Rankings r ON c.competitor_id = r.competitor_id
        ORDER BY r.points DESC
        LIMIT 10
    """)
    st.dataframe(top_players, use_container_width=True)

    st.subheader("📊 Player Count by Category")
    category_df = execute_query("""
        SELECT cat.category_name AS Category, COUNT(*) AS Players
        FROM Competitions comp
        JOIN Categories cat ON comp.category_id = cat.category_id
        GROUP BY cat.category_name
    """)

    chart = alt.Chart(category_df).mark_bar().encode(
        x="Category",
        y="Players",
        tooltip=["Category", "Players"],
        color="Category"
    )
    st.altair_chart(chart, use_container_width=True)

# =========================
# SEARCH COMPETITORS
# =========================
elif page == "🔍 Search Competitors":

    player_list = ["All"] + sorted(Competitors["name"].dropna().unique().tolist())
    country_list = ["All"] + sorted(Competitors["country"].dropna().unique().tolist())

    col1, col2 = st.columns(2)
    with col1:
        selected_player = st.selectbox("🧑 Player Name", player_list)
    with col2:
        selected_country = st.selectbox("🌍 Country", country_list)

    rank_range = st.slider("🏅 Rank Range", 1, 1000, (1, 100))
    min_points = st.number_input("🔥 Minimum Points", value=0)

    df = execute_query("""
        SELECT c.name, c.country, r.rank, r.points
        FROM Competitors c
        JOIN Competitor_Rankings r ON c.competitor_id = r.competitor_id
    """)

    if selected_player != "All":
        df = df[df["name"] == selected_player]
    if selected_country != "All":
        df = df[df["country"] == selected_country]

    df = df[
        (df["rank"].between(rank_range[0], rank_range[1])) &
        (df["points"] >= min_points)
    ]

    st.dataframe(df, use_container_width=True)

# =========================
# PLAYER DETAILS
# =========================
elif page == "🧑 Player Details":

    selected_name = st.selectbox("🎾 Select Player", sorted(Competitors["name"].unique()))

    df = execute_query(f"""
        SELECT c.name, c.country, r.rank, r.points
        FROM Competitors c
        JOIN Competitor_Rankings r ON c.competitor_id = r.competitor_id
        WHERE c.name = '{selected_name}'
    """)
    st.table(df)

# =========================
# COUNTRY ANALYSIS
# =========================
elif page == "🌍 Country Analysis":

    df = execute_query("""
        SELECT c.country, COUNT(*) AS Competitors, AVG(r.points) AS AvgPoints
        FROM Competitors c
        JOIN Competitor_Rankings r ON c.competitor_id = r.competitor_id
        GROUP BY c.country
        ORDER BY Competitors DESC
    """)
    st.dataframe(df, use_container_width=True)

# =========================
# LEADERBOARDS
# =========================
elif page == "🏆 Leaderboards":

    st.subheader("🥇 Top Ranked Competitors")
    st.table(execute_query("""
        SELECT c.name, c.country, r.rank
        FROM Competitors c
        JOIN Competitor_Rankings r ON c.competitor_id = r.competitor_id
        ORDER BY r.rank ASC
        LIMIT 10
    """))

    st.subheader("🔥 Highest Point Scorers")
    st.dataframe(execute_query("""
        SELECT c.name, c.country, r.points
        FROM Competitors c
        JOIN Competitor_Rankings r ON c.competitor_id = r.competitor_id
        ORDER BY r.points DESC
        LIMIT 10
    """), use_container_width=True)

