# def __subprocess_vosk_sr_audio(self, wf: str, last: bool, out: bool, logs: bool = True) -> List[str]:
    # results_recognized = []  # Результаты распознавания
    #
    # while True:
    #     data = wf.readframes(4000)
    #     if len(data) == 0: break
    #
    #     curr_res = []  # Текущий результат
    #
    #     # Распознанная речь
    #     if self._speech_rec.AcceptWaveform(data):
    #         speech_rec_res = json.loads(self._speech_rec.Result())  # Текущий результат
    #
    #         # Детальная информация распознавания
    #         curr_res = self.__speech_rec_result(self._keys_speech_rec, speech_rec_res)
    #     else: self._speech_rec.PartialResult()
    #
    #     if len(curr_res) == 3: results_recognized.append(curr_res)
    #
    # speech_rec_fin_res = json.loads(self._speech_rec.FinalResult())  # Итоговый результат распознавания
    # # Детальная информация распознавания
    # speech_rec_fin_res = self.__speech_rec_result(self._keys_speech_rec, speech_rec_fin_res)
    #
    # # Результат распознавания
    # if len(speech_rec_fin_res) == 3: results_recognized.append(speech_rec_fin_res)
    #
    # if len(results_recognized) == 0: self._error(self._sr_not_recognized, last = last, out = out); return []
    # else: self._test_from_sr(
    #     self._sr_recognized.format(self._info_wrapper(len(results_recognized))),
    #     results_recognized, last = last, out = out, name = self.vosk_sr.__name__, logs = logs)
    #
    # return results_recognized






# wf = wave.open(path_to_file) # WAV файл
# try:
#     # Файл не удовлетворяет требованиям
#     if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != 'NONE':
#         raise TypeError
# except TypeError:
#     self._other_error(self._audio_file_incorrect.format(
#         self._info_wrapper(self._audio_file_must_be)
#     ), last = last, out = out); return []
# else:
#     try:
#         # Текущая частота дискретизации отличается
#         if self._curr_freq != wf.getframerate():
#             # Активация распознавания речи
#             self._speech_rec = KaldiRecognizer(self._speech_model, wf.getframerate())
#             self._curr_freq = wf.getframerate()
#     except Exception: self._other_error(self._unknown_err, last = last, out = out); return []
#     else: return self.__subprocess_vosk_sr_audio(wf, last, out, logs)  # Распознавание


# Индикатор выполнения
# def progressbar(item, info, l):
#     clear_output(True)
#     self._progressbar(
#         self._audio_track_analysis.format(
#             self._audio_track_sr if sr is True else ''
#         ),
#         self._curr_progress.format(
#             item, len_paths, round(item * 100 / len_paths, 2), info
#         ), last = l, out = False
#     );
#     self.show_notebook_history_output()







                                            # # Количество каналов в аудиодорожке
                                            # channels_audio = MediaInfo.parse(audio_path).to_data()['tracks'][1]['channel_s']
                                            #
                                            # try:
                                            #     # Получение временных меток
                                            #     speech_timestamps = get_speech_ts(
                                            #         wav, model, trig_sum = trig_sum, neg_trig_sum = neg_trig_sum,
                                            #         num_steps = num_steps, batch_size = batch_size,
                                            #         num_samples_per_window = num_samples_per_window,
                                            #         min_speech_samples = min_speech_samples,
                                            #         min_silence_samples = min_silence_samples, visualize_probs = False
                                            #     )
                                            # except Exception: unprocessed_files.append(curr_path); continue
                                            # else:
                                            #     # Количество временных меток
                                            #     len_speech_timestamps = len(speech_timestamps)
                                            #
                                            #     # Текущее время для корзины с не отсортированными файлами (TimeStamp)
                                            #     # см. datetime.fromtimestamp()
                                            #     curr_ts_cart_name = str(datetime.now().timestamp()).replace('.', '_')
                                            #
                                            #     # Проход по всем найденным меткам
                                            #     for cnt, curr_timestamps in enumerate(speech_timestamps):
                                            #         # Индикатор выполнения VAD
                                            #         self.__progressbar_vad(
                                            #             self._audio_track_analysis.format(
                                            #                 self._audio_track_sr if sr is True else ''
                                            #             ), i, local_path(curr_path), True, cnt, len_paths,
                                            #             len_speech_timestamps
                                            #         )
                                            #
                                            #         # Начальное время
                                            #         start_time = timedelta(seconds = curr_timestamps['start'] / self._freq_sr)
                                            #         # Конечное время
                                            #         end_time = timedelta(seconds = curr_timestamps['end'] / self._freq_sr)
                                            #
                                            #         # Разница между начальным и конечным временем
                                            #         diff_time = end_time - start_time
                                            #
                                            #         # Путь до видеофрагмента
                                            #         part_video_path = os.path.join(
                                            #             splitted_video,
                                            #             Path(curr_path).stem + '_' + str(cnt) + Path(curr_path).suffix.lower()
                                            #         )
                                            #
                                            #         part_audio_path = []  # Пути до аудиофрагментов
                                            #
                                            #         if channels_audio == 1:  # Моно канал
                                            #             front = ['_m']  # Суффикс для аудиофрагментов
                                            #             part_audio_path.append(
                                            #                 os.path.join(
                                            #                     splitted_audio,
                                            #                     Path(curr_path).stem  + '_' + str(cnt) + self.ext_audio
                                            #                 )
                                            #             )
                                            #         elif channels_audio == 2:  # Стерео канал
                                            #             front = ['_l', '_r']  # Суффиксы для аудиофрагментов
                                            #             for ch in front:
                                            #                 part_audio_path.append(
                                            #                     os.path.join(
                                            #                         splitted_audio,
                                            #                         Path(curr_path).stem + '_' + str(cnt) + ch + self.ext_audio
                                            #                     )
                                            #                 )
                                            #
                                            #         # ##########################################################################
                                            #         # RUSAVIC
                                            #         # ##########################################################################
                                            #         if self.__rusavic(
                                            #             os.path.join(Path(curr_path).parent, Path(curr_path).stem),
                                            #             start_time, end_time, part_video_path, part_audio_path
                                            #         ) is True: continue
                                            #         # ##########################################################################
                                            #
                                            #         # Удаление видеофайла
                                            #         if os.path.isfile(part_video_path) is True: os.remove(part_video_path)
                                            #         # Удаление аудиофайлов
                                            #         for file in part_audio_path:
                                            #             if os.path.isfile(file) is True: os.remove(file)
                                            #
                                            #         # Дочерние процессы VAD
                                            #         self.__subprocesses_vad(
                                            #             type_encode = type_encode, start_time = start_time,
                                            #             end_time = end_time, diff_time = diff_time, curr_path = curr_path,
                                            #             part_video_path = part_video_path, crf_value = crf_value,
                                            #             presets_crf_encode = presets_crf_encode,
                                            #             channels_audio = channels_audio, audio_path = audio_path,
                                            #             part_audio_path = part_audio_path, sr = sr,
                                            #             sr_input_type = sr_input_type, curr_ts_cart_name = curr_ts_cart_name,
                                            #             splitted_video = splitted_video, splitted_audio = splitted_audio,
                                            #             front = front
                                            #         )
                                            #     # VAD нашел речь
                                            #     if len_speech_timestamps > 0:
                                            #         # Индикатор выполнения VAD
                                            #         self.__progressbar_vad(
                                            #             self._audio_track_analysis.format(
                                            #                 self._audio_track_sr if sr is True else ''
                                            #             ), len_paths, local_path(paths[-1]), True, len_speech_timestamps,
                                            #             len_paths, len_speech_timestamps
                                            #         )
                                            #     else:
                                            #         unprocessed_files.append(curr_path)














# Речь не найдена
#         if len(results_recognized) == 0: return 0
#
#         # Распознавание речи по видео
#         if type(results_recognized) is list: results_recognized = results_recognized[0][0].lower()
#         # Распознавание речи по аудио
#         elif type(results_recognized) is dict:
#             results_recognized = results_recognized[list(results_recognized.keys())[0]][0][0].lower()
#
#         if results_recognized == '': return 0  # Речь не найдена
#
#         results_recognized = results_recognized.replace(' ', '_')  # Директория для сохранения файла
#
#         # Рекурсивный поиск значения в списке
#         filter_sr = self._recursive_search_value_in_filter_sr(self._filter_sr, results_recognized)
#
#         # Текстовое представление речи не найдено в словаре
#         if filter_sr[0] is False:
#             if cont is True: return 0
#
#             # Текущее время (TimeStamp)
#             curr_ts = results_recognized + '_' + str(datetime.now().timestamp()).replace('.', '_')
#
#             results_recognized = self.cart_name + curr_ts_cart_name  # Директория для сохранения файла
#         else:  # Речь найдена
#             results_recognized = filter_sr[1].replace(' ', '_')  # Директория для сохранения файла
#
#             curr_ts = str(datetime.now().timestamp()).replace('.', '_')  # Текущее время (TimeStamp)
#
#         # Директория для текущей сортировки распознанной речи
#         dir_curr_sr_video = os.path.join(splitted_video, results_recognized)
#         dir_curr_sr_audio = os.path.join(splitted_audio, results_recognized)
#
#         try:
#             # Проход по всем директориям для сортировки распознанной речи
#             for dir_curr_sr in [dir_curr_sr_video, dir_curr_sr_audio]:
#                 if not os.path.exists(dir_curr_sr): os.makedirs(dir_curr_sr)  # Создание директории
#         except Exception: return 1
#         else:
#             # Переименование и перемещение файла
#             shutil.move(part_video_path, os.path.join(dir_curr_sr_video, curr_ts + Path(curr_path).suffix.lower()))
#
#             # Проход по всем Пути до аудиофрагментов
#             for cnt_audio, part_curr_audio_path in enumerate(part_audio_path):
#                 # Переименование и перемещение файла
#                 shutil.move(part_curr_audio_path,
#                             os.path.join(dir_curr_sr_audio, curr_ts + front[cnt_audio] + self.ext_audio))
#
#         if filter_sr[0] is False: return 2
#         else: return 3


# Дочерние процессы VAD
# def __subprocesses_vad(self):
#     """
#     Дочерние процессы VAD
#     """
#
#     try:
#         # Работает с пустыми кадрами в конце видео
#         # ff_video = 'ffmpeg -ss {} -i "{}" -to {} -c copy "{}"'.format(
#         #     start_time, curr_path, diff_time, part_video_path
#         # )
#
#         # Варианты кодирования
#         if type_encode == self._types_encode[0]:
#             # https://trac.ffmpeg.org/wiki/Encode/MPEG-4
#             ff_video = 'ffmpeg -ss {} -i "{}" -{} 0 -to {} "{}"'.format(
#                 start_time, curr_path, type_encode, diff_time, part_video_path
#             )
#         elif type_encode == self._types_encode[1]:
#             # https://trac.ffmpeg.org/wiki/Encode/H.264
#             ff_video = 'ffmpeg -ss {} -i "{}" -{} {} -preset {} -to {} "{}"'.format(
#                 start_time, curr_path, type_encode, crf_value, presets_crf_encode, diff_time, part_video_path
#             )
#
#         if channels_audio == 1:  # Моно канал
#             ff_audio = 'ffmpeg -i "{}" -ss {} -to {} -c copy "{}"'.format(
#                 audio_path, start_time, end_time, part_audio_path[0]
#             )
#         elif channels_audio == 2:  # Стерео канал
#             ff_audio = ('ffmpeg -i "{}" -map_channel 0.0.0 -ss {} -to {} '
#                         '"{}" -map_channel 0.0.1 -ss {} -to {} "{}"').format(
#                 audio_path, start_time, end_time, part_audio_path[0], start_time, end_time, part_audio_path[1]
#             )
#     except IndexError:
#         return curr_path
#     except Exception:
#         return curr_path
#     else:
#         call_video = subprocess.call(ff_video, shell = True)  # VAD
#         call_audio = subprocess.call(ff_audio, shell = True)  # VAD
#
#         try:
#             if call_video == 1 or call_audio == 1: raise OSError
#         except OSError:
#             return curr_path
#         except Exception:
#             return curr_path
#         else:
#             # Распознавание речи
#             if sr is True:
#                 vosk_sr_curr_res_true = False  # По умолчанию речь не распознана
#
#                 # Распознавание речи по видео
#                 if sr_input_type == self._dir_va[0]:
#                     # Сортировка файла в зависимости от распознанной речи
#                     if self.__sort_file_vad(self._vosk_sr(
#                             path_to_file = part_video_path, last = True, out = False, runtime = False, logs = False
#                     ), splitted_video = splitted_video, splitted_audio = splitted_audio,
#                             curr_ts_cart_name = curr_ts_cart_name, part_video_path = part_video_path,
#                             part_audio_path = part_audio_path, curr_path = curr_path, front = front,
#                             cont = False) > 1: vosk_sr_curr_res_true = True
#                 else:  # Распознавание речи по аудио
#                     for f_n, file in enumerate(part_audio_path):
#                         # Сортировка файла в зависимости от распознанной речи
#                         res_sort = self.__sort_file_vad(self._vosk_sr(
#                             path_to_file = file, last = True, out = False, runtime = False, logs = False
#                         ), splitted_video = splitted_video, splitted_audio = splitted_audio,
#                             curr_ts_cart_name = curr_ts_cart_name, part_video_path = part_video_path,
#                             part_audio_path = part_audio_path, curr_path = curr_path, front = front,
#                             cont = False if f_n + 1 == len(part_audio_path) else True)
#
#                         if res_sort == 2: vosk_sr_curr_res_true = True; continue
#                         if res_sort == 3: vosk_sr_curr_res_true = True; break
#                 # Речь не найдена
#                 if vosk_sr_curr_res_true is False:
#                     # Удаление видеофайла
#                     if os.path.isfile(part_video_path) is True: os.remove(part_video_path)
#                     # Удаление аудиофайлов
#                     for file in part_audio_path:
#                         if os.path.isfile(file) is True: os.remove(file)


# @staticmethod
# def __rusavic(path, start_time, end_time, part_video_path, part_audio_path):
#     # Фильтр игнорирования речи
#     import json
#
#     try:
#         with open(path + '.json') as f:
#             data = json.load(f)
#     except Exception:
#         return False
#     else:
#         l = []
#
#         for i in data[list(data.keys())[0]]:
#             res = (i[1] - i[0]) / 2
#             l.append(round(i[0] + res, 3))
#
#         for curr_val in l:
#             if start_time.total_seconds() < curr_val < end_time.total_seconds():
#                 try:
#                     # Удаление видеофайла
#                     if os.path.isfile(part_video_path) is True: os.remove(part_video_path)
#                     # Удаление аудиофайлов
#                     for file in part_audio_path:
#                         if os.path.isfile(file) is True: os.remove(file)
#                 except Exception:
#                     return False
#                 else:
#                     return True
#
#         return False


# ######################################################################################################
# RUSAVIC
# ######################################################################################################
# if self.__rusavic(
#         os.path.join(Path(self.__curr_path).parent, Path(self.__curr_path).stem),
#         start_time, end_time, self.__part_video_path, self.__part_audio_path
# ) is True: continue
# ######################################################################################################
