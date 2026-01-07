#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import pandas as pd
import altair as alt
import os

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Tennis Data Explorer",
    page_icon="🎾",
    layout="wide"
)

# =========================
# LOAD CSV DATA
# =========================
@st.cache_data
def load_data():
    competitors = pd.read_csv("competitors.csv")
    rankings = pd.read_csv("competitor_rankings.csv")
    categories = pd.read_csv("categories.csv")
    competitions = pd.read_csv("competitions.csv")
    venues = pd.read_csv("venues.csv")
    return competitors, rankings, categories, competitions, venues

competitors, rankings, categories, competitions, venues = load_data()

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

# =========================
# HOME PAGE
# =========================
if page == "🏠 Home Page":

    col_img, col_title = st.columns([1, 5])

    with col_img:
        if os.path.exists("tennis_banner.jpeg"):
            st.image("tennis_banner.jpeg", width=200)

    with col_title:
        st.markdown(
            "<h1 style='margin-bottom:0;'>Tennis Analytics Dashboard</h1>",
            unsafe_allow_html=True
        )
        st.caption("Interactive insights powered by CSV & Streamlit")

    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🎾 Competitors", competitors.shape[0])

    with col2:
        st.metric("🌍 Countries", competitors["country"].nunique())

    with col3:
        st.metric("🔥 Highest Points", rankings["points"].max())

    with col4:
        st.metric("🏟️ Venues", venues.shape[0])

    st.markdown("---")

    st.subheader("📌 Top 3 Most Active Categories")

    cat_counts = (
        competitions.merge(categories, on="category_id")
        .groupby("category_name")
        .size()
        .reset_index(name="Competitions")
        .sort_values("Competitions", ascending=False)
        .head(3)
    )

    st.dataframe(cat_counts, use_container_width=True)

    st.subheader("🏅 Top 10 Players by Points")

    top_players = (
        rankings.merge(competitors, on="competitor_id")
        .sort_values("points", ascending=False)
        .head(10)[["name", "rank", "points"]]
    )

    st.dataframe(top_players, use_container_width=True)

    st.subheader("📊 Player Count by Category")

    category_df = (
        competitions.merge(categories, on="category_id")
        .groupby("category_name")
        .size()
        .reset_index(name="Players")
    )

    chart = alt.Chart(category_df).mark_bar().encode(
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

    player = st.selectbox("🧑 Player Name", ["All"] + sorted(competitors["name"].tolist()))
    country = st.selectbox("🌍 Country", ["All"] + sorted(competitors["country"].dropna().unique().tolist()))
    rank_range = st.slider("🏅 Rank Range", 1, 1000, (1, 100))
    min_points = st.number_input("🔥 Minimum Points", value=0)

    df = rankings.merge(competitors, on="competitor_id")

    df = df[
        (df["rank"].between(rank_range[0], rank_range[1])) &
        (df["points"] >= min_points)
    ]

    if player != "All":
        df = df[df["name"] == player]

    if country != "All":
        df = df[df["country"] == country]

    st.dataframe(
        df[["name", "country", "rank", "points"]].sort_values("points", ascending=False),
        use_container_width=True
    )

# =========================
# PLAYER DETAILS
# =========================
elif page == "🧑 Player Details":

    st.title("🧑 Player Details")

    selected = st.selectbox("🎾 Select Player", sorted(competitors["name"].tolist()))

    df = rankings.merge(competitors, on="competitor_id")
    st.table(df[df["name"] == selected])

# =========================
# COUNTRY ANALYSIS
# =========================
elif page == "🌍 Country Analysis":

    st.title("🌍 Country Analysis")

    df = (
        rankings.merge(competitors, on="competitor_id")
        .groupby("country")
        .agg(
            Competitors=("competitor_id", "count"),
            AvgPoints=("points", "mean")
        )
        .reset_index()
        .sort_values("Competitors", ascending=False)
    )

    st.dataframe(df, use_container_width=True)

# =========================
# LEADERBOARDS
# =========================
elif page == "🏆 Leaderboards":

    st.title("🏆 Leaderboards")

    st.subheader("🥇 Top Ranked Players")
    st.table(
        rankings.merge(competitors, on="competitor_id")
        .sort_values("rank")
        .head(10)[["name", "country", "rank"]]
    )

    st.subheader("🔥 Highest Point Scorers")
    st.dataframe(
        rankings.merge(competitors, on="competitor_id")
        .sort_values("points", ascending=False)
        .head(10)[["name", "country", "points"]],
        use_container_width=True
    )
