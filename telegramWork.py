
import telebot
from telebot import types
from chat import GPT
from workRedis import *
import os 
from dotenv import load_dotenv
from loguru import logger
from pprint import pprint
import speech_recognition as sr
import uuid
import time

load_dotenv()

bot = telebot.TeleBot(os.getenv('TOKEN'))
# bot = telebot.TeleBot('TOKEN')
gpt = GPT()
GPT.set_key(os.getenv('KEY_AI'))
USERS = {}


language='ru_RU'
r = sr.Recognizer()

def recognise(filename):
    with sr.AudioFile(filename) as source:
        audio_text = r.listen(source)
        try:
            text = r.recognize_google(audio_text,language=language)
            print('Converting audio transcripts into text ...')
            print(text)
            return text
        except:
            print('Sorry.. run again...')
            return "Sorry.. run again..."

@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    text = message.text
    logger.debug(f'{text=}')
    filename = str(uuid.uuid4())
    file_name_full="voice/"+filename+".ogg"
    file_name_full_converted="ready/"+filename+".wav"
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open(file_name_full, 'wb') as new_file:
        new_file.write(downloaded_file)
    time.sleep(1)
    os.system("ffmpeg -i "+file_name_full+"  "+file_name_full_converted)
    time.sleep(1) 
    text=recognise(file_name_full_converted)
    bot.reply_to(message, text)
    os.remove(file_name_full)
    os.remove(file_name_full_converted)
    a = message.text
    print(f'{a=}')
    message.text = text
    a = message.text
    print(f'{a=}')

    print(f'{message=}')
    send_text(message)    

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет, я бот, который отвечает на вопросы. Напиши мне что-нибудь. Сейчас вы работаете с open_ai_assign.')
    USERS[message.chat.id] = 'gpt'
    clear_history(message.chat.id)

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, 'Подключенные нейросети: \n/gpt \n/yandex \n/giga \n/start - начать все заново(сбросить контекст) Чтобы переключится на другого бота введите /имя_бота')
    # bot.send_message(message.chat.id, 'Подключенные нейросети: \n/gpt \n/yandex \n/giga\n/open_ai_assign - чтобы вести диалог с asst_iFpmwH8rOc2faiQ0pH3mgPTR \n/start - начать новый диалог (сбросить контекст)\nЕсли вы хотите сгенерировать изображение, то введите /image промт изображения одной коммандой')

@bot.message_handler(commands=['gpt'])
def openai(message):
    bot.send_message(message.chat.id, 'Вы переключились на gpt')
    USERS[message.chat.id] = 'gpt'

@bot.message_handler(commands=['yandex'])
def yandex(message):
    bot.send_message(message.chat.id, 'Вы переключились на yandex')
    USERS[message.chat.id] = 'yandex'

@bot.message_handler(commands=['giga'])
def gigachat(message):
    bot.send_message(message.chat.id, 'Вы переключились на giga')
    USERS[message.chat.id] = 'giga'

@bot.message_handler(commands=['open_ai_assign'])
def open_ai_assign(message):
    bot.send_message(message.chat.id, 'Вы переключились на open_ai_assign')
    USERS[message.chat.id] = 'open_ai_assign'



@bot.message_handler(content_types=['text'])
@logger.catch
def send_text(message):
    text= message.text
    try:
        model = USERS[message.chat.id]
    except:
        USERS[message.chat.id] = 'open_ai_assign'

    add_message_to_history(message.chat.id, 'user', message.text)
    history = get_history(message.chat.id)
    pprint(history)
    # if history is None:
    #     history = []

    if text.startswith('/image'):
        text = text.replace('/image ', '')
        url = gpt.create_image(promt=text)
        bot.send_photo(message.chat.id, url)
        return 0

    promt = 'Ты бот-помошник, который помогает пользователю решить его проблемы.'
    answer = gpt.answer(promt, history, 1, MODEL=model)[0]
    bot.send_message(message.chat.id, answer)

   
    add_message_to_history(message.chat.id, 'assistant', answer)


       


if __name__ == '__main__':
    # bot.infinity_polling()


    print('bot started')
    bot.infinity_polling()
    


# if __name__ == '__main__':
    # main()
# a = gpt.answer('Какие факторы влияют на стоимость страховки на дом?',[],1,MODEL='giga')
# a = gpt.answer('Какие факторы влияют на стоимость страховки на дом?',[],1,MODEL='yandex')
# print(a)



