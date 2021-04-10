#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Разархивирование архивов
"""

# ######################################################################################################################
# Импорт необходимых инструментов
# ######################################################################################################################
# Подавление Warning
import warnings
for warn in [UserWarning, FutureWarning]: warnings.filterwarnings('ignore', category = warn)

from dataclasses import dataclass  # Класс данных

import os                                # Взаимодействие с файловой системой
from zipfile import ZipFile, BadZipFile  # Работа с ZIP архивами
from pathlib import Path                 # Работа с путями в файловой системе
import shutil                            # Набор функций высокого уровня для обработки файлов, групп файлов, и папок

from typing import List  # Типы данных

from IPython.display import clear_output

# Персональные
from neweraai.modules.core.core import Core  # Ядро

# ######################################################################################################################
# Сообщения
# ######################################################################################################################
@dataclass
class Messages(Core):
    """Сообщения"""

    # ------------------------------------------------------------------------------------------------------------------
    # Конструктор
    # ------------------------------------------------------------------------------------------------------------------

    def __post_init__(self):
        super().__post_init__()  # Выполнение конструктора из суперкласса

        self._automatic_unzip: str = self._('Разархивирование архива "{}"')
        self._download_precent: str = ' ({}%) ...'
        self._error_unzip: str = self._oh + self._('не удалось разархивировать архив "{}" ...')
        self._error_rename: str = self._oh + self._('не удалось переименовать директорию из "{}" в "{}" ...')


# ######################################################################################################################
# Разархивирование архивов
# ######################################################################################################################
class Unzip(Messages):
    """Разархивирование архивов"""

    # ------------------------------------------------------------------------------------------------------------------
    # Конструктор
    # ------------------------------------------------------------------------------------------------------------------

    def __post_init__(self):
        super().__post_init__()  # Выполнение конструктора из суперкласса

        self._exts_zip: List = ['.zip']  # Поддерживаемые расширения архивов

        self._path_to_unzip: str or None = None  # Имя директории для разархивирования

    # ------------------------------------------------------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------------------------------------------------------

    # Получение директории для разархивирования
    @property
    def path_to_unzip(self): return self._path_to_unzip

    # ------------------------------------------------------------------------------------------------------------------
    # Внутренние методы
    # ------------------------------------------------------------------------------------------------------------------

    # Индикатор выполнения
    def __progressbar_unzip(self, path_to_zipfile: str, item: float, out: bool):
        """
        Индикатор выполнения

        Аргументы:
            path_to_zipfile - Путь до архива
            item - Процент выполнения
            out - Отображение
        """

        clear_output(True)
        self._info(self._automatic_unzip.format(self._info_wrapper(Path(path_to_zipfile).name))
                   + self._download_precent.format(item), last = True, out = False)

        if out: self.show_notebook_history_output()

    # ------------------------------------------------------------------------------------------------------------------
    # Внутренние методы
    # ------------------------------------------------------------------------------------------------------------------

    # Распаковка архивов
    def _unzip(self, path_to_zipfile: str, new_name: str or None = None, force_reload: bool = True,
               out: bool = True, runtime: bool = True, run: bool = True) -> bool:
        """
        Распаковка архивов

        Аргументы:
            path_to_zipfile - Путь до архива
            new_name - Имя директории для разархивирования
            force_reload - Принудительное разархивирование
            out - Отображение
            runtime - Подсчет времени выполнения
            run - Блокировка выполнения

        Возвращает: True если разархивирование прошло успешно, в обратном случае False
        """

        try:
            if new_name is None: new_name = path_to_zipfile  # Имя директории для разархивирования не задана

            # Проверка аргументов
            if (type(path_to_zipfile) is not str or not path_to_zipfile or type(new_name) is not str or not new_name
                or type(force_reload) is not bool or type(out) is not bool or type(runtime) is not bool
                or type(run) is not bool): raise TypeError
        except TypeError: self._inv_args(__class__.__name__, self._unzip.__name__, out = out); return False
        else:
            # Блокировка выполнения
            if run is False: self._error(self._lock_user, out = out); return False

            if runtime: self._r_start()

            # Нормализация путей
            path_to_zipfile = os.path.normpath(path_to_zipfile)
            new_name = os.path.normpath(new_name)

            # Имя директории для разархивирования
            if path_to_zipfile == new_name: self._path_to_unzip = str(Path(path_to_zipfile).with_suffix(''))
            else: self._path_to_unzip = os.path.join(self.path_to_save, Path(new_name).name)

            try:
                # Расширение файла неверное
                if (Path(path_to_zipfile).suffix in self._exts_zip) is False: raise TypeError
            except TypeError: self._other_error(self._wrong_extension.format(
                self._info_wrapper(', '.join(x.replace('.', '') for x in self._exts_zip))
            ), out = out); return False
            else:
                # Информационное сообщение
                self._info(self._automatic_unzip.format(self._info_wrapper(Path(path_to_zipfile).name)), out = False)
                if out: self.show_notebook_history_output()  # Отображение истории вывода сообщений в ячейке Jupyter

                # Принудительное разархивирование отключено
                if force_reload is False:
                    # Каталог уже существует
                    if os.path.isdir(self._path_to_unzip): return True
                try:
                    # Файл не найден
                    if os.path.isfile(path_to_zipfile) is False: raise FileNotFoundError
                except FileNotFoundError: self._other_error(self._file_not_found.format(
                    self._info_wrapper(Path(path_to_zipfile).name)
                ), out = out); return False
                except Exception: self._other_error(self._unknown_err, out = out); return False
                else:
                    extracted_size = 0  # Объем извлеченной информации

                    try:
                        # Процесс разархивирования
                        with ZipFile(path_to_zipfile, 'r') as zf:
                            self.__progressbar_unzip(path_to_zipfile, 0.0, out = out)  # Индикатор выполнения
                            uncompress_size = sum((file.file_size for file in zf.infolist()))  # Общий размер
                            # Проход по всем файлам, которые необходимо разархивировать
                            for file in zf.infolist():
                                extracted_size += file.file_size  # Увеличение общего объема
                                zf.extract(file, self.path_to_save)  # Извлечение файла из архива
                                # Индикатор выполнения
                                self.__progressbar_unzip(path_to_zipfile,
                                                         round(extracted_size * 100 / uncompress_size, 2), out = out)

                            self.__progressbar_unzip(path_to_zipfile, 100, out = out)  # Индикатор выполнения
                    except BadZipFile:
                        self._error(self._error_unzip.format(self._info_wrapper(Path(path_to_zipfile).name)), out = out)
                        return False
                    except Exception: self._other_error(self._unknown_err, out = out); return False
                    else:
                        # Переименовывать директорию не нужно
                        if path_to_zipfile == new_name: return True

                        try:
                            # Принудительное разархивирование включено и каталог уже существует
                            if force_reload is True and os.path.isdir(self._path_to_unzip):
                                # Удаление директории
                                try: shutil.rmtree(self._path_to_unzip)
                                except OSError: os.remove(self._path_to_unzip)
                                except Exception: raise Exception
                        except Exception: self._other_error(self._unknown_err, out = out); return False
                        else:
                            try:
                                # Переименование
                                os.rename(Path(path_to_zipfile).with_suffix(''), self._path_to_unzip)
                            except Exception:
                                self._error(self._error_rename.format(
                                    self._info_wrapper(Path(path_to_zipfile).with_suffix('')),
                                    self._info_wrapper(Path(new_name).name)
                                ), out = out)
                                return False
                            else: return True
            finally:
                if runtime: self._r_end(out = out)

    # ------------------------------------------------------------------------------------------------------------------
    # Внешние методы
    # ------------------------------------------------------------------------------------------------------------------

    # Распаковка архивов (обертка)
    def unzip(self, path_to_zipfile: str, new_name: str or None = None, force_reload: bool = True, out: bool = True,
              runtime: bool = True, run: bool = True) -> bool:
        """
        Распаковка архивов

        Аргументы:
            path_to_zipfile - Путь до архива
            new_name - Имя директории для разархивирования
            force_reload - Принудительное разархивирование
            out - Отображение
            runtime - Подсчет времени выполнения
            run - Блокировка выполнения

        Возвращает: True если разархивирование прошло успешно, в обратном случае False
        """

        self._clear_notebook_history_output()  # Очистка истории вывода сообщений в ячейке Jupyter

        return self._unzip(path_to_zipfile = path_to_zipfile, new_name = new_name, force_reload = force_reload,
                           out = out, runtime = runtime, run = run)