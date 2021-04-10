#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Определение языка
"""

# ######################################################################################################################
# Импорт необходимых инструментов
# ######################################################################################################################
# Интернационализация (I18N) и локализация (L10N) (см. https://www.loc.gov/standards/iso639-2/php/code_list.php)
#     1. locate pygettext.py
#     2. /usr/local/Cellar/python@3.8/3.8.8/Frameworks/Python.framework/Versions/3.8/share/doc/python3.8/examples/Tools/
#        i18n/pygettext.py -d neweraai -o neweraai/modules/locales/base.pot neweraai
#     3. locate msgfmt.py
#     4. /usr/local/Cellar/python@3.8/3.8.8/Frameworks/Python.framework/Versions/3.8/share/doc/python3.8/examples/Tools/
#        i18n/msgfmt.py neweraai/modules/locales/en/LC_MESSAGES/base.po neweraai/modules/locales/en/LC_MESSAGES/base
# Подавление Warning
import warnings
for warn in [UserWarning, FutureWarning]: warnings.filterwarnings('ignore', category = warn)

from dataclasses import dataclass  # Класс данных

import gettext  # Формирование языковых пакетов
import os       # Взаимодействие с файловой системой
import inspect  # Инспектор

# Типы данных
from typing import List, Dict
from types import MethodType

# ######################################################################################################################
# Определение языка
# ######################################################################################################################
@dataclass
class Language:
    """Определение языка"""

    # ------------------------------------------------------------------------------------------------------------------
    # Конструктор
    # ------------------------------------------------------------------------------------------------------------------

    lang_: str = 'en'  # Язык

    def __post_init__(self):
        self.__lang_default: str = self.lang_  # Язык по умолчанию
        # Директория с поддерживаемыми языками
        self.__path_to_locales: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'locales'))

        self.__locales: List[str] = self.__get_languages()  # Поддерживаемые языковые пакеты
        self.__i18n: Dict[str, MethodType] = self.__get_locales()  # Получение языковых пакетов

        self._: MethodType = self.__set_locale(self.lang_)  # Установка языка

    # ------------------------------------------------------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------------------------------------------------------

    @property  # Получение текущего языкового пакета
    def lang_default(self): return self.__lang_default

    @property  # Получение директории с языковыми пакетами
    def path_to_locales(self): return os.path.normpath(self.__path_to_locales)  # Нормализация пути

    @property  # Получение поддерживаемых языковых пакетов
    def locales(self): return self.__locales

    # ------------------------------------------------------------------------------------------------------------------
    # Внутренние методы
    # ------------------------------------------------------------------------------------------------------------------

    # Получение поддерживаемых языков
    def __get_languages(self) -> List[str]:
        """
        Получение поддерживаемых языков

        Возвращает: List поддерживаемых языков
        """

        # Директория с языками найдена
        if os.path.exists(self.path_to_locales):
            # Формирование списка с подерживаемыми языками
            return next(os.walk(self.path_to_locales))[1]

        return []

    # Получение языковых пакетов
    def __get_locales(self) -> Dict[str, MethodType]:
        """
        Получение языковых пакетов

        Возвращает: Dict[MethodType] с языковыми пакетами
        """

        trs_base = {}  # Языки

        # Проход по всем языкам
        for curr_lang in self.locales:
            trs_base[curr_lang] = gettext.translation(
                'base',  # Домен
                localedir = self.path_to_locales,  # Директория с поддерживаемыми языками
                languages = [curr_lang],  # Язык
                fallback = True  # Отключение ошибки
            ).gettext

            self.__lang_default = curr_lang  # Изменение языка

        return trs_base

    # Установка языка
    def __set_locale(self, lang: str = '') -> MethodType or None:
        """
        Установка языка

        Аргументы:
           lang - Язык пакета

        Возвращает: MethodType перевода строк на один из поддерживаемых языков если метод запущен через конструктор
        """

        try:
            # Проверка аргументов
            if type(lang) is not str: raise TypeError
        except TypeError: pass
        else:
            # Проход по всем языкам
            for curr_lang in self.locales:
                # В аргументах командной строки не найден язык
                if lang != curr_lang: continue

                self.__lang_default = curr_lang  # Изменение языка

            # Метод запущен в конструкторе
            if inspect.stack()[1].function == "__init__" or inspect.stack()[1].function == "__post_init__":
                return self.__i18n[self.lang_default]
            else: self._ = self.__i18n[self.lang_default]  # Установка языка
