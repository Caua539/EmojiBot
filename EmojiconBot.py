#!/usr/bin/env python
# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled

import json
import logging

from uuid import uuid4
from telegram import InlineQueryResultAudio, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Updater, CommandHandler, InlineQueryHandler, MessageHandler, ConversationHandler, Filters
from telegram.ext.dispatcher import run_async

import EmojiconFinder

# Enable logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

#global variables
RESPONSE_DICT = {}
emojiconname = ""
emojicon = ""

# Load config file
with open('config.json') as config_file:
    CONFIGURATION = json.load(config_file)
    
#handlers
def start_command(bot, update):
    """ Responde ao comando /start """
    bot.sendMessage(update.message.chat_id, text='pt-br (for english, /starten): Olá, sou o EmojiconBot! Minha função é te ajudar a ' 
                                                 'encontrar o melhor emojicon para você se expressar nos chats!\n'
                                                 'Digite /help para entender meu funcionamento.\n')
                      
                                                 
def starten_command(bot, update):
    """ Handle the /starten command """
    bot.sendMessage(update.message.chat_id, text='en: Hello, I\'m emojiconbot! I\'m here to help you ' 
                                                 'find the best emojicon to express yourself in chat!\n'
                                                 'Type /help to understand how I work.\n')
              
                                                
def help_command(bot, update):
    """ Responde ao comando /help """
    bot.sendMessage(update.message.chat_id, text='pt-br (for english, /helpen):')
    
    
def helpen_command(bot, update):
    """ Handle the /helpen command """
    bot.sendMessage(update.message.chat_id, text='en:')
    
    
EMOJICONNAME, EMOJICON = range(2)

def addemojicon_command(bot, update):
    update.message.reply_text('Para começar, me mande o nome do emojicon que deseja adicionar (para poder buscá-lo).')
    
    return EMOJICONNAME

    
def emojiconname_command(bot, update):
    user = update.message.from_user
    logger.info("Emojicon Name sent by %s: %s" % (user.first_name, update.message.text))
    global emojiconname
    emojiconname = update.message.text
    update.message.reply_text('Certo, agora mande o emojicon (em texto):')
    
    return EMOJICON
    
    
def newemojicon_command(bot, update):
    user = update.message.from_user
    logger.info("Emojicon sent by %s: %s" % (user.first_name, update.message.text))
    global emojicon
    emojicon = update.message.text
    update.message.reply_text('Emojicon adicionado a lista! Obrigado!')
    EmojiconFinder.newemojicon(emojiconname, emojicon, RESPONSE_DICT)
    
    return ConversationHandler.END
    
def inline_busca_emojicon(bot, update):
    message = update.inline_query.query
    user = update.inline_query.from_user.first_name
    
    emojicons = EmojiconFinder.prepare_emojicons(message, RESPONSE_DICT)
    results = []
    
    
    if not emojicons:
        pass
    else:
        for i in range(len(emojicons)):
            if emojicons[i] == {}:
                continue
            sresult = InlineQueryResultArticle(
            id = uuid4(),
            title = "{}:  {}".format(emojicons[i]["Nome"], emojicons[i]["Emojicon"]),
            input_message_content=InputTextMessageContent(emojicons[i]["Emojicon"]))
            
            results.append(sresult)
        bot.answerInlineQuery(update.inline_query.id, results=results)
    
def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation." % user.first_name)
    update.message.reply_text('Ok! Estou aqui se precisar!')
    
    return ConversationHandler.END

    
def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))
    
#main
    
def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(CONFIGURATION["telegram_token"])

    global RESPONSE_DICT
    # Load the responses
    RESPONSE_DICT = EmojiconFinder.load_response_json(CONFIGURATION["responses_file"])
    
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states EMOJICONNAME e EMOJICON
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('addemojicon', addemojicon_command)],

        states={

            EMOJICONNAME: [MessageHandler(Filters.text, emojiconname_command)],

            EMOJICON: [MessageHandler(Filters.text, newemojicon_command)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("starten", starten_command))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("helpen", helpen_command))
    dp.add_handler(InlineQueryHandler(inline_busca_emojicon))

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

    