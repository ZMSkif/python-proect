import openai
import speech_recognition as sr
from gtts import gTTS 
import io
import pygame
import requests
from bs4 import BeautifulSoup

# Authenticate with OpenAI's API
try:
    openai.api_key = "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"
except Exception as e:
    print("Ошибка при аутентификации с OpenAI API:")
    print(str(e))

# Function to process user query and return relevant results
def complete_query(prompt):
    # Check if prompt is a search query
    if prompt.lower().startswith("search google for"):
        # Execute the search and parse the results
        query = prompt[18:]
        url = f"https://www.google.com/search?q={query}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        results = [h3.text for h3 in soup.select("#search div.r h3")]
        return "\n".join(results[:3])
    else:
        # Execute the GPT-3 prompt completion
        response = openai.Completion.create(
            engine="davinci", prompt=prompt, max_tokens=1024, n=1, stop=None, temperature=0.5,
        )
        message = response.choices[0].text.strip()
        return message

# Function to recognize user speech
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

# Function to synthesize text as speech
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
    # Recognize user speech and ask for confirmation
    query = recognize_speech()
    speak_text(f"Вы сказали: {query}. Это то, что вы хотели узнать?")

    # Process user query and speak the response
    response = complete_query(f"respond to \"{query}\"")
    speak_text(response)

    # Quit pygame mixer
    pygame.mixer.quit()