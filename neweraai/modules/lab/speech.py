#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Распознавание речи
"""

# ######################################################################################################################
# Импорт необходимых инструментов
# ######################################################################################################################
# Подавление Warning
import warnings
for warn in [UserWarning, FutureWarning]: warnings.filterwarnings('ignore', category = warn)

from dataclasses import dataclass  # Класс данных

import os            # Взаимодействие с файловой системой
import urllib.parse  # Парсинг URL
import subprocess    # Работа с процессами
import json          # Кодирование и декодирование данных в удобном формате
import pymediainfo   # Получение meta данных из медиафайлов
import pandas as pd  # Обработка и анализ данных

from pymediainfo import MediaInfo  # Получение meta данных из медиафайлов
from pathlib import Path  # Работа с путями в файловой системе

from typing import Dict, List  # Типы данных

from IPython.display import clear_output

from vosk import Model, KaldiRecognizer, SetLogLevel  # Распознавание речи

# Персональные
from neweraai.modules.core.exceptions import LanguagesSRError, DictSRError, SRModelNotActivatedError
from neweraai.modules.lab.statistics import Statistics  # Статистика

# ######################################################################################################################
# Сообщения
# ######################################################################################################################
@dataclass
class Messages(Statistics):
    """Сообщения"""

    # ------------------------------------------------------------------------------------------------------------------
    # Конструктор
    # ------------------------------------------------------------------------------------------------------------------

    def __post_init__(self):
        super().__post_init__()  # Выполнение конструктора из суперкласса

        self._wrong_language: str = self._oh + self._('язык для распознавания должен быть одним из "{}" ...')
        self._wrong_dict: str = self._oh + self._('словарь для распознавания должен быть одним из "{}" ...')
        self._sr_error: str = self._oh + self._('модель распознавания речи не активирована ...')
        self._num_ch_audio_error: str = self._('Количество аудиоканалов должно быть не больше {} ...')
        self._sr_in_progress = self._('Идет процесс распознавания речи ...')
        self._sr_not_recognized: str = self._('Речь не найдена ...')
        self._sr_recognized_stereo : str = self._(' и {}')
        self._sr_recognized: str = self._('Всего найдено {}{} текстовых последовательностей ...')

# ######################################################################################################################
# Распознавание речи
# ######################################################################################################################
class Speech(Messages):
    """Распознавание речи"""

    # ------------------------------------------------------------------------------------------------------------------
    # Конструктор
    # ------------------------------------------------------------------------------------------------------------------

    def __post_init__(self):
        super().__post_init__()  # Выполнение конструктора из суперкласса

        # Пути к моделям распознавания речи
        self._models_url: Dict = {
            'vosk': 'https://alphacephei.com/vosk/models/'
        }

        # Модели для распознавания речи
        self._models_for_sr: Dict = {
            'vosk': {
                'languages': ['ru', 'en'],  # Поддерживаемые языки
                'dicts': ['small', 'big'],  # Размеры словарей
                # Русский язык
                'ru' : {
                    'big': 'vosk-model-ru-0.10.zip',
                    'small': 'vosk-model-small-ru-0.4.zip'
                },
                # Английский язык
                'en': {
                    'big': 'vosk-model-en-us-aspire-0.2.zip',
                    'small': 'vosk-model-small-en-us-0.15.zip'
                }
            },
        }

        self._freq_sr: int = 16000  # Частота дискретизации

        self._speech_model: Model or None = None  # Модель распознавания речи
        self._speech_rec: KaldiRecognizer or None = None  # Активация распознавания речи
        self._keys_speech_rec = ['result', 'text']  # Ключи из результата распознавания речи

        # ----------------------- Только для внутреннего использования внутри класса

        self.__path_to_file: str = ''  # Путь к аудио или видео файлу
        self.__ss: str or None = None  # Начало аудио или видеофрагмента
        self.__to: str or None = None  # Конец аудио или видеофрагмента


    # ------------------------------------------------------------------------------------------------------------------
    # Внутренние методы
    # ------------------------------------------------------------------------------------------------------------------

    # Детальная информация о текущем процессе распознавания речи (Vosk)
    @staticmethod
    def __speech_rec_result(keys: List, speech_rec_res: Dict) -> List:
        """
        Детальная информация о текущем процессе распознавания речи (Vosk)

        Аргументы:
            keys - Ключи из результата распознавания
            speech_rec_res - Текущий результат

        Возвращает: Список из текстового представления речи, начала и конца речи
        """

        # Детальная информация распознавания
        if keys[0] in speech_rec_res.keys():
            start = speech_rec_res[keys[0]][0]['start']  # Начало речи

            if len(speech_rec_res[keys[0]]) == 1: idx = 0  # Индекс
            else: idx = -1  # Индекс

            end = speech_rec_res[keys[0]][idx]['end']  # Конец речи
            curr_text = speech_rec_res[keys[1]]  # Распознанный текст

            return [curr_text, round(start, 2), round(end, 2)]  # Текущий результат

        return []

    # Дочерний процесс распознавания речи (Vosk) - видео
    def __subprocess_vosk_sr_video(self, last: bool, out: bool, logs: bool = True) -> List[str]:
        """
        Дочерний процесс распознавания речи (Vosk) - видео

        Аргументы:
            last - Замена последнего сообщения
            out - Отображение
            logs - При необходимости формировать LOG файл

        Возвращает: Список с текстовыми представлениями речи, начала и конца речи
        """

        fragment = []  # Обработка не всего видео

        if type(self.__ss) is str: fragment = fragment + ['-ss', self.__ss]  # Задано время начала видеофрагмента
        if type(self.__to) is str: fragment = fragment + ['-to', self.__to]  # Задано время окончания видеофрагмента

        try:
            # https://trac.ffmpeg.org/wiki/audio%20types
            # Выполнение в новом процессе
            with subprocess.Popen(
                    ['ffmpeg', '-loglevel', 'quiet', '-i', self.__path_to_file] + fragment +
                     ['-ar', str(self._freq_sr), '-ac', str(1), '-f', 's16le', '-'],
                    stdout = subprocess.PIPE) as process:
                results_recognized = []  # Результаты распознавания

                while True:
                    data = process.stdout.read(4000)
                    if len(data) == 0: break

                    curr_res = []  # Текущий результат

                    # Распознанная речь
                    if self._speech_rec.AcceptWaveform(data):
                        speech_rec_res = json.loads(self._speech_rec.Result())  # Текущий результат

                        # Детальная информация распознавания
                        curr_res = self.__speech_rec_result(self._keys_speech_rec, speech_rec_res)
                    else: self._speech_rec.PartialResult()

                    if len(curr_res) == 3: results_recognized.append(curr_res)

                speech_rec_fin_res = json.loads(self._speech_rec.FinalResult())  # Итоговый результат распознавания
                # Детальная информация распознавания
                speech_rec_fin_res = self.__speech_rec_result(self._keys_speech_rec, speech_rec_fin_res)

                # Результат распознавания
                if len(speech_rec_fin_res) == 3: results_recognized.append(speech_rec_fin_res)

                if len(results_recognized) == 0: self._error(self._sr_not_recognized, last = last, out = out); return []
                else: self._test_from_sr(self._sr_recognized.format(self._info_wrapper(len(results_recognized)), ''),
                                         results_recognized, last = last, out = out,
                                         name = self.vosk_sr.__name__ + '_' + Path(self.__path_to_file).stem,
                                         logs = logs)
                return results_recognized
        except OSError: self._error(self._sr_not_recognized, last = last, out = out); return []
        except Exception: self._other_error(self._unknown_err, last = last, out = out); return []

    # Дочерний процесс распознавания речи (Vosk) - аудио
    def __subprocess_vosk_sr_audio(self, last: bool, out: bool, logs: bool = True) -> Dict[str, List]:
        """
        Дочерний процесс распознавания речи (Vosk)  - аудио

        Аргументы:
            last - Замена последнего сообщения
            out - Отображение
            logs - При необходимости формировать LOG файл

        Возвращает: Словарь со вложенными списками из текстового представления речи, начала и конца речи
        """

        # Количество каналов в аудиодорожке
        channels_audio = MediaInfo.parse(self.__path_to_file).to_data()['tracks'][1]['channel_s']

        if channels_audio > 2:
            self._error(self._num_ch_audio_error.format(self._info_wrapper('2')), out = out)
            return {}  # Количество каналов больше 2

        map_channels = {'Mono': '0.0.0'}  # Извлечение моно
        if channels_audio == 2: map_channels = {'Left': '0.0.0', 'Right': '0.0.1'}  # Стерео

        fragment = []  # Обработка не всего аудио

        if type(self.__ss) is str: fragment = fragment + ['-ss', self.__ss]  # Задано время начала аудиофрагмента
        if type(self.__to) is str: fragment = fragment + ['-to', self.__to]  # Задано время окончания аудиофрагмента

        try:
            results_recognized = {}  # Результаты распознавания

            # Проход по всем каналам
            for front, channel in map_channels.items():
                try:
                    # Активация распознавания речи
                    self._speech_rec = KaldiRecognizer(self._speech_model, self._freq_sr)
                except Exception: self._other_error(self._unknown_err, last = last, out = out); return {}
                else:
                    results_recognized[front] = []  # Словарь для результатов определенного канала
                    # https://trac.ffmpeg.org/wiki/audio%20types
                    # Выполнение в новом процессе
                    with subprocess.Popen(
                            ['ffmpeg', '-loglevel', 'quiet', '-i', self.__path_to_file] + fragment +
                            ['-ar', str(self._freq_sr), '-map_channel', channel, '-acodec', 'pcm_s16le',
                             '-ac', str(1), '-f', 's16le', '-'],
                            stdout = subprocess.PIPE) as process:
                        while True:
                            data = process.stdout.read(4000)
                            if len(data) == 0: break

                            curr_res = []  # Текущий результат

                            # Распознанная речь
                            if self._speech_rec.AcceptWaveform(data):
                                speech_rec_res = json.loads(self._speech_rec.Result())  # Текущий результат

                                # Детальная информация распознавания
                                curr_res = self.__speech_rec_result(self._keys_speech_rec, speech_rec_res)
                            else: self._speech_rec.PartialResult()

                            if len(curr_res) == 3: results_recognized[front].append(curr_res)

                        speech_rec_fin_res = json.loads(self._speech_rec.FinalResult())  # Итоговый результат распознавания
                        # Детальная информация распознавания
                        speech_rec_fin_res = self.__speech_rec_result(self._keys_speech_rec, speech_rec_fin_res)

                        # Результат распознавания
                        if len(speech_rec_fin_res) == 3: results_recognized[front].append(speech_rec_fin_res)

            if bool([l for l in results_recognized.values() if l != []]) is False:
                self._error(self._sr_not_recognized, last = last, out = out); return {}
            else:
                self._test_from_sr(
                    self._sr_recognized.format(
                        self._info_wrapper(len(results_recognized[list(results_recognized.keys())[0]])),
                        self._sr_recognized_stereo.format(self._info_wrapper(
                            len(results_recognized[list(results_recognized.keys())[1]])
                        )) if channels_audio == 2 else ''),
                    results_recognized, last = last, out = out,
                    name = self.vosk_sr.__name__ + '_' + Path(self.__path_to_file).stem, logs = logs)
            return results_recognized
        except OSError: self._error(self._sr_not_recognized, last = last, out = out); return {}
        except Exception: self._other_error(self._unknown_err, last = last, out = out); return {}

    # Проверка формата времени на корректное написание
    @staticmethod
    def __check_valid_timedelta(t: str):
        """
        Проверка формата времени на корректное написание

        Аргументы:
            t - Время

        Возвращает: True если формат времени задан верно, в обратном случае False
        """

        # Начало аудио или видеофрагмента
        if t is not None and type(t) is not str: return False
        else:
            if type(t) is str:
                ss_split = t.split(':')  # Разделение времени на составные элементы
                # Формат времени не соответствует 00:00:00.00
                if len(ss_split) != 3 or len(ss_split[-1].split('.')) != 2: return False

                ss_split = ss_split[:-1] + ss_split[-1].split('.') # Разбиение секунд и миллисекунд

                # Проход по всем временым значениям
                for cnt, val in enumerate(ss_split):
                    try:
                        ss_split[cnt] = int(val)  # Попытка приведения строкового числа к числу

                        if ss_split[cnt] < 0: raise ValueError # Значение меньше 0
                    except ValueError: return False  # Нельзя преобразовать временной отрезок в число
                    except Exception: return False

                # Часы и минуты указаны в некорректном диапазоне
                if ss_split[1] >= 60 or ss_split[2] >= 60: return False

        return True

    # ------------------------------------------------------------------------------------------------------------------
    #  Внутренние методы
    # ------------------------------------------------------------------------------------------------------------------

    # Загрузка и активация модели Vosk для распознавания речи
    def _vosk(self, new_name: str or None = None, force_reload: bool = True, out: bool = True, runtime: bool = True,
              run: bool = True) -> bool:
        """
        Загрузка и активация модели Vosk для распознавания речи

        Аргументы:
            new_name - Имя директории для разархивирования модели
            force_reload - Принудительная загрузка модели из сети
            out - Отображение
            runtime - Подсчет времени выполнения
            run - Блокировка выполнения

        Возвращает: True если распознавание речи запущено, в обратном случае False
        """

        try:
            # Проверка аргументов
            if (((type(new_name) is not str or not new_name) and new_name is not None) or type(out) is not bool
                or type(force_reload) is not bool or type(runtime) is not bool or type(run) is not bool):
                    raise TypeError
        except TypeError: self._inv_args(__class__.__name__, self._vosk.__name__, out = out); return False
        else:
            # Блокировка выполнения
            if run is False: self._error(self._lock_user, out = out); return False

            if runtime: self._r_start()

            name = 'vosk'  # Модель для распознавания речи

            # Язык для распознавания речи по умолчанию
            if self.language_sr is None: self.language_sr = self._models_for_sr[name]['languages'][0]
            # Размер словаря для распознавания речи по умолчанию
            if self.dict_language_sr is None: self.dict_language_sr = self._models_for_sr[name]['dicts'][0]

            lsr = self.language_sr  # Язык для распознавания речи
            dlsr = self.dict_language_sr  # Размер словаря для распознавания речи

            try:
                # Проверка настроек ядра
                if type(lsr) is not str or (lsr in self._models_for_sr[name]['languages']) is False:
                    raise LanguagesSRError
                if type(dlsr) is not str or (dlsr in self._models_for_sr[name]['dicts']) is False: raise DictSRError
            except LanguagesSRError: self._other_error(self._wrong_language.format(
                self._info_wrapper(', '.join(x.replace('.', '') for x in self._models_for_sr[name]['languages']))
            ), out = out); return False
            except DictSRError: self._other_error(self._wrong_dict.format(
                self._info_wrapper(', '.join(x.replace('.', '') for x in self._models_for_sr[name]['dicts']))
            ), out = out); return False
            except Exception: self._other_error(self._unknown_err, out = out); return False
            else:
                SetLogLevel(-1)  # Уровень LOG

                try:
                    # Загрузка файла из URL
                    res_download_file_from_url = self._download_file_from_url(
                        url = urllib.parse.urljoin(self._models_url[name], self._models_for_sr[name][lsr][dlsr]),
                        force_reload = force_reload, runtime = False, out = out, run = True)
                except Exception: self._other_error(self._unknown_err, out = out); return False
                else:
                    # Файл загружен
                    if res_download_file_from_url == 200:
                        clear_output(True)

                        try:
                            # Распаковка архива
                            res_unzip = self._unzip(
                                path_to_zipfile = os.path.join(self.path_to_save, self._models_for_sr[name][lsr][dlsr]),
                                new_name = new_name, force_reload = force_reload, runtime = False, out = out, run = True
                            )
                        except Exception: self._other_error(self._unknown_err, out = out); return False
                        else:
                            # Файл распакован
                            if res_unzip is True:
                                try:
                                    self._speech_model = Model(str(self._path_to_unzip))  # Активация модели
                                    # Активация распознавания речи
                                    self._speech_rec = KaldiRecognizer(self._speech_model, self._freq_sr)
                                except Exception: self._other_error(self._unknown_err, out = out)
                                else: return True
                    else: return False
            finally:
                if runtime: self._r_end(out = out)

    # Распознавание речи (Vosk)
    def _vosk_sr(self, path_to_file: str, ss: str or None = None, to: str or None = None, last: bool = False,
                 runtime: bool = True, out: bool = True, logs: bool = True, run: bool = True
                 ) -> Dict[str, List] or List[str]:
        """
        Распознавание речи (Vosk)

        Аргументы:
            path_to_file - Путь к аудио или видео файлу
            ss - Начало аудио или видеофрагмента
            to - Конец аудио или видеофрагмента
            last - Замена последнего сообщения
            runtime - Подсчет времени выполнения
            out - Отображение
            logs - При необходимости формировать LOG файл
            run - Блокировка выполнения

        Возвращает: Словарь со вложенными списками или список из текстового представления речи, начала и конца речи
        """

        # Сброс
        self._df_sr = pd.DataFrame()  # Пустой DataFrame

        try:
            # Проверка аргументов
            if (type(path_to_file) is not str or not path_to_file or Speech.__check_valid_timedelta(ss) is False
                    or Speech.__check_valid_timedelta(to) is False or type(last) is not bool
                    or type(runtime) is not bool or type(out) is not bool or type(logs) is not bool
                    or type(run) is not bool):
                raise TypeError
        except TypeError: self._inv_args(__class__.__name__, self._vosk_sr.__name__, last = last, out = out); return []
        else:
            # Блокировка выполнения
            if run is False: self._error(self._lock_user, out = out); return []

            if runtime: self._r_start()

            self.__path_to_file = os.path.normpath(path_to_file)  # Нормализация пути к аудио или видео файлу
            self.__ss = ss  # Начало аудио или видеофрагмента
            self.__to = to  # Конец аудио или видеофрагмента

            try:
                # Модель распознавания речи не активирована
                if self._speech_model is None or self._speech_rec is None: raise SRModelNotActivatedError
            except SRModelNotActivatedError: self._other_error(self._sr_error, last = last, out = out); return []
            except Exception: self._other_error(self._unknown_err, last = last, out = out); return []
            else:
                try:
                    # Файл не найден
                    if os.path.isfile(self.__path_to_file) is False: raise FileNotFoundError
                except FileNotFoundError: self._other_error(self._file_not_found.format(
                        self._info_wrapper(Path(self.__path_to_file).name)
                    ), last = last, out = out); return []
                except Exception: self._other_error(self._unknown_err, last = last, out = out); return []
                else:
                    if last is False:
                        self._info(self._sr_in_progress, out = False)  # Информационное сообщение
                        # Отображение истории вывода сообщений в ячейке Jupyter
                        if out: self.show_notebook_history_output()

                    # Meta данные
                    metadata = pymediainfo.MediaInfo.parse(self.__path_to_file).to_data()

                    type_info = [*self._type_meta_info]  # Тип файла
                    # Видео обработка
                    if type_info[0] in [track['track_type'] for track in metadata['tracks']]:
                        try:
                            # Активация распознавания речи
                            self._speech_rec = KaldiRecognizer(self._speech_model, self._freq_sr)
                        except Exception: self._other_error(self._unknown_err, last = last, out = out); return []
                        else:
                            return self.__subprocess_vosk_sr_video(last, out, logs)
                    elif type_info[1] in [track['track_type'] for track in metadata['tracks']]:  # Аудио
                        return self.__subprocess_vosk_sr_audio(last, out, logs)
                    else:
                        try: raise TypeError
                        except TypeError: self._other_error(self._som_ww, last = last, out = out); return []
            finally:
                if runtime: self._r_end(out = out)

    # ------------------------------------------------------------------------------------------------------------------
    # Внешние методы
    # ------------------------------------------------------------------------------------------------------------------

    # Загрузка и активация модели Vosk для распознавания речи (обертка)
    def vosk(self, new_name: str or None = None, force_reload: bool = True, out: bool = True, runtime: bool = True,
             run: bool = True) -> bool:
        """
        Загрузка и активация модели Vosk для распознавания речи

        Аргументы:
            new_name - Имя директории для разархивирования модели
            force_reload - Принудительная загрузка модели из сети
            out - Отображение
            runtime - Подсчет времени выполнения
            run - Блокировка выполнения

        Возвращает: True если распознавание речи запущено, в обратном случае False
        """

        self._clear_notebook_history_output()  # Очистка истории вывода сообщений в ячейке Jupyter

        return self._vosk(new_name = new_name, force_reload = force_reload, out = out, runtime = runtime, run = run)

    # Распознавание речи (Vosk) (обертка)
    def vosk_sr(self, path_to_file: str, ss: str or None = None, to: str or None = None, logs: bool = True,
                runtime: bool = True, out: bool = True, run: bool = True) -> Dict[str, List] or List[str]:
        """
        Распознавание речи (Vosk)

        Аргументы:
            path_to_file - Путь к аудио или видео файлу
            ss - Начало аудио или видеофрагмента
            to - Конец аудио или видеофрагмента
            logs - При необходимости формировать LOG файл
            out - Отображение
            runtime - Подсчет времени выполнения
            run - Блокировка выполнения

        Возвращает: Словарь со вложенными списками или список из текстового представления речи, начала и конца речи
        """

        self._clear_notebook_history_output()  # Очистка истории вывода сообщений в ячейке Jupyter

        return self._vosk_sr(path_to_file = path_to_file, ss = ss, to = to, last = False, out = out, logs = logs,
                             runtime = runtime, run = run)