import io
import threading
import time
import speech_recognition as sr
from gtts import gTTS
from deep_translator import GoogleTranslator
from googletrans import LANGUAGES
import pygame
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import StringProperty

Window.clearcolor = (0.1, 0.1, 0.3, 1)  # Dark blue

recognizer = sr.Recognizer()
pygame.mixer.init()
class TranslatorLayout(BoxLayout):
    speaking_text = StringProperty("")
    translated_text = StringProperty("")
    input_lang = StringProperty("")
    output_lang = StringProperty("")
    running = False

    def start_listening(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.listen_and_translate, daemon=True).start()

    def stop_listening(self):
        self.running = False

    def get_lang_code(self, name):
        name = name.lower()
        for code, lang_name in LANGUAGES.items():
            if lang_name.lower() == name:
                return code
        return None

    def speak(self, text, lang_code):
        tts = gTTS(text=text, lang=lang_code)
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        pygame.mixer.music.load(mp3_fp)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

    def listen_and_translate(self):
        while self.running:
            s = self.get_lang_code(self.input_lang)
            t = self.get_lang_code(self.output_lang)

            if not s or not t:
                self.speaking_text = "Invalid language input."
                return

            self.speaking_text = "🎤 Listening..."
            with sr.Microphone() as source:
                try:
                    audio = recognizer.listen(source)
                    text = recognizer.recognize_google(audio, language=s)
                    translated = GoogleTranslator(source=s, target=t).translate(text)

                    def update_ui():
                        self.speaking_text += f"\n{text}"
                        self.translated_text += f"\n{translated}"

                    Clock.schedule_once(lambda dt: update_ui())
                    self.speak(translated, t)

                except Exception as e:
                    Clock.schedule_once(lambda dt: setattr(self, "speaking_text", "⏳ No speech detected."))


class TranslatorApp(App):
    def build(self):
        self.title = "Real Time Voice Translator"
        Window.size = (400, 700)
        return TranslatorLayout()

if __name__ == '__main__':
    TranslatorApp().run()
