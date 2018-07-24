#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Bot for sending menu and other services
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import datetime
import json
import codecs

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Test change

# Define command handlers
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi! \n Try /start /help and /ipp')

def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def ipp(bot, update):
    """Send IPP meals of the day when the command /ipp is issued."""
    weekday = datetime.datetime.today().weekday()
    
    with open('menu.json', 'r') as f:
        menu = json.load(f)
        today = ""
        categories = ['Veggie', 'Traditionelle Küche', 'Internationale Küche', 'Specials']
        for category in categories:
            today += category + ":\n" + "- " + menu[category][weekday]["meal"] + "\n" + menu[category][weekday]["price"] + "\n\n"

        message = 'Heute gibt es folgende Gerichte im IPP: \n\n' + today
        update.message.reply_text(message)

def echo(bot, update):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    with open('token.txt', 'r') as t:
        token = t.read()
        updater = Updater(token)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("ipp", ipp))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()