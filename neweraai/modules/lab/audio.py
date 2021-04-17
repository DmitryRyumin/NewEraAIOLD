#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Аудио
"""

# ######################################################################################################################
# Импорт необходимых инструментов
# ######################################################################################################################
# Подавление Warning
import warnings
for warn in [UserWarning, FutureWarning]: warnings.filterwarnings('ignore', category = warn)

from dataclasses import dataclass  # Класс данных

import os            # Взаимодействие с файловой системой
import subprocess    # Работа с процессами
import torch         # Машинное обучение от Facebook
import urllib.parse  # Парсинг URL
import urllib.error  # Обработка ошибок URL
import pandas as pd  # Обработка и анализ данных

from pathlib import Path  # Работа с путями в файловой системе

from pymediainfo import MediaInfo         # Получение meta данных из медиафайлов
from datetime import datetime, timedelta  # Работа со временем

from typing import List, Callable  # Типы данных

from IPython.display import clear_output, display
from IPython.utils import io  # Подавление вывода

# Персональные
from neweraai.modules.core.exceptions import TypeEncodeVideoError, PresetCFREncodeVideoError, SRInputTypeError,\
    IsADirectoryOriginalError, IsADirectorySplittedError
from neweraai.modules.lab.speech import Speech  # Распознавание речи

# ######################################################################################################################
# Сообщения
# ######################################################################################################################
@dataclass
class Messages(Speech):
    """Сообщения"""

    # ------------------------------------------------------------------------------------------------------------------
    # Конструктор
    # ------------------------------------------------------------------------------------------------------------------

    def __post_init__(self):
        super().__post_init__()  # Выполнение конструктора из суперкласса

        self._extract_audio_from_video: str = self._('Извлечение аудиодорожек из видеофайлов ...')
        self._curr_progress: str = '{} ' + self._from_precent + ' {} ({}%) ... {} ...'
        self._curr_progress_vad: str = ('{} ' + self._from_precent + ' {} ({}%) ... {} ({} '
                                        + self._from_precent + ' {} - {}%) ...')
        self._extract_audio_from_video_err: str = self._('Всего видеофайлов из которых аудиодорожка не была '
                                                         'извлечена - {} ...')
        self._extract_audio_from_video_true: str = self._('Все аудиодорожки были успешно извлечены ... это хороший '
                                                          'знак ...')

        self._download_model_from_repo: str = self._('Загрузка VAD модели "{}" из репозитория {} ...')
        self._create_folder_filter_sr: str = self._('Создание директорий под фильтр распознавания речи ...')

        self._url_error_code: str = self._(' (ошибка {})')
        self._url_error: str = self._oh + self._('не удалось скачать модель{} ...')

        self._audio_track_analysis: str = self._('Анализ аудиодорожек {}...')
        self._audio_track_sr: str = self._(' и распознавание речи ')
        self._vad_err: str = self._('Всего видеофайлов на которых VAD не отработал - {} ...')
        self._save_sr_err: str = self._('Всего видеофрагментов, которые не сохранились - {} ...')
        self._vad_true: str = self._('Все аудиодорожки были проанализированы ... это хороший знак ...')

        self._wrong_type_encode: str = self._oh + self._('тип кодирования видео должен быть одним из "{}" ...')
        self._wrong_preset_crf_encode: str = self._oh + self._('скорость кодирования и сжатия видео должна быть '
                                                               'одной из "{}" ...')
        self._wrong_sr_input_type: str = self._oh + self._('тип файла для распознавания должен быть одним из "{}" ...')


# ######################################################################################################################
# Аудио
# ######################################################################################################################
class Audio(Messages):
    """Аудио"""

    # ------------------------------------------------------------------------------------------------------------------
    # Конструктор
    # ------------------------------------------------------------------------------------------------------------------

    def __post_init__(self):
        super().__post_init__()  # Выполнение конструктора из суперкласса

        # DataFrame c видеофайлами из которых аудиодорожка не извлечена
        self._df_unprocessed_afv: pd.DataFrame = pd.DataFrame()
        # DataFrame c видеофайлами из которых VAD не отработал
        self._df_unprocessed_vad: pd.DataFrame = pd.DataFrame()
        # DataFrame c видеофайлами которые не сохранились при обработке VAD
        self._df_not_saved_files_sr: pd.DataFrame = pd.DataFrame()

        self._github_repo_vad: str = 'snakers4/silero-vad'  # Репозиторий для загрузки VAD
        self._vad_model: str = 'silero_vad'  # VAD модель

        self._types_encode: List[str] = ['qscale', 'crf']  # Типы кодирования
        # Параметр обеспечивающий определенную скорость кодирования и сжатия
        self._presets_crf_encode: List[str] = [
            'ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow'
        ]

        # ----------------------- Только для внутреннего использования внутри класса

        self.__audio_path: str = ''  # Путь до аудиофайла
        self.__wav: torch.Tensor or None = None  # Аудиофайл для VAD
        self.__get_speech_ts: Callable or None = None  # Временные метки VAD
        self.__model: torch.jit._script.RecursiveScriptModule or None = None  # VAD модель
        self.__trig_sum: float = 0.0  # Средняя вероятность переключения между перекрывающими окнами (речь)
        self.__neg_trig_sum: float = 0.0 # Средняя вероятность переключения между перекрывающими окнами (речи нет)
        self.__num_steps: int = 0  # Количество перекрывающихся окон для разделения звукового фрагмента
        self.__batch_size: int = 0  # Размер выборки
        self.__num_samples_per_window: int = 0  # Количество выборок в каждом окне
        self.__min_speech_samples: int = 0  # Минимальная длительность речевого фрагмента в сэмплах
        # Минимальная длительность тишины в выборках между отдельными речевыми фрагментами
        self.__min_silence_samples: int = 0
        self.__unprocessed_files: List[str] = []  # Видеофайлы на которых VAD не отработал
        self.__not_saved_files: List[str] = []  # Видеофайлы которые не сохранились при обработке VAD
        self.__curr_path: str = ''  # Текущий видеофайл, который обрабатывается VAD + SR
        self.__local_path: Callable or None  # Локальный путь
        self.__sr: bool = True  # Распознавать речь
        self.__i: int = 0  # Счетчик
        self.__len_paths: int = 0  # Количество видеофайлов
        self.__splitted_video: List[str] = []  # Директории с разделенными видеофрагментами
        self.__splitted_audio: List[str] = []  # Директории с разделенными аудиофрагментами
        self.__curr_path_parent: str = ''  # Родительский каталог
        self.__sr_input_type: str = ''  # Тип файла для распознавания речи
        self.__type_encode: str = ''  # Тип кодирования
        self.__crf_value: int = 0  # Качество кодирования
        self.__presets_crf_encode: str = ''  # Параметр обеспечивающий определенную скорость кодирования и сжатия
        self.__curr_ts_cart_name: str = ''  # Текущее время для корзины с не отсортированными файлами (TimeStamp)
        self.__part_video_path: str = ''  # Путь до видеофрагмента
        self.__part_audio_path: str = ''  # Пути до аудиофрагментов
        self.__front: List[str] = []  # Суффикс для аудиофрагментов
        self.__key_audio_sr: int = 0  #Ключ для имен аудиофрагментов

    # ------------------------------------------------------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------------------------------------------------------

    # DataFrame c видеофайлами из которых аудиодорожка не извлечена
    @property
    def df_unprocessed_audio_from_video(self): return self._df_unprocessed_afv

    # DataFrame c видеофайлами из которых VAD не отработал
    @property
    def df_unprocessed_vad(self): return self._df_unprocessed_vad

    # DataFrame c видеофайлами которые не сохранились при обработке VAD
    @property
    def df_not_saved_files_sr(self): return self._df_not_saved_files_sr

    # ------------------------------------------------------------------------------------------------------------------
    # Внутренние методы
    # ------------------------------------------------------------------------------------------------------------------

    # Индикатор выполнения извлечения аудиодорожки из видеофайла
    def __progressbar_audio(self, message: str, item: int, info: str, l: bool, len_paths: int, out: bool):
        """
        Индикатор выполнения

        Аргументы:
            message - Сообщение
            item - Номер видеофайла
            info - Локальный путь
            l - Замена последнего сообщения
            len_paths - Количество видеофайлов
            out - Отображение
        """

        clear_output(True)
        self._progressbar(
            message, self._curr_progress.format(item, len_paths, round(item * 100 / len_paths, 2), info),
            last = l, out = False
        )
        if out: self.show_notebook_history_output()

    # Индикатор выполнения VAD
    def __progressbar_vad(self, message: str, item: int, info: str, l: bool, item2: int, len_paths: int,
                          len_timestamp: int, out: bool):
        """
        Индикатор выполнения

        Аргументы:
            message - Сообщение
            item - Номер видеофайла
            info - Локальный путь
            l - Замена последнего сообщения
            item2 - Номер фрагмента
            len_paths - Количество видеофайлов
            len_timestamp - Количество фрагментов
            out - Отображение
        """

        clear_output(True)
        self._progressbar(
            message,
            self._curr_progress_vad.format(
                item, len_paths, round(item * 100 / len_paths, 2), info,
                item2, len_timestamp, round(item2 * 100 / len_timestamp, 2)
            ), last = l, out = False
        )
        if out: self.show_notebook_history_output()

    # Сохранение списка с видеофайлами из которых аудиодорожка не извлечена
    def __save_log_extract_audio_from_video(self, unprocessed_files: List, out: bool, logs: bool):
        """
        Сохранение списка с видеофайлами из которых аудиодорожка не извлечена

        Аргументы:
            unprocessed_files - Список видеофайлов из которых аудиодорожка не извлечена
            out - Отображение
            logs - При необходимости формировать LOG файл
        """

        self._error(self._extract_audio_from_video_err.format(self._error_wrapper(len(unprocessed_files))), out = out)

        # Формирование DataFrame
        dict_unprocessed_files = {'Files': unprocessed_files}

        self._df_unprocessed_afv = pd.DataFrame(data = dict_unprocessed_files)
        self._df_unprocessed_afv.index += 1
        self._df_unprocessed_afv.index.name = self._keys_id

        # Отображение
        if self.is_notebook is True and out is True: display(self._df_unprocessed_afv.iloc[0:self.num_to_df_display, :])

        if logs is True:
            # Текущее время для лог файла
            # см. datetime.fromtimestamp()
            curr_ts = str(datetime.now().timestamp()).replace('.', '_')

            # Сохранение LOG
            res_save_logs = self._save_logs(self.df_unprocessed_audio_from_video,
                self.extract_audio_from_video.__name__ + '_' + curr_ts)

            if res_save_logs is True: self._info_true(self._logs_save_true, out = out)

    # Сохранение списка с видеофайлами из которых VAD не отработал
    def __save_log_vad(self, unprocessed_files_unique: List, out: bool, logs: bool):
        """
        Сохранение списка с видеофайлами из которых VAD не отработал

        Аргументы:
            unprocessed_files_unique - Список видеофайлов из которых VAD не отработал
            out - Отображение
            logs - При необходимости формировать LOG файл
        """

        self._error(self._vad_err.format(self._error_wrapper(len(unprocessed_files_unique))), out = out)

        # Формирование DataFrame
        dict_unprocessed_files = {'Files': unprocessed_files_unique}

        self._df_unprocessed_vad = pd.DataFrame(data = dict_unprocessed_files)
        self._df_unprocessed_vad.index += 1
        self._df_unprocessed_vad.index.name = self._keys_id

        # Отображение
        if self.is_notebook is True and out is True: display(self._df_unprocessed_vad.iloc[0:self.num_to_df_display, :])

        if logs is True:
            # Текущее время для лог файла
            # см. datetime.fromtimestamp()
            curr_ts = str(datetime.now().timestamp()).replace('.', '_')

            # Сохранение LOG
            res_save_logs = self._save_logs(self._df_unprocessed_vad, self.vad.__name__ + '_' + curr_ts)

            if res_save_logs is True: self._info_true(self._logs_save_true, out = out)

    # Сохранение списка с видеофайлами которые не сохранились при обработке VAD
    def __save_log_save_sr(self, not_saved_files_unique: List, out: bool, logs: bool):
        """
        Сохранение списка с видеофайлами из которых VAD не отработал

        Аргументы:
            not_saved_files_unique - Список видеофайлов которые не сохранились при обработке VAD
            out - Отображение
            logs - При необходимости формировать LOG файл
        """

        self._error(self._save_sr_err.format(self._error_wrapper(len(not_saved_files_unique))), out = out)

        # Формирование DataFrame
        files, starts, ends = map(list, zip(*not_saved_files_unique))  # Распаковка вложенного списка
        dict_not_saved_files = {'Files': files, 'Start': starts, 'End': ends}


        self._df_not_saved_files_sr = pd.DataFrame(data = dict_not_saved_files)
        self._df_not_saved_files_sr.index += 1
        self._df_not_saved_files_sr.index.name = self._keys_id

        # Отображение
        if self.is_notebook is True and out is True:
            display(self._df_not_saved_files_sr.iloc[0:self.num_to_df_display, :])

        if logs is True:
            # Текущее время для лог файла
            # см. datetime.fromtimestamp()
            curr_ts = str(datetime.now().timestamp()).replace('.', '_')

            # Сохранение LOG
            res_save_logs = self._save_logs(self._df_not_saved_files_sr, self.vad.__name__ + '_' + curr_ts)

            if res_save_logs is True: self._info_true(self._logs_save_true, out = out)

    # Уровень вложенности списка
    @staticmethod
    def _nest_level(lst) -> int:
        """
        Уровень вложенности списка

        Аргументы:
            lst - Список

        Возвращает: Уровень вложенности списка в виде числа
        """

        if not isinstance(lst, list): return 0
        if not lst: return 1
        return max(Audio._nest_level(lst[0]) + 1, Audio._nest_level(lst[1:]))

    # Рекурсивный поиск значения в списке
    @staticmethod
    def _recursive_search_value_in_filter_sr(l: List, val: str) -> bool and (str or None):
        """
        Рекурсивный поиск значения в списке

        Аргументы:
            l - Список
            val - Искомое значение

        Возвращает: Результат поиска в виде (bool, str or None)
        """

        # Проход по всему списку
        for item in l:
            # Текущее значение не пустая строка
            if type(item) is str and item:
                try:
                    # Искомое значение найдено
                    if item.lower().replace(' ', '_').strip() == val.lower(): return True, item
                except Exception: continue
            # Текущее значение - список не вложенный
            if type(item) is list and Audio._nest_level(item) < 2:
                recursive = Audio._recursive_search_value_in_filter_sr(item, val)  # Рекурсия
                if recursive[0] is True: return recursive[0], item[0] # Искомое значение найдено
        return False, None

    # Сортировка файла в зависимости от распознанной речи
    def __sort_file_vad(self, results_recognized):
        """
        Сортировка файла в зависимости от распознанной речи

        Аргументы:
            results_recognized - Текстовое представление речи

        Возвращает: True если текстовое представление речи найдено в словаре, в обратном случае False
        """

        curr_val = results_recognized.replace(' ', '_').lower().capitalize().strip()  # Директория для сохранения файла

        # Рекурсивный поиск значения в списке
        filter_sr = self._recursive_search_value_in_filter_sr(self._filter_sr, curr_val)

        # Текстовое представление речи не найдено в словаре
        if filter_sr[0] is False:
            # Текущее время (TimeStamp)
            curr_ts = curr_val + '_' + str(datetime.now().timestamp()).replace('.', '_')

            # Директория для сохранения файла
            curr_val = self.cart_name + self.__curr_ts_cart_name
        else:  # Речь найдена
            curr_val = filter_sr[1].replace(' ', '_')  # Директория для сохранения файла

            curr_ts = str(datetime.now().timestamp()).replace('.', '_')  # Текущее время (TimeStamp)

        # Директория для текущей сортировки распознанной речи
        dir_curr_sr_video = os.path.join(
            self.path_to_original_videos, self._re_inv_chars(self.sub_folder[1]),
            '' if self.__curr_path_parent == '.' else self.__curr_path_parent, self._dir_va[0],
            curr_val if len(self._filter_sr) > 0 else '')
        dir_curr_sr_audio = os.path.join(
            self.path_to_original_videos, self._re_inv_chars(self.sub_folder[1]),
            '' if self.__curr_path_parent == '.' else self.__curr_path_parent, self._dir_va[1],
            curr_val if len(self._filter_sr) > 0 else '')

        try:
            # Проход по всем директориям для сортировки распознанной речи
            for dir_curr_sr in [dir_curr_sr_video, dir_curr_sr_audio]:
                if not os.path.exists(dir_curr_sr): os.makedirs(dir_curr_sr)  # Создание директории
        except Exception: return False
        else:
            # Путь до видеофрагмента
            self.__part_video_path = os.path.join(dir_curr_sr_video, curr_ts + Path(self.__curr_path).suffix.lower())

            if len(self._filter_sr) > 0:
                for cnt_audio, _ in enumerate(self.__part_audio_path):
                    self.__part_audio_path[cnt_audio] = os.path.join(
                        dir_curr_sr_audio, curr_ts + self.__front[cnt_audio] + self.ext_audio)
            else:
                self.__part_audio_path[self.__key_audio_sr] = os.path.join(
                    dir_curr_sr_audio, curr_ts + self.__front[self.__key_audio_sr] + self.ext_audio)

        # Текстовое представление речи найдено в словаре
        if len(self._filter_sr) > 0 and filter_sr[0] is True: return True
        else: return False

    # Анализ аудиодорожки и процесс распознавания речи
    def __audio_analysis(self, out: bool):
        """
        Анализ аудиодорожки и процесс распознавания речи

        Аргументы:
            out - Отображение
        """

        # Количество каналов в аудиодорожке
        channels_audio = MediaInfo.parse(self.__audio_path).to_data()['tracks'][1]['channel_s']
        if channels_audio > 2: self.__unprocessed_files.append(self.__curr_path); return None

        try:
            # Получение временных меток
            speech_timestamps = self.__get_speech_ts(
                self.__wav, self.__model, trig_sum = self.__trig_sum, neg_trig_sum = self.__neg_trig_sum,
                num_steps = self.__num_steps, batch_size = self.__batch_size,
                num_samples_per_window = self.__num_samples_per_window,
                min_speech_samples = self.__min_speech_samples,
                min_silence_samples = self.__min_silence_samples, visualize_probs = False)
        except Exception:
            self.__unprocessed_files.append(self.__curr_path); return None
        else:
            len_speech_timestamps = len(speech_timestamps)  # Количество временных меток

            # Текущее время для корзины с не отсортированными файлами (TimeStamp)
            # см. datetime.fromtimestamp()
            self.__curr_ts_cart_name = str(datetime.now().timestamp()).replace('.', '_')

            # Проход по всем найденным меткам
            for cnt, curr_timestamps in enumerate(speech_timestamps):
                # Индикатор выполнения VAD
                self.__progressbar_vad(
                    self._audio_track_analysis.format(self._audio_track_sr if self.__sr is True else ''),
                    self.__i, self.__local_path(self.__curr_path), True, cnt, self.__len_paths,
                    len_speech_timestamps, out)

                start_time = timedelta(seconds = curr_timestamps['start'] / self._freq_sr)  # Начальное время
                end_time = timedelta(seconds = curr_timestamps['end'] / self._freq_sr)  # Конечное время

                diff_time = end_time - start_time  # Разница между начальным и конечным временем

                self.__curr_path_parent = str(Path(self.__local_path(self.__curr_path)).parent)  # Родительский каталог

                # Путь до видеофрагмента
                self.__part_video_path = os.path.join(
                    self.path_to_original_videos, self._re_inv_chars(self.sub_folder[1]),
                    '' if self.__curr_path_parent == '.' else self.__curr_path_parent, self._dir_va[0],
                    Path(self.__curr_path).stem + '_' + str(cnt) + Path(self.__curr_path).suffix.lower())

                self.__part_audio_path = []  # Пути до аудиофрагментов

                if channels_audio == 1:  # Моно канал
                    self.__front = ['_m']  # Суффикс для аудиофрагментов
                    self.__part_audio_path.append(os.path.join(
                        self.path_to_original_videos, self._re_inv_chars(self.sub_folder[1]),
                        '' if self.__curr_path_parent == '.' else self.__curr_path_parent, self._dir_va[1],
                        Path(self.__curr_path).stem + '_' + str(cnt) + self.ext_audio))
                elif channels_audio == 2:  # Стерео канал
                    self.__front = ['_l', '_r']  # Суффиксы для аудиофрагментов
                    for ch in self.__front:
                        self.__part_audio_path.append(os.path.join(
                            self.path_to_original_videos, self._re_inv_chars(self.sub_folder[1]),
                            '' if self.__curr_path_parent == '.' else self.__curr_path_parent, self._dir_va[1],
                            Path(self.__curr_path).stem + '_' + str(cnt) + ch + self.ext_audio))

                # Удаление видеофайла
                if os.path.isfile(self.__part_video_path) is True: os.remove(self.__part_video_path)
                # Удаление аудиофайлов
                for file in self.__part_audio_path:
                    if os.path.isfile(file) is True: os.remove(file)

                # Распознавание речи по видео
                if self.__sr_input_type == self._dir_va[0]: path_to_file_vosk_sr = self.__curr_path
                else: path_to_file_vosk_sr = self.__audio_path  # Распознавание речи по аудио

                # Распознавание речи
                if self.__sr is True:
                    # Распознавание речи (Vosk)
                    res_vosk_sr = self._vosk_sr(
                        path_to_file = path_to_file_vosk_sr, ss = str(start_time), to = str(end_time), runtime = False,
                        last = True, out = False, logs = False, run = True)

                    if len(res_vosk_sr) == 0: continue  # Речь не найдена

                    sr_curr_res_true = False  # По умолчанию речь не найдена

                    # Распознавание речи по видео
                    if type(res_vosk_sr) is list:
                        res_vosk_sr = res_vosk_sr[0][0].lower()

                        if res_vosk_sr == '': continue  # Речь не найдена

                        sr_curr_res_true = True  # Речь найдена

                        self.__sort_file_vad(res_vosk_sr)  # Сортировка файла в зависимости от распознанной речи
                    # Распознавание речи по аудио
                    elif type(res_vosk_sr) is dict:
                        # Пройтись по аудиоканалам
                        for key, val in enumerate(res_vosk_sr.items()):
                            if len(val[1]) == 0: continue  # Речь не найдена

                            curr_val = val[1][0][0].lower()  # Текущий результат распознавания

                            if curr_val == '': continue  # Речь не найдена

                            sr_curr_res_true = True  # Речь найдена

                            self.__key_audio_sr = key
                            if self.__sort_file_vad(curr_val) is True: break
                else: sr_curr_res_true = True  # VAD

                # Речь найдена
                if sr_curr_res_true is True:
                    not_saved_files = lambda: self.__not_saved_files.append(
                        [self.__curr_path, str(start_time), str(end_time)])
                    try:
                        # Работает с пустыми кадрами в конце видео
                        # ff_video = 'ffmpeg -ss {} -i "{}" -to {} -c copy "{}"'.format(
                        #     start_time, self.__curr_path, diff_time, part_video_path)

                        # Варианты кодирования
                        if self.__type_encode == self._types_encode[0]:
                            # https://trac.ffmpeg.org/wiki/Encode/MPEG-4
                            ff_video = 'ffmpeg -loglevel quiet -ss {} -i "{}" -{} 0 -to {} "{}"'.format(
                                start_time, self.__curr_path, self.__type_encode, diff_time, self.__part_video_path)
                        elif self.__type_encode == self._types_encode[1]:
                            # https://trac.ffmpeg.org/wiki/Encode/H.264
                            ff_video = 'ffmpeg -loglevel quiet -ss {} -i "{}" -{} {} -preset {} -to {} "{}"'.format(
                                start_time, self.__curr_path, self.__type_encode, self.__crf_value,
                                self.__presets_crf_encode, diff_time, self.__part_video_path)

                        if channels_audio == 1:  # Моно канал
                            ff_audio = 'ffmpeg -loglevel quiet -i "{}" -ss {} -to {} -c copy "{}"'.format(
                                self.__audio_path, start_time, end_time, self.__part_audio_path[0])
                        elif channels_audio == 2:  # Стерео канал
                            ff_audio = ('ffmpeg -loglevel quiet -i "{}" -map_channel 0.0.0 -ss {} -to {} '
                                        '"{}" -map_channel 0.0.1 -ss {} -to {} "{}"').format(
                                self.__audio_path, start_time, end_time, self.__part_audio_path[0],
                                start_time, end_time, self.__part_audio_path[1])
                    except IndexError: not_saved_files()
                    except Exception: not_saved_files()
                    else:
                        # VAD
                        call_video = subprocess.call(ff_video, shell = True)
                        call_audio = subprocess.call(ff_audio, shell = True)

                        try:
                            if call_video == 1 or call_audio == 1: raise OSError
                        except OSError: not_saved_files()
                        except Exception: not_saved_files()
            # VAD нашел речь
            if len_speech_timestamps > 0:
                # Индикатор выполнения VAD
                self.__progressbar_vad(
                    self._audio_track_analysis.format(
                        self._audio_track_sr if self.__sr is True else ''
                    ), self.__len_paths, self.__local_path(self.__curr_path), True, len_speech_timestamps,
                    self.__len_paths, len_speech_timestamps, out
                )
            else:
                self.__unprocessed_files.append(self.__curr_path)

    # ------------------------------------------------------------------------------------------------------------------
    # Внешние методы
    # ------------------------------------------------------------------------------------------------------------------

    # Извлечение аудиодорожки из видеофайла
    def extract_audio_from_video(self, logs: bool = True, runtime: bool = True, out: bool = True, run: bool = True):
        """
        Извлечение аудиодорожки из видеофайла

        Аргументы:
            logs - При необходимости формировать LOG файл
            runtime - Подсчет времени выполнения
            out - Отображение
            run - Блокировка выполнения
        """

        self._clear_notebook_history_output()  # Очистка истории вывода сообщений в ячейке Jupyter

        # Сброс
        self._df_unprocessed_afv = pd.DataFrame()  # Пустой DataFrame

        try:
            # Проверка аргументов
            if type(logs) is not bool or type(runtime) is not bool or type(out) is not bool or type(run) is not bool:
                raise TypeError
        except TypeError: self._inv_args(__class__.__name__, self.extract_audio_from_video.__name__, out = out)
        else:
            # Блокировка выполнения
            if run is False: self._error(self._lock_user, out = out); return None

            if runtime: self._r_start()

            try:
                # Директория с оригинальными видео
                original = os.path.join(self.path_to_original_videos, self._re_inv_chars(self.sub_folder[0]))
            except (TypeError, IndexError): self._other_error(self._som_ww, out = out); return None
            except Exception: self._other_error(self._unknown_err, out = out); return None
            else:
                try:
                    original = self._create_folder(original)  # Создание директории с оригинальными видео
                    if not original: raise IsADirectoryError  # Директория не создана
                except IsADirectoryError:
                    self._other_error(self._folder_not_found.format(self._info_wrapper(original)), out = out)
                    return None
                except Exception: self._other_error(self._unknown_err, out = out); return None
                else:
                    paths = []  # Пути до видеофайлов

                    # Формирование списка с видеофайлами
                    for p in Path(original).rglob('*'):
                        try:
                            if type(self.ext_video) is not list or len(self.ext_video) < 1: raise TypeError

                            self.ext_video = [x.lower() for x in self.ext_video]
                        except TypeError: self._other_error(self._som_ww, out = out); return None
                        except Exception: self._other_error(self._unknown_err, out = out); return None
                        else:
                            # Добавление текущего пути к видеофайлу в список
                            if p.suffix.lower() in self.ext_video: paths.append(p.resolve())

                    # Директория с оригинальными видео не содержит видеофайлов с необходимым расширением
                    try:
                        self.__len_paths = len(paths) # Количество видеофайлов

                        if self.__len_paths == 0: raise TypeError
                    except TypeError: self._other_error(self._files_not_found, out = out)
                    except Exception: self._other_error(self._unknown_err, out = out)
                    else:
                        unprocessed_files = []  # Список видеофайлов из которых аудиодорожка не извлечена

                        # Локальный путь
                        self.__local_path = lambda path:\
                            os.path.join(*Path(path).parts[-abs((len(Path(path).parts) - len(Path(original).parts))):])

                        last = False  # Замена последнего сообщения

                        # Проход по всем найденным видеофайлам
                        for i, curr_path in enumerate(paths):
                            if i != 0: last = True

                            # Индикатор выполнения
                            self.__progressbar_audio(
                                self._extract_audio_from_video, i, self.__local_path(curr_path), last, self.__len_paths,
                                out)

                            try:
                                if not self.ext_audio: raise ValueError

                                # Путь до аудиофайла
                                audio_path = os.path.join(Path(curr_path).parent, Path(curr_path).stem + self.ext_audio)
                            except (TypeError, ValueError): unprocessed_files.append(curr_path); continue
                            except Exception: unprocessed_files.append(curr_path); continue
                            else:
                                # Удаление аудиофайла
                                if os.path.isfile(audio_path) is True: os.remove(audio_path)

                                try:
                                    ff = 'ffmpeg -loglevel quiet -i "{}" -vn -codec:v copy -ac {} "{}"'.format(
                                        curr_path, MediaInfo.parse(curr_path).to_data()['tracks'][2]['channel_s'],
                                        audio_path)
                                except IndexError: unprocessed_files.append(curr_path); continue
                                except Exception: unprocessed_files.append(curr_path); continue
                                else:
                                    call = subprocess.call(ff, shell = True)  # Конвертация видео в аудио

                                    try:
                                        if call == 1: raise OSError
                                    except OSError: unprocessed_files.append(curr_path); continue
                                    except Exception: unprocessed_files.append(curr_path); continue

                        # Индикатор выполнения
                        self.__progressbar_audio(self._extract_audio_from_video, self.__len_paths,
                                                 self.__local_path(paths[-1]), True, self.__len_paths, out)

                        # Список видеофайлов из которых аудиодорожка не извлечена
                        if len(unprocessed_files) > 0: self.__save_log_extract_audio_from_video(
                            unprocessed_files, out, logs)
                        else: self._info_true(self._extract_audio_from_video_true, out = out)
            finally:
                if runtime: self._r_end(out = out)

    # VAD (Voice Activity Detector)
    def vad(self, force_reload: bool = True, type_encode: str or None = None, crf_value: int = 23,
            presets_crf_encode: str or None = None, trig_sum: float = 0.25, neg_trig_sum: float = 0.07,
            num_steps: int = 8, batch_size: int = 200, num_samples_per_window: int = 4000,
            min_speech_samples: int = 10000, min_silence_samples: int = 500, sr: bool = True,
            new_name_sr: str or None = None, sr_input_type: str = 'audio', logs: bool = True,
            create_folder_filter_sr: bool = False, clear_dir: bool = False,
            runtime: bool = True, out: bool = True, run: bool = True):
        """
        VAD (Voice Activity Detector)

        Аргументы:
            force_reload - Принудительная загрузка модели из сети
            type_encode - Тип кодирования
            crf_value - Качество кодирования
            presets_crf_encode - Параметр обеспечивающий определенную скорость кодирования и сжатия
            trig_sum - Средняя вероятность переключения между перекрывающими окнами (речь)
            neg_trig_sum - Средняя вероятность переключения между перекрывающими окнами (речи нет)
            num_steps - Количество перекрывающихся окон для разделения звукового фрагмента
            batch_size - Размер выборки
            num_samples_per_window - Количество выборок в каждом окне
            min_speech_samples - Минимальная длительность речевого фрагмента в сэмплах
            min_silence_samples - Минимальная длительность тишины в выборках между отдельными речевыми фрагментами
            sr - Распознавать речь
            new_name_sr - Имя директории для разархивирования модели распознавания речи
            sr_input_type - Тип файла для распознавания речи
            logs - При необходимости формировать LOG файл
            create_folder_filter_sr - Создание директорий под фильтр распознавания речи
            clear_dir - Очистка директории с разделенными видеофрагментами
            runtime - Подсчет времени выполнения
            out - Отображение
            run - Блокировка выполнения
        """

        self._clear_notebook_history_output()  # Очистка истории вывода сообщений в ячейке Jupyter

        # Сброс
        self._df_unprocessed_vad = pd.DataFrame()  # Пустой DataFrame
        self._df_not_saved_files_sr = pd.DataFrame()  # Пустой DataFrame

        try:
            if type_encode is None: type_encode = self._types_encode[1]
            if presets_crf_encode is None: presets_crf_encode = self._presets_crf_encode[5]

            # Проверка аргументов
            if (type(force_reload) is not bool or type(crf_value) is not int or crf_value < 0 or crf_value > 51
                    or type(trig_sum) is not float or trig_sum < 0
                    or type(neg_trig_sum) is not float or neg_trig_sum < 0 or type(num_steps) is not int
                    or num_steps < 0 or type(batch_size) is not int or batch_size < 0
                    or type(num_samples_per_window) is not int or num_samples_per_window < 0
                    or type(min_speech_samples) is not int or min_speech_samples < 0
                    or type(min_silence_samples) is not int or min_silence_samples < 0 or type(sr) is not bool
                    or ((type(new_name_sr) is not str or not new_name_sr) and new_name_sr is not None)
                    or type(logs) is not bool or type(create_folder_filter_sr) is not bool
                    or type(clear_dir) is not bool or type(runtime) is not bool
                    or type(out) is not bool or type(run) is not bool):
                raise TypeError
        except TypeError: self._inv_args(__class__.__name__, self.vad.__name__, out = out)
        else:
            # Блокировка выполнения
            if run is False: self._error(self._lock_user, out = out); return None

            if runtime: self._r_start()

            try:
                # Проверка настроек ядра
                if type(type_encode) is not str or (type_encode in self._types_encode) is False:
                    raise TypeEncodeVideoError
                if type(presets_crf_encode) is not str or (presets_crf_encode in self._presets_crf_encode) is False:
                    raise PresetCFREncodeVideoError
                if type(sr_input_type) is not str or (sr_input_type in [x.lower() for x in self._dir_va]) is False:
                    raise SRInputTypeError
            except TypeEncodeVideoError: self._other_error(self._wrong_type_encode.format(
                self._info_wrapper(', '.join(x.replace('.', '') for x in self._types_encode))
            ), out = out); return False
            except PresetCFREncodeVideoError: self._other_error(self._wrong_preset_crf_encode.format(
                self._info_wrapper(', '.join(x.replace('.', '') for x in self._presets_crf_encode))
            ), out = out); return False
            except SRInputTypeError: self._other_error(self._wrong_sr_input_type.format(
                self._info_wrapper(', '.join(x.replace('.', '') for x in [x.lower() for x in self._dir_va]))
            ), out = out); return False
            except Exception: self._other_error(self._unknown_err, out = out); return False
            else:
                # Только для внутреннего использования внутри класса
                self.__trig_sum = trig_sum
                self.__neg_trig_sum = neg_trig_sum
                self.__num_steps = num_steps
                self.__batch_size = batch_size
                self.__num_samples_per_window = num_samples_per_window
                self.__min_speech_samples = min_speech_samples
                self.__min_silence_samples = min_silence_samples
                self.__sr = sr
                self.__sr_input_type = sr_input_type
                self.__type_encode = type_encode
                self.__crf_value = crf_value
                self.__presets_crf_encode = presets_crf_encode

                torch.set_num_threads(1)  # Установка количества потоков для внутриоперационного параллелизма на ЦП

                torch.hub.set_dir(self.path_to_save)  # Установка директории куда будет загружена модель VAD

                # Информационное сообщение
                self._info(self._download_model_from_repo.format(
                    self._info_wrapper(self._vad_model),
                    urllib.parse.urljoin('https://github.com/', self._github_repo_vad)
                ), last = False, out = False)
                if out: self.show_notebook_history_output()  # Отображение истории вывода сообщений в ячейке Jupyter

                try:
                    # Подавление вывода
                    with io.capture_output():
                        # Загрузка VAD модели
                        self.__model, utils = torch.hub.load(
                            repo_or_dir = self._github_repo_vad, model = self._vad_model, force_reload = force_reload)
                except FileNotFoundError:
                    self._other_error(self._folder_not_found.format(self._info_wrapper(self.path_to_save)), out = out)
                except RuntimeError: self._other_error(self._url_error.format(''), out = out)
                except urllib.error.HTTPError as e:
                    self._other_error(
                        self._url_error.format(self._url_error_code.format(self._error_wrapper(e.code))), out = out)
                except urllib.error.URLError: self._other_error(self._url_error.format(''), out = out)
                except Exception: self._other_error(self._unknown_err, out = out)
                else:
                    self.__get_speech_ts, _, read_audio, _, _, _ = utils

                    try:
                        # Директория с оригинальными видео
                        original = os.path.join(self.path_to_original_videos, self._re_inv_chars(self.sub_folder[0]))
                        # Директория с разделенными видеофрагментами
                        splitted = os.path.join(self.path_to_original_videos, self._re_inv_chars(self.sub_folder[1]))
                    except (TypeError, IndexError): self._other_error(self._som_ww, out = out); return None
                    except Exception: self._other_error(self._unknown_err, out = out); return None
                    else:
                        original_side = []  # Директории с оригинальными видео
                        splitted_side = []  # Директории с разделенными видеофрагментами

                        # Названия каталогов для обработки видео с разных ракурсов
                        side_folder = [
                            f.name for f in Path(original).iterdir() if f.is_dir() and not f.name.startswith('.')
                        ]

                        # Названия каталогов для обработки видео с разных ракурсов
                        if len(side_folder) > 0:
                            # Проход по всем ракурсам
                            for side in side_folder:
                                if type(side) is str and side:
                                    # Директории с оригинальными видео
                                    original_side.append(os.path.join(original, self._re_inv_chars(side)))
                                    # Директории с разделенными видеофрагментами
                                    splitted_side.append(os.path.join(splitted, self._re_inv_chars(side)))

                        # Каталоги с видео записанных с разных ракурсов не указаны
                        if len(original_side) == 0 and len(splitted_side) == 0:
                            original_side.append(original)  # Директории с оригинальными видео
                            splitted_side.append(splitted)  # Директории с разделенными видеофрагментами

                        try:
                            if len(original_side) != len(splitted_side): raise IndexError
                        except IndexError: self._other_error(self._som_ww, out = out); return None

                        # Очистка директории с разделенными видеофрагментами
                        if clear_dir is True: self._clear_folder(splitted)

                        paths = []  # Пути до видеофайлов

                        self.__splitted_video = []  # Директории с разделенными видеофрагментами
                        self.__splitted_audio = []  # Директории с разделенными аудиофрагментами

                        # Проход по всем индексам каталогов
                        for i in range(len(original_side)):
                            try:
                                # Создание директории с разделенными видеофрагментами
                                splitted = self._create_folder(splitted_side[i])
                                if not splitted: raise IsADirectorySplittedError  # Директория не создана

                                if os.path.isdir(original_side[i]) is False: raise IsADirectoryOriginalError
                            except IsADirectorySplittedError:
                                self._other_error(self._folder_not_found.format(self._info_wrapper(splitted)),
                                                  out = out); return None
                            except IsADirectoryOriginalError:
                                self._other_error(self._folder_not_found.format(self._info_wrapper(original_side[i])),
                                                  out = out); return None
                            except Exception: self._other_error(self._unknown_err, out = out); return None
                            else:
                                # Директория с разделенными видеофрагментами
                                self.__splitted_video.append(os.path.join(splitted, self._dir_va[0]))
                                if not os.path.exists(self.__splitted_video[-1]): os.makedirs(self.__splitted_video[-1])
                                # Директория с разделенными аудиофрагментами
                                self.__splitted_audio.append(os.path.join(splitted, self._dir_va[1]))
                                if not os.path.exists(self.__splitted_audio[-1]): os.makedirs(self.__splitted_audio[-1])

                                # Формирование списка с видеофайлами
                                for p in Path(original_side[i]).rglob('*'):
                                    try:
                                        if type(self.ext_video) is not list or len(self.ext_video) < 1: raise TypeError

                                        self.ext_video = [x.lower() for x in self.ext_video]
                                    except TypeError: self._other_error(self._som_ww, out = out); return None
                                    except Exception: self._other_error(self._unknown_err, out = out); return None
                                    else:
                                        # Добавление текущего пути к видеофайлу в список
                                        if p.suffix.lower() in self.ext_video: paths.append(p.resolve())
                        # Директория с оригинальными видео не содержит видеофайлов с необходимым расширением
                        try:
                            self.__len_paths = len(paths) # Количество видеофайлов

                            if self.__len_paths == 0: raise TypeError
                        except TypeError: self._other_error(self._files_not_found, out = out)
                        except Exception: self._other_error(self._unknown_err, out = out)
                        else:
                            # Распознавание речи
                            if self.__sr is True:
                                # Загрузка и активация модели Vosk для распознавания речи
                                if self._vosk(new_name = new_name_sr, force_reload = force_reload, runtime = False,
                                              out = out, run = True) is False: return None

                                # Создание директорий под фильтр распознавания речи
                                if create_folder_filter_sr is True:
                                    show_info = False  # Информационное сообщение не показано

                                    # Проход по всему фильтру
                                    for item in self.filter_sr:
                                        # Текущее значение не пустая строка
                                        if type(item) is str and item:
                                            try: item = item.lower().replace(' ', '_').capitalize().strip()
                                            except Exception: continue
                                        # Текущее значение - список не вложенный
                                        if type(item) is list and self._nest_level(item) < 2:
                                            try: item = item[0].lower().replace(' ', '_').capitalize().strip()
                                            except Exception: continue

                                        # Информационное сообщение не показано
                                        if show_info is False:
                                            clear_output(True)
                                            # Информационное сообщение
                                            self._info(self._create_folder_filter_sr, last = False, out = False)
                                            # Отображение истории вывода сообщений в ячейке Jupyter
                                            if out: self.show_notebook_history_output()

                                            show_info = True  # Информационное сообщение показано

                                        # Директории для сортировки распознанной речи
                                        for splitted in list(set().union(
                                                self.__splitted_video, self.__splitted_audio)):
                                            dir_curr_sr_video = os.path.join(splitted, item)

                                            try:
                                                # Создание директории
                                                if not os.path.exists(dir_curr_sr_video):
                                                    os.makedirs(dir_curr_sr_video)
                                            except Exception:
                                                self._other_error(self._unknown_err, out = out); return None

                            self.__unprocessed_files = []  # Видеофайлы на которых VAD не отработал
                            self.__not_saved_files = []  # Видеофайлы которые не сохранились при обработке VAD

                            # Локальный путь
                            self.__local_path = lambda path: os.path.join(
                                *Path(path).parts[-abs((len(Path(path).parts) - len(Path(original).parts))):])

                            last = False  # Замена последнего сообщения

                            # Проход по всем найденным видеофайлам
                            for i, curr_path in enumerate(paths):
                                self.__curr_path = curr_path  # Текущий видеофайл, который обрабатывается VAD + SR
                                self.__i = i  # Счетчик

                                if self.__i != 0: last = True

                                # Индикатор выполнения
                                self.__progressbar_audio(
                                    self._audio_track_analysis.format(self._audio_track_sr if sr is True else ''),
                                    self.__i, self.__local_path(self.__curr_path), last, self.__len_paths,
                                    out = out)

                                try:
                                    if not self.ext_audio: raise ValueError
                                    # Путь до аудиофайла
                                    self.__audio_path = os.path.join(
                                        Path(self.__curr_path).parent, Path(self.__curr_path).stem + self.ext_audio)
                                except (TypeError, ValueError):
                                    self.__unprocessed_files.append(self.__curr_path); continue
                                except Exception: self.__unprocessed_files.append(self.__curr_path); continue
                                else:
                                    # Аудиофайл не найден
                                    if os.path.isfile(self.__audio_path) is False:
                                        self.__unprocessed_files.append(self.__curr_path); continue

                                    try:
                                        # Чтение аудиофайла
                                        self.__wav = read_audio(self.__audio_path, target_sr = self._freq_sr)
                                    except RuntimeError: self.__unprocessed_files.append(self.__curr_path); continue
                                    except Exception: self.__unprocessed_files.append(self.__curr_path); continue
                                    else:
                                        # Анализ аудиодорожки и процесс распознавания речи
                                        self.__audio_analysis(out = out)
                            # Индикатор выполнения извлечения аудиодорожки из видеофайла
                            self.__progressbar_audio(
                                self._audio_track_analysis.format(self._audio_track_sr if sr is True else ''),
                                self.__len_paths, self.__local_path(paths[-1]), True, self.__len_paths, out = out)

                            # Уникальные значения
                            unprocessed_files_unique = set()
                            for x in self.__unprocessed_files: unprocessed_files_unique.add(x)
                            unprocessed_files_unique = list(unprocessed_files_unique)

                            if len(unprocessed_files_unique) == 0 and len(self.__not_saved_files) == 0:
                                self._info_true(self._vad_true, out = out); return None

                            # Список видеофайлов на которых VAD не отработал
                            if len(unprocessed_files_unique) > 0:
                                self.__save_log_vad(unprocessed_files_unique, out, logs)
                            # Список видеофайлов которые не сохранились
                            if len(self.__not_saved_files) > 0:
                                self.__save_log_save_sr(self.__not_saved_files, out, logs)
            finally:
                if runtime: self._r_end(out = out)