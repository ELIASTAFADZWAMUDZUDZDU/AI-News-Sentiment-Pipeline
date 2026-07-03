import requests
from datetime import datetime

from config import API_KEY
from database import get_connection
from sentiment import predict_sentiment

def extract():

    url = (
        f"https://newsapi.org/v2/top-headlines?"
        f"country=us&pageSize=5&apiKey={API_KEY}"
    )

    response = requests.get(url)

    data = response.json()

    return data["articles"]

def load(articles):

    conn = get_connection()
    cursor = conn.cursor()

    for article in articles:

        title = article["title"]
        source = article["source"]["name"]
        published_at = article["publishedAt"]
        content = article["content"]

        if published_at:

            published_at = datetime.fromisoformat(
                published_at.replace("Z", "+00:00")
            )

        else:

            published_at = None

        cursor.execute("""
            INSERT INTO raw_articles
            (title, source, published_at, content)

            VALUES(%s,%s,%s,%s)

            ON CONFLICT(title)
            DO NOTHING;
        """,
        (
            title,
            source,
            published_at,
            content
        ))

    conn.commit()

    cursor.close()

    conn.close()

    print("Raw articles loaded.")

def transform():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT id, content

        FROM raw_articles

        WHERE content IS NOT NULL;

    """)

    articles = cursor.fetchall()

    for article in articles:

        raw_id = article[0]

        text = article[1].strip()

        word_count = len(text.split())

        cursor.execute("""

        INSERT INTO processed_articles

        (raw_article_id, clean_text, word_count)

        VALUES(%s,%s,%s)

        ON CONFLICT DO NOTHING;

        """,

        (raw_id, text, word_count))

    conn.commit()

    cursor.close()

    conn.close()

    print("Transformation complete.") 
    
def sentiment_prediction():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT raw_article_id,

               clean_text

        FROM processed_articles

    """)

    articles = cursor.fetchall()

    for article in articles:

        article_id = article[0]

        text = article[1]

        sentiment, confidence = predict_sentiment(text)

        cursor.execute("""

        INSERT INTO sentiment_predictions

        (article_id,
         sentiment_label,
         confidence_score)

        VALUES(%s,%s,%s)

        ON CONFLICT(article_id)

        DO NOTHING;

        """,

        (article_id,
         sentiment,
         confidence))

    conn.commit()

    cursor.close()

    conn.close()

    print("Sentiment prediction complete.")     

def run_pipeline():

    articles = extract()

    load(articles)

    transform()

    sentiment_prediction()


if __name__ == "__main__":

    run_pipeline()      