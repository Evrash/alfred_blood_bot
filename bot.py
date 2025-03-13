import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackQueryHandler

from config import settings
import text_strings as ts

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

STEP_YELLOW, STEP_RED, VK_GROUP_URL, VK_TOKEN, YD_URL, YD_PASS, YD_LOGIN, STEP_CHOICE, ORG_NAME, JOIN_TO_ORG, \
    SET_TIME, SET_HASHTAG, SET_START_TEXT, SET_END_TEXT, STEP_DONE = range(15)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=ts.MESSAGE_START)

async def start_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['yellow_string'] = ''
    context.user_data['red_string'] = ''
    inline_keyboard = [
        [
            InlineKeyboardButton('🅾️➕', callback_data=f'{STEP_YELLOW}_I+'),
            InlineKeyboardButton('🅾️➖', callback_data=f'{STEP_YELLOW}_I-'),
            InlineKeyboardButton('🅰️➕', callback_data=f'{STEP_YELLOW}_II+'),
            InlineKeyboardButton('🅰️➖', callback_data=f'{STEP_YELLOW}_II-')
        ],
        [
            InlineKeyboardButton('🅱️➕', callback_data=f'{STEP_YELLOW}_III+'),
            InlineKeyboardButton('🅱️➖', callback_data=f'{STEP_YELLOW}_III-'),
            InlineKeyboardButton('🆎➕', callback_data=f'{STEP_YELLOW}_IV+'),
            InlineKeyboardButton('🆎➖', callback_data=f'{STEP_YELLOW}_IV-')
        ],
        [
            InlineKeyboardButton(ts.BTN_RED, callback_data=f'{STEP_RED}')
        ]
    ]
    reply_keyboard = [['I+', 'I-', 'II+', 'II-'], ['III+', 'III-', 'IV+', 'IV-'], [ts.BTN_NEXT]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
    # await update.message.reply_text(f'Начнём. Жёлтый цвет?',
    #                                 reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))
    await update.message.reply_text(f'Начнём. Жёлтый цвет?',
                                    reply_markup=reply_markup)
    return STEP_YELLOW

async def more_yellow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == ts.BTN_NEXT:
        reply_keyboard = [['I+', 'I-', 'II+', 'II-'], ['III+', 'III-', 'IV+', 'IV-'], [ts.BTN_NEXT]]
        await update.message.reply_text(f'Красный цвет?',
                                        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))
        return STEP_RED
    else:
        if not context.user_data['yellow_string']:
            context.user_data['yellow_string'] += update.message.text
        else:
            if update.message.text not in context.user_data['yellow_string']:
                context.user_data['yellow_string'] += ',' + update.message.text
        reply_keyboard = [['I+', 'I-', 'II+', 'II-'], ['III+', 'III-', 'IV+', 'IV-'], [ts.BTN_NEXT]]
        await update.message.reply_text(
            f"Жёлтые {context.user_data['yellow_string']}. Ещё жёлтые?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))
        return STEP_YELLOW

async def more_yellow_inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    print(query.data)
    blood_group: str = query.data.split('_')[-1]
    await query.answer()
    if not context.user_data['yellow_string']:
        context.user_data['yellow_string'] += blood_group
    else:
        if blood_group not in context.user_data['yellow_string']:
            context.user_data['yellow_string'] += ',' + blood_group
        else:
            return STEP_YELLOW

    # inline_keyboard = [
    #     [
    #         InlineKeyboardButton('I+', callback_data='I+'),
    #         InlineKeyboardButton('I-', callback_data='I-'),
    #         InlineKeyboardButton('II+', callback_data='II+'),
    #         InlineKeyboardButton('II-', callback_data='II-')
    #     ],
    #     [
    #         InlineKeyboardButton('III+', callback_data='III+'),
    #         InlineKeyboardButton('III-', callback_data='III-'),
    #         InlineKeyboardButton('IV+', callback_data='IV+'),
    #         InlineKeyboardButton('IV-', callback_data='IV-')
    #     ],
    #     [
    #         InlineKeyboardButton(ts.BTN_NEXT, callback_data=ts.BTN_NEXT)
    #     ]
    # ]

    inline_keyboard = [
        [
            InlineKeyboardButton('🅾️➕', callback_data=f'{STEP_YELLOW}_I+'),
            InlineKeyboardButton('🅾️➖', callback_data=f'{STEP_YELLOW}_I-'),
            InlineKeyboardButton('🅰️➕', callback_data=f'{STEP_YELLOW}_II+'),
            InlineKeyboardButton('🅰️➖', callback_data=f'{STEP_YELLOW}_II-')
        ],
        [
            InlineKeyboardButton('🅱️➕', callback_data=f'{STEP_YELLOW}_III+'),
            InlineKeyboardButton('🅱️➖', callback_data=f'{STEP_YELLOW}_III-'),
            InlineKeyboardButton('🆎➕', callback_data=f'{STEP_YELLOW}_IV+'),
            InlineKeyboardButton('🆎➖', callback_data=f'{STEP_YELLOW}_IV-')
        ],
        [
            InlineKeyboardButton(ts.BTN_RED, callback_data=f'{STEP_RED}')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
    print(query)

    await update.callback_query.edit_message_text(text=f'Выбрали 🟡 {context.user_data['yellow_string']}\nЕщё?', reply_markup=reply_markup)
    return STEP_YELLOW

async def red_inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    print(query.data)
    if '_' in query.data:
        blood_group: str = query.data.split('_')[-1]
        if not context.user_data['red_string']:
            context.user_data['red_string'] = blood_group
        elif blood_group not in context.user_data['red_string']:
            context.user_data['red_string'] += ',' + blood_group
    await query.answer()

    inline_keyboard = [
        [
            InlineKeyboardButton('🅾️➕', callback_data=f'{STEP_RED}_I+'),
            InlineKeyboardButton('🅾️➖', callback_data=f'{STEP_RED}_I-'),
            InlineKeyboardButton('🅰️➕', callback_data=f'{STEP_RED}_II+'),
            InlineKeyboardButton('🅰️➖', callback_data=f'{STEP_RED}_II-')
        ],
        [
            InlineKeyboardButton('🅱️➕', callback_data=f'{STEP_RED}_III+'),
            InlineKeyboardButton('🅱️➖', callback_data=f'{STEP_RED}_III-'),
            InlineKeyboardButton('🆎➕', callback_data=f'{STEP_RED}_IV+'),
            InlineKeyboardButton('🆎➖', callback_data=f'{STEP_RED}_IV-')
        ],
        [
            InlineKeyboardButton(ts.BTN_DONE, callback_data=f'{STEP_DONE}')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
    print(query)
    msg = ''
    if context.user_data['yellow_string']:
        msg = f'Выбрали 🟡 {context.user_data['yellow_string']}\n'
    if context.user_data['red_string']:
        msg += f'Выбрали 🔴 {context.user_data['red_string']}\nЕщё?'
    else:
        msg += f'Укажите красные 🔴 группы крови'
    await update.callback_query.edit_message_text(text=msg, reply_markup=reply_markup)
    return STEP_YELLOW



async def cancel(update:Update, context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выполнение задание прервано.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

if __name__ == '__main__':
    application = ApplicationBuilder().token(settings.token).build()
    start_handler = CommandHandler('start', start)
    # image_handler = ConversationHandler(
    #     entry_points=[CommandHandler('image', start_image)],
    #     states={
    #         STEP_YELLOW: [MessageHandler(filters.TEXT, more_yellow)],
    #         # STEP_RED: [MessageHandler(filters.TEXT, red)],
    #     },
    #     fallbacks=[CommandHandler('cancel', cancel)]
    # )

    image_handler = ConversationHandler(
        entry_points=[CommandHandler('image', start_image)],
        states={
            STEP_YELLOW: [CallbackQueryHandler(more_yellow_inline, pattern= str(STEP_YELLOW)),
                          CallbackQueryHandler(red_inline, pattern= str(STEP_RED))],
            # STEP_RED: [CallbackQueryHandler(red_inline, pattern= str(STEP_RED))],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(start_handler)
    application.add_handler(image_handler)

    application.run_polling()