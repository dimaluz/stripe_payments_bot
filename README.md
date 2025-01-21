# Telegram Bot with Stripe Integration

This project implements a Telegram bot integrated with the Stripe payment system to generate payment links for products and handle webhook events.

## Features

- Generate Stripe payment links directly from the Telegram bot.
- Process Stripe webhook events to confirm payment status.
- Support for test mode in Stripe for safe testing.

---

## Prerequisites

### 1. Stripe Setup

1. [Create a Stripe account](https://stripe.com/).
2. In the Stripe Dashboard, navigate to the **Products** section and add test products.
3. Enable **test mode** in Stripe for using test credit cards.
4. Obtain your `STRIPE_SECRET_KEY` from the Developer section.
5. Install the [Stripe CLI](https://stripe.com/docs/stripe-cli) (optional for local testing of webhooks).

### 2. Telegram Bot Setup

1. Create a bot using [BotFather](https://core.telegram.org/bots#botfather).
2. Copy the `TELEGRAM_TOKEN` provided after creating the bot.
3. Install Python 3.10+ and `virtualenv`.

---

## Installation

### Step 1: Clone the Repository

```bash
$ git clone https://github.com/your-username/telegram-stripe-bot.git
$ cd telegram-stripe-bot
```

### Step 2: Set Up a Virtual Environment

```bash
$ python3 -m venv .venv
$ source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
$ pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root and configure it as follows:

```env
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
TELEGRAM_TOKEN=your_telegram_token
DOMAIN_URL=https://your-ngrok-url.ngrok.io  # Replace with your actual ngrok forwarding URL
PRICE_ID_FIRST_PRODUCT=price_id_for_your_product_1
PRICE_ID_SECOND_PRODUCT=price_id_for_your_product_2
```

---

## Usage

### Step 1: Run ngrok for Webhook Testing

```bash
$ ngrok http 8000
```

Copy the HTTPS URL provided by ngrok and update the `DOMAIN_URL` in your `.env` file.

### Step 2: Run the Bot

```bash
$ python main.py
```

### Step 3: Set Stripe Webhook URL

In the Stripe Dashboard, configure your webhook endpoint as follows:

```
https://<your-ngrok-url>/webhook
```

Set events to listen for:
- `checkout.session.completed`
- `payment_intent.succeeded`
- `payment_intent.payment_failed`

---

## How to Interact with the Bot

1. Start a conversation with your bot on Telegram.
2. Use the command `/choose_product` to get a Stripe payment link for a product.
3. Complete the payment using Stripe's test card details:

   - **Card Number**: `4242 4242 4242 4242`
   - **Expiration Date**: Any future date
   - **CVC**: Any 3 digits

4. The bot will confirm the payment status.

---

## Possible Errors and Solutions

### 1. **Invalid Webhook Signature**
   - Ensure the `STRIPE_WEBHOOK_SECRET` matches the one provided in Stripe.

### 2. **Ngrok Tunnel Error**
   - Check if ngrok is running and the `DOMAIN_URL` in `.env` matches the ngrok URL.

### 3. **Telegram Bot Token Invalid**
   - Ensure the `TELEGRAM_TOKEN` is correct and the bot is active.

### 4. **Unresponsive Bot**
   - Verify that the bot process is running and that network access is enabled.

---

## Dependencies

- Python 3.10+
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Stripe Python Library](https://github.com/stripe/stripe-python)
- Flask
- python-dotenv

---

## License

This project is licensed under the MIT License.

---

## Author

Dmitrii
