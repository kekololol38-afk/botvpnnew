import os
import threading
import asyncio
from flask import Flask

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)


from database import (
    create_tables,
    add_user,
    get_user,
    activate_subscription
)



TOKEN = os.getenv("TOKEN")


ADMIN_ID = 8803797878



# =========================
# Flask для Render
# =========================


web_app = Flask(__name__)



@web_app.route("/")
def home():

    return "MoonVPN is running!"



def run_web():

    web_app.run(
        host="0.0.0.0",
        port=10000
    )



# =========================
# START
# =========================


async def start(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):


    add_user(
        update.effective_user
    )


    keyboard = [

        [
            InlineKeyboardButton(
                "🛒 КУПИТЬ / ПРОДЛИТЬ",
                callback_data="buy"
            )
        ],

        [
            InlineKeyboardButton(
                "👤 ЛИЧНЫЙ КАБИНЕТ",
                callback_data="profile"
            )
        ],

        [
            InlineKeyboardButton(
                "👥 ПРИГЛАСИТЬ ДРУГА",
                callback_data="invite"
            )
        ],

        [
            InlineKeyboardButton(
                "💬 ПОДДЕРЖКА",
                callback_data="support"
            )
        ]

    ]



    text = (

        "🚀 <b>Добро пожаловать в MoonVPN!</b>\n\n"

        "🌍 Быстрый и безопасный VPN\n"

        "⚡ Высокая скорость соединения\n"

        "🔒 Полная конфиденциальность\n\n"

        "Выберите нужный раздел:"

    )


    with open(
        "banner.png",
        "rb"
    ) as photo:


        await update.message.reply_photo(

            photo=photo,

            caption=text,

            parse_mode="HTML",

            reply_markup=InlineKeyboardMarkup(keyboard)

        )



# =========================
# ADMIN
# =========================


async def admin(

        update: Update,

        context: ContextTypes.DEFAULT_TYPE

):


    if update.effective_user.id != ADMIN_ID:

        await update.message.reply_text(
            "❌ Нет доступа"
        )

        return



    keyboard = [

        [

            InlineKeyboardButton(
                "📊 Статистика",
                callback_data="admin_stats"
            )

        ]

    ]



    await update.message.reply_text(

        "🔐 <b>Админ-панель MoonVPN</b>",

        parse_mode="HTML",

        reply_markup=InlineKeyboardMarkup(keyboard)

    )

# =========================
# BUTTONS
# =========================


async def buttons(

        update: Update,

        context: ContextTypes.DEFAULT_TYPE

):


    query = update.callback_query

    await query.answer()



    # =====================
    # ПОКУПКА
    # =====================


    if query.data == "buy":


        keyboard = [

            [
                InlineKeyboardButton(
                    "📱 1 устройство",
                    callback_data="device_1"
                )
            ],

            [
                InlineKeyboardButton(
                    "📱 2 устройства",
                    callback_data="device_2"
                )
            ],

            [
                InlineKeyboardButton(
                    "📱 3 устройства",
                    callback_data="device_3"
                )
            ],

            [
                InlineKeyboardButton(
                    "📱 5 устройств",
                    callback_data="device_5"
                )
            ]

        ]



        await query.edit_message_caption(

            caption=(

                "🛒 <b>Шаг 1 из 2</b>\n\n"

                "Выберите количество устройств:"

            ),

            parse_mode="HTML",

            reply_markup=InlineKeyboardMarkup(keyboard)

        )





    # =====================
    # ВЫБОР УСТРОЙСТВ
    # =====================


    elif query.data.startswith("device_"):


        devices = query.data.split("_")[1]



        keyboard = [

            [

                InlineKeyboardButton(
                    "📅 1 месяц",
                    callback_data=f"month_1_{devices}"
                )

            ],

            [

                InlineKeyboardButton(
                    "📅 3 месяца",
                    callback_data=f"month_3_{devices}"
                )

            ],

            [

                InlineKeyboardButton(
                    "📅 6 месяцев",
                    callback_data=f"month_6_{devices}"
                )

            ]

        ]



        await query.edit_message_caption(

            caption=(

                "🛒 <b>Шаг 2 из 2</b>\n\n"

                f"📱 Устройств: {devices}\n\n"

                "Выберите срок подписки:"

            ),

            parse_mode="HTML",

            reply_markup=InlineKeyboardMarkup(keyboard)

        )





    # =====================
    # ВЫБОР СРОКА
    # =====================


    elif query.data.startswith("month_"):


        data = query.data.split("_")


        months = data[1]

        devices = data[2]



        prices = {

            "1": {
                "1": 99,
                "2": 149,
                "3": 199,
                "5": 299
            },


            "3": {
                "1": 249,
                "2": 399,
                "3": 549,
                "5": 799
            },


            "6": {
                "1": 449,
                "2": 699,
                "3": 999,
                "5": 1499
            }

        }



        price = prices[months][devices]



        keyboard = [

            [

                InlineKeyboardButton(

                    "💳 ОПЛАТИТЬ",

                    callback_data=f"pay_{price}_{devices}_{months}"

                )

            ]

        ]



        await query.edit_message_caption(

            caption=(

                "🛒 <b>Ваш заказ</b>\n\n"

                f"📱 Устройства: {devices}\n"

                f"📅 Срок: {months} мес.\n"

                f"💰 Цена: {price}₽\n\n"

                "Нажмите оплатить:"

            ),

            parse_mode="HTML",

            reply_markup=InlineKeyboardMarkup(keyboard)

        )

    # =====================
    # ОПЛАТА (ТЕСТ)
    # =====================


    elif query.data.startswith("pay_"):


        data = query.data.split("_")


        price = data[1]

        devices = data[2]

        months = data[3]



        activate_subscription(

            query.from_user.id,

            int(devices),

            int(months)

        )



        await query.edit_message_caption(


            caption=(

                "✅ <b>Оплата прошла успешно!</b>\n\n"

                f"📱 Устройств: {devices}\n"

                f"📅 Срок: {months} месяцев\n"

                f"💰 Сумма: {price}₽\n\n"

                "🎉 Подписка активирована!"

            ),


            parse_mode="HTML",


            reply_markup=InlineKeyboardMarkup(

                [

                    [

                        InlineKeyboardButton(

                            "👤 Личный кабинет",

                            callback_data="profile"

                        )

                    ]

                ]

            )

        )





    # =====================
    # ЛИЧНЫЙ КАБИНЕТ
    # =====================


    elif query.data == "profile":


        user = get_user(

            query.from_user.id

        )



        if user:


            devices = user[4]

            expire = user[6]



            if devices == 0:

                devices = "Нет подписки"



            if expire is None:

                expire = "Нет"



            text = (

                "👤 <b>Личный кабинет</b>\n\n"

                f"🆔 ID: <code>{query.from_user.id}</code>\n"

                f"📱 Устройства: {devices}\n"

                f"📅 Действует до: {expire}"

            )


        else:


            text = "❌ Пользователь не найден"




        await query.edit_message_caption(


            caption=text,


            parse_mode="HTML",


            reply_markup=InlineKeyboardMarkup(

                [

                    [

                        InlineKeyboardButton(

                            "⬅️ Назад",

                            callback_data="menu"

                        )

                    ]

                ]

            )

        )





    # =====================
    # РЕФЕРАЛЫ
    # =====================


    elif query.data == "invite":



        bot_username = (

            await context.bot.get_me()

        ).username



        link = (

            f"https://t.me/{bot_username}"

            f"?start={query.from_user.id}"

        )



        await query.edit_message_caption(


            caption=(

                "👥 <b>Реферальная программа</b>\n\n"

                "Приглашайте друзей и получайте бонусы.\n\n"

                "Ваша ссылка:\n"

                f"{link}"

            ),


            parse_mode="HTML",


            reply_markup=InlineKeyboardMarkup(

                [

                    [

                        InlineKeyboardButton(

                            "⬅️ Назад",

                            callback_data="menu"

                        )

                    ]

                ]

            )

        )





    # =====================
    # ПОДДЕРЖКА
    # =====================


    elif query.data == "support":



        await query.edit_message_caption(


            caption=(

                "💬 <b>Поддержка MoonVPN</b>\n\n"

                "@support"

            ),


            parse_mode="HTML",


            reply_markup=InlineKeyboardMarkup(

                [

                    [

                        InlineKeyboardButton(

                            "⬅️ Назад",

                            callback_data="menu"

                        )

                    ]

                ]

            )

        )

    # =====================
    # НАЗАД В МЕНЮ
    # =====================


    elif query.data == "menu":


        keyboard = [

            [

                InlineKeyboardButton(
                    "🛒 КУПИТЬ / ПРОДЛИТЬ",
                    callback_data="buy"
                )

            ],

            [

                InlineKeyboardButton(
                    "👤 ЛИЧНЫЙ КАБИНЕТ",
                    callback_data="profile"
                )

            ],

            [

                InlineKeyboardButton(
                    "👥 ПРИГЛАСИТЬ ДРУГА",
                    callback_data="invite"
                )

            ],

            [

                InlineKeyboardButton(
                    "💬 ПОДДЕРЖКА",
                    callback_data="support"
                )

            ]

        ]



        await query.edit_message_caption(

            caption=(

                "🚀 <b>Добро пожаловать в MoonVPN!</b>\n\n"

                "🌍 Быстрый и безопасный VPN\n"

                "⚡ Высокая скорость соединения\n"

                "🔒 Полная конфиденциальность\n\n"

                "Выберите нужный раздел:"

            ),

            parse_mode="HTML",

            reply_markup=InlineKeyboardMarkup(keyboard)

        )





    # =====================
    # АДМИН СТАТИСТИКА
    # =====================


    elif query.data == "admin_stats":


        if query.from_user.id != ADMIN_ID:

            return



        from database import connect



        conn = connect()

        cursor = conn.cursor()



        cursor.execute(
            "SELECT COUNT(*) FROM users"
        )


        users_count = cursor.fetchone()[0]


        conn.close()



        await query.edit_message_text(


            text=(

                "📊 <b>Статистика MoonVPN</b>\n\n"

                f"👥 Пользователей: {users_count}"

            ),


            parse_mode="HTML"

        )





# =========================
# ЗАПУСК
# =========================


def main():

    asyncio.set_event_loop(
        asyncio.new_event_loop()
    )



    # запускаем Flask для Render

    threading.Thread(

        target=run_web,

        daemon=True

    ).start()



    create_tables()



    app = Application.builder().token(TOKEN).build()



    app.add_handler(

        CommandHandler(

            "start",

            start

        )

    )



    app.add_handler(

        CommandHandler(

            "admin",

            admin

        )

    )



    app.add_handler(

        CallbackQueryHandler(

            buttons

        )

    )



    print("✅ MoonVPN запущен!")



    app.run_polling(

        allowed_updates=Update.ALL_TYPES

    )





if __name__ == "__main__":

    main()