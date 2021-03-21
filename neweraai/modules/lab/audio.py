#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Аудио
"""

# ######################################################################################################################
# Импорт необходимых инструментов
# ######################################################################################################################
import os          # Взаимодействие с файловой системой
import subprocess  # Работа с процессами

from pathlib import Path  # Работа с путями в файловой системе

from pymediainfo import MediaInfo  # Получение meta данных из медиафайлов

from IPython.display import clear_output

# Персональные
from neweraai.modules.lab.statistics import Statistics  # Статистика

# ######################################################################################################################
# Сообщения
# ######################################################################################################################
class Messages(Statistics):
    """Сообщения"""

    # ------------------------------------------------------------------------------------------------------------------
    # Конструктор
    # ------------------------------------------------------------------------------------------------------------------

    def __init__(self):
        super().__init__()  # Выполнение конструктора из суперкласса

        self._files_not_found: str = self._('В указанной директории необходимые файлы не найдены ...')
        self._extract_audio_from_video: str = self._('Извлечение аудиодорожки из видеофайла ...')
        self._curr_progress: str = '{} ' + self._('из') + ' {} ({}%) ...'

# ######################################################################################################################
# Статистика
# ######################################################################################################################
class Audio(Messages):
    """Статистика"""

    # ------------------------------------------------------------------------------------------------------------------
    # Конструктор
    # ------------------------------------------------------------------------------------------------------------------

    def __init__(self):
        super().__init__()  # Выполнение конструктора из суперкласса

    # ------------------------------------------------------------------------------------------------------------------
    # Внешние методы
    # ------------------------------------------------------------------------------------------------------------------

    # Извлечение аудиодорожки из видеофайла
    def extract_audio_from_video(self, runtime: bool = True):
        """
        Извлечение аудиодорожки из видеофайла

        Аргументы:
            runtime: Подсчет времени выполнения
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
            except IsADirectoryError: self._other_error(self.extract_audio_from_video.format(original))
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

                # # Директория с оригинальными видео не содержит видеофайлов с необходимым расширением
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

                            ff = 'ffmpeg -i {} -vn -codec:v copy -ac {} {}'.format(
                                curr_path, MediaInfo.parse(curr_path).to_data()['tracks'][2]['channel_s'],
                                audio_path
                            )

                            call = subprocess.call(ff, shell = True)  # Конвертация видео в аудио

                            try:
                                if call == 1: raise OSError
                            except OSError: self._other_error(self._som_ww); return None
                            except Exception:
                                self._other_error(self._unknown_err); return None
                            else:
                                progressbar(i)  # Индикатор выполнения
            finally:
                if runtime: self._r_end()
