from flask import Flask, request, jsonify, render_template
import pickle
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Ensure necessary NLTK data is downloaded
# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('wordnet')

app = Flask(__name__)

# Load the pre-trained model and the TF-IDF vectorizer
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
    print(f"Processed Text: {processed_text}") 
    text_transformed = vectorizer.transform([processed_text])
    print(f"Transformed Text Shape: {text_transformed.shape}") 
    prediction = model.predict(text_transformed)
    label_map = {0: "Hate Speech", 1: "Offensive Speech", 2: "Neither"}
    print(f"Prediction: {label_map[prediction[0]]}")  
    return label_map[prediction[0]]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    speech_text = data.get('speech')
    prediction = predict_speech(speech_text)
    return jsonify({'result': prediction})

if __name__ == '__main__':
    app.run(debug=True)
