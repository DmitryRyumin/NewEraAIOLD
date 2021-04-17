#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ядро
"""

# ######################################################################################################################
# Импорт необходимых инструментов
# ######################################################################################################################
# Подавление Warning
import warnings
for warn in [UserWarning, FutureWarning]: warnings.filterwarnings('ignore', category = warn)

from dataclasses import dataclass  # Класс данных

import os                  # Взаимодействие с файловой системой
import sys                 # Доступ к некоторым переменным и функциям Python
import time                # Работа со временем
import pandas as pd        # Обработка и анализ данных
import numpy as np         # Научные вычисления
import matplotlib as mpl   # Визуализация графиков
import jupyterlab as jlab  # Интерактивная среда разработки для работы с блокнотами, кодом и данными
import pymediainfo         # Получение meta данных из медиафайлов
import torch               # Машинное обучение от Facebook
import torchaudio          # Работа с аудио
import soundfile as sf     # Работа с аудио
import urllib.error        # Обработка ошибок URL
import requests            # Отправка HTTP запросов
import shutil              # Набор функций высокого уровня для обработки файлов, групп файлов, и папок
import re                  # Регулярные выражения
import seaborn as sns      # Визуализация графиков (надстройка над matplotlib)

from datetime import datetime  # Работа со временем
from pathlib import Path       # Работа с путями в файловой системе
from typing import Dict, List  # Типы данных
import pkg_resources           # Работа с ресурсами внутри пакетов

from IPython.display import Markdown, display

# Персональные
import neweraai                                      # NewEraAI - новая эра искусственного интеллекта
from neweraai.modules.core.settings import Settings  # Глобальный файл настроек

# ######################################################################################################################
# Сообщения
# ######################################################################################################################
@dataclass
class Messages(Settings):
    """Сообщения"""

    # ------------------------------------------------------------------------------------------------------------------
    # Конструктор
    # ------------------------------------------------------------------------------------------------------------------

    def __post_init__(self):
        super().__post_init__()  # Выполнение конструктора из суперкласса

        self._trac_file: str = self._('Файл')
        self._trac_line: str = self._('Линия')
        self._trac_method: str = self._('Метод')
        self._trac_type_err: str = self._('Тип ошибки')

        self._sec: str = self._('сек.')

        self._wrong_extension: str = self._oh + self._('расширение файла должно быть одно из "{}" ...')
        self._url_error_code_log: str = self._(' (ошибка {})')
        self._url_error_log: str = self._oh + self._('не удалось сохранить LOG файл{} ...')
        self._file_not_found: str = self._oh + self._('файл "{}" не найден ...')
        self._meta_not_found: str = self._oh + self._('META информация не найдена ...')

        self._folder_not_found: str = self._oh + self._('директория "{}" не найдена ...')

# ######################################################################################################################
# Ядро модулей
# ######################################################################################################################
@dataclass
class Core(Messages):
    """Ядро модулей"""

    # ------------------------------------------------------------------------------------------------------------------
    # Конструктор
    # ------------------------------------------------------------------------------------------------------------------

    def __post_init__(self):
        super().__post_init__()  # Выполнение конструктора из суперкласса

        self._is_notebook: bool = self.__is_notebook()  # Определение запуска пакета в Jupyter или аналогах

        self._start_time: int = -1  # Старт времени выполнения
        self._runtime: int = -1  # Время выполнения

        self._df_pkgs: pd.DataFrame = pd.DataFrame()  # DataFrame c версиями установленных библиотек
        self._df_media_info: pd.DataFrame = pd.DataFrame()  # DataFrame c meta данными из медиафайла
        self._df_sr: pd.DataFrame = pd.DataFrame()  # DataFrame с текстовыми представлениями речи, начала и конца речи

        self._keys_id: str = 'ID'  # Идентификатор
        self._keys_id_media_info: str = 'Name'  # Идентификатор
        self._ext_for_logs: str = '.csv'  # Расширение для сохранения lOG файлов

        # Директория для загрузки моделей по умолчанию
        self._path_to_save_model_default: str = pkg_resources.resource_filename('neweraai', 'models')

        self._notebook_history_output: List = []  # История вывода сообщений в ячейке Jupyter

        # Тип файла с META информацией
        self._type_meta_info: Dict[str, List] = {
            'Video' : ['format', 'other_width', 'other_height', 'other_display_aspect_ratio',
                       'minimum_frame_rate', 'frame_rate', 'maximum_frame_rate', 'other_bit_rate', 'encoded_date'],
            'Audio' : ['format', 'other_bit_rate', 'other_channel_s', 'other_sampling_rate']
        }

    # ------------------------------------------------------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------------------------------------------------------

    # Получение результата определения запуска пакета в Jupyter или аналогах
    @property
    def is_notebook(self): return self._is_notebook

    # Получение времени выполнения
    @property
    def runtime(self): return self._runtime

    # DataFrame c версиями установленных библиотек
    @property
    def df_pkgs(self): return self._df_pkgs

    # DataFrame c meta данными из медиафайла
    @property
    def df_media_info(self): return self._df_media_info

    # DataFrame с текстовыми представлениями речи, начала и конца речи
    @property
    def df_sr(self): return self._df_sr

    # ------------------------------------------------------------------------------------------------------------------
    # Внутренние методы (сообщения)
    # ------------------------------------------------------------------------------------------------------------------

    # Трассировка исключений
    @staticmethod
    def _traceback() -> Dict:
        """
        Трассировка исключений

        Возвращает: Dict с описанием исключения
        """

        exc_type, exc_value, exc_traceback = sys.exc_info()  # Получение информации об ошибке

        _trac = {
            'filename': exc_traceback.tb_frame.f_code.co_filename,
            'lineno': exc_traceback.tb_lineno,
            'name': exc_traceback.tb_frame.f_code.co_name,
            'type': exc_type.__name__
        }

        return _trac

    # Отображение сообщения
    def _notebook_display_markdown(self, message: str, last: bool = False, out: bool = True):
        """
        Отображение сообщения

        Аргументы:
            message - Сообщение
            last - Замена последнего сообщения
            out - Отображение
        """

        if self.is_notebook is True:
            self._add_notebook_history_output(message, last)  # Добавление истории вывода сообщений в ячейке Jupyter

            if out is True: display(Markdown(message))  # Отображение

    # Информация об пакете
    def _metadata_info(self, last: bool = False, out: bool = True):
        """
        Информация об пакете

        Аргументы:
            last - Замена последнего сообщения
            out - Отображение
        """

        tab = '&nbsp;' * 4

        if self.is_notebook is True:
            b = '**' if self.bold_text is True else ''
            cr = self.color_simple

            # Отображение сообщения
            self._notebook_display_markdown(('{}' * 9).format(
                f'<span style=\"color:{self.color_simple}\">{b}[</span><span style=\"color:{self.color_info}\">',
                datetime.now().strftime(self._format_time),
                f'</span><span style=\"color:{self.color_simple}\">]</span> ',
                f'<span style=\"color:{self.color_simple}\">{self._metadata[0]}:</span>{b}',
                f'<p><span style=\"color:{cr}\">{tab}{self._metadata[1]}: <u>{neweraai.__author__}</u></span>',
                f'<br /><span style=\"color:{cr}\">{tab}{self._metadata[2]}: <u>{neweraai.__email__}</u></span>',
                f'<br /><span style=\"color:{cr}\">{tab}{self._metadata[3]}: <u>{neweraai.__maintainer__}</u></span>',
                f'<br /><span style=\"color:{cr}\">{tab}{self._metadata[4]}: <u>{neweraai.__version__}</u></span>',
                f'<br /><span style=\"color:{cr}\">{tab}{self._metadata[5]}: <u>{neweraai.__license__}</u></span></p>'
            ), last, out)

    # Неверные типы аргументов
    def _inv_args(self, class_name: str, build_name: str, last: bool = False, out: bool = True):
        """
        Построение аргументов командной строки

        Аргументы:
            class_name - Имя класса
            build_name - Имя метода/функции
            last - Замена последнего сообщения
            out - Отображение
        """

        inv_args = self._invalid_arguments.format(class_name + '.' + build_name)

        if self.is_notebook is True:
            b = '**' if self.bold_text is True else ''

            # Отображение сообщения
            self._notebook_display_markdown('{}[{}{}{}] {}{}'.format(
                f'<span style=\"color:{self.color_simple}\">{b}',
                f'</span><span style=\"color:{self.color_err}\">',
                datetime.now().strftime(self._format_time),
                f'</span><span style=\"color:{self.color_simple}\">', inv_args, f'{b}</span>'
            ), last, out)

    # Информация
    def _info(self, message: str, last: bool = False, out: bool = True):
        """
        Информация

        Аргументы:
            message - Сообщение
            last - Замена последнего сообщения
            out - Отображение
        """

        if self.is_notebook is True:
            b = '**' if self.bold_text is True else ''

            # Отображение сообщения
            self._notebook_display_markdown(('{}' * 4).format(
                f'<span style=\"color:{self.color_simple}\">{b}[</span><span style=\"color:{self.color_info}\">',
                datetime.now().strftime(self._format_time),
                f'</span><span style=\"color:{self.color_simple}\">]</span> ',
                f'<span style=\"color:{self.color_simple}\">{message}</span>{b}'
            ), last, out)

    # Информационная обертка
    def _info_wrapper(self, message: str) -> str:
        """
        Информационная обертка

        Аргументы:
            message - Сообщение

        Возвращает: Информационную строку
        """

        if self.is_notebook is True:
            return ('{}' * 3).format(f'<span style=\"color:{self.color_info}\">', message, f'</span>')

    # Ошибки
    def _error(self, message: str, last: bool = False, out: bool = True):
        """
        Ошибки

        Аргументы:
            message - Сообщение
            last - Замена последнего сообщения
            out - Отображение
        """

        if self.is_notebook is True:
            b = '**' if self.bold_text is True else ''

            # Отображение сообщения
            self._notebook_display_markdown('{}[{}{}{}] {}{}'.format(
                f'<span style=\"color:{self.color_simple}\">{b}', f'</span><span style=\"color:{self.color_err}\">',
                datetime.now().strftime(self._format_time),
                f'</span><span style=\"color:{self.color_simple}\">', message, f'{b}</span>'
            ), last, out)

    # Прочие ошибки
    def _other_error(self, message: str, last: bool = False, out: bool = True):
        """
        Прочие ошибки

        Аргументы:
            message - Сообщение
            last - Замена последнего сообщения
            out - Отображение
        """

        trac = self._traceback()  # Трассировка исключений
        tab = '&nbsp;' * 4

        if self.is_notebook is True:
            b = '**' if self.bold_text is True else ''
            cr = self.color_simple

            # Отображение сообщения
            self._notebook_display_markdown(('{}' * 8).format(
                f'<span style=\"color:{cr}\">{b}[</span><span style=\"color:{self.color_err}\">',
                datetime.now().strftime(self._format_time),
                f'</span><span style=\"color:{cr}\">]</span> ',
                f'<span style=\"color:{cr}\">{message}</span>{b}',
                f'<p><span style=\"color:{cr}\">{tab}{self._trac_file}: <u>{trac["filename"]}</u></span>',
                f'<br /><span style=\"color:{cr}\">{tab}{self._trac_line}: <u>{trac["lineno"]}</u></span>',
                f'<br /><span style=\"color:{cr}\">{tab}{self._trac_method}: <u>{trac["name"]}</u></span>',
                f'<br /><span style=\"color:{cr}\">{tab}{self._trac_type_err}: <u>{trac["type"]}</u></span></p>'
            ), last, out)

    # Обертка для ошибки
    def _error_wrapper(self, message: str) -> str:
        """
        Обертка для ошибки

        Аргументы:
            message - Сообщение

        Возвращает: Строка ошибки
        """

        if self.is_notebook is True:
            return ('{}' * 3).format(f'<span style=\"color:{self.color_err}\">', message, f'</span>')

    # Положительная информация
    def _info_true(self, message: str, last: bool = False, out: bool = True):
        """
        Положительная информация

        Аргументы:
            message: Сообщение
            last - Замена последнего сообщения
            out - Отображение
        """

        if self.is_notebook is True:
            b = '**' if self.bold_text is True else ''

            # Отображение сообщения
            self._notebook_display_markdown(
                '{}'.format(f'<span style=\"color:{self.color_true}\">{b}{message}{b}</span>'), last, out)

    # Начало времени выполнения
    def _r_start(self):
        """
        Начало времени выполнения
        """

        self._runtime = self._start_time = -1  # Сброс значений

        self._start_time = time.time()  # Отсчет времени выполнения

    # Конец времени выполнения
    def _r_end(self, last: bool = False, out: bool = True):
        """
        Конец времени выполнения

        Аргументы:
            last - Замена последнего сообщения
            out - Отображение
        """

        self._runtime = round(time.time() - self._start_time, 3)  # Время выполнения

        t = '--- {}: {} {} ---'.format(self.text_runtime, self._runtime, self._sec)

        if self.is_notebook is True:
            b = '**' if self.bold_text is True else ''

            # Отображение сообщения
            self._notebook_display_markdown(
                '{}'.format(f'<span style=\"color:{self.color_simple}\">{b}{t}{b}</span>'), last, out)

    # Индикатор выполнения
    def _progressbar(self, message: str, progress: str, last: bool = False, out: bool = True):
        """
        Индикатор выполнения

        Аргументы:
           message - Сообщение
           progress - Индикатор выполнения
           last - Замена последнего сообщения
           out - Отображение
        """

        tab = '&nbsp;' * 4

        if self.is_notebook is True:
            b = '**' if self.bold_text is True else ''

            # Отображение сообщения
            self._notebook_display_markdown(('{}' * 5).format(
                f'<span style=\"color:{self.color_simple}\">{b}[</span><span style=\"color:{self.color_info}\">',
                datetime.now().strftime(self._format_time),
                f'</span><span style=\"color:{self.color_simple}\">]</span> ',
                f'<span style=\"color:{self.color_simple}\">{message}</span>{b}',
                f'<p><span style=\"color:{self.color_simple}\">{tab}{progress}</span></p>'
            ), last, out)

    # Результат распознавания речи
    def _test_from_sr(self, message: str, results_recognized: Dict or List, last: bool = False, out: bool = True,
                      name: str = '', logs: bool = True):
        """
        Результат распознавания речи

        Аргументы:
           message - Сообщение
           results_recognized - Результаты распознавания
           last - Замена последнего сообщения
           out - Отображение
           name - Имя LOG файла
           logs - При необходимости формировать LOG файл
        """

        # Аудио
        if type(results_recognized) is dict:
            self._df_sr = pd.concat(
                {k: pd.DataFrame(v, columns = ['Text', 'Start', 'End'])
                 for k, v in results_recognized.items()}, axis = 1)
            self._df_sr.index.name = self._keys_id
            self._df_sr.index += 1
        # Видео
        if type(results_recognized) is list:
            texts, starts, ends = map(list, zip(*results_recognized)) # Распаковка вложенного списка
            d_sr = {'Text': texts, 'Start': starts, 'End': ends}

            self._df_sr = pd.DataFrame(data = d_sr)  # Версии используемых библиотек
            self._df_sr.index.name = self._keys_id
            self._df_sr.index += 1

        if self.is_notebook is True:
            b = '**' if self.bold_text is True else ''

            # Отображение сообщения
            self._notebook_display_markdown(('{}' * 4).format(
                f'<span style=\"color:{self.color_simple}\">{b}[</span><span style=\"color:{self.color_true}\">',
                datetime.now().strftime(self._format_time),
                f'</span><span style=\"color:{self.color_simple}\">]</span> ',
                f'<span style=\"color:{self.color_simple}\">{message}</span>{b}'
            ), last, out)

            # Отображение
            if out is True: display(self._df_sr.iloc[0:self.num_to_df_display, :])

            if logs is True:
                # Сохранение LOG
                res_save_logs = self._save_logs(self.df_sr, name)

                if res_save_logs is True: self._info_true(self._logs_save_true, out = out)

    # Очистка истории вывода сообщений в ячейке Jupyter
    def _clear_notebook_history_output(self):
        """
        Очистка истории вывода сообщений в ячейке Jupyter
        """

        self._notebook_history_output.clear()  # Очистка истории вывода сообщений в ячейке Jupyter

    # Добавление истории вывода сообщений в ячейке Jupyter
    def _add_notebook_history_output(self, messages: str, last: bool = False):
        """
        Добавление истории вывода сообщений в ячейке Jupyter

        Аргументы:
           message - Сообщение
           last - Замена последнего сообщения
        """

        if last is True: self._notebook_history_output[-1] = messages
        else: self._notebook_history_output.append(messages)

    # ------------------------------------------------------------------------------------------------------------------
    # Внутренние методы
    # ------------------------------------------------------------------------------------------------------------------

    # Определение запуска пакета в Jupyter или аналогах
    @staticmethod
    def __is_notebook() -> bool:
        """
        Определение запуска пакета в Jupyter или аналогах

        Возвращает: True если пакет запущен в Jupyter или аналогах, в обратном случае False
        """

        try:
            # Определение режима запуска пакета
            shell = get_ipython().__class__.__name__
        except (NameError, Exception): return False  # Запуск в Python
        else:
            if shell == 'ZMQInteractiveShell' or shell == 'Shell': return True
            elif shell == 'TerminalInteractiveShell': return False
            else: return False

    # Создание директории для сохранения LOG файлов
    def _create_folder_for_logs(self):
        """
        Создание директории для сохранения LOG файлов

        Возвращает: True если директория создана или существует, в обратном случае False
        """

        try:
            if not os.path.exists(self.logs): os.makedirs(self.logs)
        except (FileNotFoundError, TypeError): self._other_error(self._som_ww); return False
        except Exception: self._other_error(self._unknown_err); return False
        else: return True

    # Сохранение LOG
    def _save_logs(self, df: pd.DataFrame, name: str):
        """
        Сохранение LOG

        Аргументы:
           df - DataFrame который будет сохранен в LOG файл
           name - Имя LOG файла

        Возвращает: True если LOG файл сохранен, в обратном случае False
        """

        # Создание директории для сохранения LOG файлов
        if self._create_folder_for_logs() is True:
            # Сохранение LOG файла
            try:
                df.to_csv(os.path.join(self.logs, name + self._ext_for_logs), index_label = self._keys_id)
            except urllib.error.HTTPError as e:
                self._other_error(self._url_error_log.format(self._url_error_code_log.format(
                    self._error_wrapper(e.code))))
            except urllib.error.URLError: self._other_error(self._url_error_log.format(''))
            except Exception: self._other_error(self._unknown_err); return False
            else: return True

        return False

    # Удаление недопустимых символов из пути
    @staticmethod
    def _re_inv_chars(path: str) -> str:
        """
        Удаление недопустимых символов из пути

        Аргументы:
           path - Путь

        Возвращает: Новый путь
        """

        return re.sub('[\\/:"*?<>|]+', '', path)

    # Создание директории в случае ее отсутствия
    @staticmethod
    def _create_folder(path: str) -> str:
        """
        Создание директории в случае ее отсутствия

        Аргументы:
           path - Путь

        Возвращает: Директорию
        """

        try:
            if not os.path.exists(path): os.makedirs(path)
        except Exception: return ''
        else: return path

    # Очистка директории
    @staticmethod
    def _clear_folder(path: str):
        """
        Очистка директории

        Аргументы:
           path - Путь
        """

        # Каталог с файлами найден
        if os.path.exists(path):
            for filename in os.listdir(path):
                filepath = os.path.join(path, filename)
                try: shutil.rmtree(filepath)
                except OSError: os.remove(filepath)

    # ------------------------------------------------------------------------------------------------------------------
    # Внешние методы
    # ------------------------------------------------------------------------------------------------------------------

    # Версии установленных библиотек
    def libs_vers(self, runtime: bool = True, run: bool = True):
        """
        Версии установленных библиотек

        Аргументы:
            runtime - Подсчет времени выполнения
            run - Блокировка выполнения
        """

        self._clear_notebook_history_output()  # Очистка истории вывода сообщений в ячейке Jupyter

        # Сброс
        self._df_pkgs = pd.DataFrame()  # Пустой DataFrame

        try:
            # Проверка аргументов
            if type(runtime) is not bool or type(run) is not bool: raise TypeError
        except TypeError: self._inv_args(__class__.__name__, self.libs_vers.__name__)
        else:
            # Блокировка выполнения
            if run is False: self._error(self._lock_user); return None

            if runtime: self._r_start()

            pkgs = {
                'Package': [
                    'PyTorch', 'Torchaudio', 'SoundFile', 'NumPy', 'Pandas', 'Matplotlib', 'Seaborn', 'JupyterLab',
                    'PyMediaInfo', 'Requests', 'Vosk'
                ],
                'Version': [i.__version__ for i in [
                    torch, torchaudio, sf, np, pd, mpl, sns, jlab, pymediainfo, requests
                ]]
            }
            pkgs['Version'].append(pkg_resources.get_distribution('vosk').version)

            self._df_pkgs = pd.DataFrame(data = pkgs)  # Версии используемых библиотек
            self._df_pkgs.index += 1

            # Отображение
            if self.is_notebook is True: display(self._df_pkgs)

            if runtime: self._r_end()

    # Отображение истории вывода сообщений в ячейке Jupyter
    def show_notebook_history_output(self):
        """
        Отображение истории вывода сообщений в ячейке Jupyter
        """

        if self.is_notebook is True and len(self._notebook_history_output) > 0:
            for e in self._notebook_history_output: display(Markdown(e))  # Отображение

    # Получение meta данных из медиафайла
    def media_info(self, path_to_file: str, runtime: bool = True, run: bool = True):
        """
        Получение meta данных из медиафайла

        Аргументы:
            path_to_file - Путь к файлу
            runtime - Подсчет времени выполнения
            run - Блокировка выполнения
        """

        self._clear_notebook_history_output()  # Очистка истории вывода сообщений в ячейке Jupyter

        # Сброс
        self._df_media_info = pd.DataFrame()  # Пустой DataFrame

        try:
            # Проверка аргументов
            if type(path_to_file) is not str or not path_to_file or type(run) is not bool or type(runtime) is not bool:
                raise TypeError
        except TypeError: self._inv_args(__class__.__name__, self.media_info.__name__)
        else:
            # Блокировка выполнения
            if run is False: self._error(self._lock_user); return None

            if runtime: self._r_start()

            try:
                # Meta данные
                metadata = pymediainfo.MediaInfo.parse(os.path.normpath(path_to_file)).to_data()
            except FileNotFoundError: self._other_error(self._file_not_found.format(
                    self._info_wrapper(Path(path_to_file).name)))
            except Exception: self._other_error(self._unknown_err)
            else:
                media_info = {}  # Словарь для meta данных

                # Проход по всем meta словарям
                for track in metadata['tracks']:
                    # Извлечение meta данных
                    if track['track_type'] in [*self._type_meta_info]:
                        media_info[track['track_type']] = {}  # Словарь для meta данных определенного формата

                        # Проход по всем необходимым meta данным
                        for i, curr_necessary in enumerate(self._type_meta_info[track['track_type']]):
                            try:
                                val = track[curr_necessary]  # Текущее значение
                            except Exception: continue
                            else:
                                if curr_necessary == 'encoded_date':
                                    val = datetime.strptime(val.replace('UTC ', ''), '%Y-%m-%d %H:%M:%S')

                                # Список в строку
                                if type(val) is list:
                                    if len(val) < 2: val = val[0]
                                    else: val = ', '.join([str(elem) for elem in val])

                                media_info[track['track_type']][curr_necessary] = val
                try:
                    if len(media_info) == 0: raise TypeError
                except TypeError: self._other_error(self._meta_not_found)
                else:
                    # Meta данные
                    self._df_media_info = pd.concat(
                        {k: pd.DataFrame.from_dict(v, 'index', columns = [Path(path_to_file).name])
                            for k, v in media_info.items()
                        }, axis = 0)
                    self._df_media_info.index.name = self._keys_id_media_info

                    try:
                        if self._df_media_info.empty is True: raise TypeError
                    except TypeError: self._other_error(self._meta_not_found)
                    else:
                        # Отображение
                        if self.is_notebook is True: display(self._df_media_info)
            finally:
                if runtime: self._r_end()