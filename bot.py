import logging
from typing import TYPE_CHECKING

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from datetime import datetime

from config import settings
import text_strings as ts
from draw_image import LightImage
import models.crud as crud
from utils import *

if TYPE_CHECKING:
    from models import User, Organisation

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
STEP_YELLOW, STEP_RED, STEP_DONE, MAKE_IMAGE = range(4)
VK_GROUP_URL, VK_TOKEN, YD_URL, YD_PASS, YD_LOGIN, STEP_CHOICE, ORG_NAME, JOIN_TO_ORG, SET_TIME, SET_HASHTAG, SET_START_TEXT, SET_END_TEXT, ORG_RENAME = range(4,17)
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

#Функции генерации светофора
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
            context.user_data['red_list'] = []
        if blood_group not in context.user_data['red_list']:
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

    # Формируем строку с состоянием светофора для YD
    colors = ['2'] * 8
    for count, value in enumerate(light_template.values()):
        match value:
            case 'yellow':
                colors[count] = '1'
            case 'red':
                colors[count] = '0'
    yd_group_str = ','.join(colors)

    # Получаем данные для светофора
    org = await crud.get_org_by_tg_id(tg_id=update.effective_user.id)
    img_template = settings.default_img_template
    if org:
        org_str = 'org' + str(org.id)
        org.last_yd_str = yd_group_str
        await crud.set_organisation_yd_str(org)
        if org.vk_template:
            img_template = org.vk_template
    else:
        user = await crud.get_user(tg_id=update.effective_user.id)
        org_str = 'usr' + str(user.id)

    image = LightImage(img_template, light_template, org_str)
    image.draw_image()
    msg = make_message(light=light_template)
    msg_author = f"Светофор сформирован {update.callback_query.from_user.full_name}"
    if update.callback_query.from_user.username:
        msg_author += ' @' + update.callback_query.from_user.username
    # if context.user_data['yellow_list']:
    #     msg = f'🟡 {get_text_from_groups(context.user_data['yellow_list'])}\n'
    # if context.user_data['red_list']:
    #     msg += f'🔴 {get_text_from_groups(context.user_data['red_list'])}\n'
    await update.callback_query.edit_message_text(text=ts.IMG_READY)
    if org:
        org.vk_last_light_post = msg
        org.last_create_date = datetime.now()
        org.last_image_name = image.image_name.name
        await crud.set_last_light_post_info(org)
        org_users = await crud.get_org_users(org.id)
        for user in org_users:
            await context.bot.send_message(chat_id=user.tg_id, text=msg)
            await context.bot.send_document(chat_id=user.tg_id, document=open(image.image_name, 'rb'))
            await context.bot.send_message(chat_id=user.tg_id, text=msg_author)
    return END

async def cancel(update:Update, context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выполнение задания прервано.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Функции для сбора информации о пользователе
async def set_info_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user: User = await crud.get_user(tg_id=update.effective_user.id)
    if not user:
        user = await crud.create_user(tg_id=update.effective_user.id)
    if user.organisation_id is None or update.message.text == ts.BTN_YES:
        # context.user_data['User'] = User.get(User.telegram_chat_id == update.effective_user.id)
        await update.message.reply_text(ts.SET_INFO_ORG_NAME)
        return ORG_NAME
    elif update.message.text == ts.BTN_NO:
        await update.message.reply_text(ts.SET_INFO_NO_RENAME)
        return ConversationHandler.END
    else:
        reply_keyboard = [[ts.BTN_YES, ts.BTN_NO]]
        await update.message.reply_text(ts.SET_INFO_DBL_REG,
                                        reply_markup=ReplyKeyboardMarkup(reply_keyboard,one_time_keyboard=True))
        context.user_data['rename'] = True
        return ORG_RENAME

async def set_info_org(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('rename'):
        user = await crud.get_user(tg_id=update.effective_user.id)
        org = await crud.get_org_by_tg_id(user.tg_id)
        if not user.is_admin:
            await update.message.reply_text(ts.SET_INFO_NOT_ADMIN)
            return ConversationHandler.END
        org.name = update.message.text.strip()
        await crud.org_set_name(org)
    else:
        org = await crud.get_organisation_by_name(name=update.message.text.strip())
        if org:
            await update.message.reply_text(ts.SET_INFO_SAME_ORG)
            #TODO: Добвить сброс организации
            return ConversationHandler.END
        org: Organisation = await crud.create_organisation(name=update.message.text)
        user: User = await crud.get_user(tg_id=update.effective_user.id)
        user.organisation = org
        user.is_admin = True
        await crud.user_set_org(user=user)
    context.user_data['org'] = org
    await update.message.reply_text(ts.SET_INFO_EXPL)
    reply_keyboard = [[ts.BTN_GRANT_ALL], [ts.BTN_GRANT_VK], [ts.BTN_GRANT_YD], [ts.BTN_GRANT_NONE]]
    await update.message.reply_text(ts.SET_INFO_EXPL_QUEST,
                                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return STEP_CHOICE

async def set_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # update.message.reply_text(reply_markup = ReplyKeyboardRemove())
    match update.message.text:
        case ts.BTN_GRANT_ALL:
            context.user_data['choice'] = 'ALL'
            await update.message.reply_text(ts.SET_INFO_CHOOSE_ALL)
            await update.message.reply_text(ts.SET_INFO_YD_LOGIN, reply_markup=ReplyKeyboardRemove())
            return YD_LOGIN
        case ts.BTN_GRANT_YD:
            context.user_data['choice'] = 'YD'
            await update.message.reply_text(ts.SET_INFO_CHOOSE_YD)
            await update.message.reply_text(ts.SET_INFO_YD_LOGIN, reply_markup=ReplyKeyboardRemove())
            return YD_LOGIN
        case ts.BTN_GRANT_VK:
            context.user_data['choice'] = 'VK'
            await update.message.reply_text(ts.SET_INFO_CHOOSE_VK)
            return await get_vk_token(update, context)
        case _:
            await update.message.reply_text('Хорошо')
            return ConversationHandler.END

async def get_yd_login(update, context):
    message = ts.SET_INFO_YD_LOGIN
    await update.message.reply_text(message, reply_markup=ReplyKeyboardRemove())
    return YD_LOGIN

async def get_yd_pass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['org'].yd_login = encode_str(update.message.text)
    message = ts.SET_INFO_YD_PASS
    await update.message.reply_text(message)
    return YD_PASS

async def get_yd_url(update, context):
    context.user_data['org'].yd_pass = encode_str(update.message.text)
    # TODO: Додавить картинку с копированием УРЛа
    message = ts.SET_INFO_YD_URL
    await update.message.reply_text(message)
    await context.bot.send_document(chat_id=update.effective_chat.id, document=open('bot_img/yd_site.jpg', 'rb'))
    return YD_URL

async def get_vk_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Если отдаёт всё, то сначала сохраняем параметры ЯД
    if context.user_data['choice'] in ['ALL', 'YD']:
        groups, station_id, is_user = await yd_ids(url=update.message.text,
                                                   login=decode_str(context.user_data['org'].yd_login),
                                                   password=decode_str(context.user_data['org'].yd_pass))
        if is_user:
            context.user_data['org'].yd_station_id = station_id
            context.user_data['org'].yd_groups_ids = ','.join(groups)
            await crud.set_yd_all(context.user_data['org'])
            if context.user_data['choice'] == 'YD':
                await update.message.reply_text(ts.SET_INFO_YD_OK)
                return ConversationHandler.END
            else:
                await update.message.reply_text(f"{ts.SET_INFO_YD_OK} Займёмся ВК")
        else:
            await update.message.reply_text(ts.SET_INFO_YD_ERROR)
            return YD_LOGIN
    message = ts.SET_INFO_VK_TOKEN
    await update.message.reply_text(message, reply_markup=ReplyKeyboardRemove())
    return VK_TOKEN

async def set_vk_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: Добавить проверку на правильность ссылки
    params = update.message.text.split('#')[1].split('&')
    for param in params:
        if param.split('=')[0] == 'access_token':
            context.user_data['org'].vk_token = encode_str(param.split('=')[1])
            await crud.org_set_token(org=context.user_data['org'])
            break
    if context.user_data['org'].vk_token is None:
        await update.message.reply_text(ts.SET_INFO_VK_ERROR)
        return ConversationHandler.END
    else:
        await update.message.reply_text(ts.SET_INFO_VK_GROUP)
        return VK_GROUP_URL


async def set_vk_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    vk_token = update.message.text.strip()
    result = await get_vk_group_id(token=decode_str(context.user_data['org'].vk_token), group_link=update.message.text)
    if 'group_id' in result:
        context.user_data['org'].vk_group_id = result['group_id']
        await crud.org_set_vk_group_id(org=context.user_data['org'])
        await update.message.reply_text(ts.SET_INFO_VK_OK)
        context.user_data.pop('org')
        return ConversationHandler.END
    else:
        await update.message.reply_text(ts.SET_INFO_VK_GROUP_ERROR)
        await update.message.reply_text(result['error_msg'])
        return VK_TOKEN

#Функции публикации светофора
async def publish_everywhere(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async def send_to_admins(org_id :int, text :str):
        admin_users = await crud.get_org_admins(org_id)
        for admin_user in admin_users:
            await context.bot.send_message(chat_id=admin_user.tg_id, text=text)

    org = await crud.get_org_by_tg_id(tg_id=update.effective_user.id)
    if org:
        if not (org.vk_token and org.vk_group_id and org.yd_login and org.yd_pass):
            await update.message.reply_text(ts.NO_LOGIN_DATA)
        user = await crud.get_user(tg_id=update.effective_user.id)
        if org.yd_login and org.yd_pass and org.yd_station_id and org.yd_groups_ids and user.is_admin:
            if org.yd_last_pub_date and org.yd_last_pub_date > org.last_create_date:
                await update.message.reply_text(ts.ALREADY_PUB)
            else:
                await update.message.reply_text(ts.YD_PUB_POS)
                await publish_to_yd(login=decode_str(org.yd_login), password=decode_str(org.yd_pass),
                                    station_id=org.yd_station_id, group_ids=org.yd_groups_ids,
                                    group_vals=org.last_yd_str)
                await crud.set_yd_last_pub_date(org=org)
                await send_to_admins(org_id=org.id, text=ts.YD_PUB_SUCCESS)
        if org.vk_token and org.vk_group_id and user.is_admin:
            if org.vk_last_pub_date and org.vk_last_pub_date > org.last_create_date:
                await update.message.reply_text(ts.ALREADY_PUB)
            else:
                await update.message.reply_text(ts.VK_PUB_POS)
                post_id = await publish_to_vk(vk_token=decode_str(org.vk_token), org_dir=f'org{str(org.id)}',
                                              group_id=org.vk_group_id, is_pin=org.vk_is_pin_image,
                                              prev_post_id=org.vk_last_post_id, text=org.vk_last_light_post,
                                              image_name=org.last_image_name)
                if 'post_id' in post_id:
                    org.vk_last_post_id = post_id['post_id']
                    org.vk_last_pub_date = datetime.now()
                    await crud.set_vk_last_post_id(org=org)
                    await send_to_admins(org_id=org.id, text=ts.VK_PUB_SUCCESS)
                else:
                    await send_to_admins(org_id=org.id, text=ts.VK_PUB_FAIL)
    else:
        await update.message.reply_text(ts.NO_ORG_DATA)

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

    info_handler = ConversationHandler(
        entry_points=[CommandHandler('info', set_info_start)],
        states={
            ORG_RENAME: [MessageHandler(filters.TEXT & (~ filters.COMMAND), set_info_start)],
            ORG_NAME: [MessageHandler(filters.TEXT & (~ filters.COMMAND), set_info_org)],
            STEP_CHOICE: [MessageHandler(filters.TEXT & (~ filters.COMMAND), set_choice)],
            YD_LOGIN: [MessageHandler(filters.TEXT & (~ filters.COMMAND), get_yd_pass)],
            YD_PASS: [MessageHandler(filters.TEXT & (~ filters.COMMAND), get_yd_url)],
            YD_URL: [MessageHandler(filters.TEXT & (~ filters.COMMAND), get_vk_token)],
            VK_TOKEN: [MessageHandler(filters.TEXT & (~ filters.COMMAND), set_vk_token)],
            VK_GROUP_URL: [MessageHandler(filters.TEXT, set_vk_group_id)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    publish_handler = CommandHandler('pub', publish_everywhere)

    application.add_handler(start_handler)
    application.add_handler(image_handler)
    application.add_handler(info_handler)
    application.add_handler(publish_handler)

    application.run_polling()