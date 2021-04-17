#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Настройки ядра
"""

# ######################################################################################################################
# Импорт необходимых инструментов
# ######################################################################################################################
# Подавление Warning
import warnings
for warn in [UserWarning, FutureWarning]: warnings.filterwarnings('ignore', category = warn)

from dataclasses import dataclass  # Класс данных

import os                 # Взаимодействие с файловой системой
from pathlib import Path  # Работа с путями в файловой системе

from typing import List, Tuple  # Типы данных

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
    num_to_df_display_: int = 0   # Количество строк для отображения в таблицах
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

        # Количество строк для отображения в таблицах
        self.num_to_df_display: int = 30
        self.num_to_df_display = self.num_to_df_display_

        # Директория для сохранения LOG файлов
        self.logs: str = './logs'
        self.logs = self.logs_

        self.path_to_original_videos: str = ''  # Директория для анализа и обработки
        # Названия каталогов для обработки видео
        #     1. Каталог с оригинальными видео
        #     2. Каталог с разделенными видеофрагментами
        #     3. Каталог с аннотированными видеофрагментами
        self.sub_folder: List[str] = ['Original', 'Splitted', 'Annotated']
        self.ext_video: List[str] = []  # Расширения искомых видеофайлов
        self.ext_audio: str = ''  # Расширение для создаваемого аудиофайла

        self.chunk_size = 1000000  # Размер загрузки файла из сети за 1 шаг (1 Mb)

        self.language_sr: str or None = None  # Язык для распознавания речи
        self.dict_language_sr: str or None = None  # Размер словаря для распознавания речи
        self.path_to_save: str = './models'  # Директория для сохранения
        self.cart_name: str = '__garbage__'  # Директория для корзины с не отсортированными файлами
        self._filter_sr: List[str] = []  # Фильтр распознавания речи

        self.path_to_dataset: str = ''  # Директория набора данных
        self.keys_dataset: List[str] = ['Path', 'Class', 'ID_class']  # Названия ключей для DataFrame набора данных
        self.ext: List[str] = [] # Расширения искомых файлов
        self.ignore_dirs: List[str] = []  # Директории не входящие в выборку
        self.filter_dirs: List[str] = [] # Директории входящие в выборку

        self.keys_stats: List[str] = ['Class_name', 'Number_of_images']  # Названия ключей для DataFrame со статистикой
        self.figsize: Tuple[int, int] = (0, 0)  # Размер фигуры в дюймах
        self.ymargin: float = 0  # Y отступ от ряда до рамки
        self.bbox_to_anchor: Tuple[float, float] = (0, 0)  # Отступы от графика до легенды
        self.pad: int = 24  # Y отступ в графиках от ряда до его значения

        self.keys_folds: List[str] = ['train', 'val', 'test']  # Названия ключей для словаря стратифицированного набора
        self.subplots_adjust: Tuple[float, float] = (0, 0)  # Отступы между фигурами
        self.suptitle_y: float = 0  # Y отступ заголовка от вершины осей

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
        self._text_runtime = text

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

    # Получение количества строк для отображения в таблицах
    @property
    def num_to_df_display(self): return self._num_to_df_display

    # Установка количества строк для отображения в таблицах
    @num_to_df_display.setter
    def num_to_df_display(self, num):
        if type(num) is not int or num < 1 or num > 50: return self._num_to_df_display
        self._num_to_df_display = num

    # Получение директории для сохранения LOG файлов
    @property
    def logs(self): return self._logs

    # Установка директории для сохранения LOG файлов
    @logs.setter
    def logs(self, path):
        if type(path) is not str or len(path) < 1: return self._logs
        self._logs = os.path.normpath(path)

    # Получение директории для анализа и обработки
    @property
    def path_to_original_videos(self): return self._path_to_original_videos

    # Установка директории для анализа и обработки
    @path_to_original_videos.setter
    def path_to_original_videos(self, path): self._path_to_original_videos = os.path.normpath(path)

    # Получение названий каталогов для обработки видео
    @property
    def sub_folder(self): return self._sub_folder

    # Установка названий каталогов для обработки видео
    @sub_folder.setter
    def sub_folder(self, names):
        if type(names) is not list: return []
        else: self._sub_folder = names

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

    # Получение размера загрузки файла из сети за 1 шаг
    @property
    def chunk_size(self): return self._chunk_size

    # Установка размера загрузки файла из сети за 1 шаг
    @chunk_size.setter
    def chunk_size(self, size):
        if type(size) is not int or size < 1: return self._size
        self._chunk_size = size

    # Получение языка для распознавания речи
    @property
    def language_sr(self): return self._language_sr

    # Установка языка для распознавания речи
    @language_sr.setter
    def language_sr(self, lang): self._language_sr = lang

    # Получение размера словаря для распознавания речи
    @property
    def dict_language_sr(self): return self._dict_language_sr

    # Установка размера словаря для распознавания речи
    @dict_language_sr.setter
    def dict_language_sr(self, dict_lang): self._dict_language_sr = dict_lang

    # Получение директории для сохранения
    @property
    def path_to_save(self): return self._path_to_save

    # Установка директории для сохранения
    @path_to_save.setter
    def path_to_save(self, path):
        if type(path) is not str or len(path) < 1: return self._path_to_save
        self._path_to_save = os.path.normpath(path)

    # Получение директории для корзины с не отсортированными файлами
    @property
    def cart_name(self): return self._cart_name

    # Установка директории для корзины с не отсортированными файлами
    @cart_name.setter
    def cart_name(self, name):
        if type(name) is not str or len(name) < 1: return self._cart_name
        self._cart_name = Path(name).name

    # Получение списка для фильтра распознавания речи
    @property
    def filter_sr(self): return self._filter_sr

    # Установка списка для фильтра распознавания речи
    @filter_sr.setter
    def filter_sr(self, l):
        if type(l) is not list: return self._filter_sr
        else: self._filter_sr = l

    # Получение директории набора данных
    @property
    def path_to_dataset(self): return self._path_to_dataset

    # Установка директории набора данных
    @path_to_dataset.setter
    def path_to_dataset(self, path): self._path_to_dataset = os.path.normpath(path)

    # Получение названий ключей набора данных
    @property
    def keys_dataset(self): return self._keys_dataset

    # Установка названий ключей набора данных
    @keys_dataset.setter
    def keys_dataset(self, keys): self._keys_dataset = keys

    # Получение расширения искомых файлов
    @property
    def ext(self): return self._ext

    # Установка расширения искомых файлов
    @ext.setter
    def ext(self, ext): self._ext = ext

    # Получение списка с директориями не входящими в выборку
    @property
    def ignore_dirs(self): return self._ignore_dirs

    # Установка списка с директориями не входящими в выборку
    @ignore_dirs.setter
    def ignore_dirs(self, l):
        if type(l) is not list: self._ignore_dirs = []
        else: self._ignore_dirs = l

    # Получение списка с директориями входящими в выборку
    @property
    def filter_dirs(self): return self._filter_dirs

    # Установка списка с директориями входящими в выборку
    @filter_dirs.setter
    def filter_dirs(self, l):
        if type(l) is not list: self._filter_dirs = []
        else: self._filter_dirs = l

    # Получение названий ключей для статистики
    @property
    def keys_stats(self): return self._keys_stats

    # Установка названий ключей для статистики
    @keys_stats.setter
    def keys_stats(self, keys_stats): self._keys_stats = keys_stats

    # Получение размера фигуры в дюймах
    @property
    def figsize(self): return self._figsize

    # Установка размера фигуры в дюймах
    @figsize.setter
    def figsize(self, figsize):
        if type(figsize) is not tuple or len(figsize) != 2: return self._figsize
        else: self._figsize = figsize

    # Получение Y отступа от ряда до рамки
    @property
    def ymargin(self): return self._ymargin

    # Установка Y отступа от ряда до рамки
    @ymargin.setter
    def ymargin(self, ymargin): self._ymargin = ymargin

    # Получение отступов от графика до легенды
    @property
    def bbox_to_anchor(self): return self._bbox_to_anchor

    # Установка отступов от графика до легенды
    @bbox_to_anchor.setter
    def bbox_to_anchor(self, bbox):
        if type(bbox) is not tuple or len(bbox) != 2: return self._bbox_to_anchor
        else: self._bbox_to_anchor = bbox

    # Получение Y отступа в графиках от ряда до его значения
    @property
    def pad(self): return self._pad

    # Установка Y отступа в графиках от ряда до его значения
    @pad.setter
    def pad(self, pad): self._pad = pad

    # Получение названий ключей для словаря стратифицированного набора
    @property
    def keys_folds(self): return self._keys_folds

    # Установка названий ключей для словаря стратифицированного набора
    @keys_folds.setter
    def keys_folds(self, keys_folds):
        if type(keys_folds) is not list: return self._keys_folds
        else: self._keys_folds = keys_folds

    # Получение отступов между фигурами
    @property
    def subplots_adjust(self): return self._subplots_adjust

    # Установка отступов между фигурами
    @subplots_adjust.setter
    def subplots_adjust(self, pad):
        if type(pad) is not tuple or len(pad) != 2: return self._subplots_adjust
        else: self._subplots_adjust = pad

    # Получение Y отступа заголовка от вершины осей
    @property
    def suptitle_y(self): return self._suptitle_y

    # Установка Y отступа заголовка от вершины осей
    @suptitle_y.setter
    def suptitle_y(self, pad): self._suptitle_y = pad