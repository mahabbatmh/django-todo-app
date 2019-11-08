from channels import Group


def ws_add(message):
    message.reply_channel.send({"accept": True})
    Group('comment').add(message.reply_channel)


def ws_message(message):
    Group('comment').send({'comment': message.content['comment']})


def ws_disconnect(message):
    Group('chat').discard(message.reply_channel)
