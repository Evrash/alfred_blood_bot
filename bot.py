import logging
from typing import TYPE_CHECKING

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackQueryHandler

from config import settings
import text_strings as ts
from draw_image import LightImage
import models.crud as crud
from models.crud import get_user, create_user

if TYPE_CHECKING:
    from models import User, Organisation

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
    await crud.get_or_create(tg_id=update.effective_chat.id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=ts.MESSAGE_START)

async def start_image_inline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Старт генерации донорского светофора"""
    context.user_data['yellow_list'] = []
    context.user_data['red_list'] = []
    inline_keyboard = get_keyboard(STEP_YELLOW, STEP_RED, ts.BTN_RED)
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
    msg = 'Начнём. Выберите "жёлтые" группы крови.'
    await update.message.reply_text(msg, reply_markup=reply_markup)
    return MAKE_IMAGE

async def more_yellow_inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор жёлтых групп крови"""
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
    """Выбор красных групп крови"""
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
    """Получение и отправка картинки со светофором"""
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

# Функции для сбора информации о пользователе
async def set_info_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user: User = crud.get_user(tg_id=update.effective_user.id)
    if not user:
        user = crud.create_user(tg_id=update.effective_user.id)
    if user.organisation_id is None:
        # context.user_data['User'] = User.get(User.telegram_chat_id == update.effective_user.id)
        message = ts.SET_INFO_ORG_NAME
        await update.message.reply_text(message)
        return ORG_NAME
    else:
        await update.message.reply_text(ts.SET_INFO_DBL_REG)
        return ConversationHandler.END

async def set_info_org(update: Update, context: ContextTypes.DEFAULT_TYPE):
    org = crud.get_organisation_by_name(name=update.message.text.strip())
    if org:
        await update.message.reply_text(ts.SET_INFO_SAME_ORG)
        return ConversationHandler.END
    org: Organisation = crud.create_organisation(name=update.message.text)
    user: User = crud.get_user(tg_id=update.effective_user.id)
    user.organisation = org
    user.is_admin = 1
    user.save()
    context.user_data['org'] = org
    message = ts.SET_INFO_EXPL
    await update.message.reply_text(message)
    message = ts.SET_INFO_EXPL_QUEST
    reply_keyboard = [[ts.BTN_GRANT_ALL], [ts.BTN_GRANT_VK], [ts.BTN_GRANT_VK], [ts.BTN_GRANT_NONE]]
    await update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return STEP_CHOICE


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