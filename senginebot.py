#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import datetime
import json
import codecs
import requests as r
from bs4 import BeautifulSoup

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# command handlers
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi! \n Try /start or /help')

def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def getEisbachTemp():
    url = 'https://www.eisbachwetter.de/'

    response = r.get(url)
    # print(response)

    if response is not None:
        html = BeautifulSoup(response.text, 'html.parser')
        temp_raw = html.findAll('h1', {"class": "value-big", "id": "water"})

        temp = float(temp_raw[0].contents[0].replace(',','.'))

        return temp

# message handler
def buildMorningBriefing():

    temp = -273.0
    temp = getEisbachTemp()

    kalt = 'nur die harten kommen in den Garten...'
    ok = 'man sieht sich im englischen ... Badehose nicht vergessen!'
    warm = 'Absolute Badepflicht! Badehose optional.'

    if temp <= 12:
        eisbachscore = kalt
    elif temp < 17 and temp >=13:
        eisbachscore = ok
    elif temp > 17:
        eisbachscore = warm

    text='Guten Morgen! \n\nDer Eisbach hat aktuell ' + str(temp) + '°C - ' + eisbachscore + '\n\nQuelle: https://www.eisbachwetter.de/'
    return text

def sendMorningBriefing(bot, update):

    chat_id_self = ''
    chat_id_group = ''

    with open('chat_id_self.txt', 'r') as t:
        chat_id_self = t.read()

    with open('chat_id_group.txt', 'r') as t:
        chat_id_group = t.read()

    # bot.send_message(chat_id=chat_id_self, text=buildMorningBriefing()) # dev
    bot.send_message(chat_id=chat_id_group, text=buildMorningBriefing()) # prod

# def ipp(bot, update):
#     """Send IPP meals of the day when the command /ipp is issued."""
#     weekday = datetime.datetime.today().weekday()

#     with open('menu.json', 'r') as f:
#         menu = json.load(f)
#         today = ""
#         categories = ['Veggie', 'Traditionelle Küche', 'Internationale Küche', 'Specials']
#         for category in categories:
#             today += category + ":\n" + "- " + menu[category][weekday]["meal"] + "\n" + menu[category][weekday]["price"] + "\n\n"

#         message = 'Heute gibt es folgende Gerichte im IPP: \n\n' + today
#         update.message.reply_text(message)

def main():
    """Start the bot."""
    token = ''
    with open('token.txt', 'r') as t:
        token = str.strip(t.read())
    updater = Updater(token)
    dp = updater.dispatcher

    ### handle commands
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    # dp.add_handler(CommandHandler("ipp", ipp))

    ### timer
    job = updater.job_queue.run_daily(sendMorningBriefing, time = datetime.time(7, 00)) # send daily on time (for prod)
    # job = updater.job_queue.run_repeating(sendMorningBriefing, interval=30, first=0) # send repeating (for dev)

    # log all errors
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
