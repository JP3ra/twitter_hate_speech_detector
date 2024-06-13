import tweepy

# Replace these values with your actual keys and tokens
API_KEY = 'VlNPBrB2YRSkxsQuVuShewk8c'
API_SECRET_KEY = 'jPsTju5cICrgyeEQx4P2F8jJ43xQOIE8WG9F5A1iaxsI2EqucP'
ACCESS_TOKEN = '1540966872736464896-Kk4nttb7pk94JysgAI5gCaEhqJlNmm'
ACCESS_TOKEN_SECRET = 'mHe3ZHVSDgTQuawqcQpPdWV7ut4X1kETg6uHTdus6zt9o'
BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAAeetAEAAAAAX0osqpMjatpzmnN12dyfRk225ME%3DMUMoP7OILy3epsfRlPOHW1bh5yvLmMdUcpSEnaHk99dLNMNbU5'

# Initialize the Tweepy client
client = tweepy.Client(bearer_token=BEARER_TOKEN,
                       consumer_key=API_KEY,
                       consumer_secret=API_SECRET_KEY,
                       access_token=ACCESS_TOKEN,
                       access_token_secret=ACCESS_TOKEN_SECRET)

def get_tweets(username):
    try:
        user = client.get_user(username=username)
        print(user)
    except tweepy.errors.TweepyException as e:
        print(f"Error: {e}")

# Test the function with a Twitter handle
get_tweets("@narendramodi")
