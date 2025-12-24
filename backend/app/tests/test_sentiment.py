def test_sentiment_labels():
    from app.services.sentiment import analyze_sentiment

    pos = analyze_sentiment("I love this product")
    neg = analyze_sentiment("I hate this service")

    assert pos["label"] == "positive"
    assert neg["label"] == "negative"
