import openai
import speech_recognition as sr
from gtts import gTTS 
import io
import pygame
import requests
from bs4 import BeautifulSoup

# Аутентификация в OpenAI API
try:
    openai.api_key = "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"
except Exception as e:
    print("Ошибка при аутентификации с OpenAI API:")
    print(str(e))

# Функция для обработки запроса пользователя и возврата соответствующих результатов
def complete_query(prompt):
    if prompt.lower().startswith("найди мне") or prompt.lower().startswith("я хочу найти"):
        # Искать в Google и парсить результаты
        query = prompt[11:]
        url = f"https://www.google.com/search?q={query}&hl=ru"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        results = [h3.text for h3 in soup.select("#search div.r h3")]
        return "\n".join(results[:3])
    else:
        # Использовать API OpenAI для получения ответа
        response = openai.Completion.create(
            engine="davinci", prompt=prompt, max_tokens=1024, n=1, stop=None, temperature=0.5,
        )
        message = response.choices[0].text.strip()
        return message

# Функция для распознавания речи пользователя
def recognize_speech():
    r = sr.Recognizer() 
    with sr.Microphone(device_index=0) as source: 
        print("Скажите что-нибудь!")
        try:
            audio = r.listen(source, timeout=5)
            query = r.recognize_google(audio, language="ru-RU")
            print(f"Вы сказали: {query}")
        except sr.UnknownValueError:
            print("Не удалось распознать вашу речь")
            query = ""
        except Exception as e:
            print("Ошибка в процессе распознавания речи:")
            print(str(e))
            query = ""
    return query

# Функция для синтеза текста в речь
def speak_text(text):
    try:
        tts = gTTS(text=text, lang="ru")
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        pygame.mixer.init()
        pygame.mixer.music.load(fp)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
    except Exception as e:
        print("Ошибка в процессе синтеза речи:")
        print(str(e))

if __name__ == "__main__":
    # Распознать речь пользователя и запросить подтверждение
    query = recognize_speech()
    speak_text(f"Вы сказали: {query}. Это то, что вы хотели узнать?")

    # Обработать запрос пользователя и выдать ответ в речи
    response = complete_query(query)
    speak_text(response)

    # Завершить работу pygame mixer
    pygame.mixer.quit()
