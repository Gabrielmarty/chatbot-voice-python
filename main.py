

# INSTALAR DEPENDÊNCIAS:
# pip install openai gtts sounddevice scipy python-dotenv playsound

import os
import sounddevice as sd
from scipy.io.wavfile import write
from gtts import gTTS
from openai import OpenAI
from dotenv import load_dotenv

# =============================
# CONFIG
# =============================
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=API_KEY)

AUDIO_FILE = "audio.wav"
RESPONSE_AUDIO = "resposta.mp3"

# =============================
# 1. GRAVAR ÁUDIO
# =============================
def gravar_audio(segundos=5):
    fs = 44100
    print("🎤 Fale agora...")
    audio = sd.rec(int(segundos * fs), samplerate=fs, channels=1)
    sd.wait()
    write(AUDIO_FILE, fs, audio)
    print("✅ Áudio gravado!\n")

# =============================
# 2. TRANSCRIÇÃO (WHISPER)
# =============================
def transcrever_audio():
    with open(AUDIO_FILE, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )
    print("🧠 Você disse:", transcript.text, "\n")
    return transcript.text

# =============================
# 3. CHATGPT
# =============================
def gerar_resposta(texto):
    resposta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um assistente útil e responde em português."},
            {"role": "user", "content": texto}
        ]
    )
    resposta_texto = resposta.choices[0].message.content
    print("🤖 ChatGPT:", resposta_texto, "\n")
    return resposta_texto

# =============================
# 4. TEXTO → VOZ
# =============================
def falar_resposta(texto):
    from gtts import gTTS
    import pygame

    tts = gTTS(texto, lang="pt")
    tts.save(RESPONSE_AUDIO)

    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(RESPONSE_AUDIO)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        continue
# =============================
# LOOP PRINCIPAL
# =============================
def main():
    print("=== Assistente por Voz iniciado ===\n")
    while True:
        try:
            gravar_audio(5)
            texto = transcrever_audio()

            if "sair" in texto.lower():
                print("👋 Encerrando...")
                break

            resposta = gerar_resposta(texto)
            falar_resposta(resposta)

        except Exception as e:
            print("❌ Erro:", e)

# =============================
# EXECUÇÃO
# =============================
if __name__ == "__main__":
    main()
