import json
import telebot
from main import bot 


def handler(event, context):
    body = json.loads(event['body'])
    message = telebot.types.Update.de_json(body)
    bot.process_new_updates([message])
    return {
        'statusCode': 200,
        'body': ''
    }