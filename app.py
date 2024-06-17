from flask import Flask, request, jsonify, render_template
import pickle
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from pymongo import MongoClient
from datetime import datetime, timedelta

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb+srv://jyotiprakash2409:jp3ra@cluster0.tvxyswb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client.your_database_name
users_collection = db.users

model = pickle.load(open('xgb_model.pkl', 'rb'))
with open('tfidf_vectorizer.pkl', 'rb') as vectorizer_file:
    vectorizer = pickle.load(vectorizer_file)

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()


def data_processing(tweet):
    tweet = tweet.lower()
    tweet = re.sub(r"https\S+|www\S+http\S+", '', tweet, flags=re.MULTILINE)
    tweet = re.sub(r'\@\w+|\#','', tweet)
    tweet = re.sub(r'[^\w\s]','',tweet)
    tweet = re.sub(r'ð','',tweet)
    tweet_tokens = word_tokenize(tweet)
    filtered_tweets = [w for w in tweet_tokens if not w in stop_words]
    lemmatized_tweet = [lemmatizer.lemmatize(word) for word in filtered_tweets]
    return " ".join(lemmatized_tweet)


def predict_speech(text):
    processed_text = data_processing(text)
    text_transformed = vectorizer.transform([processed_text])
    prediction = model.predict(text_transformed)
    label_map = {0: "Hate Speech", 1: "Offensive Speech", 2: "Neither"}
    return label_map[prediction[0]]

def ban_user(username):
    ban_until = datetime.now() + timedelta(days=2)
    users_collection.update_one({"username": username}, {"$set": {"ban_until": ban_until}})

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        username = request.form['username']
        speech_text = request.form['tweet_id_or_url']

        user = users_collection.find_one({"username": username})
        if not user:
            users_collection.insert_one({"username": username, "hate_count": 0, "offensive_count": 0, "ban_until": None})
            user = {"username": username, "hate_count": 0, "offensive_count": 0, "ban_until": None}

        if user.get("ban_until") and user.get("ban_until") > datetime.now():
            return render_template('predict.html', username=username, tweet=speech_text, result="Banned", message="Your account is banned until {}".format(user.get("ban_until").strftime('%Y-%m-%d %H:%M:%S')))

        prediction = predict_speech(speech_text)
        if prediction == "Hate Speech":
            users_collection.update_one({"username": username}, {"$inc": {"hate_count": 1}})
            if user.get("hate_count", 0) >= 5:
                ban_user(username)
                return render_template('predict.html', username=username, tweet=speech_text, result="Banned", message="Your account is banned for 2 days due to excessive hate speech.")
        elif prediction == "Offensive Speech":
            users_collection.update_one({"username": username}, {"$inc": {"offensive_count": 1}})
            if user.get("offensive_count", 0) >= 5:
                ban_user(username)
                return render_template('predict.html', username=username, tweet=speech_text, result="Banned", message="Your account is banned for 2 days due to excessive offensive speech.")

        return render_template('predict.html', username=username, tweet=speech_text, result=prediction)

    return render_template('predict.html')

if __name__ == '__main__':
    app.run(debug=True)
