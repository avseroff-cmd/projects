import telebot
import os
from telebot import apihelper
import moviepy.editor as mp
import random
from queue import Queue
import threading
import time

TOKEN = ''

bot = telebot.TeleBot(TOKEN)

user_data = {}
queue = Queue()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id not in user_data:
        user_data[message.chat.id] = {}
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Сгенерируй рилс!')
    bot.reply_to(message, "Привет🤗 Отправь мне горизонтальное видео в формате 16:9, а затем выбери фон для твоего видео", reply_markup=markup)

@bot.message_handler(content_types=['video'])
def handle_video(message):
    if message.chat.id not in user_data:
        user_data[message.chat.id] = {}

    try:
        file_info = bot.get_file(message.video.file_id)
        file_size = file_info.file_size
        if file_size > 20 * 1024 * 1024:
            bot.reply_to(message, "Видео слишком большое, отправь видео до 20 Мб 🥺")
            return

        downloaded_file = bot.download_file(file_info.file_path)
        current_dir = os.path.dirname(__file__)
        video_dir = os.path.join(current_dir, 'videos')
        os.makedirs(video_dir, exist_ok=True)
        file_name = os.path.basename(file_info.file_path)
        src = os.path.join(video_dir, file_name)
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)

        video = mp.VideoFileClip(src)
        aspect_ratio = video.w / video.h
        if abs(aspect_ratio - 16 / 9) > 0.1:
            bot.reply_to(message, "Пожалуйста, отправь ГОРИЗОНТАЛЬНОЕ видео в формате 16:9 😵‍💫")
            video.close()
            os.remove(src)
            return

        bot.reply_to(message, "Я его сохранил 🤩")
        user_data[message.chat.id]['video'] = src

        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('GTA V', 'Гидропресс', 'Ковры', 'CarCrash')
        bot.reply_to(message, "Выбери фон для твоего видео 🤩", reply_markup=markup)

    except Exception as e:
        bot.reply_to(message, "Произошла ошибка, попробуйте отправить видео заново")
        print(f"Ошибка при обработке видео: {e}")

@bot.message_handler(func=lambda message: message.text in ['GTA V', 'Гидропресс', 'Ковры', 'CarCrash'])
def choose_background(message):
    if message.chat.id not in user_data:
        user_data[message.chat.id] = {}
    background_dir = os.path.join(os.path.dirname(__file__), 'backgrounds')
    background_path = os.path.join(background_dir, message.text + '.mp4')
    user_data[message.chat.id]['background'] = background_path
    
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Сгенерируй рилс!')
    bot.reply_to(message, "Фон выбран! Жми 'Сгенерируй рилс!' чтобы начать обработку 🤩", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Сгенерируй рилс!')
def generate_reel(message):
    if message.chat.id not in user_data:
        user_data[message.chat.id] = {}

    if 'video' not in user_data[message.chat.id] or 'background' not in user_data[message.chat.id]:
        bot.reply_to(message, "Ты должен отправить мне видео и выбрать фон 😵‍💫")
        return

    if message.chat.id in [item[0] for item in queue.queue]:
        bot.reply_to(message, "Ты уже в очереди на обработку. Подожди своей очереди 😵‍💫")
        return

    queue.put((message.chat.id, queue.qsize() + 1))

    bot.reply_to(message, f"Твое место в очереди - {queue.qsize()}. Обработка займет несколько минут, в зависимости от очереди ⌛")
    print(f"в очереди - {queue.qsize()} пользователей")

def process_queue():
    while True:
        try:
            user_id, queue_number = queue.get()
            if 'video' not in user_data[user_id] or 'background' not in user_data[user_id]:
                bot.send_message(user_id, "Ты должен отправить мне видео и выбрать фон 😵‍💫")
                queue.task_done()
                continue

            video_path = user_data[user_id]['video']
            background_path = user_data[user_id]['background']

            main_video = mp.VideoFileClip(video_path)
            background_video = mp.VideoFileClip(background_path)

            main_duration = main_video.duration

            start_time = random.uniform(0, background_video.duration - main_duration)
            background_video = background_video.subclip(start_time, start_time + main_duration)

            aspect_ratio = 9 / 8

            main_width = int(960 * main_video.w / main_video.h)
            main_resized = main_video.resize(height=960, width=main_width)

            back_width = int(960 * background_video.w / background_video.h)
            back_resized = background_video.resize(height=960, width=back_width)

            target_width = int(960 * aspect_ratio)

            main_left_edge = (main_resized.w - target_width) // 2
            main_right_edge = main_left_edge + target_width
            main_cropped = main_resized.crop(x1=main_left_edge, x2=main_right_edge)

            back_left_edge = (back_resized.w - target_width) // 2
            back_right_edge = back_left_edge + target_width
            back_cropped = back_resized.crop(x1=back_left_edge, x2=back_right_edge)

            dummy_video = mp.ColorClip((target_width, 960 + 960), color=(0, 0, 0), duration=main_duration)

            main_resized = main_cropped.set_position((0, 0))

            background_clip = back_cropped.set_position((0, 960))

            main_audio = mp.AudioFileClip(video_path)

            final_video = mp.CompositeVideoClip([dummy_video, background_clip, main_resized])
            final_video.audio = main_audio
            final_video = final_video.resize((1080, 1920))

            final_video.write_videofile("output.mp4", fps=25, codec='libx264', audio_codec='aac')
            final_video.write_videofile("output.mov", fps=25, codec='libx264', audio_codec='aac')
            
            final_video.close()
            main_video.close()
            background_video.close()

            bot.send_message(user_id, "Готово! Сейчас отправлю тебе видео 🥰")

            with open("output.mp4", 'rb') as f:
                bot.send_document(user_id, f, caption="Твой рилс- формат MP4 🤩")

            with open("output.mov", 'rb') as f:
                bot.send_document(user_id, f, caption="Твой рилс- формат MOV 🤩")

            time.sleep(1)  
            user_data[user_id] = {}

            queue.task_done()

        except Exception as e:
            bot.send_message(user_id, "Произошла ошибка🥺 Попробуйте отправить видео заново")
            print(f"Ошибка при обработке видео: {e}")
            queue.task_done()

if __name__ == '__main__':
    threading.Thread(target=process_queue).start()
    bot.infinity_polling()
