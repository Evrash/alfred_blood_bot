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
    user: User = await crud.get_user(tg_id=update.effective_user.id)
    if not user:
        user = await crud.create_user(tg_id=update.effective_user.id)
    if user.organisation_id is None:
        # context.user_data['User'] = User.get(User.telegram_chat_id == update.effective_user.id)
        message = ts.SET_INFO_ORG_NAME
        await update.message.reply_text(message)
        return ORG_NAME
    else:
        await update.message.reply_text(ts.SET_INFO_DBL_REG)
        return ConversationHandler.END

async def set_info_org(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    message = ts.SET_INFO_EXPL
    await update.message.reply_text(message)
    message = ts.SET_INFO_EXPL_QUEST
    reply_keyboard = [[ts.BTN_GRANT_ALL], [ts.BTN_GRANT_VK], [ts.BTN_GRANT_VK], [ts.BTN_GRANT_NONE]]
    await update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return STEP_CHOICE

async def yd_ids(url, login, password):
    s = requests.Session()
    r = s.post('https://adm.yadonor.ru/index.php?obj=BLOOD_STATIONS', data={'login': login, 'password': password})
    # TODO: добавить проверку ту ли ссылку нам пихнули
    params_url = url.split('?')[1]
    station_id = ''
    for param in params_url.split('&'):
        if param.split('=')[0] == 'BLOOD_STATIONS_ID':
            station_id = param.split('=')[1]
    r = s.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    soup = soup.find_all(attrs={'name': re.compile('reserv')})
    groups = []
    for block in soup:
        if block.get('name')[7:10] not in groups:
            groups.append(block.get('name')[7:10])
    # print(groups)
    ready_groups = [groups[0], groups[4], groups[1], groups[5], groups[2], groups[6], groups[3], groups[7]]
    return ready_groups, station_id

async def get_vk_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Если отдаёт всё, то сначала сохраняем параметры ЯД
    if context.user_data['choice'] in [3, 1]:
        DB.connect(reuse_if_open=True)
        groups, station_id = yd_ids(url=update.message.text, login=decode_str(context.user_data['org'].yd_login),
                                    password=decode_str(context.user_data['org'].yd_pass))
        context.user_data['org'].yd_station_id = station_id
        context.user_data['org'].yd_groups_ids = ','.join(groups)
        context.user_data['org'].save()
        if context.user_data['choice'] == 1:
            await update.message.reply_text(tstr.SET_INFO_YD_OK)
            DB.close()
            return ConversationHandler.END
        else:
            await update.message.reply_text(f"{tstr.SET_INFO_YD_OK} Займёмся ВК")
    message = tstr.SET_INFO_VK_TOKEN
    await update.message.reply_text(message, reply_markup=ReplyKeyboardRemove())
    DB.close()
    return VK_TOKEN

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