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
import shutil        # Набор функций высокого уровня для обработки файлов, групп файлов, и папок

from pathlib import Path  # Работа с путями в файловой системе

from pymediainfo import MediaInfo  # Получение meta данных из медиафайлов
from datetime import timedelta

import pkg_resources  # Работа с ресурсами внутри пакетов

from IPython.display import clear_output, display
from IPython.utils import io  # Подавление вывода

# Персональные
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

        self._files_not_found: str = self._('В указанной директории необходимые файлы не найдены ...')
        self._extract_audio_from_video: str = self._('Извлечение аудиодорожек из видеофайлов ...')
        self._from_precent = self._('из')
        self._curr_progress: str = '{} ' + self._from_precent + ' {} ({}%) ... {} ...'
        self._curr_progress_vad: str = ('{} ' + self._from_precent + ' {} ({}%) ... {} ({} '
                                        + self._from_precent + ' {} - {}%) ...')
        self._folder_not_found: str = self._('Директория "{}" не найдена ...')
        self._extract_audio_from_video_err: str = self._('Всего видеофайлов из которых аудиодорожка не была '
                                                        'извлечена - {}{}{} ...')
        self._extract_audio_from_video_true: str = self._('Все аудиодорожки были успешно извлечены ... это хороший '
                                                          'знак ...')

        self._download_model_from_repo: str = self._('Загрузка модели "{}{}{}" из репозитория {} ...')

        self._url_error_code: str = self._(' (ошибка {}{}{})')
        self._url_error: str = self._('Ой! Что-то пошло не так ... не удалось скачать модель{} ...')

        self._audio_track_analysis: str = self._('Анализ аудиодорожек ...')
        self._vad_err: str = self._('Всего видеофайлов на которых VAD не отработал - {}{}{} ...')
        self._vad_true: str = self._('Все аудиодорожки были проанализированы ... это хороший знак ...')


# ######################################################################################################################
# Статистика
# ######################################################################################################################
class Audio(Messages):
    """Статистика"""

    # ------------------------------------------------------------------------------------------------------------------
    # Конструктор
    # ------------------------------------------------------------------------------------------------------------------

    def __post_init__(self):
        super().__post_init__()  # Выполнение конструктора из суперкласса

        # DataFrame c видеофайлами из которых аудиодорожка не извлечена
        self._df_unprocessed_audio_from_video: pd.DataFrame = pd.DataFrame()
        # DataFrame c видеофайлами из которых VAD не отработал
        self._df_unprocessed_vad: pd.DataFrame = pd.DataFrame()

        self._github_repo_vad: str = 'snakers4/silero-vad'  # Репозиторий для загрузки VAD
        self._vad_model: str = 'silero_vad'  # VAD модель

        self._types_encode = ('qscale', 'crf')  # Типы кодирования
        # Параметр обеспечивающий определенную скорость кодирования и сжатия
        self._presets_crf_encode = (
            'ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow'
        )

    # ------------------------------------------------------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------------------------------------------------------

    # DataFrame c видеофайлами из которых аудиодорожка не извлечена
    @property
    def df_unprocessed_audio_from_video(self): return self._df_unprocessed_audio_from_video

    # ------------------------------------------------------------------------------------------------------------------
    # Внешние методы
    # ------------------------------------------------------------------------------------------------------------------

    # Извлечение аудиодорожки из видеофайла
    def extract_audio_from_video(self, num_to_display: int = 10, logs: bool = True, runtime: bool = True):
        """
        Извлечение аудиодорожки из видеофайла

        Аргументы:
            num_to_display - Количество видеофайлов для отображения, из которых аудиодорожка не извлечена
            logs - При необходимости формировать LOG файл
            runtime - Подсчет времени выполнения
        """

        # Сброс
        self._df_unprocessed_audio_from_video = pd.DataFrame()  # Пустой DataFrame

        try:
            # Проверка аргументов
            if (type(num_to_display) is not int or num_to_display > 50 or 0 >= num_to_display
                    or type(logs) is not bool or type(runtime) is not bool): raise TypeError
        except TypeError: self._inv_args(__class__.__name__, self.extract_audio_from_video.__name__)
        else:
            if runtime: self._r_start()

            try:
                # Директория с оригинальными видео
                original = os.path.join(self.path_to_original_videos, self.sub_folder[0])

                try:
                    if not os.path.exists(original): os.makedirs(original)
                except (FileNotFoundError, TypeError): raise TypeError
                except Exception: raise TypeError
                else:
                    if os.path.isdir(original) is False: raise IsADirectoryError
            except IsADirectoryError: self._other_error(self._folder_not_found.format(original))
            except (TypeError, IndexError): self._other_error(self._som_ww)
            except Exception: self._other_error(self._unknown_err)
            else:
                paths = []  # Пути к видеофайлам

                # Формирование списка с видеофайлами
                for p in Path(original).rglob('*'):
                    try:
                        if type(self.ext_video) is not list or len(self.ext_video) < 1: raise TypeError

                        self.ext_video = [x.lower() for x in self.ext_video]
                    except TypeError: self._other_error(self._som_ww); return None
                    except Exception: self._other_error(self._unknown_err); return None
                    else:
                        if p.suffix.lower() in self.ext_video:
                            # Добавление текущего пути к видеофайлу в список
                            paths.append(p.resolve())

                # Директория с оригинальными видео не содержит видеофайлов с необходимым расширением
                try:
                    len_paths = len(paths) # Количество видеофайлов

                    if len_paths == 0: raise TypeError
                except TypeError: self._other_error(self._files_not_found)
                except Exception: self._other_error(self._unknown_err)
                else:
                    unprocessed_files = []  # Список видеофайлов из которых аудиодорожка не извлечена

                    # Индикатор выполнения
                    progressbar = lambda item, info: self._progressbar(
                        self._extract_audio_from_video,
                        self._curr_progress.format(item, len_paths, round(item * 100 / len_paths, 2), info)
                    )

                    # Локальный путь
                    local_path = lambda path:\
                        os.path.join(*Path(path).parts[-abs((len(Path(path).parts) - len(Path(original).parts))):])

                    # Проход по всем найденным видеофайлам
                    for i, curr_path in enumerate(paths):
                        if i != 0: clear_output(wait = True)

                        progressbar(i, local_path(curr_path))  # Индикатор выполнения

                        try:
                            if not self.ext_audio: raise ValueError

                            # Путь до аудиофайла
                            audio_path = os.path.join(Path(curr_path).parent, Path(curr_path).stem + self.ext_audio)
                        except (TypeError, ValueError):
                            self._other_error(self._som_ww); unprocessed_files.append(curr_path); continue
                        except Exception:
                            self._other_error(self._unknown_err); unprocessed_files.append(curr_path); continue
                        else:
                            # Удаление аудиофайла
                            if os.path.isfile(audio_path) is True: os.remove(audio_path)

                            try:
                                ff = 'ffmpeg -i "{}" -vn -codec:v copy -ac {} "{}"'.format(
                                    curr_path, MediaInfo.parse(curr_path).to_data()['tracks'][2]['channel_s'],
                                    audio_path
                                )
                            except IndexError:
                                self._other_error(self._som_ww); unprocessed_files.append(curr_path); continue
                            except Exception:
                                self._other_error(self._unknown_err); unprocessed_files.append(curr_path); continue
                            else:
                                call = subprocess.call(ff, shell = True)  # Конвертация видео в аудио

                                try:
                                    if call == 1: raise OSError
                                except OSError:
                                    self._other_error(self._som_ww); unprocessed_files.append(curr_path); continue
                                except Exception:
                                    self._other_error(self._unknown_err); unprocessed_files.append(curr_path); continue

                    clear_output(wait = True)
                    progressbar(len_paths, local_path(paths[-1]))  # Индикатор выполнения

                    # Список видеофайлов из которых аудиодорожка не извлечена
                    if len(unprocessed_files) > 0:
                        self._error(self._extract_audio_from_video_err.format(
                            f'<span style=\"color:{self.color_err}\">', len(unprocessed_files), f'</span>'
                        ))

                        # Формирование DataFrame
                        dict_unprocessed_files = {
                            'Files': unprocessed_files
                        }

                        self._df_unprocessed_audio_from_video = pd.DataFrame(data = dict_unprocessed_files)
                        self._df_unprocessed_audio_from_video.index += 1
                        self._df_unprocessed_audio_from_video.index.name = self._keys_id

                        # Отображение
                        if self.is_notebook is True:
                            display(self._df_unprocessed_audio_from_video.iloc[0:num_to_display, :])

                        if logs is True:
                            # Сохранение LOG
                            res_save_logs = self._save_logs(
                                self.df_unprocessed_audio_from_video, self.extract_audio_from_video.__name__
                            )

                            if res_save_logs is True: self._info_true(self._logs_save_true)
                    else:
                        self._info_true(self._extract_audio_from_video_true)
            finally:
                if runtime: self._r_end()

    # VAD (Voice Activity Detector)
    def vad(self, path_to_model: str = pkg_resources.resource_filename('neweraai', 'models'),
            force_reload: bool = True, type_encode: str or None = None, crf_value: int = 23,
            presets_crf_encode: str or None = None, freq: int = 16000, trig_sum: float = 0.25,
            neg_trig_sum: float = 0.07, num_steps: int = 8, batch_size: int = 200, num_samples_per_window: int = 4000,
            min_speech_samples: int = 10000, min_silence_samples: int = 500,
            num_to_display: int = 10, logs: bool = True, runtime: bool = True):
        """
        VAD (Voice Activity Detector)

        Аргументы:
            path_to_load_model - Директория для загрузки модели
            force_reload - Принудительная загрузка модели из сети
            type_encode - Тип кодирования
            crf_value - Качество кодирования
            presets_crf_encode - Параметр обеспечивающий определенную скорость кодирования и сжатия
            freq - Частота дискретизации
            trig_sum - Средняя вероятность переключения между перекрывающими окнами (речь)
            neg_trig_sum - Средняя вероятность переключения между перекрывающими окнами (речи нет)
            num_steps - Количество перекрывающихся окон для разделения звукового фрагмента
            batch_size - Размер выборки
            num_samples_per_window - Количество выборок в каждом окне
            min_speech_samples - Минимальная длительность речевого фрагмента в сэмплах
            min_silence_samples - Минимальная длительность тишины в выборках между отдельными речевыми фрагментами
            num_to_display - Количество видеофайлов для отображения, на которых VAD не отработал
            logs - При необходимости формировать LOG файл
            runtime - Подсчет времени выполнения
        """

        # Сброс
        self._df_unprocessed_vad = pd.DataFrame()  # Пустой DataFrame

        try:
            if type_encode is None: type_encode = self._types_encode[1]
            if presets_crf_encode is None: presets_crf_encode = self._presets_crf_encode[5]

            # Проверка аргументов
            if (type(path_to_model) is not str or type(force_reload) is not bool or type(type_encode) is not str
                    or (type_encode in self._types_encode) is False or type(presets_crf_encode) is not str
                    or (presets_crf_encode in self._presets_crf_encode) is False or type(crf_value) is not int
                    or crf_value < 0 or crf_value > 51 or type(freq) is not int or freq <= 0
                    or type(num_to_display) is not int or num_to_display > 50 or 0 >= num_to_display
                    or type(trig_sum) is not float or trig_sum < 0 or type(neg_trig_sum) is not float
                    or neg_trig_sum < 0 or type(num_steps) is not int or num_steps < 0
                    or type(batch_size) is not int or batch_size < 0 or type(num_samples_per_window) is not int
                    or num_samples_per_window < 0 or type(min_speech_samples) is not int or min_speech_samples < 0
                    or type(min_silence_samples) is not int or min_silence_samples < 0
                    or type(logs) is not bool or type(runtime) is not bool):
                raise TypeError
        except TypeError: self._inv_args(__class__.__name__, self.vad.__name__)
        else:
            if runtime: self._r_start()

            torch.set_num_threads(1)  # Установка количества потоков для внутриоперационного параллелизма на ЦП

            torch.hub.set_dir(path_to_model)  # Установка директории куда будет загружена модель VAD

            # Информационное сообщение
            self._info(self._download_model_from_repo.format(
                f'<span style=\"color:{self.color_info}\">', self._vad_model, f'</span>',
                urllib.parse.urljoin('https://github.com/', self._github_repo_vad)
            ))

            try:
                # Подавление вывода
                with io.capture_output():
                    # Загрузка VAD модели
                    model, utils = torch.hub.load(
                        repo_or_dir = self._github_repo_vad, model = self._vad_model, force_reload = force_reload
                    )
            except FileNotFoundError: self._other_error(self._folder_not_found.format(path_to_model))
            except RuntimeError: self._other_error(self._url_error.format(''))
            except urllib.error.HTTPError as e:
                self._other_error(self._url_error.format(self._url_error_code.format(
                    f'<span style=\"color:{self.color_err}\">', e.code, f'</span>'
                )))
            except urllib.error.URLError: self._other_error(self._url_error.format(''))
            except Exception: self._other_error(self._unknown_err)
            else:
                get_speech_ts, _, read_audio, _, _, _ = utils

                try:
                    # Директория с оригинальными видео
                    original = os.path.join(self.path_to_original_videos, self.sub_folder[0])
                    # Директория с разделенными видеофрагментами
                    splitted = os.path.join(self.path_to_original_videos, self.sub_folder[1])

                    try:
                        if not os.path.exists(splitted): os.makedirs(splitted)
                        else:
                            # Очистка директории
                            for filename in os.listdir(splitted):
                                filepath = os.path.join(splitted, filename)
                                try:
                                    shutil.rmtree(filepath)
                                except OSError: os.remove(filepath)
                                except Exception: raise Exception
                    except (FileNotFoundError, TypeError): raise TypeError
                    except Exception: raise TypeError
                    else:
                        if os.path.isdir(original) is False: raise IsADirectoryError

                except IsADirectoryError: self._other_error(self._folder_not_found.format(original))
                except (TypeError, IndexError): self._other_error(self._som_ww)
                except Exception: self._other_error(self._unknown_err)
                else:
                    paths = []  # Пути к видеофайлам

                    # Формирование списка с видеофайлами
                    for p in Path(original).rglob('*'):
                        try:
                            if type(self.ext_video) is not list or len(self.ext_video) < 1: raise TypeError

                            self.ext_video = [x.lower() for x in self.ext_video]
                        except TypeError: self._other_error(self._som_ww); return None
                        except Exception: self._other_error(self._unknown_err); return None
                        else:
                            if p.suffix.lower() in self.ext_video:
                                # Добавление текущего пути к видеофайлу в список
                                paths.append(p.resolve())

                    # Директория с оригинальными видео не содержит видеофайлов с необходимым расширением
                    try:
                        len_paths = len(paths) # Количество видеофайлов

                        if len_paths == 0: raise TypeError
                    except TypeError: self._other_error(self._files_not_found)
                    except Exception: self._other_error(self._unknown_err)
                    else:
                        unprocessed_files = []  # Список видеофайлов на которых VAD не отработал

                        # Индикатор выполнения
                        progressbar = lambda item, info: self._progressbar(
                            self._audio_track_analysis,
                            self._curr_progress.format(
                                item, len_paths, round(item * 100 / len_paths, 2), info
                            )
                        )

                        progressbar_vad = lambda item, info, item2, len_timestamp: self._progressbar(
                            self._audio_track_analysis,
                            self._curr_progress_vad.format(
                                item, len_paths, round(item * 100 / len_paths, 2), info,
                                item2, len_timestamp, round(item2 * 100 / len_timestamp, 2)
                            )
                        )

                        # Локальный путь
                        local_path = lambda path: \
                            os.path.join(*Path(path).parts[-abs((len(Path(path).parts) - len(Path(original).parts))):])

                        # Проход по всем найденным видеофайлам
                        for i, curr_path in enumerate(paths):
                            if i != 0:
                                clear_output(wait = True)
                                self._info('')  # Информационное сообщение

                            progressbar(i, local_path(curr_path))  # Индикатор выполнения

                            try:
                                if not self.ext_audio: raise ValueError

                                # Путь до аудиофайла
                                audio_path = os.path.join(Path(curr_path).parent, Path(curr_path).stem + self.ext_audio)
                            except (TypeError, ValueError):
                                self._other_error(self._som_ww); unprocessed_files.append(curr_path); continue
                            except Exception:
                                self._other_error(self._unknown_err); unprocessed_files.append(curr_path); continue
                            else:
                                # Аудиофайл найден
                                if os.path.isfile(audio_path) is True:
                                    try:
                                        wav = read_audio(audio_path, target_sr = freq)  # Чтение аудиофайла
                                    except RuntimeError:
                                        self._other_error(self._som_ww); unprocessed_files.append(curr_path); continue
                                    except Exception:
                                        self._other_error(self._unknown_err); unprocessed_files.append(curr_path)
                                        continue
                                    else:
                                        try:
                                            # Получение временных меток
                                            speech_timestamps = get_speech_ts(
                                                wav, model,
                                                trig_sum = trig_sum,
                                                neg_trig_sum = neg_trig_sum,
                                                num_steps = num_steps,
                                                batch_size = batch_size,
                                                num_samples_per_window = num_samples_per_window,
                                                min_speech_samples = min_speech_samples,
                                                min_silence_samples = min_silence_samples,
                                                visualize_probs = False
                                            )
                                        except Exception:
                                            self._other_error(self._unknown_err); unprocessed_files.append(curr_path)
                                            continue
                                        else:
                                            len_speech_timestamps = len(speech_timestamps)

                                            # Проход по всем найденным меткам
                                            for cnt, curr_timestamps in enumerate(speech_timestamps):
                                                clear_output(wait = True)
                                                self._info('')  # Информационное сообщение

                                                # Индикатор выполнения
                                                progressbar_vad(i, local_path(curr_path), cnt, len_speech_timestamps)

                                                # Начальное время
                                                start_time = timedelta(seconds = curr_timestamps['start'] / freq)
                                                # Конечное время
                                                end_time = timedelta(seconds = curr_timestamps['end'] / freq)

                                                # Разница между начальным и конечным временем
                                                diff_time = end_time - start_time

                                                part_audio_path = os.path.join(
                                                    splitted,
                                                    Path(curr_path).stem + '_' + str(cnt)
                                                        + Path(curr_path).suffix.lower()
                                                )

                                                # Удаление аудиофайла
                                                if os.path.isfile(part_audio_path) is True:
                                                    os.remove(part_audio_path)

                                                try:
                                                    # Работает с пустыми кадрами в конце видео
                                                    # ff = 'ffmpeg -ss {} -i "{}" -to {} -c copy "{}"'.format(
                                                    #     start_time, curr_path, diff_time, part_audio_path
                                                    # )

                                                    # Варианты кодирования
                                                    if type_encode == self._types_encode[0]:
                                                        # https://trac.ffmpeg.org/wiki/Encode/MPEG-4
                                                        ff = 'ffmpeg -ss {} -i "{}" -{} 0 -to {} "{}"'.format(
                                                            start_time, curr_path, type_encode, diff_time,
                                                            part_audio_path
                                                        )
                                                    elif type_encode == self._types_encode[1]:
                                                        # https://trac.ffmpeg.org/wiki/Encode/H.264
                                                        ff = ('ffmpeg -ss {} -i "{}" -{} {} '
                                                              '-preset {} -to {} "{}"').format(
                                                            start_time, curr_path, type_encode, crf_value,
                                                            presets_crf_encode, diff_time, part_audio_path
                                                        )
                                                except IndexError:
                                                    self._other_error(self._som_ww)
                                                    unprocessed_files.append(curr_path); continue
                                                except Exception:
                                                    self._other_error(self._unknown_err)
                                                    unprocessed_files.append(curr_path); continue
                                                else:
                                                    call = subprocess.call(ff, shell = True)  # VAD

                                                    try:
                                                        if call == 1: raise OSError
                                                    except OSError:
                                                        self._other_error(self._som_ww)
                                                        unprocessed_files.append(curr_path); continue
                                                    except Exception:
                                                        self._other_error(self._unknown_err)
                                                        unprocessed_files.append(curr_path); continue

                                            # VAD нашел речь
                                            if len_speech_timestamps > 0:
                                                clear_output(wait = True)
                                                self._info('')  # Информационное сообщение
                                                # Индикатор выполнения
                                                progressbar_vad(
                                                    len_paths, local_path(paths[-1]),
                                                    len_speech_timestamps, len_speech_timestamps
                                                )
                                            else:
                                                unprocessed_files.append(curr_path)
                                else:
                                    unprocessed_files.append(curr_path)
                        clear_output(wait = True)
                        self._info('')  # Информационное сообщение
                        progressbar(len_paths, local_path(paths[-1]))  # Индикатор выполнения

                        # Уникальные значения
                        unprocessed_files_unique = set()
                        for x in unprocessed_files: unprocessed_files_unique.add(x)
                        unprocessed_files_unique = list(unprocessed_files_unique)

                        # Список видеофайлов на которых VAD не отработал
                        if len(unprocessed_files_unique) > 0:
                            self._error(self._vad_err.format(
                                f'<span style=\"color:{self.color_err}\">', len(unprocessed_files_unique), f'</span>'
                            ))

                            # Формирование DataFrame
                            dict_unprocessed_files = {
                                'Files': unprocessed_files_unique
                            }

                            self._df_unprocessed_vad = pd.DataFrame(data = dict_unprocessed_files)
                            self._df_unprocessed_vad.index += 1
                            self._df_unprocessed_vad.index.name = self._keys_id

                            # Отображение
                            if self.is_notebook is True:
                                display(self._df_unprocessed_vad.iloc[0:num_to_display, :])

                            if logs is True:
                                # Сохранение LOG
                                res_save_logs = self._save_logs(
                                    self._df_unprocessed_vad, self.vad.__name__
                                )

                                if res_save_logs is True: self._info_true(self._logs_save_true)
                        else:
                            self._info_true(self._vad_true)
            finally:
                if runtime: self._r_end()