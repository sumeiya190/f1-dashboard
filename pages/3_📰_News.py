"""
F1 News Feed Page
Latest F1 news, updates, and articles
"""

import streamlit as st
import feedparser
import requests
from datetime import datetime
import pandas as pd

st.set_page_config(
    page_title="F1 News - F1 Dashboard",
    page_icon="📰",
    layout="wide"
)

st.title("📰 F1 News & Updates")
st.markdown("Latest Formula 1 news from around the web")

# News source selection
st.sidebar.header("📡 News Sources")

sources = st.sidebar.multiselect(
    "Select Sources",
    ["Formula1.com", "BBC Sport F1", "Autosport", "The Race"],
    default=["Formula1.com", "BBC Sport F1"]
)

# Refresh button
if st.sidebar.button("🔄 Refresh News", type="primary"):
    st.cache_data.clear()
    st.rerun()

# News feeds dictionary
NEWS_FEEDS = {
    "Formula1.com": "https://www.formula1.com/content/fom-website/en/latest/all.xml",
    "BBC Sport F1": "https://feeds.bbci.co.uk/sport/formula1/rss.xml",
    "Autosport": "https://www.autosport.com/rss/feed/f1",
    "The Race": "https://the-race.com/feed/"
}

@st.cache_data(ttl=600)  # Cache for 10 minutes
def fetch_news(source_name, feed_url):
    """Fetch news from RSS feed"""
    try:
        feed = feedparser.parse(feed_url)
        articles = []
        
        for entry in feed.entries[:10]:  # Get top 10 articles
            # Parse published date
            pub_date = None
            if hasattr(entry, 'published_parsed'):
                pub_date = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed'):
                pub_date = datetime(*entry.updated_parsed[:6])
            
            # Get summary
            summary = entry.get('summary', entry.get('description', 'No description available'))
            # Clean HTML tags from summary
            import re
            summary = re.sub('<[^<]+?>', '', summary)
            summary = summary[:200] + '...' if len(summary) > 200 else summary
            
            articles.append({
                'title': entry.get('title', 'No title'),
                'link': entry.get('link', '#'),
                'published': pub_date,
                'summary': summary,
                'source': source_name
            })
        
        return articles
    except Exception as e:
        st.error(f"Error fetching from {source_name}: {str(e)}")
        return []

# Fetch news from selected sources
all_articles = []

with st.spinner("Loading latest F1 news..."):
    for source in sources:
        if source in NEWS_FEEDS:
            articles = fetch_news(source, NEWS_FEEDS[source])
            all_articles.extend(articles)

# Sort by date (most recent first)
all_articles.sort(key=lambda x: x['published'] if x['published'] else datetime.min, reverse=True)

# Display news
if all_articles:
    st.success(f"📰 Found {len(all_articles)} recent articles")
    
    # Filter by date
    st.sidebar.markdown("---")
    st.sidebar.subheader("🗓️ Filter by Date")
    
    date_filter = st.sidebar.radio(
        "Show articles from:",
        ["Today", "Last 24 hours", "Last 3 days", "Last week", "All"],
        index=2
    )
    
    # Apply date filter
    now = datetime.now()
    filtered_articles = []
    
    for article in all_articles:
        if article['published']:
            age = now - article['published']
            
            if date_filter == "Today" and age.days == 0:
                filtered_articles.append(article)
            elif date_filter == "Last 24 hours" and age.total_seconds() <= 86400:
                filtered_articles.append(article)
            elif date_filter == "Last 3 days" and age.days <= 3:
                filtered_articles.append(article)
            elif date_filter == "Last week" and age.days <= 7:
                filtered_articles.append(article)
            elif date_filter == "All":
                filtered_articles.append(article)
    
    if not filtered_articles:
        filtered_articles = all_articles  # Show all if filter returns nothing
    
    # Search functionality
    st.sidebar.markdown("---")
    search_query = st.sidebar.text_input("🔍 Search articles", "")
    
    if search_query:
        filtered_articles = [
            article for article in filtered_articles
            if search_query.lower() in article['title'].lower() or 
               search_query.lower() in article['summary'].lower()
        ]
    
    # Display articles
    st.markdown(f"### Showing {len(filtered_articles)} articles")
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["📰 Article Feed", "📊 News Summary"])
    
    with tab1:
        # Display articles in cards
        for idx, article in enumerate(filtered_articles):
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"### [{article['title']}]({article['link']})")
                    
                    # Date and source
                    date_str = article['published'].strftime('%B %d, %Y at %I:%M %p') if article['published'] else 'Date unknown'
                    st.caption(f"🕐 {date_str} | 📡 {article['source']}")
                    
                    # Summary
                    st.markdown(article['summary'])
                
                with col2:
                    st.link_button("Read More →", article['link'], use_container_width=True)
                
                st.markdown("---")
    
    with tab2:
        st.subheader("📊 News Statistics")
        
        # Articles by source
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Articles by Source**")
            source_counts = {}
            for article in filtered_articles:
                source = article['source']
                source_counts[source] = source_counts.get(source, 0) + 1
            
            source_df = pd.DataFrame(list(source_counts.items()), columns=['Source', 'Count'])
            st.dataframe(source_df, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("**Recent Activity**")
            
            # Count articles by day
            daily_counts = {}
            for article in filtered_articles:
                if article['published']:
                    date_key = article['published'].strftime('%Y-%m-%d')
                    daily_counts[date_key] = daily_counts.get(date_key, 0) + 1
            
            if daily_counts:
                daily_df = pd.DataFrame(list(daily_counts.items()), columns=['Date', 'Articles'])
                daily_df = daily_df.sort_values('Date', ascending=False)
                st.dataframe(daily_df, use_container_width=True, hide_index=True)
        
        # Most recent article
        st.markdown("---")
        st.subheader("🔥 Latest Update")
        
        if filtered_articles:
            latest = filtered_articles[0]
            st.info(f"**{latest['title']}**\n\n{latest['summary']}")
            st.link_button("Read Full Article", latest['link'])

else:
    st.warning("No articles found. Try selecting different news sources or check your internet connection.")

# Footer with news source info
st.markdown("---")
st.markdown("### 📡 News Sources")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Formula1.com**  
    Official F1 news and updates
    
    **BBC Sport F1**  
    Comprehensive F1 coverage and analysis
    """)

with col2:
    st.markdown("""
    **Autosport**  
    In-depth motorsport journalism
    
    **The Race**  
    Expert F1 commentary and features
    """)

st.caption("💡 News is refreshed every 10 minutes. Click 'Refresh News' to update manually.")
