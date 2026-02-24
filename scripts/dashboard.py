import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

# 1. Page Config
st.set_page_config(page_title="Steam Market Intelligence", layout="wide", page_icon="📊")

# 2. Secure Connection Function
def run_query(query, params=None):
    conn = psycopg2.connect(
        database="postgres", user="postgres", password="postgres", host="localhost", port="5432"
    )
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Global Filters")
search_term = st.sidebar.text_input("Search Game Title", "Monster Hunter")
price_limit = st.sidebar.slider("Max Price ($)", 0, 100, 60)

# --- MAIN UI ---
st.title("🎮 Steam Intelligence Dashboard")
st.markdown("Analyzing **27,075** games via Relational PostgreSQL")

# 3. TABS FOR YOUR 4 POWER QUERIES
tab1, tab2, tab3, tab4 = st.tabs(["🔎 Live Search", "💰 Price Analysis", "⏳ Sustainability", "📈 Market Share"])

with tab1:
    st.subheader(f"Results for '{search_term}' (Under ${price_limit})")
    
    # Use %s placeholders for both Title and Price
    query = """
        SELECT title, developer, positive_ratings, owners, price 
        FROM games 
        WHERE title ILIKE %s 
        AND price <= %s 
        ORDER BY positive_ratings DESC
    """
    
    # Pass the variables as a tuple in the correct order
    df = run_query(query, (f"%{search_term}%", price_limit))
    
    st.dataframe(df, use_container_width=True)

with tab2:
    st.subheader("The 'Sweet Spot': Price vs. Approval")
    # This is your "Prompt #2" from the terminal!
    query = """
    SELECT 
        CASE 
            WHEN price = 0 THEN '0_Free'
            WHEN price <= 10 THEN '1_Low_0_10'
            WHEN price <= 20 THEN '2_Mid_10_20'
            ELSE '3_High_20_plus' 
        END as price_bracket,
        COUNT(*) as game_count,
        ROUND(AVG(positive_ratings::float / (positive_ratings + negative_ratings) * 100)::numeric, 2) as avg_approval
    FROM games
    WHERE (positive_ratings + negative_ratings) > 500
    GROUP BY price_bracket ORDER BY price_bracket ASC;
    """
    price_df = run_query(query)
    fig_price = px.bar(price_df, x='price_bracket', y='avg_approval', color='game_count', 
                       title="Average Approval Rating by Price Bracket", text_auto=True)
    st.plotly_chart(fig_price, use_container_width=True)

with tab3:
    st.subheader("The 'Stickiest' Games (High Playtime)")
    # This is your "Prompt #3" from the terminal!
    query = "SELECT title, developer, ROUND(average_playtime / 60.0, 1) as avg_hours FROM games WHERE average_playtime > 0 ORDER BY average_playtime DESC LIMIT 15"
    sust_df = run_query(query)
    fig_sust = px.bar(sust_df, x='avg_hours', y='title', orientation='h', title="Top Games by Average Hours Played")
    st.plotly_chart(fig_sust, use_container_width=True)

with tab4:
    st.subheader("Genre Dominance (The Bridge Table)")
    # This is your "Prompt #4" from the terminal using the game_genres bridge!
    query = """
    SELECT gn.genre_name, COUNT(gg.appid) as total_games
    FROM genres gn
    JOIN game_genres gg ON gn.genre_id = gg.genre_id
    GROUP BY gn.genre_name ORDER BY total_games DESC LIMIT 10
    """
    genre_df = run_query(query)
    fig_genre = px.pie(genre_df, values='total_games', names='genre_name', title="Market Share of Top 10 Genres")
    st.plotly_chart(fig_genre, use_container_width=True)