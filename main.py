import telebot
import requests
import jsons
from Class_ModelResponse import ModelResponse

# Замените 'YOUR_BOT_TOKEN' на ваш токен от BotFather
API_TOKEN = '7636771912:AAFgs8HxkzssDBwiC_EhaVmQWvAG9x9k7mk'
bot = telebot.TeleBot(API_TOKEN)

# контекст диалога
user_data = {}

# Команды
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Привет! Я ваш Telegram бот.\n"
        "Доступные команды:\n"
        "/start - вывод всех доступных команд\n"
        "/model - выводит название используемой языковой модели\n"
        "/clear - очистка контекста\n"
        "Отправьте любое сообщение, и я отвечу с учетом предыдущих сообщений."
    )
    bot.reply_to(message, welcome_text)


@bot.message_handler(commands=['model'])
def send_model_name(message):
    # Запрос к LM Studio для получения информации о модели
    response = requests.get('http://localhost:1234/v1/models')

    if response.status_code == 200:
        model_info = response.json()
        model_name = model_info['data'][0]['id']
        bot.reply_to(message, f"Используемая модель: {model_name}")
    else:
        bot.reply_to(message, 'Не удалось получить информацию о модели.')


@bot.message_handler(commands=['clear'])
def clear_context(message):
    user_data[message.chat.id] = []  # Очистка контекста для данного пользователя
    bot.reply_to(message, "Контекст очищен.")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    
    # Инициализируем контекст для нового пользователя, если его еще нет
    if user_id not in user_data:
        user_data[user_id] = []

    # Добавляем текущее сообщение пользователя в контекст
    user_data[user_id].append({"role": "user", "content": message.text})

    request = {
        "messages": user_data[user_id]
    }

    # Отправляем запрос к LM Studio
    response = requests.post(
        'http://localhost:1234/v1/chat/completions',
        json=request
    )

    if response.status_code == 200:
        model_response: ModelResponse = jsons.loads(response.text, ModelResponse)
        bot_response = model_response.choices[0].message.content
        
        # Добавляем ответ модели в контекст
        user_data[user_id].append({"role": "assistant", "content": bot_response})
        
        bot.reply_to(message, bot_response)
    else:
        bot.reply_to(message, 'Произошла ошибка при обращении к модели.')

# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)