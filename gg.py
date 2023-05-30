@bot.on(events.NewMessage)
async def new_message(event):
    peer_user = event.from_id
    peer_channel = event.peer_id

    user_entity = await bot.get_entity(peer_user)

    captcha = wait_captcha.get((peer_user.user_id, peer_channel.channel_id))

    if captcha is not None:
        if event.text != captcha:
            await event.respond('Капча введена неверно.')
            await bot.delete_messages(peer_channel, event.message)
            await bot.kick_participant(peer_channel, peer_user)
        else:
            await event.respond(f'Добро пожаловать, {user_entity.first_name}!')
            await bot.delete_messages(peer_channel, [event.message.id, event.message.id - 1])
            await bot.send_message(entity=peer_channel, file='Gifs/Buddy.mp4')
            del wait_captcha[(peer_user.user_id, peer_channel.channel_id)]
            return