import streamlit as st
import pandas as pd

from database import get_connection
from pipeline import run_pipeline

st.set_page_config(page_title="AI News Sentiment Dashboard")

st.title("📰 AI News Sentiment Dashboard")

if st.button("🔄 Refresh News"):
    run_pipeline()
    st.success("Pipeline Updated Successfully!")

conn = get_connection()

query = """
SELECT
r.title,
r.source,
s.sentiment_label,
s.confidence_score,
p.word_count

FROM raw_articles r

JOIN processed_articles p
ON r.id=p.raw_article_id

JOIN sentiment_predictions s
ON r.id=s.article_id

ORDER BY r.created_at DESC;
"""

df = pd.read_sql(query, conn)

conn.close()

positive = len(df[df["sentiment_label"]=="POSITIVE"])
negative = len(df[df["sentiment_label"]=="NEGATIVE"])

col1,col2 = st.columns(2)

col1.metric("Positive Articles",positive)
col2.metric("Negative Articles",negative)

st.subheader("Sentiment Distribution")
st.bar_chart(df["sentiment_label"].value_counts())

st.subheader("Confidence Scores")
st.line_chart(df["confidence_score"])

st.subheader("Latest Articles")
st.dataframe(df)