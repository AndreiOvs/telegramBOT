import telebot
from telebot import types
import requests
from PIL import Image, ImageFilter
import io

# Замените на ваш токен от BotFather
API_TOKEN = '8484634753:AAGA0MavOB7hzCZAUW2WCtBHao0yd7rXWqI'

# Создаем экземпляр бота
bot = telebot.TeleBot(API_TOKEN)

# Словарь для хранения выбора пользователя
user_choices = {}

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
🤖 Добро пожаловать в CipherBot!

Я умею:
• Шифровать текст шифром Цезаря
• Конвертировать текст в двоичный код
• Обрабатывать изображения

Доступные команды:
/start - начать работу
/help - помощь
/cipher - меню шифрования

Просто отправьте мне текст или изображение!
    """
    bot.reply_to(message, welcome_text)

# Команда /help
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
📖 Помощь по использованию бота:

🔐 Шифрование текста:
Используйте /cipher чтобы выбрать метод обработки текста

🔢 Двоичный код:
Выберите в меню "Двоичный код" и отправьте текст

🖼️ Обработка изображений:
Отправьте изображение, и я применю к нему фильтр и верну обратно.

💡 Как использовать:
1. Нажмите /cipher
2. Выберите тип обработки
3. Отправьте текст
4. Получите результат!
    """
    bot.reply_to(message, help_text)

# Команда /cipher
@bot.message_handler(commands=['cipher'])
def cipher_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton('🔐 Шифр Цезаря')
    btn2 = types.KeyboardButton('🔢 Двоичный код')
    btn3 = types.KeyboardButton('📝 Обычный текст')
    btn4 = types.KeyboardButton('❌ Скрыть меню')
    markup.add(btn1, btn2, btn3, btn4)
    
    bot.send_message(message.chat.id, 
                    "Выберите тип обработки текста:\n\n"
                    "🔐 Шифр Цезаря - зашифрует текст\n"
                    "🔢 Двоичный код - переведет в двоичную систему\n"
                    "📝 Обычный текст - просто покажет ваш текст\n"
                    "❌ Скрыть меню - уберет клавиатуру", 
                    reply_markup=markup)

# Функция шифра Цезаря
def caesar_cipher(text, shift=3):
    result = ""
    for char in text:
        if char.isalpha():
            if char.isupper():
                # Для русских букв
                if 'А' <= char <= 'Я':
                    result += chr((ord(char) + shift - 1040) % 32 + 1040)
                # Для английских букв
                elif 'A' <= char <= 'Z':
                    result += chr((ord(char) + shift - 65) % 26 + 65)
                else:
                    result += char
            else:
                # Для русских букв
                if 'а' <= char <= 'я':
                    result += chr((ord(char) + shift - 1072) % 32 + 1072)
                # Для английских букв
                elif 'a' <= char <= 'z':
                    result += chr((ord(char) + shift - 97) % 26 + 97)
                else:
                    result += char
        else:
            result += char
    return result

# Функция преобразования в двоичный код
def text_to_binary(text):
    binary_result = []
    for char in text:
        # Преобразуем символ в его числовое представление, затем в двоичный код
        binary_char = format(ord(char), '08b')
        binary_result.append(binary_char)
    return ' '.join(binary_result)

# Обработка выбора из меню
@bot.message_handler(func=lambda message: message.text in ['🔐 Шифр Цезаря', '🔢 Двоичный код', '📝 Обычный текст', '❌ Скрыть меню'])
def handle_menu_choice(message):
    user_id = message.chat.id
    
    if message.text == '🔐 Шифр Цезаря':
        user_choices[user_id] = 'caesar'
        bot.send_message(message.chat.id, "✅ Выбран Шифр Цезаря. Теперь отправьте текст для шифрования!")
        
    elif message.text == '🔢 Двоичный код':
        user_choices[user_id] = 'binary'
        bot.send_message(message.chat.id, "✅ Выбран Двоичный код. Теперь отправьте текст для преобразования!")
        
    elif message.text == '📝 Обычный текст':
        user_choices[user_id] = 'normal'
        bot.send_message(message.chat.id, "✅ Выбран Обычный текст. Теперь отправьте текст!")
        
    elif message.text == '❌ Скрыть меню':
        markup = types.ReplyKeyboardRemove()
        user_choices[user_id] = None
        bot.send_message(message.chat.id, 
                        "Клавиатура скрыта. Используйте /cipher чтобы вернуть меню.\n"
                        "Вы можете продолжать отправлять текст - бот будет выбирать метод случайно.",
                        reply_markup=markup)

# Обработка текстовых сообщений
@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = message.chat.id
    user_text = message.text
    
    # Пропускаем команды меню
    if user_text in ['🔐 Шифр Цезаря', '🔢 Двоичный код', '📝 Обычный текст', '❌ Скрыть меню']:
        return
    
    # Проверяем, есть ли выбор пользователя
    if user_id in user_choices and user_choices[user_id]:
        choice = user_choices[user_id]
    else:
        # Если выбора нет - случайный выбор
        import random
        choice = random.choice(['caesar', 'binary', 'normal'])
    
    # Обрабатываем текст в зависимости от выбора
    if choice == 'caesar':
        encrypted = caesar_cipher(user_text)
        response = f"🔐 **Шифр Цезаря (сдвиг 3):**\n`{encrypted}`"
        
    elif choice == 'binary':
        try:
            binary = text_to_binary(user_text)
            # Обрезаем если слишком длинное
            if len(binary) > 4000:
                binary = binary[:4000] + "...\n⚠️ Текст слишком длинный, показаны первые 4000 символов"
            response = f"🔢 **Двоичный код:**\n`{binary}`"
        except Exception as e:
            response = f"❌ Ошибка при преобразовании в двоичный код: {str(e)}"
            
    elif choice == 'normal':
        response = f"📝 **Ваш текст:**\n{user_text}"
    
    bot.send_message(message.chat.id, response, parse_mode='Markdown')

# Обработка изображений
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        # Получаем файл изображения
        file_info = bot.get_file(message.photo[-1].file_id)
        file = requests.get(f'https://api.telegram.org/file/bot{API_TOKEN}/{file_info.file_path}')
        
        # Открываем изображение
        image = Image.open(io.BytesIO(file.content))
        
        # Применяем фильтр (размытие)
        processed_image = image.filter(ImageFilter.GaussianBlur(2))
        
        # Сохраняем обработанное изображение в буфер
        bio = io.BytesIO()
        processed_image.save(bio, 'JPEG')
        bio.seek(0)
        
        # Отправляем обработанное изображение
        bot.send_photo(message.chat.id, photo=bio, caption="🖼️ Ваше изображение с примененным фильтром размытия!")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Произошла ошибка при обработке изображения: {str(e)}")

# Обработка других типов контента
@bot.message_handler(content_types=['document', 'audio', 'video', 'sticker'])
def handle_other(message):
    bot.reply_to(message, "❌ Этот тип контента пока не поддерживается. Отправьте текст или изображение.")

# Запуск бота
if __name__ == '__main__':
    print("Бот запущен...")
    bot.polling(none_stop=True)