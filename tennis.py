#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import pandas as pd
import altair as alt

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Tennis Data Explorer",
    page_icon="🎾",
    layout="wide"
)

# =========================
# LOAD DATA (CSV)
# =========================
@st.cache_data
def load_data():
    competitors = pd.read_csv("competitors.csv")
    rankings = pd.read_csv("competitor_rankings.csv")
    competitions = pd.read_csv("competitions.csv")
    categories = pd.read_csv("categories.csv")
    venues = pd.read_csv("venues.csv")

    df = (
        competitors
        .merge(rankings, on="competitor_id", how="left")
        .merge(competitions, on="competition_id", how="left")
        .merge(categories, on="category_id", how="left")
        .merge(venues, on="venue_id", how="left")
    )

    return df

df = load_data()

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
    sorted(df["category_name"].dropna().unique()),
    default=sorted(df["category_name"].dropna().unique())
)

ranking_movement = st.sidebar.radio(
    "📈 Ranking Movement",
    ["All", "Improving ⬆️", "Declining ⬇️", "Stable ➖"]
)

view_mode = st.sidebar.selectbox(
    "🧠 View Mode",
    ["Summary View", "Detailed View", "Analyst View"]
)

# =========================
# FILTER LOGIC (CORE)
# =========================
filtered_df = df.copy()

# Competition filter
filtered_df = filtered_df[filtered_df["category_name"].isin(competition_level)]

# Performance tier
if performance_tier == "Elite (Top 10)":
    filtered_df = filtered_df[filtered_df["rank"] <= 10]
elif performance_tier == "Strong (Top 50)":
    filtered_df = filtered_df[filtered_df["rank"] <= 50]
elif performance_tier == "Rising (Top 100)":
    filtered_df = filtered_df[filtered_df["rank"] <= 100]

# Ranking movement
if ranking_movement == "Improving ⬆️":
    filtered_df = filtered_df[filtered_df["movement"] > 0]
elif ranking_movement == "Declining ⬇️":
    filtered_df = filtered_df[filtered_df["movement"] < 0]
elif ranking_movement == "Stable ➖":
    filtered_df = filtered_df[filtered_df["movement"] == 0]

# =========================
# HOME PAGE
# =========================
if page == "🏠 Home Page":

    col_img, col_title = st.columns([1, 5])

    with col_img:
        st.image("tennis_banner.jpeg", width=200)

    with col_title:
        st.markdown("<h1 style='margin-bottom:0;'>Tennis Analytics Dashboard</h1>", unsafe_allow_html=True)
        st.caption("Interactive insights powered by Streamlit")

    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🎾 Competitors", filtered_df["competitor_id"].nunique())
    col2.metric("🌍 Countries", filtered_df["country"].nunique())
    col3.metric("🔥 Highest Points", int(filtered_df["points"].max()))
    col4.metric("🏟️ Venues", filtered_df["venue_id"].nunique())

    st.markdown("---")

    if view_mode != "Summary View":
        st.subheader("📌 Top 3 Most Active Categories")
        st.dataframe(
            filtered_df.groupby("category_name")
            .size()
            .reset_index(name="Competitions")
            .sort_values("Competitions", ascending=False)
            .head(3),
            use_container_width=True
        )

    st.subheader("🏅 Top 10 Players by Points")
    st.dataframe(
        filtered_df[["name", "rank", "points"]]
        .sort_values("points", ascending=False)
        .head(10),
        use_container_width=True
    )

    st.subheader("📊 Player Count by Category")
    chart = alt.Chart(
        filtered_df.groupby("category_name")
        .size()
        .reset_index(name="Players")
    ).mark_bar().encode(
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

    st.title("🔍 Search Competitors")

    player = st.selectbox("🧑 Player Name", ["All"] + sorted(filtered_df["name"].unique()))
    country = st.selectbox("🌍 Country", ["All"] + sorted(filtered_df["country"].dropna().unique()))
    rank_range = st.slider("🏅 Rank Range", 1, 1000, (1, 100))
    min_points = st.number_input("🔥 Minimum Points", value=0)

    temp = filtered_df.copy()

    if player != "All":
        temp = temp[temp["name"] == player]
    if country != "All":
        temp = temp[temp["country"] == country]

    temp = temp[
        (temp["rank"].between(rank_range[0], rank_range[1])) &
        (temp["points"] >= min_points)
    ]

    st.dataframe(
        temp[["name", "country", "rank", "points"]],
        use_container_width=True
    )

# =========================
# PLAYER DETAILS
# =========================
elif page == "🧑 Player Details":

    st.title("🧑 Player Details")
    player = st.selectbox("🎾 Select Player", sorted(filtered_df["name"].unique()))

    st.table(
        filtered_df[filtered_df["name"] == player][
            ["name", "country", "rank", "movement", "points"]
        ]
    )

# =========================
# COUNTRY ANALYSIS
# =========================
elif page == "🌍 Country Analysis":

    st.title("🌍 Country-Wise Analysis")

    st.dataframe(
        filtered_df.groupby("country")
        .agg(Competitors=("competitor_id", "nunique"), AvgPoints=("points", "mean"))
        .reset_index()
        .sort_values("Competitors", ascending=False),
        use_container_width=True
    )

# =========================
# LEADERBOARDS
# =========================
elif page == "🏆 Leaderboards":

    st.title("🏆 Leaderboards")

    st.subheader("🥇 Top Ranked Competitors")
    st.table(
        filtered_df.sort_values("rank").head(10)[["name", "country", "rank"]]
    )

    st.subheader("🔥 Highest Point Scorers")
    st.dataframe(
        filtered_df.sort_values("points", ascending=False).head(10)[["name", "country", "points"]],
        use_container_width=True
    )

    st.subheader("🎯 Categories with Highest Matches")
    st.dataframe(
        filtered_df.groupby("category_name").size().reset_index(name="Matches"),
        use_container_width=True
    )

    st.subheader("🌍 Countries with Most Competitors")
    st.dataframe(
        filtered_df.groupby("country")["competitor_id"].nunique().reset_index(name="Competitors"),
        use_container_width=True
    )
