#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ядро
"""

# ######################################################################################################################
# Импорт необходимых инструментов
# ######################################################################################################################
import sys                 # Доступ к некоторым переменным и функциям Python
import argparse            # Парсинг аргументов и параметров командной строки
import time                # Работа со временем
import pandas as pd        # Обработка и анализ данных
import numpy as np         # Научные вычисления
import matplotlib as mpl   # Визуализация графиков
import jupyterlab as jlab  # Интерактивная среда разработки для работы с блокнотами, кодом и данными
import colorama            # Цветной текст терминала
import tabulate as tb      # Отображение DataFrame в консоле

from datetime import datetime  # Работа со временем
from typing import Dict        # Типы данных
from tabulate import tabulate  # Отображение DataFrame в консоле

from IPython.display import Markdown, display, clear_output

# Персональные
from neweraai.modules.core.settings import Settings  # Глобальный файл настроек

# ######################################################################################################################
# Сообщения
# ######################################################################################################################
class Messages(Settings):
    """Класс для сообщений"""

    # ------------------------------------------------------------------------------------------------------------------
    # Конструктор
    # ------------------------------------------------------------------------------------------------------------------

    def __init__(self):
        super().__init__()  # Выполнение конструктора из суперкласса

        self._trac_file: str = self._('Файл')
        self._trac_line: str = self._('Линия')
        self._trac_method: str = self._('Метод')
        self._trac_type_err: str = self._('Тип ошибки')

        self._sec: str = self._('сек.')

# ######################################################################################################################
# Ядро модулей
# ######################################################################################################################
class Core(Messages):
    """Ядро модулей"""

    # ------------------------------------------------------------------------------------------------------------------
    # Конструктор
    # ------------------------------------------------------------------------------------------------------------------

    def __init__(self):
        super().__init__()  # Выполнение конструктора из суперкласса

        self._is_notebook = self.__is_notebook()  # Определение запуска пакета в Jupyter или аналогах

        self._ap: argparse.ArgumentParser or None = None  # Парсер для параметров командной строки

        self._start_time: int = -1  # Старт времени выполнения
        self._runtime: int = -1  # Время выполнения

        self._df_pkgs: pd.DataFrame = pd.DataFrame()  # DataFrame c версиями установленных библиотек


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
            b = '**' if self.bold_runtime is True else ''

            # Отображение
            display(Markdown('{}[{}{}{}] {}{}'.format(
                f'<span style=\"color:{self.color_runtime}\">{b}', f'</span><span style=\"color:#FF0000\">',
                datetime.now().strftime(self._format_time),
                f'</span><span style=\"color:{self.color_runtime}\">', inv_args, f'{b}</span>'
            )))
        else:
            print('[{}{}{}] {}'.format(
                self.red, datetime.now().strftime(self._format_time),
                self.end, inv_args,
            ))

    # Ошибки
    def _other_error(self, message: str):
        """
        Ошибки

        Аргументы:
           message: Сообщение
        """

        trac = self._traceback()  # Трассировка исключений
        tab = '&nbsp;' * 4

        if self.is_notebook is True:
            b = '**' if self.bold_runtime is True else ''
            cr = self.color_runtime

            # Отображение
            display(Markdown(('{}' * 8).format(
                f'<span style=\"color:{cr}\">{b}[</span><span style=\"color:#FF0000\">',
                datetime.now().strftime(self._format_time),
                f'</span><span style=\"color:{cr}\">]</span> ',
                f'<span style=\"color:{cr}\">{message}</span>{b}',
                f'<p><span style=\"color:{cr}\">{tab}{self._trac_file}: <u>{trac["filename"]}</u></span>',
                f'<br /><span style=\"color:{cr}\">{tab}{self._trac_line}: <u>{trac["lineno"]}</u></span>',
                f'<br /><span style=\"color:{cr}\">{tab}{self._trac_method}: <u>{trac["name"]}</u></span>',
                f'<br /><span style=\"color:{cr}\">{tab}{self._trac_type_err}: <u>{trac["type"]}</u></span></p>'
            )))
        else:
            template = '[{}{}{}] {} \n    ' + ('{}: {}{}{}\n    ' * 3) + '{}: {}{}{}'

            print(template.format(
                self.red, datetime.now().strftime(self._format_time), self.end, message,
                self._trac_file, self.underline, trac["filename"], self.end,
                self._trac_line, self.underline, trac["lineno"], self.end,
                self._trac_method, self.underline, trac["name"], self.end,
                self._trac_type_err, self.underline, trac["type"], self.end
            ))

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
            b = '**' if self.bold_runtime is True else ''

            # Отображение
            display(Markdown('{}'.format(f'<span style=\"color:{self.color_runtime}\">{b}{t}{b}</span>')))
        else:
            print(t)


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

    # ------------------------------------------------------------------------------------------------------------------
    # Внешние методы
    # ------------------------------------------------------------------------------------------------------------------

    # Построение аргументов командной строки
    def build_args(self, description: str, conv_to_dict: bool = True) -> Dict or None:
        """
        Построение аргументов командной строки

        Аргументы:
           description  - Описание парсера командной строки
           conv_to_dict - Преобразование списка аргументов командной строки в словарь

        Возвращает: Dict если парсер командной строки окончательный, в обратном случае None
        """

        try:
            if self.is_notebook is True: raise PermissionError
        except PermissionError:
            self._other_error(self._method_not_supported.format(__class__.__name__, self.build_args.__name__))
        else:
            try:
                # Проверка аргументов
                if type(description) is not str or not description or type(conv_to_dict) is not bool: raise TypeError
            except TypeError: self._inv_args(__class__.__name__, self.build_args.__name__)
            else:
                # Парсер для параметров командной строки
                self._ap = argparse.ArgumentParser(description = description)

                if conv_to_dict is True:
                    return vars(self._ap.parse_args())  # Преобразование списка аргументов командной строки в словарь

    # Версии установленных библиотек
    def libs_vers(self, runtime: bool = True):
        """
        Версии установленных библиотек

        Аргументы:
            runtime: Подсчет времени выполнения
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
                    'NumPy', 'Pandas', 'Matplotlib', 'JupyterLab', 'Colorama', 'Tabulate'
                ],
                'Version': [i.__version__ for i in [np, pd, mpl, jlab, colorama, tb]]
            }

            self._df_pkgs = pd.DataFrame(data = pkgs)  # Версии используемых библиотек
            self._df_pkgs.index += 1

            # Отображение
            if self.is_notebook is True: display(self._df_pkgs)
            else: print(tabulate(self._df_pkgs, headers='keys', tablefmt='psql'))

            if runtime: self._r_end()
