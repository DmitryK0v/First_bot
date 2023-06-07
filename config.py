import os

import asyncpraw


from captcha_script import Captcha

API_ID = int(os.environ['API_ID'])
API_HASH = os.environ['API_HASH']
API_BOT_TOKEN = os.environ['API_BOT_TOKEN']


wait_captcha = {}
capt = Captcha()
bad_words = ['сука', 'блять', 'нахуй', 'довбойоб', 'придурок', 'сучка', 'падаль', 'хер', 'залупа', 'хуй', 'бля', 'лох']
bad_participants = {}

reddit = asyncpraw.Reddit(
    client_id=os.environ["REDDIT_CLIENT_ID"],
    client_secret=os.environ["REDDIT_CLIENT_SECRET"],
    user_agent="python:TelegBotMemes:v1 (by u/Kaadis)"
)

buttons_name = ("Memes", "ScienceMemes", "Music", "Cats", "Space", "Awww")