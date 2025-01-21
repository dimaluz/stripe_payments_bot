import stripe
from flask import (
    Flask, 
    request, 
    jsonify, 
    render_template,
)
from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler, 
    CallbackContext,
)
from decouple import config
import threading

# Инициализация ключей Stripe и Flask
stripe.api_key = config("STRIPE_SECRET_KEY")  # Ваш секретный ключ Stripe
endpoint_secret = config("STRIPE_WEBHOOK_SECRET")  # Секрет вебхука
server_url = config("SERVER_URL")

PRODUCTS = {
    "Arbitrage base": config("PRICE_ID_FIRST_PRODUCT"),
    "Arbitrage start": config("PRICE_ID_SECOND_PRODUCT")
}

app = Flask(__name__)

# Telegram API токен
TELEGRAM_TOKEN = config("TELEGRAM_TOKEN")

# Хост и порт сервера Flask
HOST = "0.0.0.0"
PORT = 4242


# Telegram-бот
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Добро пожаловать в платежный бот!\n\n"
        "Используйте команду /choose_product, чтобы выбрать продукт и получить ссылку на оплату."
    )


# Функция для отправки кнопок выбора продукта
async def choose_product(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Arbitrage base", callback_data="Arbitrage base")],
        [InlineKeyboardButton("Arbitrage start", callback_data="Arbitrage start")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите продукт для оплаты:", reply_markup=reply_markup)


# Функция для обработки выбора продукта
async def pay(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    # Получаем выбранный продукт
    chosen_product = query.data
    price_id = PRODUCTS.get(chosen_product)

    if price_id:
        # Создаем Stripe-сессию для выбранного продукта
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price": price_id,  # Используем price_id выбранного продукта
                    "quantity": 1,
                }],
                mode="subscription",
                success_url=f"{server_url}/success",
                cancel_url=f"{server_url}/cancel",
            )
            # Отправляем ссылку на оплату
            await query.edit_message_text(
                f"Вы выбрали продукт: {chosen_product}\n"
                f"Вот ваша ссылка для оплаты: {session.url}\n\n"
                "Оплатите, чтобы завершить заказ."
            )
        except Exception as e:
            await query.edit_message_text(f"Произошла ошибка при создании платежной сессии: {e}")
    else:
        await query.edit_message_text("Выбранный продукт не найден.")


# Flask обработчик вебхуков
@app.route('/success')
def success():
    return render_template("success.html")


@app.route('/cancel')
def cancel():
    return render_template("cancel.html")


@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.data
    sig_header = request.headers.get("STRIPE_SIGNATURE", None)
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError as e:
        return "Invalid signature", 400

    # Обработка события Stripe
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print(f"Payment succeeded for session {session['id']}")
    elif event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        print(f"PaymentIntent succeeded: {payment_intent['id']}")
    elif event["type"] == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]
        print(f"Payment failed: {payment_intent['last_payment_error']['message']}")
    else:
        print(f"Unhandled event type {event['type']}")

    return jsonify(success=True)


# Функция для запуска Flask в отдельном потоке
def run_flask():
    print(f"Запуск Flask-сервера на {HOST}:{PORT}")
    app.run(host=HOST, port=PORT)


# Основной запуск Telegram-бота и Flask
def main():
    # Telegram-бот
    bot = Application.builder().token(TELEGRAM_TOKEN).build()

    # Обработчики команд
    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(CommandHandler("choose_product", choose_product))
    bot.add_handler(CallbackQueryHandler(pay))

    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Запуск Telegram-бота
    print("Запуск Telegram-бота...")
    bot.run_polling()


if __name__ == "__main__":
    main()
