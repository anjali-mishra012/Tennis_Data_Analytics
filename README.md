# Tennis Data Analytics

This repository contains code and analysis for extracting, storing, and analyzing Tennis competition data using the Sportradar API.  
The project focuses on SQL-based analysis and an interactive Streamlit dashboard for exploring tennis competitions, venues, and player rankings.


## Problem Statement

The *SportRadar Event Explorer* project aims to build a complete data analytics solution for Tennis data by:

- Extracting competition data from the Sportradar API
- Transforming complex JSON responses into structured tabular data
- Storing data in a relational SQL database
- Performing analytical queries using SQL
- Visualizing insights using an interactive Streamlit dashboard

This project helps analysts and sports enthusiasts understand competition structures, venues, and player performance.


## Data Extraction

- Parsed and extracted data from *Sportradar API JSON responses*
- Converted nested JSON structures into flat relational tables
- Cleaned and prepared data for analysis

## Data Storage

- Designed a *SQL relational database*
- Defined appropriate:
  - Primary keys
  - Foreign keys
  - Data types
- Stored extracted data into structured tables


## Tables Used

- Categories  
- Competitions  
- Complexes  
- Venues  
- Competitor_Rankings  
- Competitors  


## Build a Streamlit Application

- Connected Streamlit app with the SQL database / CSV data
- Executed queries dynamically
- Displayed outputs using:
  - Tables
  - Charts
  - Dashboards
- Added interactive filters for:
  - Competition types
  - Competition levels
  - Categories

## Data Analysis Using SQL

The following analytical questions were implemented:

1. List all competitions along with their category name  
2. Count the number of competitions in each category  
3. Find all competitions of type *doubles*  
4. Get competitions that belong to a specific category (e.g., ITF Men)  
5. Identify parent competitions and their sub-competitions  
6. Analyze the distribution of competition types by category  
7. List all competitions with no parent (top-level competitions)  
8. List all venues along with their associated complex name  
9. Count the number of venues in each complex  
10. Get details of venues in a specific country (e.g., Chile)  
11. Identify all venues and their timezones  
12. Find complexes that have more than one venue  
13. List venues grouped by country  
14. Find all venues for a specific complex (e.g., Nacional)  
15. Get all competitors with their rank and points  
16. Find competitors ranked in the top 5  
17. List competitors with no rank movement (stable rank)  
18. Get the total points of competitors from a specific country (e.g., Croatia)  
19. Count the number of competitors per country  
20. Find competitors with the highest points in the current week  

## Technologies Used

- Python  
- SQL    
- Streamlit    
- GitHub  


## Project Outcome

- Built a complete end-to-end data analytics pipeline
- Performed real-world SQL analysis on sports data
- Developed an interactive Streamlit dashboard for insights
- Successfully analyzed Tennis competition and player performance data
