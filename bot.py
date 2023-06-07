import os
import time
import asyncpraw
from telethon.sync import TelegramClient, events
from telethon.tl.types import (
    PeerChannel, PeerUser,
    ReplyKeyboardMarkup,
    KeyboardButtonRow, KeyboardButton
)

from captcha_script import Captcha

API_ID = int(os.environ['API_ID'])
API_HASH = os.environ['API_HASH']
API_BOT_TOKEN = os.environ['API_BOT_TOKEN']

reddit = asyncpraw.Reddit(
    client_id=os.environ["REDDIT_CLIENT_ID"],
    client_secret=os.environ["REDDIT_CLIENT_SECRET"],
    user_agent="python:TelegBotMemes:v1 (by u/Kaadis)"
)
buttons_name = ("Memes", "ScienceMemes", "Music", "Cats", "Space", "Awww")
bot = TelegramClient('test_bot', API_ID, API_HASH).start(bot_token=API_BOT_TOKEN)

wait_captcha = {}
capt = Captcha()
bad_words = ['сука', 'блять', 'нахуй', 'довбойоб', 'придурок', 'сучка', 'падаль', 'хер', 'залупа', 'хуй', 'бля', 'лох']
bad_participants = {}


@bot.on(events.ChatAction)
async def chat_greeting(event):
    """Greeting new member chat and check that is not a bot"""
    if event.user_joined:
        user_entity = event.user
        chat_entity = event.chat

        if user_entity.username is not None:  # Make sure that user have a username
            greetings = '@' + user_entity.username
        else:
            greetings = user_entity.first_name

        await bot.send_message(
            entity=chat_entity,
            message=f'Hello, {greetings}, Please, input captcha if you are not a bot.',
            file=capt.captcha_image
        )

        wait_captcha[(user_entity.id, chat_entity.id)] = capt.captcha_text  # For everyone user add his captcha text and
        # id channel where is that user to dict


@bot.on(events.NewMessage)
async def captcha_message_checking(event):
    """Checking that user input text and text in captcha is the same"""
    if isinstance(event.peer_id, PeerChannel):
        peer_user = event.from_id
        peer_channel = event.peer_id
        captchas = wait_captcha.get((peer_user.user_id, peer_channel.channel_id))  # We get the text of the captcha

        if captchas is not None:
            if event.text != captchas:
                await event.respond("Captcha isn't correct.")
                await bot.delete_messages(peer_channel, event.message)
                await bot.kick_participant(peer_channel, peer_user)
            else:
                await event.respond(f'Greeting, new member and welcome to our little secret group buddy.', )
                await bot.send_message(entity=peer_channel,
                                       file='Gifs/Buddy.mp4')
                del wait_captcha[(peer_user.user_id, peer_channel.channel_id)]
                return


@bot.on(events.NewMessage)
async def bad_word_message_checking(event):
    peer_user = event.from_id
    peer_channel = event.peer_id
    user_entity = await bot.get_entity(peer_user)
    if any(bad_word in event.text.lower() for bad_word in bad_words):
        if not bad_participants.get((peer_user.user_id, peer_channel.channel_id)):
            bad_participants[(peer_user.user_id, peer_channel.channel_id)] = 1
        else:
            bad_participants[(peer_user.user_id, peer_channel.channel_id)] += 1

        await bot.delete_messages(
            entity=peer_channel,
            message_ids=[event.message]
        )
        if user_entity.username is not None:
            await bot.send_message(
                entity=peer_channel,
                message=f'An unpleasant word was found, The @{user_entity.username} has been warned '
                        f'{bad_participants[(peer_user.user_id, peer_channel.channel_id)]}/3 times.')
        else:
            await bot.send_message(
                entity=peer_channel,
                message=f'An unpleasant word was found, The {user_entity.first_name} has been warned '
                        f'{bad_participants[(peer_user.user_id, peer_channel.channel_id)]}/3 times.')
        if bad_participants[(peer_user.user_id, peer_channel.channel_id)] == 3:
            await bot.kick_participant(entity=peer_channel, user=peer_user)


@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    """Create a start command"""
    await event.respond('Fuck off dude, give me a fucking rest!')
    if isinstance(event.peer_id, PeerChannel):
        keyboard_buttons = ReplyKeyboardMarkup(  # This is our keyboard
            [
                KeyboardButtonRow(  # Row of buttons
                    [
                        KeyboardButton(text='Action')  # This is the button itself, if we want more than one buttons in
                        # a row we can add one more KeyboardButton.
                    ]
                )
            ]
        )
        await bot.send_message(
            entity=event.peer_id,
            message='Make your choice.',
            buttons=keyboard_buttons
        )


@bot.on(events.NewMessage(pattern='Action'))
async def actions(event):
    """This is our main functionality, in total we have six buttons, each with its own theme."""
    user_entity = await bot.get_entity(event.from_id)
    if isinstance(event.peer_id, PeerChannel):
        keyboard_buttons = ReplyKeyboardMarkup(
            [
                KeyboardButtonRow(
                    [
                        KeyboardButton(text=buttons_name[0]),
                        KeyboardButton(text=buttons_name[1]),
                        KeyboardButton(text=buttons_name[2]),

                    ]
                ),
                KeyboardButtonRow(
                    [
                        KeyboardButton(text=buttons_name[3]),
                        KeyboardButton(text=buttons_name[4]),
                        KeyboardButton(text=buttons_name[5]),
                    ],
                )
            ]
        )
        await bot.send_message(
            entity=event.peer_id,
            message=f'@{user_entity.username}, choose your type of memes and get fun.',
            buttons=keyboard_buttons
        )
        time.sleep(2)
        await bot.delete_messages(  # Delete all message before, for not spamming or flooding chat.
            entity=event.peer_id,
            message_ids=[event.message.id + 2, event.message.id + 1, event.message.id, event.message.id - 1,
                         event.message.id - 2, event.message.id - 3]

        )


async def reddits(event, name):
    """Main function of our functionality"""
    subreddit = await reddit.subreddit(name)
    if name == 'indie_rock':  # I decided to separate this topic, because music has only links or video.
        async for submission in subreddit.new(limit=1):
            await bot.send_message(
                entity=event.chat,
                message=submission.url,
            )
    else:
        async for submission in subreddit.new(limit=10):
            if submission.url[-4:] in ['.jpg', '.gif',
                                       '.png', ]:  # Checking last four symbol of url and if they have one of format.
                if isinstance(event.peer_id, PeerUser):
                    entity = event.peer_id
                else:
                    entity = event.chat
                await bot.send_message(
                    entity=entity,
                    message=submission.title,
                    file=submission.url
                )
                break


@bot.on(events.NewMessage(pattern=buttons_name[0]))
async def memes(event):
    name = 'memes'
    await reddits(event, name)


@bot.on(events.NewMessage(pattern=buttons_name[1]))
async def sciencememes(event):
    name = 'sciencememes'
    await reddits(event, name)


@bot.on(events.NewMessage(pattern=buttons_name[2]))
async def sciencememes(event):
    name = 'indie_rock'
    await reddits(event, name)


@bot.on(events.NewMessage(pattern=buttons_name[3]))
async def sciencememes(event):
    name = 'cats'
    await reddits(event, name)


@bot.on(events.NewMessage(pattern=buttons_name[4]))
async def sciencememes(event):
    name = 'spaceporn'
    await reddits(event, name)


@bot.on(events.NewMessage(pattern=buttons_name[5]))
async def sciencememes(event):
    name = 'aww'
    await reddits(event, name)


def main():
    bot.run_until_disconnected()


if __name__ == "__main__":
    main()
