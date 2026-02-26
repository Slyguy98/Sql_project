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
search_term = st.sidebar.text_input("Search Game Title", "")
price_limit = st.sidebar.slider("Max Price ($)", 0, 100, 50)

# --- MAIN UI ---
st.title("🎮 Steam Intelligence Dashboard")
st.markdown("Analyzing **27,075** games via Relational Queries")

# 3. TABS FOR SELECT QUERIES
tab1, tab2, tab3, tab4 = st.tabs(["🔎 Live Search", "💰 Price Analysis", "⏳ Sustainability", "📈 Market Share"])

with tab1:
    st.subheader(f"Results for '{search_term}' (Under ${price_limit})")
    
    # Use %s placeholders for both Title and Price
    query = """
        SELECT title, developer, rating_pct, owners, price 
        FROM games 
        WHERE title ILIKE %s AND price <= %s 
        ORDER BY rating_pct DESC
    """
    
    # Pass the variables as a tuple in the correct order
    df = run_query(query, (f"%{search_term}%", price_limit))
    
    st.dataframe(df, use_container_width=True)

with tab2:
    st.subheader("Price vs. Approval")
    query = """
    SELECT 
        CASE 
            WHEN price = 0 THEN '0_Free'
            WHEN price <= 10 THEN '1_Low_0_10'
            WHEN price <= 20 THEN '2_Mid_10_20'
            ELSE '3_High_20_plus' 
        END as price_bracket,
        COUNT(*) as game_count,
        ROUND(AVG(rating_pct)::numeric, 2) as avg_approval
    FROM games
    WHERE (positive_ratings + negative_ratings) > 500
    GROUP BY price_bracket ORDER BY price_bracket ASC;
    """
    price_df = run_query(query)
    fig_price = px.bar(price_df, x='price_bracket', y='avg_approval', color='game_count', 
                       title="Average Approval Rating by Price Bracket", text_auto=True)
    fig_price.update_traces(
        hovertemplate="<b>%{x}</b><br>AVG Approval: %{y}%<extra></extra>"
    )
    st.plotly_chart(fig_price, use_container_width=True)

with tab3:
    st.subheader("Highest Playtime on Average")
    query = "SELECT title, developer, ROUND(average_playtime / 60.0, 1) as avg_hours FROM games WHERE average_playtime > 0 ORDER BY average_playtime DESC LIMIT 15"
    sust_df = run_query(query)
    fig_sust = px.bar(sust_df, x='avg_hours', y='title', orientation='h', title="Top Games by Average Hours Played")
    fig_sust.update_traces(
        hovertemplate="<b>%{y}</b><br>AVG: %{x}Hr<extra></extra>"
    )
    st.plotly_chart(fig_sust, use_container_width=True)

with tab4:
    st.subheader("Genre Dominance & Community Approval")
    
    # 1. Pull data from our optimized View
    query = "SELECT genre, total_games, approval_rating FROM genre_analysis"
    genre_df = run_query(query)
    
    # --- CHART 1: TOP 10 BY APPROVAL (BAR CHART) ---
    top_10_approval = genre_df.sort_values("approval_rating", ascending=False).head(10)
    
    fig_bar = px.bar(
        top_10_approval, 
        x='approval_rating', 
        y='genre', 
        orientation='h',
        title="Top 10 Rated Genres (Min. 50 Games)",
        color='approval_rating',
        color_continuous_scale='Viridis',
        labels={
            'approval_rating': 'Approval Rating (%)',
            'genre': 'Genre'
        }
    )
    
    
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
    fig_bar.update_traces(
        hovertemplate="<b>%{y}</b><br>AVG: %{x}%<extra></extra>"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # --- CHART 2: TOP 10 BY VOLUME (PIE CHART) ---
    top_10_volume = genre_df.sort_values("total_games", ascending=False).head(10)
    
    fig_genre = px.pie(
        top_10_volume, 
        values='total_games', 
        names='genre', 
        title="Market Share of Top 10 Genres (By Volume)",
        hole=0.3,
        hover_data=['approval_rating']
    )
    fig_genre.update_traces(
        hovertemplate="<b>%{label}</b><br>Total Games: %{value}<extra></extra>"
    )
    st.plotly_chart(fig_genre, use_container_width=True)

    # --- DATA TABLE ---
    st.markdown("### 🏆 Detailed Genre Statistics")
    
    # Create a copy of the sorted data to avoid modifying the original dataframe
    table_df = genre_df.sort_values(by="approval_rating", ascending=False).copy()

    # --- Renamed column headers for the table to match chart diction ---
    table_df = table_df.rename(columns={
        'genre': 'Genre',
        'total_games': 'Total Games',
        'approval_rating': 'Approval Rating (%)'
    })

    # .reset_index(drop=True) discards the old database row numbers (0, 15, 19, etc.) 
    # and replaces them with a fresh 0-based sequence.
    table_df = table_df.reset_index(drop=True)
    
    # Shift the index by +1 so the visible rank starts at 1 instead of 0.
    table_df.index = table_df.index + 1
    
    # Name the index 'Rank' so the first column header looks professional.
    table_df.index.name = 'Rank'

    st.dataframe(
        table_df,
        use_container_width=True
    )