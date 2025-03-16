import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackQueryHandler

from config import settings
import text_strings as ts
from draw_image import LightImage

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
STEP_YELLOW, STEP_RED, STEP_DONE, MAKE_IMAGE = range(4)
VK_GROUP_URL, VK_TOKEN, YD_URL, YD_PASS, YD_LOGIN, STEP_CHOICE, ORG_NAME, JOIN_TO_ORG, SET_TIME, SET_HASHTAG, SET_START_TEXT, SET_END_TEXT, = range(4,16)
END = ConversationHandler.END

def get_keyboard(step_in: int, step_out: int, bt_text: str):
    keyboard = [
        [
            InlineKeyboardButton(settings.group.o_plus, callback_data=f'{step_in}__o_plus'),
            InlineKeyboardButton(settings.group.o_minus, callback_data=f'{step_in}__o_minus'),
            InlineKeyboardButton(settings.group.a_plus, callback_data=f'{step_in}__a_plus'),
            InlineKeyboardButton(settings.group.a_minus, callback_data=f'{step_in}__a_minus')
        ],
        [
            InlineKeyboardButton(settings.group.b_plus, callback_data=f'{step_in}__b_plus'),
            InlineKeyboardButton(settings.group.b_minus, callback_data=f'{step_in}__b_minus'),
            InlineKeyboardButton(settings.group.ab_plus, callback_data=f'{step_in}__ab_plus'),
            InlineKeyboardButton(settings.group.ab_minus, callback_data=f'{step_in}__ab_minus')
        ],
        [
            InlineKeyboardButton(bt_text, callback_data=f'{step_out}')
        ]
    ]
    return keyboard

def get_text_from_groups(groups: list):
    if groups:
        return ', '.join(settings.group.__getattribute__(x) for x in groups)
    return ''

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=ts.MESSAGE_START)

async def start_image_inline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['yellow_list'] = []
    context.user_data['red_list'] = []
    inline_keyboard = get_keyboard(STEP_YELLOW, STEP_RED, ts.BTN_RED)
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
    msg = 'Начнём. Выберите "жёлтые" группы крови.'
    await update.message.reply_text(msg, reply_markup=reply_markup)
    return MAKE_IMAGE

async def more_yellow_inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    print(query.data)
    blood_group: str = query.data.split('__')[-1]
    await query.answer()
    if not context.user_data['yellow_list']:
        context.user_data['yellow_list'] = [blood_group]
    else:
        if blood_group not in context.user_data['yellow_list']:
            context.user_data['yellow_list'].append(blood_group)
        else:
            return MAKE_IMAGE
    inline_keyboard = get_keyboard(STEP_YELLOW, STEP_RED, ts.BTN_RED)
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
    msg = f'Выбрали 🟡 {get_text_from_groups(context.user_data['yellow_list'])}\nЕщё?'
    await update.callback_query.edit_message_text(text=msg, reply_markup=reply_markup)
    return MAKE_IMAGE

async def red_inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    print(query.data)
    await query.answer()
    if '__' in query.data:
        blood_group: str = query.data.split('__')[-1]
        if not context.user_data['red_list']:
            context.user_data['red_list'] = [blood_group]
        elif blood_group not in context.user_data['red_list']:
            context.user_data['red_list'].append(blood_group)
            if blood_group in context.user_data['yellow_list']:
                context.user_data['yellow_list'].remove(blood_group)
        else:
            return MAKE_IMAGE
    inline_keyboard = get_keyboard(STEP_RED, STEP_DONE, ts.BTN_DONE)
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
    print(query)
    msg = ''
    if context.user_data['yellow_list']:
        msg = f'Выбрали 🟡 {get_text_from_groups(context.user_data['yellow_list'])}\n'
    if context.user_data['red_list']:
        msg += f'Выбрали 🔴 {get_text_from_groups(context.user_data['red_list'])}\nЕщё?'
    else:
        msg += f'Укажите красные 🔴 группы крови'
    await update.callback_query.edit_message_text(text=msg, reply_markup=reply_markup)
    return MAKE_IMAGE

async def light_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    light_template = {'o_plus': 'green', 'o_minus': 'green',
                      'a_plus': 'green', 'a_minus': 'green',
                      'b_plus': 'green', 'b_minus': 'green',
                      'ab_plus': 'green', 'ab_minus': 'green'}
    if context.user_data['yellow_list']:
        for group in context.user_data['yellow_list']:
            light_template[group] = 'yellow'
    if context.user_data['red_list']:
        for group in context.user_data['red_list']:
            light_template[group] = 'red'
    image = LightImage('color_drops', light_template, 'org1')
    image.draw_image()
    msg = ''
    if context.user_data['yellow_list']:
        msg = f'🟡 {get_text_from_groups(context.user_data['yellow_list'])}\n'
    if context.user_data['red_list']:
        msg += f'🔴 {get_text_from_groups(context.user_data['red_list'])}\n'
    await update.callback_query.edit_message_text(text=msg)
    await context.bot.send_document(chat_id=update.effective_message.chat_id,
                                    document=open(image.image_name, 'rb'))
    return END

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
        entry_points=[CommandHandler('image', start_image_inline)],
        states={
            MAKE_IMAGE: [CallbackQueryHandler(more_yellow_inline, pattern= str(STEP_YELLOW)),
                         CallbackQueryHandler(red_inline, pattern= str(STEP_RED)),
                         CallbackQueryHandler(light_done, pattern= str(STEP_DONE))],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(start_handler)
    application.add_handler(image_handler)

    application.run_polling()