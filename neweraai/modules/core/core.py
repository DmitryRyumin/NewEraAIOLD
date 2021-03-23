#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ядро
"""

# ######################################################################################################################
# Импорт необходимых инструментов
# ######################################################################################################################
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
import urllib.error       # Обработка ошибок URL

from datetime import datetime  # Работа со временем
from typing import Dict        # Типы данных

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

        self._url_error_code_log: str = self._(' (ошибка {}{}{})')
        self._url_error_log: str = self._('Ой! Что-то пошло не так ... не удалось сохранить LOG файл{} ...')

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

        self._is_notebook = self.__is_notebook()  # Определение запуска пакета в Jupyter или аналогах

        self._start_time: int = -1  # Старт времени выполнения
        self._runtime: int = -1  # Время выполнения

        self._df_pkgs: pd.DataFrame = pd.DataFrame()  # DataFrame c версиями установленных библиотек

        self._info_last: str = '' # Последнее информационное сообщение

        self._keys_id: str = 'ID'  # Идентификатор
        self._ext_for_logs = '.csv'  # Расширение для созранения lOG файлов

    # ------------------------------------------------------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------------------------------------------------------

    # Получениие результата определения запуска пакета в Jupyter или аналогах
    @property
    def is_notebook(self): return self._is_notebook

    # Получение времени выполнения
    @property
    def runtime(self): return self._runtime

    # DataFrame c версиями установленных библиотек
    @property
    def df_pkgs(self): return self._df_pkgs

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

    # Информация об пакете
    def _metadata_info(self):
        """
        Информация об пакете
        """

        tab = '&nbsp;' * 4

        if self.is_notebook is True:
            b = '**' if self.bold_text is True else ''
            cr = self.color_simple

            # Отображение
            display(Markdown(('{}' * 9).format(
                f'<span style=\"color:{self.color_simple}\">{b}[</span><span style=\"color:{self.color_info}\">',
                datetime.now().strftime(self._format_time),
                f'</span><span style=\"color:{self.color_simple}\">]</span> ',
                f'<span style=\"color:{self.color_simple}\">{self._metadata[0]}:</span>{b}',
                f'<p><span style=\"color:{cr}\">{tab}{self._metadata[1]}: <u>{neweraai.__author__}</u></span>',
                f'<br /><span style=\"color:{cr}\">{tab}{self._metadata[2]}: <u>{neweraai.__email__}</u></span>',
                f'<br /><span style=\"color:{cr}\">{tab}{self._metadata[3]}: <u>{neweraai.__maintainer__}</u></span>',
                f'<br /><span style=\"color:{cr}\">{tab}{self._metadata[4]}: <u>{neweraai.__version__}</u></span>',
                f'<br /><span style=\"color:{cr}\">{tab}{self._metadata[5]}: <u>{neweraai.__license__}</u></span></p>'
            )))

    # Неверные типы аргументов
    def _inv_args(self, class_name: str, build_name: str):
        """
        Построение аргументов командной строки

        Аргументы:
           class_name - Имя класса
           build_name - Имя метода/функции
        """

        inv_args = self._invalid_arguments.format(class_name + '.' + build_name)

        if self.is_notebook is True:
            b = '**' if self.bold_text is True else ''

            # Отображение
            display(Markdown('{}[{}{}{}] {}{}'.format(
                f'<span style=\"color:{self.color_simple}\">{b}', f'</span><span style=\"color:{self.color_err}\">',
                datetime.now().strftime(self._format_time),
                f'</span><span style=\"color:{self.color_simple}\">', inv_args, f'{b}</span>'
            )))

    # Информация
    def _info(self, message: str):
        """
        Информация

        Аргументы:
           message - Сообщение
        """

        if self.is_notebook is True:
            b = '**' if self.bold_text is True else ''

            if type(message) is str and message:
                # Текущее сообщение резервируется для дальшейшего использования
                self._info_last = ('{}' * 4).format(
                    f'<span style=\"color:{self.color_simple}\">{b}[</span><span style=\"color:{self.color_info}\">',
                    datetime.now().strftime(self._format_time),
                    f'</span><span style=\"color:{self.color_simple}\">]</span> ',
                    f'<span style=\"color:{self.color_simple}\">{message}</span>{b}'
                )

            # Отображение
            display(Markdown(self._info_last))

    # Ошибки
    def _error(self, message: str):
        """
        Ошибки

        Аргументы:
           message - Сообщение
        """

        if self.is_notebook is True:
            b = '**' if self.bold_text is True else ''

            # Отображение
            display(Markdown('{}[{}{}{}] {}{}'.format(
                f'<span style=\"color:{self.color_simple}\">{b}', f'</span><span style=\"color:{self.color_err}\">',
                datetime.now().strftime(self._format_time),
                f'</span><span style=\"color:{self.color_simple}\">', message, f'{b}</span>'
            )))

    # Прочие ошибки
    def _other_error(self, message: str):
        """
        Прочие ошибки

        Аргументы:
           message - Сообщение
        """

        trac = self._traceback()  # Трассировка исключений
        tab = '&nbsp;' * 4

        if self.is_notebook is True:
            b = '**' if self.bold_text is True else ''
            cr = self.color_simple

            # Отображение
            display(Markdown(('{}' * 8).format(
                f'<span style=\"color:{cr}\">{b}[</span><span style=\"color:{self.color_err}\">',
                datetime.now().strftime(self._format_time),
                f'</span><span style=\"color:{cr}\">]</span> ',
                f'<span style=\"color:{cr}\">{message}</span>{b}',
                f'<p><span style=\"color:{cr}\">{tab}{self._trac_file}: <u>{trac["filename"]}</u></span>',
                f'<br /><span style=\"color:{cr}\">{tab}{self._trac_line}: <u>{trac["lineno"]}</u></span>',
                f'<br /><span style=\"color:{cr}\">{tab}{self._trac_method}: <u>{trac["name"]}</u></span>',
                f'<br /><span style=\"color:{cr}\">{tab}{self._trac_type_err}: <u>{trac["type"]}</u></span></p>'
            )))

    # Положительная информация
    def _info_true(self, message: str):
        """
        Положительная информация

        Аргументы:
           message: Сообщение
        """

        if self.is_notebook is True:
            b = '**' if self.bold_text is True else ''

            display(Markdown('{}'.format(f'<span style=\"color:{self.color_true}\">{b}{message}{b}</span>')))

    # Начало времени выполнения
    def _r_start(self):
        """
        Начало времени выполнения
        """

        self._runtime = self._start_time = -1  # Сброс значений

        self._start_time = time.time()  # Отсчет времени выполнения

    # Конец времени выполнения
    def _r_end(self):
        """
        Конец времени выполнения
        """

        self._runtime = round(time.time() - self._start_time, 3)  # Время выполнения

        t = '--- {}: {} {} ---'.format(self.text_runtime, self._runtime, self._sec)

        if self.is_notebook is True:
            b = '**' if self.bold_text is True else ''

            # Отображение
            display(Markdown('{}'.format(f'<span style=\"color:{self.color_simple}\">{b}{t}{b}</span>')))

    # Индикатор выполнения
    def _progressbar(self, message: str, progress: str):
        """
        Индикатор выполнения

        Аргументы:
           message - Сообщение
           progress - Индикатор выполнения
        """

        tab = '&nbsp;' * 4

        if self.is_notebook is True:
            b = '**' if self.bold_text is True else ''

            # Отображение
            display(Markdown(('{}' * 5).format(
                f'<span style=\"color:{self.color_simple}\">{b}[</span><span style=\"color:{self.color_info}\">',
                datetime.now().strftime(self._format_time),
                f'</span><span style=\"color:{self.color_simple}\">]</span> ',
                f'<span style=\"color:{self.color_simple}\">{message}</span>{b}',
                f'<p><span style=\"color:{self.color_simple}\">{tab}{progress}</span></p>'
            )))

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
        else:
            return True

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
                    f'<span style=\"color:{self.color_err}\">', e.code, f'</span>'
                )))
            except urllib.error.URLError: self._other_error(self._url_error_log.format(''))
            except Exception:
                self._other_error(self._unknown_err); return False
            else:
                return True

        return False

    # ------------------------------------------------------------------------------------------------------------------
    # Внешние методы
    # ------------------------------------------------------------------------------------------------------------------

    # Версии установленных библиотек
    def libs_vers(self, runtime: bool = True):
        """
        Версии установленных библиотек

        Аргументы:
            runtime - Подсчет времени выполнения
        """

        # Сброс
        self._df_pkgs = pd.DataFrame()  # Пустой DataFrame

        try:
            # Проверка аргументов
            if type(runtime) is not bool: raise TypeError
        except TypeError: self._inv_args(__class__.__name__, self.libs_vers.__name__)
        else:
            if runtime: self._r_start()

            pkgs = {
                'Package': [
                    'PyTorch', 'Torchaudio', 'NumPy', 'Pandas', 'Matplotlib', 'JupyterLab', 'Pymediainfo'
                ],
                'Version': [i.__version__ for i in [torch, torchaudio, np, pd, mpl, jlab, pymediainfo]]
            }

            self._df_pkgs = pd.DataFrame(data = pkgs)  # Версии используемых библиотек
            self._df_pkgs.index += 1

            # Отображение
            if self.is_notebook is True: display(self._df_pkgs)

            if runtime: self._r_end()
