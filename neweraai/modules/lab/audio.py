#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Аудио
"""

# ######################################################################################################################
# Импорт необходимых инструментов
# ######################################################################################################################
from dataclasses import dataclass  # Класс данных

import os            # Взаимодействие с файловой системой
import subprocess    # Работа с процессами
import torch         # Машинное обучение от Facebook
import urllib.parse  # Парсинг URL
import urllib.error  # Обработка ошибок URL

from pathlib import Path  # Работа с путями в файловой системе

from pymediainfo import MediaInfo  # Получение meta данных из медиафайлов
from datetime import timedelta

import pkg_resources  # Работа с ресурсами внутри пакетов

from IPython.display import clear_output
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
        self._curr_progress: str = '{} ' + self._('из') + ' {} ({}%) ...'
        self._folder_not_found: str = self._('Директория "{}" не найдена ...')

        self._download_model_from_repo: str = self._('Загрузка модели "{}{}{}" из репозитория {} ...')

        self._url_error_code: str = self._(' (ошибка {}{}{})')
        self._url_error: str = self._('Ой! Что-то пошло не так ... не удалось скачать модель{} ...')

        self._audio_track_analysis: str = self._('Анализ аудиодорожек ...')


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

        self._github_repo_vad: str = 'snakers4/silero-vad'  # Репозиторий для загрузки VAD
        self._vad_model: str = 'silero_vad'  # VAD модель

    # ------------------------------------------------------------------------------------------------------------------
    # Внешние методы
    # ------------------------------------------------------------------------------------------------------------------

    # Извлечение аудиодорожки из видеофайла
    def extract_audio_from_video(self, runtime: bool = True):
        """
        Извлечение аудиодорожки из видеофайла

        Аргументы:
            runtime - Подсчет времени выполнения
        """

        try:
            # Проверка аргументов
            if type(runtime) is not bool: raise TypeError
        except TypeError: self._inv_args(__class__.__name__, self.extract_audio_from_video.__name__)
        else:
            if runtime: self._r_start()

            try:
                # Директория с оригинальными видео
                original = os.path.join(self.path_to_original_videos, self.sub_folder[0])

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
                    # Индикатор выполнения
                    progressbar = lambda item: self._progressbar(
                        self._extract_audio_from_video,
                        self._curr_progress.format(item, len_paths, round(item * 100 / len_paths, 2))
                    )

                    progressbar(0)  # Индикатор выполнения

                    # Проход по всем найденным видеофайлам
                    for i, curr_path in enumerate(paths):
                        if i != len_paths: clear_output(wait = True)

                        i += 1  # Текущий индекс

                        try:
                            if self.ext_audio == '': raise ValueError

                            # Путь до аудиофайла
                            audio_path = os.path.join(Path(curr_path).parent, Path(curr_path).stem + self.ext_audio)
                        except (TypeError, ValueError): self._other_error(self._som_ww); return None
                        except Exception: self._other_error(self._unknown_err); return None
                        else:
                            # Удаление аудиофайла
                            if os.path.isfile(audio_path) is True: os.remove(audio_path)

                            try:
                                ff = 'ffmpeg -i "{}" -vn -codec:v copy -ac {} "{}"'.format(
                                    curr_path, MediaInfo.parse(curr_path).to_data()['tracks'][2]['channel_s'],
                                    audio_path
                                )
                            except IndexError: self._other_error(self._som_ww); return None
                            except Exception: self._other_error(self._unknown_err); return None
                            else:
                                call = subprocess.call(ff, shell = True)  # Конвертация видео в аудио

                                try:
                                    if call == 1: raise OSError
                                except OSError: self._other_error(self._som_ww); return None
                                except Exception: self._other_error(self._unknown_err); return None
                                else:
                                    progressbar(i)  # Индикатор выполнения
            finally:
                if runtime: self._r_end()

    # VAD (Voice Activity Detector)
    def vad(self, path_to_model: str = pkg_resources.resource_filename('neweraai', 'models'),
            force_reload: bool = True, runtime: bool = True):
        """
        VAD (Voice Activity Detector)

        Аргументы:
            path_to_load_model - Директория для загрузки модели
            force_reload - Принудительная загрузка модели из сети
            runtime - Подсчет времени выполнения
        """

        try:
            # Проверка аргументов
            if type(path_to_model) is not str or type(force_reload) is not bool or type(runtime) is not bool:
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
            except (urllib.error.HTTPError, urllib.error.URLError) as e:
                self._other_error(self._url_error.format(self._url_error_code.format(
                    f'<span style=\"color:{self.color_err}\">', e.code, f'</span>',
                )))
            except Exception: self._other_error(self._unknown_err)
            else:
                get_speech_ts, _, read_audio, _, _, _ = utils

                try:
                    # Директория с оригинальными видео
                    original = os.path.join(self.path_to_original_videos, self.sub_folder[0])

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
                        # Индикатор выполнения
                        progressbar = lambda item: self._progressbar(
                            self._audio_track_analysis,
                            self._curr_progress.format(item, len_paths, round(item * 100 / len_paths, 2))
                        )

                        progressbar(0)  # Индикатор выполнения

                        # Проход по всем найденным видеофайлам
                        for i, curr_path in enumerate(paths):
                            if i != len_paths: clear_output(wait = True)

                            i += 1  # Текущий индекс

                            try:
                                if self.ext_audio == '': raise ValueError

                                # Путь до аудиофайла
                                audio_path = os.path.join(Path(curr_path).parent, Path(curr_path).stem + self.ext_audio)
                            except (TypeError, ValueError): self._other_error(self._som_ww); return None
                            except Exception: self._other_error(self._unknown_err); return None
                            else:
                                # Аудиофайл найден
                                if os.path.isfile(audio_path) is True:
                                    try:
                                        wav = read_audio(audio_path)  # Чтение аудиофайла
                                    except RuntimeError: self._other_error(self._som_ww); return None
                                    except Exception: self._other_error(self._unknown_err); return None
                                    else:
                                        speech_timestamps = get_speech_ts(wav, model, num_steps = 4)


                                        print(len(wav), MediaInfo.parse(curr_path).to_data()['tracks'][0]['frame_count'],
                                              MediaInfo.parse(curr_path).to_data()['tracks'][2])

                                        print()

                                        for cnt, curr_timestamps in enumerate(speech_timestamps):
                                            print(audio_path, curr_timestamps,
                                                  MediaInfo.parse(curr_path).to_data()['tracks'][0]['frame_rate'],
                                                  MediaInfo.parse(curr_path).to_data()['tracks'][2]['sampling_rate']
                                                  )


                                            fc = int(MediaInfo.parse(curr_path).to_data()['tracks'][0]['frame_count'])
                                            fr = int(float(MediaInfo.parse(curr_path).to_data()['tracks'][0]['frame_rate']))

                                            # res = int(
                                            #     curr_timestamps['start'] * fc / len(wav)) / fr
                                            # res2 = int(curr_timestamps['end'] * fc / len(wav)) / fr

                                            res = curr_timestamps['start'] / 16000
                                            res2 = curr_timestamps['end'] / 16000

                                            start_time = timedelta(seconds = res)
                                            end_time = timedelta(seconds = res2)

                                            # start_time = timedelta(seconds = curr_timestamps['start'] / 10000)
                                            # end_time = timedelta(seconds = curr_timestamps['end'] / 10000)
                                            #
                                            diff_time = end_time - start_time

                                            ff = 'ffmpeg -ss {} -i "{}" -to {} -c copy "{}"'.format(
                                                start_time,
                                                curr_path,
                                                diff_time,
                                                os.path.join(
                                                    Path(curr_path).parent, Path(curr_path).stem + '_' + str(cnt) + '.mov'
                                                )
                                            )

                                            subprocess.call(ff, shell = True)
            finally:
                if runtime: self._r_end()