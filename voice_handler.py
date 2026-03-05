import logging
import os
import tempfile
from typing import Optional
from faster_whisper import WhisperModel
from pyrogram import filters

logger = logging.getLogger("parser.voice_handler")

# Инициализация Whisper
VOICE_MODEL = "medium"
voice_model = None


def get_voice_model():
    """Загружает модель Whisper с кэшированием"""
    global voice_model
    if voice_model is None:
        logger.info(f"Загрузка модели Whisper: {VOICE_MODEL}")
        voice_model = WhisperModel(VOICE_MODEL, device="auto", compute_type="int8")
        logger.info("Whisper готов!")
    return voice_model


async def transcribe_voice(audio_path: str) -> str:
    """Распознаёт речь из аудиофайла"""
    try:
        model = get_voice_model()
        
        # Транскрибация
        segments, info = model.transcribe(
            audio_path,
            beam_size=5,
            language="ru"  # Русский язык
        )
        
        text = "".join(segment.text for segment in segments)
        logger.info(f"Распознано: {text}")
        return text.strip()
        
    except Exception as e:
        logger.error(f"Ошибка транскрипции: {e}", exc_info=True)
        return None


async def convert_audio(input_path: str, output_format: str = "wav") -> str:
    """Конвертирует аудио (OGG → WAV для Whisper)"""
    try:
        from pydub import AudioSegment
        
        audio = AudioSegment.from_file(input_path)
        
        # Создаём временный файл
        temp_file = tempfile.NamedTemporaryFile(
            delete=False, 
            suffix=f".{output_format}"
        )
        audio.export(temp_file.name, format=output_format)
        
        logger.info(f"Конвертация: {input_path} → {temp_file.name}")
        return temp_file.name
        
    except Exception as e:
        logger.error(f"Ошибка конвертации: {e}", exc_info=True)
        return None


async def handle_voice_message(message, db, registry):
    """Обработчик голосовых сообщений"""
    try:
        # Получаем файл
        file = await message.download()
        
        # Конвертируем OGG → WAV
        wav_path = await convert_audio(file)
        
        if not wav_path:
            await message.answer("❌ Не смог обработать голосовое сообщение")
            return
        
        # Транскрибируем
        text = await transcribe_voice(wav_path)
        
        if not text:
            await message.answer("❌ Не удалось распознать речь")
            return
        
        # Отправляем текст и ответ
        await message.answer(f"🎤 **Голосовое:**\n{text}")
        
        # Удаляем временный файл
        os.unlink(wav_path)
        
    except Exception as e:
        logger.error(f"Ошибка обработки голосового: {e}", exc_info=True)
        await message.answer("❌ Ошибка при обработке")


def register_voice_handler(app, db, registry):
    """Регистрирует хендлер голосовых сообщений"""
    @app.on_message(filters.voice)
    async def on_voice_message(client, message):
        await handle_voice_message(message, db, registry)
        logger.info(f"Обработан голосовой от {message.from_user.username}")
