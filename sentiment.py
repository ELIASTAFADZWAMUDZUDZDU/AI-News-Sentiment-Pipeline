from transformers import pipeline

# Load the model once
sentiment_model = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)


def predict_sentiment(text):
    """
    Predict sentiment for a piece of text.
    """

    result = sentiment_model(text)

    sentiment = result[0]["label"]
    confidence = result[0]["score"]

    return sentiment, confidence

