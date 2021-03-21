#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Настройки ядра
"""

# ######################################################################################################################
# Импорт необходимых инструментов
# ######################################################################################################################
from typing import List  # Типы данных

# Персональные
from neweraai.modules.core.messages import Messages  # Сообщения

# ######################################################################################################################
# Настройки ядра
# ######################################################################################################################
class Settings(Messages):
    """Настройки ядра"""

    # ------------------------------------------------------------------------------------------------------------------
    # Конструктор
    # ------------------------------------------------------------------------------------------------------------------

    def __init__(self):
        super().__init__()  # Выполнение конструктора из суперкласса

        self.text_runtime: str = self._('Время выполнения')  # Текст времени выполнения
        self.color_runtime: str = '#666'  # Цвет текста
        self.bold_runtime: bool = True  # Жирность текста

        self.path_to_original_videos: str = ''  # Директория для анализа и обработки
        self.sub_folder: List[str] = ['Original', 'Splitted', 'Annotated']  # Названия каталогов для обработки видео
        self.ext_video: List[str] = []  # Расширения искомых видеофайлов
        self.ext_audio: str = ''  # Расширение для создаваемого аудиофайла

    # ------------------------------------------------------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------------------------------------------------------

    # Получение текста времени выполнения
    @property
    def text_runtime(self): return self._text_runtime

    # Установка текста времени выполнения
    @text_runtime.setter
    def text_runtime(self, text):
        if type(text) is not str or len(text) < 1: return self._text_runtime
        else: self._text_runtime = text

    # Получение цвета текста времени выполнения
    @property
    def color_runtime(self): return self._color_runtime

    # Установка цвета текста времени выполнения
    @color_runtime.setter
    def color_runtime(self, color): self._color_runtime = color

    # Получение жирности текста времени выполнения
    @property
    def bold_runtime(self): return self._bold_runtime

    # Установка жирности текста времени выполнения
    @bold_runtime.setter
    def bold_runtime(self, bold): self._bold_runtime = bold

    # Получение директории для анализа и обработки
    @property
    def path_to_original_videos(self): return self._path_to_original_videos

    # Установка директории для анализа и обработки
    @path_to_original_videos.setter
    def path_to_original_videos(self, path): self._path_to_original_videos = path

    # Получение названий каталогов для обработки видео
    @property
    def sub_folder(self): return self._sub_folder

    # Установка названий каталогов для обработки видео
    @sub_folder.setter
    def sub_folder(self, name): self._sub_folder = name

    # Получение расширения искомых видеофайлов
    @property
    def ext_video(self): return self._ext_video

    # Установка расширения искомых видеофайлов
    @ext_video.setter
    def ext_video(self, ext): self._ext_video = ext

    # Получение расширения для создаваемого аудиофайла
    @property
    def ext_audio(self): return self._ext_audio

    # Установка расширения для создаваемого аудиофайла
    @ext_audio.setter
    def ext_audio(self, ext): self._ext_audio = ext