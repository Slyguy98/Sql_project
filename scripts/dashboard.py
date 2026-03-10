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

def format_steam_range(val):
    if not val or not isinstance(val, (int, float)): return "Unknown"
    if val >= 1_000_000: return f"{val/1_000_000:g}M+"
    if val >= 1_000: return f"{val/1_000:g}k+"
    return str(val)

with tab3:
    st.subheader("🏢 Publisher Impact & Sustainability")
    st.markdown("Analyzing market outcomes: How much Time and Money do these publishers actually use?")

    # 1. Fetch ALL data (no LIMIT in query so the table is complete)
    df_pub = run_query("SELECT * FROM publisher_outcomes")

    # --- TOP FILTERS (Affects Graphs only) ---
    st.markdown("### 🎯 Visual Focus")
    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        # This only limits the "Noise" in the graphs
        chart_limit = st.slider("Graph Focus: Top N Publishers", 5, 100, 25)
    with col_f2:
        selected_tiers = st.multiselect("Filter Graphs by Tier", 
                                       options=df_pub['market_tier'].unique(),
                                       default=df_pub['market_tier'].unique())

    # Create a separate dataframe just for the messy visuals
    df_visual = df_pub[df_pub['market_tier'].isin(selected_tiers)].head(chart_limit)

    # --- Summary Metrics (Uses Top 1 of the whole dataset) ---
    top_pub = df_pub.iloc[0]
    m1, m2, m3 = st.columns(3)
    m1.metric("Market Leader", top_pub['publisher'])
    m2.metric("Est. Top Revenue", f"${top_pub['total_revenue']:,.0f}")
    m3.metric("Avg. Engagement", f"{top_pub['engagement_score']} Hrs")

    # --- Visual Analysis Row (Uses df_visual) ---
    col1, col2 = st.columns(2)

    with col1:
        # Treemap: Market Dominance
        fig_whale = px.treemap(
            df_visual, 
            path=['market_tier', 'publisher'], 
            values='total_revenue',
            color='satisfaction_score',
            color_continuous_scale='RdYlGn',
            title=f"Market Dominance (Top {chart_limit})",
            labels={'satisfaction_score': 'Approval Rating', 'market_tier': 'Market Tier'},
            # This "backpack" carries only the 4 clean data points we want
            custom_data=['publisher', 'total_revenue', 'market_tier', 'satisfaction_score']
        )
        
        # 0=pub, 1=rev, 2=tier, 3=sat
        fig_whale.update_traces(
            hovertemplate="""
            <b>%{customdata[0]}</b><br>
            %{customdata[2]}<br>
            Revenue: $%{customdata[1]:,.0f}<br>
            Approval: %{customdata[3]}%
            <extra></extra>"""
        )
        st.plotly_chart(fig_whale, use_container_width=True)

    # Pre-calculate the display range for the "backpack"
    df_visual['display_range'] = df_visual['total_owners'].apply(format_steam_range)

    with col2:
        fig_stickiness = px.scatter(
            df_visual, # Use filtered data
            x="satisfaction_score", y="engagement_score",
            size="total_owners", color="market_tier", hover_name="publisher",
            # High-contrast colors: Orange, Purple, Red, Cyan, etc.
            color_discrete_sequence=px.colors.qualitative.G10,
            title="Quality vs. Engagement",
            labels={
                'satisfaction_score': 'Approval Rating (%)',
                'engagement_score': 'Avg. Engagement (Hrs)',
                'market_tier': 'Market Tier'
            },
            custom_data=['market_tier', 'satisfaction_score', 'engagement_score', 'display_range', 'publisher']
        )

        fig_stickiness.update_traces(
            hovertemplate="""
            <b>%{customdata[4]}</b><br>
            %{customdata[0]}<br>
            Satisfaction: %{customdata[1]}%<br>
            Engagement: %{customdata[2]} Hrs<br>
            Owners: %{customdata[3]}
            <extra></extra>"""
        )

        # Add Reference Lines (Market Averages)
        avg_eng = df_pub['engagement_score'].mean()
        avg_sat = df_pub['satisfaction_score'].mean()
        fig_stickiness.add_hline(y=avg_eng, line_dash="dot", opacity=0.5)
        fig_stickiness.add_vline(x=avg_sat, line_dash="dot", opacity=0.5)
        st.plotly_chart(fig_stickiness, use_container_width=True)

    # --- Detailed Data Table (Uses ALL data) ---
    st.markdown("---")
    st.markdown("### 📊 Complete Publisher Performance Index")
    st.markdown(f"Displaying all **{len(df_pub)}** active publishers in the database.")
    
    styled_df = df_pub.style.background_gradient(subset=['total_revenue'], cmap='Greens') \
                            .background_gradient(subset=['satisfaction_score'], cmap='RdYlGn')
    
    # Clean the Column Names (Remove underscores)
    df_display = df_pub.rename(columns={
        'publisher': 'Publisher',
        'total_titles': 'Total Titles',
        'total_owners': 'Total Owners',
        'total_revenue': 'Total Revenue',
        'engagement_score': 'Avg. Engagement',
        'satisfaction_score': 'Approval Rating',
        'market_tier': 'Market Tier'
    })

    # Fix the Index (Start at 1 instead of 0)
    df_display.index = df_display.index + 1
    df_display.index.name = 'Rank'

    # Apply formatting to remove those trailing zeros (*)
    styled_df = df_display.style.background_gradient(subset=['Total Revenue'], cmap='Greens') \
                                .background_gradient(subset=['Approval Rating'], cmap='RdYlGn') \
                                .format({
                                    'Total Owners': '{:,.0f}',
                                    'Total Revenue': '${:,.0f}',
                                    'Avg. Engagement': '{:.1f} Hrs',
                                    'Approval Rating': '{:.2f}%'
                                })

    st.dataframe(
        styled_df,
        use_container_width=True
    )

with tab4:
    st.subheader("Genre Dominance & Community Approval")
    
    # 1. Pull data from optimized View
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