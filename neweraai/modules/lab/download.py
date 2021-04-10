#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Загрузка
"""

# ######################################################################################################################
# Импорт необходимых инструментов
# ######################################################################################################################
# Подавление Warning
import warnings
for warn in [UserWarning, FutureWarning]: warnings.filterwarnings('ignore', category = warn)

from dataclasses import dataclass  # Класс данных

import os           # Взаимодействие с файловой системой
import numpy as np  # Научные вычисления
import requests     # Отправка HTTP запросов
import re           # Регулярные выражения
import shutil       # Набор функций высокого уровня для обработки файлов, групп файлов, и папок

from pathlib import Path  # Работа с путями в файловой системе

from IPython.display import clear_output

# Персональные
from neweraai.modules.lab.unzip import Unzip  # Распаковка архивов

# ######################################################################################################################
# Сообщения
# ######################################################################################################################
@dataclass
class Messages(Unzip):
    """Сообщения"""

    # ------------------------------------------------------------------------------------------------------------------
    # Конструктор
    # ------------------------------------------------------------------------------------------------------------------

    def __post_init__(self):
        super().__post_init__()  # Выполнение конструктора из суперкласса

        self._could_not_process_url = self._oh + self._('не удалось обработать указанный URL ...')
        self._url_incorrect = self._oh + self._('URL указан некорректно ...')
        self._automatic_download: str = self._('Загрузка файла "{}"')
        self._url_error_code_http: str = self._(' (ошибка {})')
        self._url_error_http: str = self._oh + self._('не удалось скачать файл "{}"{} ...')

# ######################################################################################################################
# Загрузка
# ######################################################################################################################
class Download(Messages):
    """Загрузка"""

    # ------------------------------------------------------------------------------------------------------------------
    # Конструктор
    # ------------------------------------------------------------------------------------------------------------------

    def __post_init__(self):
        super().__post_init__()  # Выполнение конструктора из суперкласса

        self._headers: str = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/89.0.4389.90 Safari/537.36')  # User-Agent

    # ------------------------------------------------------------------------------------------------------------------
    # Внутренние методы
    # ------------------------------------------------------------------------------------------------------------------

    # Индикатор выполнения
    def __progressbar_download_file_from_url(self, url_filename: str, item: float, out: bool):
        """
        Индикатор выполнения

        Аргументы:
            url_filename - Путь до файла
            item - Процент выполнения
        """

        clear_output(True)
        self._info(
            self._automatic_download.format(self._info_wrapper(url_filename))
            + self._download_precent.format(item), last = True, out = False
        )
        if out: self.show_notebook_history_output()

    # ------------------------------------------------------------------------------------------------------------------
    # Внутренние методы
    # ------------------------------------------------------------------------------------------------------------------

    # Загрузка файла из URL
    def _download_file_from_url(self, url: str, force_reload: bool = True, out: bool = True, runtime: bool = True,
                                run: bool = True) -> int:
        """
        Загрузка файла из URL

        Аргументы:
            url - Полный путь к файлу
            force_reload - Принудительная загрузка файла из сети
            out - Отображение
            runtime - Подсчет времени выполнения
            run - Блокировка выполнения

        Возвращает: Код статуса ответа
            200 - Файл загружен
            400 - Ошибка при проверке аргументов
            403 - Выполнение заблокировано пользователем
            404 - Не удалось скачать файл
        """

        try:
            # Проверка аргументов
            if (type(url) is not str or not url or type(force_reload) is not bool or type(out) is not bool
                or type(runtime) is not bool or type(run) is not bool): raise TypeError
        except TypeError:
            self._inv_args(__class__.__name__, self._download_file_from_url.__name__, out = out); return 400
        else:
            # Блокировка выполнения
            if run is False: self._error(self._lock_user, out = out); return 403

            if runtime: self._r_start()

            try:
                # Отправка GET запроса для получения файла
                r = requests.get(url, headers = {'user-agent': self._headers}, stream = True)
            except (
                # https://requests.readthedocs.io/en/master/_modules/requests/exceptions/
                requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema,
                requests.exceptions.ConnectionError, requests.exceptions.InvalidURL
            ): self._other_error(self._could_not_process_url, out = out); return 404
            except Exception: self._other_error(self._unknown_err, out = out); return 404
            else:
                # Имя файла
                if 'Content-Disposition' in r.headers.keys():
                    url_filename = re.findall('filename=(.+)', r.headers['Content-Disposition'])[0]
                else: url_filename = url.split('/')[-1]

                try:
                    # URL файл невалидный
                    if len(url.split('/')) < 4 or not url_filename: raise requests.exceptions.InvalidURL
                except requests.exceptions.InvalidURL: self._other_error(self._url_incorrect, out = out); return 404
                except Exception: self._other_error(self._unknown_err, out = out); return 404
                else:
                    # Информационное сообщение
                    self._info(self._automatic_download.format(self._info_wrapper(url_filename)), out = False)
                    if out: self.show_notebook_history_output()  # Отображение истории вывода сообщений в ячейке Jupyter

                    # Директория для сохранения файла
                    if not os.path.exists(self.path_to_save): os.makedirs(self.path_to_save)

                    local_file = os.path.join(self.path_to_save, url_filename)  # Путь к файлу

                    try:
                        # Принудительная загрузка файла из сети
                        if force_reload is True:
                            # Файл найден
                            if os.path.isfile(local_file) is True:
                                # Удаление файла
                                try: shutil.rmtree(local_file)
                                except OSError: os.remove(local_file)
                                except Exception: raise Exception
                    except Exception: self._other_error(self._unknown_err, out = out); return 404
                    else:
                        # Файл с указанным именем найден локально и принудительная загрузка файла из сети не указана
                        if Path(local_file).is_file() is True and force_reload is False: return 200
                        else:
                            # Ответ получен
                            if r.status_code == 200:
                                total_length = int(r.headers.get('content-length', 0))  # Длина файла

                                num_bars = int(np.ceil(total_length / self.chunk_size))  # Количество загрузок

                                try:
                                    # Открытие файла для записи
                                    with open(local_file, 'wb') as f:
                                        # Индикатор выполнения
                                        self.__progressbar_download_file_from_url(url_filename, 0.0, out = out)

                                        # Сохранение файла по частям
                                        for i, chunk in enumerate(r.iter_content(chunk_size = self.chunk_size)):
                                            f.write(chunk)  # Запись в файл
                                            f.flush()

                                            # Индикатор выполнения
                                            self.__progressbar_download_file_from_url(
                                                url_filename, round(i * 100 / num_bars, 2), out = out)

                                        # Индикатор выполнения
                                        self.__progressbar_download_file_from_url(url_filename, 100, out = out)
                                except Exception: self._other_error(self._unknown_err, out = out); return 404
                                else: return 200
                            else:
                                self._error(self._url_error_http.format(
                                    self._info_wrapper(url_filename),
                                    self._url_error_code_http.format(self._error_wrapper(r.status_code))
                                ), out = out)

                                return 404
            finally:
                if runtime: self._r_end(out = out)

    # ------------------------------------------------------------------------------------------------------------------
    # Внешние методы
    # ------------------------------------------------------------------------------------------------------------------

    # Загрузка файла из URL (обертка)
    def download_file_from_url(self, url: str, force_reload: bool = True, out: bool = True, runtime: bool = True,
                               run: bool = True) -> int:
        """
        Загрузка файла из URL

        Аргументы:
            url - Полный путь к файлу
            force_reload - Принудительная загрузка файла из сети
            out - Отображение
            runtime - Подсчет времени выполнения
            run - Блокировка выполнения

        Возвращает: Код статуса ответа
            200 - Файл загружен
            400 - Ошибка при проверке аргументов
            403 - Выполнение заблокировано пользователем
            404 - Не удалось скачать файл
        """

        self._clear_notebook_history_output()  # Очистка истории вывода сообщений в ячейке Jupyter

        return self._download_file_from_url(url = url, force_reload = force_reload, out = out, runtime = runtime,
                                            run = run)