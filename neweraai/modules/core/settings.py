#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Настройки ядра
"""

# ######################################################################################################################
# Импорт необходимых инструментов
# ######################################################################################################################
from dataclasses import dataclass  # Класс данных

import os  # Взаимодействие с файловой системой

from typing import List  # Типы данных

# Персональные
from neweraai.modules.core.messages import Messages  # Сообщения

# ######################################################################################################################
# Настройки ядра
# ######################################################################################################################
@dataclass
class Settings(Messages):
    """Настройки ядра"""

    # ------------------------------------------------------------------------------------------------------------------
    # Конструктор
    # ------------------------------------------------------------------------------------------------------------------

    # Цвет текстов
    color_simple_: str = '#666'   # Обычный текст
    color_info_: str = '#1776D2'  # Информация
    color_err_: str = '#FF0000'   # Ошибка
    color_true_: str = '#008001'  # Положительная информация
    bold_text_: bool = True       # Жирность текста
    text_runtime_: str = ''       # Текст времени выполнения
    logs_: str = ''               # Директория для сохранения LOG файлов

    def __post_init__(self):
        super().__post_init__()  # Выполнение конструктора из суперкласса

        # Цвет текстов
        self.color_simple: str = self.color_simple_  # Обычный текст
        self.color_info: str = self.color_info_      # Информация
        self.color_err: str = self.color_err_        # Ошибка
        self.color_true: str = self.color_true_      # Положительная информация
        self.bold_text: bool = self.bold_text_       # Жирность текста

        # Текст времени выполнения
        self.text_runtime: str = self._('Время выполнения')
        self.text_runtime = self.text_runtime_

        # Директория для сохранения LOG файлов
        self.logs: str = './logs'
        self.logs = self.logs_

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

    # Получение цвета обычного текста
    @property
    def color_simple(self): return self._color_simple

    # Установка цвета обычного текста
    @color_simple.setter
    def color_simple(self, color): self._color_simple = color

    # Получение цвета текста с информацией
    @property
    def color_info(self): return self._color_info

    # Установка цвета текста с информацией
    @color_info.setter
    def color_info(self, color): self._color_info = color

    # Получение цвета текста с ошибкой
    @property
    def color_err(self): return self._color_err

    # Установка цвета текста с ошибкой
    @color_err.setter
    def color_err(self, color): self._color_err = color

    # Получение цвета текста с положительной информацией
    @property
    def color_true(self): return self._color_true

    # Установка цвета текста с положительной информацией
    @color_true.setter
    def color_true(self, color): self._color_true = color

    # Получение жирности текста
    @property
    def bold_text(self): return self._bold_text

    # Установка жирности текста
    @bold_text.setter
    def bold_text(self, bold): self._bold_text = bold

    # Получение директории для сохранения LOG файлов
    @property
    def logs(self): return self._logs

    # Установка директории для сохранения LOG файлов
    @logs.setter
    def logs(self, path):
        if type(path) is not str or len(path) < 1: return self._logs
        else: self._logs = os.path.normpath(path)

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