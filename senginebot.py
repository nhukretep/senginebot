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
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi! \n Try /start, /help or /eisbach')

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Try /eisbach to get the current temperatur of eisbach.')

def error(update, context, error):
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
def buildEisbachBriefing():

    temp = -273.0
    try:
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

        text='Der Eisbach hat aktuell ' + str(temp) + '°C - ' + eisbachscore + '\n\nQuelle: https://www.eisbachwetter.de/'
        return text

    except:
        return "Aktuell ist die Eisbach-Temperatur nicht verfügbar. Da gibt's nur eines: Ausprobieren! \n\nQuelle: https://www.eisbachwetter.de/"

def sendEisbachBriefing(update, context):
    """Send a message when the command /eisbach is issued."""
    update.message.reply_text(buildEisbachBriefing())

def sendMorningBriefing(context):
    job = context.job
    message ='Guten Morgen \n\n' + buildEisbachBriefing()
    context.bot.send_message(job.context, text=message)


def setMorningBriefing(update, context):
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        # due = int(context.args[0])
        # if due < 0:
        #     update.message.reply_text('Sorry we can not go back to future!')
        #     return

        # Add job to queue
        job = context.job_queue.run_daily(sendMorningBriefing, time = datetime.time(7, 00)) # send daily on time (for prod)
        # job = context.job_queue.run_repeating(sendMorningBriefing, interval=30, first=0, context=chat_id) # send repeating (for dev)

        context.chat_data['job'] = job

        update.message.reply_text('Morning briefing successfully subscribed!')

    except (IndexError, ValueError):
        update.message.reply_text('Error')


def unsetMorningBriefing(update, context):
    """Remove the job if the user changed their mind."""
    if 'job' not in context.chat_data:
        update.message.reply_text('You have no active briefing')
        return

    job = context.chat_data['job']
    job.schedule_removal()
    del context.chat_data['job']

    update.message.reply_text('Briefing successfully canceled!')

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
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    ### handle commands
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("eisbach", sendEisbachBriefing))
    # dp.add_handler(CommandHandler("ipp", ipp))

    ### timer
    dp.add_handler(CommandHandler("getbriefing", setMorningBriefing, pass_args=True, pass_job_queue=True, pass_chat_data=True))
    dp.add_handler(CommandHandler("stopbriefing", unsetMorningBriefing))
    
    # log all errors
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
