from flask import Flask, request, jsonify
from flasgger import Swagger
import pandas as pd
import re

app = Flask(__name__)
swagger = Swagger(app)

data_df = pd.read_csv('data.csv', encoding="ISO-8859-1")
kamus_slang = pd.read_csv('new_kamusalay.csv', header=None, names=['slang', 'baku'], encoding="ISO-8859-1")
abusive_words = pd.read_csv('abusive.csv', encoding="ISO-8859-1")['ABUSIVE'].tolist()

def clean_tweet(tweet):
    # Remove "USER" and "RT"
    tweet = re.sub(r'USER', '', tweet)
    tweet = re.sub(r'RT', '', tweet)

    # Convert to lowercase
    tweet = tweet.lower()

    # Remove punctuation
    tweet = re.sub(r'[^\w\s]', '', tweet)

    # Remove numbers
    tweet = re.sub(r'\d', '', tweet)

    # Remove extra whitespaces
    tweet = re.sub(r'\s+', ' ', tweet)

    # Remove repeated punctuation
    tweet = re.sub(r'(?:(\.)\1+)+', r'\1', tweet)

    # Remove emojis
    tweet = re.sub(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U000024C2-\U0001F251]+', '', tweet)

    # Remove emoticons
    tweet = re.sub(r'[\U00002600-\U000027BF\U0001f300-\U0001f64F\U0001f680-\U0001f6FF\U0001f700-\U0001f77F\U0001f780-\U0001f7FF\U0001f800-\U0001f8FF\U0001f900-\U0001f9FF\U0001fa00-\U0001fa6F\U0001fa70-\U0001faFF\U00002190-\U000021FF]+', '', tweet)

    # Remove duplicates
    tweet = ' '.join(list(dict.fromkeys(tweet.split())))

    # Replace slang with standard language
    words = tweet.split()
    updated_words = []

    for word in words:
        replacement = kamus_slang[kamus_slang['slang'] == word]['baku'].values
        updated_words.append(replacement[0] if replacement else word)

    tweet = ' '.join(updated_words)

    # Remove abusive words
    tweet = ' '.join(['' if word in abusive_words else word for word in tweet.split()])

    return tweet

# Define the API endpoint
@app.route('/clean-tweets', methods=['POST'])
def clean_tweets():
    """
    Endpoint to clean tweets.
    ---
    parameters:
      - name: tweet
        in: formData
        type: string
        required: true
        description: The input tweet to be cleaned.
    responses:
      200:
        description: Cleaned tweet.
    """
    tweet = request.form['tweet']
    cleaned_tweet = clean_tweet(tweet)
    return jsonify({'cleaned_tweet': cleaned_tweet})

if __name__ == '__main__':
    app.run(debug=True)
