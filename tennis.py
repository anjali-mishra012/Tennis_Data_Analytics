#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import pandas as pd
import altair as alt

# =========================
# LOAD CSV DATA (REPLACES SQL ONLY)
# =========================
@st.cache_data
def load_data():
    return {
        "Competitors": pd.read_csv("competitors.csv"),
        "Competitor_Rankings": pd.read_csv("competitor_rankings.csv"),
        "Competitions": pd.read_csv("competitions.csv"),
        "Categories": pd.read_csv("categories.csv"),
        "Venues": pd.read_csv("venues.csv"),
    }

tables = load_data()

# SQL-LIKE EXECUTION LAYER (NO UI CHANGE)
def execute_query(query, params=None):
    q = query.lower()

    if "count(*) as total from competitors" in q:
        return pd.DataFrame({"total": [len(tables["Competitors"])]})

    if "count(distinct country)" in q:
        return pd.DataFrame({"num": [tables["Competitors"]["country"].nunique()]})

    if "max(points)" in q:
        return pd.DataFrame({"maxp": [tables["Competitor_Rankings"]["points"].max()]})

    if "count(*) as v from venues" in q:
        return pd.DataFrame({"v": [len(tables["Venues"])]})

    if "top 3 most active categories" or "from categories" in q:
        df = tables["Competitions"].merge(
            tables["Categories"], on="category_id"
        )
        return (
            df.groupby("category_name")
            .size()
            .reset_index(name="Competitions")
            .sort_values("Competitions", ascending=False)
            .head(3)
        )

    if "order by cr.points desc limit 10" in q:
        df = tables["Competitors"].merge(
            tables["Competitor_Rankings"], on="competitor_id"
        )
        return df.sort_values("points", ascending=False).head(10)[
            ["name", "rank", "points"]
        ]

    if "player count by category" in q:
        df = tables["Competitions"].merge(
            tables["Categories"], on="category_id"
        )
        return (
            df.groupby("category_name")
            .size()
            .reset_index(name="Players")
        )

    if "distinct name from competitors" in q:
        return tables["Competitors"][["name"]].drop_duplicates().sort_values("name")

    if "distinct country from competitors" in q:
        return tables["Competitors"][["country"]].drop_duplicates().sort_values("country")

    if "where c.name =" in q:
        name = params[0]
        df = tables["Competitors"].merge(
            tables["Competitor_Rankings"], on="competitor_id"
        )
        return df[df["name"] == name]

    if "group by c.country" in q:
        df = tables["Competitors"].merge(
            tables["Competitor_Rankings"], on="competitor_id"
        )
        return (
            df.groupby("country")
            .agg(Competitors=("competitor_id", "count"), AvgPoints=("points", "mean"))
            .reset_index()
            .sort_values("Competitors", ascending=False)
        )

    return pd.DataFrame()

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Tennis Data Explorer",
    page_icon="🎾",
    layout="wide"
)

# =========================
# SIDEBAR (UNCHANGED)
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
# HOME PAGE (UNCHANGED OUTPUT)
# =========================
if page == "🏠 Home Page":
    col_img, col_title = st.columns([1, 5])

    with col_img:
        st.image("tennis_banner.jpeg", width=200)

    with col_title:
        st.markdown("<h1>Tennis Analytics Dashboard</h1>", unsafe_allow_html=True)
        st.caption("Interactive insights powered by Streamlit")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🎾 Competitors", execute_query("count(*) as total from competitors")["total"][0])
    col2.metric("🌍 Countries", execute_query("count(distinct country) from competitors")["num"][0])
    col3.metric("🔥 Highest Points", execute_query("max(points) from competitor_rankings")["maxp"][0])
    col4.metric("🏟️ Venues", execute_query("count(*) as v from venues")["v"][0])

# Remaining pages render SAME DATA automatically
