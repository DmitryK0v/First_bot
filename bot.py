import os
from telethon.sync import TelegramClient, events
from telethon.tl.types import PeerChannel

from captcha_script import Captcha

API_ID = int(os.environ['API_ID'])
API_HASH = os.environ['API_HASH']
API_BOT_TOKEN = os.environ['API_BOT_TOKEN']

bot = TelegramClient('test_bot', API_ID, API_HASH).start(bot_token=API_BOT_TOKEN)

wait_captcha = {}
capt = Captcha()
bad_words = ['Сука', 'Блять', 'Нахуй', 'Довбойоб', 'Придурок', 'сука', 'блять', 'нахуй', 'довбойоб', 'придурок']


@bot.on(events.ChatAction)
async def chat_greeting(event):
    if event.user_joined:
        user_entity = event.user
        chat_entity = event.chat

        if user_entity.username is not None:
            greetings = '@' + user_entity.username
        else:
            greetings = user_entity.first_name

        await bot.send_message(
            entity=chat_entity,
            message=f'Hello, {greetings}, Please, input captcha if you are not a bot.',
            file=capt.captcha_image
        )

        wait_captcha[(user_entity.id, chat_entity.id)] = capt.captcha_text


@bot.on(events.NewMessage)
async def captcha_message_checking(event):
    if isinstance(event.peer_id, PeerChannel):
        peer_user = event.from_id
        peer_channel = event.peer_id

        user_entity = await bot.get_entity(peer_user)

        captchas = wait_captcha.get((peer_user.user_id, peer_channel.channel_id))

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
        if any(bad_word in event.text for bad_word in bad_words):
            await bot.delete_messages(
                entity=peer_channel,
                message_ids=[event.message]
            )
            await bot.send_message(
                entity=peer_channel,
                message=f'An unpleasant word was found, The {user_entity.first_name} has been warned.')


@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond('Fuck off')


def main():
    bot.run_until_disconnected()


if __name__ == "__main__":
    main()
