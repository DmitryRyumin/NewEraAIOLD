#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Статистика
"""

# ######################################################################################################################
# Импорт необходимых инструментов
# ######################################################################################################################
# Подавление Warning
import warnings
for warn in [UserWarning, FutureWarning]: warnings.filterwarnings('ignore', category = warn)

from dataclasses import dataclass  # Класс данных

import os                           # Взаимодействие с файловой системой
import numpy as np                  # Научные вычисления
import pandas as pd                 # Обработка и анализ данных
from pathlib import Path            # Работа с путями в файловой системе
import re                           # Регулярные выражения
import matplotlib.pyplot as plt     # MATLAB-подобный способ построения графиков
import matplotlib as mpl            # Визуализация графиков
import seaborn as sns               # Визуализация графиков (надстройка над matplotlib)
import xml.etree.ElementTree as et  # XML документ в виде дерева

from matplotlib.ticker import MaxNLocator          # Работа с метками
from matplotlib.legend_handler import HandlerBase  # Работа с легендой
from matplotlib.text import Text                   # Работа с текстом на графике

from typing import List, Dict, Iterable
from types import FunctionType
from datetime import datetime  # Работа со временем

from IPython.display import display

# Персональные
from neweraai.modules.lab.download import Download  # Загрузка

# ######################################################################################################################
# Настройки необходимых инструментов
# ######################################################################################################################
pd.set_option('display.max_columns', None)  # Максимальное количество отображаемых столбцов
pd.set_option('display.max_rows', None)     # Максимальное количество отображаемых строк

# ######################################################################################################################
# Сообщения
# ######################################################################################################################
@dataclass
class Messages(Download):
    """Сообщения"""

    # ------------------------------------------------------------------------------------------------------------------
    # Конструктор
    # ------------------------------------------------------------------------------------------------------------------

    def __post_init__(self):
        super().__post_init__()  # Выполнение конструктора из суперкласса

        self._files_not_found: str = self._('В указанной директории необходимые файлы не найдены ...')
        self._all_find_files: str = self._('Всего найдено {} файлов с расширением {} ...')
        self._df_files_is_empty: str = self._('DataFrame c данными пустой ...')
        self._all_find_empty_classes: str = self._('Всего найдено {} пустых классов ...')
        self._df_files_not_empty_classes: str = self._('В DataFrame пустых классов не найдено ... это хороший знак ...')
        self._all_find_files_with_annotated: str = self._(
            'Всего найдено синхронизированных файлов {} и {}: {} из {} ...')
        self._all_find_files_is_annotated: str = self._('Все файлы {} аннотированы ... это хороший знак ...')
        self._all_find_files_without_annotated: str = self._('Всего найдено {} файлов без аннотирования ...')

# ######################################################################################################################
# Статистика
# ######################################################################################################################
@dataclass
class Statistics(Messages):
    """Статистика"""

    # ------------------------------------------------------------------------------------------------------------------
    # Конструктор
    # ------------------------------------------------------------------------------------------------------------------

    def __post_init__(self):
        super().__post_init__()  # Выполнение конструктора из суперкласса

        self._df_files: pd.DataFrame = pd.DataFrame()  # DataFrame с данными
        self._dict_of_files: Dict[List[str], List[str], List[int]] = {}  # Словарь для DataFrame с данными
        self._labels_nan: List[int] = []  # Список с ID пустых классов

        self._df_files_without_annotated: pd.DataFrame = pd.DataFrame()  # DataFrame с данными без аннотации
        self._dict_of_files_without_annotated: Dict[List[str]] = {}  # Словарь для DataFrame с данными без аннотации

        self._stats_files: Dict[List[int], List[str], List[int]] = {}  # Словарь для статистики
        self._df_stats_files: pd.DataFrame = pd.DataFrame()  # DataFrame со статистикой
        self._min_train_size: int = 0  # Минимальное допустимое значение для количества экземпляров из каждого класса
                                       # набора данных, которые будут включены в обучающую выборку

        self._title_label_for_df_1 = False  # Заголовок осей
        self._curr_n_splits: int = 1  # Какая стратифицированная выборка будет выбрана для процесса обучения и валидации

        self._dir_va: List[str] = ['Video', 'Audio']  # Название каталогов для видео и аудио

        self._ext_annotated: str = '.xml'  # Расширения аннотированных файлов

        # ----------------------- Только для внутреннего использования внутри класса

        self.__obj_det: bool = False  # Распознавание объектов
        # Парсинг XML файла для аннотирования и распознавания объектов
        self.__tags_in_xml: Dict[str or List[str]] = {
            'obj': 'object',
            'name': 'name',
            'box': 'bndbox',
            'path': 'path',
            'bndbox': ['xmin', 'ymin', 'xmax', 'ymax']
        }

    # ------------------------------------------------------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------------------------------------------------------

    # DataFrame c данными
    @property
    def df_files(self): return self._df_files

    # DataFrame c данными без аннотации
    @property
    def df_files_without_annotated(self): return self._df_files_without_annotated

    # DataFrame со статистикой
    @property
    def df_stats_files(self): return self._df_stats_files

    # Минимальное допустимое значение для количества экземпляров из каждого класса набора данных, которые будут
    # включены в обучающую выборку
    @property
    def min_train_size(self): return self._min_train_size

    # ------------------------------------------------------------------------------------------------------------------
    # Внутренние методы
    # ------------------------------------------------------------------------------------------------------------------

    # Получение директорий где хранятся данные
    def _get_paths(self, path: Iterable[str], depth: int = 1, out: bool = True) -> List[str] or bool:
        """
        Получение директорий где хранятся данные

        Аргументы:
            path - Директория набора данных
            depth - Глубина иерархии для извлечения классов
            out - Отображение

        Возвращает: False если проверка аргументов не удалась или список с директориями
        """

        try:
            # Проверка аргументов
            if not isinstance(path, Iterable) or type(depth) is not int or depth < 1 or type(out) is not bool:
                raise TypeError
        except TypeError: self._other_error(self._som_ww, out = out); return False
        except Exception: self._other_error(self._unknown_err, out = out); return False
        else:
            if type(path) is not list: path = [path]

            new_path = []  # Список с директориями

            # Проход по всем директориям набора данных
            for curr_path in path:
                for f in os.scandir(curr_path):
                    if f.is_dir() and not f.name.startswith('.'):
                        ignore = False  # По умолчанию не игнорировать директорию
                        for curr_dir in self.ignore_dirs:
                            if type(curr_dir) is not str: continue
                            if re.search('^' + curr_dir, f.name) is not None: ignore = True  # Игнорировать директорию

                        if ignore is False: new_path.append(f.path)
            # Рекурсивный переход на следующий уровень иерархии
            if depth != 1: return self._get_paths(new_path, depth - 1)

            return new_path  # Список с директориями

    # Добавление значений в словарь для DataFrame c данными
    def __append_to_list_of_files(self, path: str, class_names: List[str], out: bool = True) -> bool:
        """
        Добавление значений в словарь для DataFrame c данными

        Аргументы:
            path - Путь к файлу
            class_names - Названия классов
            out - Отображение

        Возвращает: True если значения в словарь для DataFrame были добавлены, в обратном случае False
        """

        try:
            # Проход по всем классам
            for cl in class_names:
                self._dict_of_files[self.keys_dataset[0]].append(path)
                self._dict_of_files[self.keys_dataset[1]].append(cl)
        except IndexError: self._other_error(self._som_ww, out = out); return False
        except Exception: self._other_error(self._unknown_err, out = out); return False
        else: return True

    # Добавление значений в словарь для DataFrame c данными без аннотации
    def __append_to_list_of_files_without_annotated(self, path: str, out: bool = True) -> bool:
        """
        Добавление значений в словарь для DataFrame c данными без аннотации

        Аргументы:
            path - Путь к файлу
            out - Отображение

        Возвращает: True если значения в словарь для DataFrame были добавлены, в обратном случае False
        """

        try: self._dict_of_files_without_annotated[self.keys_dataset[0]].append(path)
        except IndexError: self._other_error(self._som_ww, out = out); return False
        except Exception: self._other_error(self._unknown_err, out = out); return False
        else: return True

    # Получение аннотаций для распознавания объектов
    def __get_annotated_classes(self, path: str):
        """
        Получение аннотаций для распознавания объектов

        Аргументы:
            path - Путь к файлу

        Возвращает: Список с названиями аннотированных объектов
        """

        try:
            if type(path) is not str: raise TypeError

            # Файла с разметкой не существует
            if os.path.isfile(path) is False: raise FileNotFoundError

            tree = et.parse(path)  # Получение XML в виде дерева
        except (TypeError, FileNotFoundError): return []
        except et.ParseError: return []
        except Exception: return []
        else:
            classes = []  # Список с названиями аннотированных объектов

            root = tree.getroot()  # Получение корневого элемента

            # Тег не найден
            if root.find(self.__tags_in_xml['obj']) is None: return []

            # Проход по всем потомкам корневого элемента
            for child in root:
                # Тег который содержит имя класса
                if child.tag == self.__tags_in_xml['obj']:
                    # Тег не найден
                    if child.find(self.__tags_in_xml['name']) is None: return []

                    # Проход по всем детям 'object'
                    for ch in child.iter():
                        # Имя класса
                        if ch.tag == self.__tags_in_xml['name']: classes.append(ch.text)  # Добавление класса в массив

            return classes

    # График подсчета количества экземпляров в каждом классе
    def _countplot(self, cols: int = 1, rows: int = 1, show_legend: bool = True, out: bool = True,
                   *df: List[pd.DataFrame]) -> bool:
        """
        График подсчета количества экземпляров в каждом классе

        Аргументы:
            cols - Количество столбцов
            rows - Количество строк
            show_legend - Отображение легенды
            out - Отображение
            df - Список DataFrame в любом количестве

        Возвращает: True если график отображен, в обратном случае False
        """

        try:
            # Проверка аргументов
            if type(cols) is not int or type(rows) is not int or type(show_legend) is not bool: raise TypeError
        except TypeError: self._inv_args(__class__.__name__, self._countplot.__name__, out = out); return False
        else:
            try:
                # Значения для размера фигуры не валидные
                if self.figsize[0] < 1 or self.figsize[1] < 1: raise ValueError

                # Создание новой фигуры (размер фигуры в дюймах)
                fig = plt.figure(figsize = self.figsize)
            except (TypeError, ValueError): self._other_error(self._som_ww, out = out); return False
            except Exception: self._other_error(self._unknown_err, out = out); return False
            else:
                # Установка эстетических параметров
                sns.set(style = 'white', palette = 'muted', color_codes = True, rc = {'lines.linewidth': 2.7})
                sns.despine(left = True)
                mpl.rcParams['axes.linewidth'] = 1  # Толщина рамки

                cnt_df = 0  # Счетчик DataFrames

                # Проход по всем строкам
                for i_rows in range(0, rows):
                    # Проход по всем столбцам
                    for j_cols in range(0, cols):
                        try:
                            curr_df = df[cnt_df]
                        except IndexError: plt.close(fig); self._other_error(self._som_ww, out = out); return False
                        except Exception: plt.close(fig); self._other_error(self._unknown_err, out = out); return False
                        else:
                            # Создание оси в определенном месте внутри регулярной сетки
                            ax = plt.subplot2grid(
                                (rows, cols), (i_rows, j_cols), rowspan = j_cols + 1, colspan = i_rows + 1
                            )

                            ax.xaxis.tick_bottom()  # Перемещение меток в нижнюю часть

                            try:
                                # DataFrame не передан или пустой
                                if type(curr_df) is not pd.DataFrame or len(curr_df) == 0: raise TypeError

                                # Количество экземпляров в каждом классе
                                ax = sns.countplot(x = curr_df[self.keys_dataset[2]], label = self._('Количество'))
                            except (KeyError, TypeError):
                                plt.close(fig); self._other_error(self._som_ww, out = out); return False
                            except Exception:
                                plt.close(fig); self._other_error(self._unknown_err, out = out); return False
                            else:
                                groupby = curr_df.groupby(curr_df[self.keys_dataset[2]])[self.keys_dataset[1]]

                                counts = groupby.count().index.tolist()

                                # DataFrames
                                if len(df) < 2: self._stats_files[self.keys_stats[0]] = counts

                                max_value = groupby.value_counts().max()  # Максимальное значение в столбцах
                                pad = max_value * self.pad / 1000  # Y отступ в графиках от ряда до его значения

                                for i, p in enumerate(ax.patches):
                                    height = p.get_height()

                                    number_of_images = 0 if counts[i] in self._labels_nan else \
                                        curr_df[self.keys_dataset[2]].value_counts()[counts[i]]

                                    if number_of_images == 0: height = 0; p.set_height(height)

                                    try:
                                        # DataFrames
                                        if len(df) < 2: self._stats_files[self.keys_stats[2]].append(number_of_images)
                                    except IndexError:
                                        plt.close(fig); self._other_error(self._som_ww, out = out); return False
                                    except Exception:
                                        plt.close(fig); self._other_error(self._unknown_err, out = out); return False
                                    else:
                                        ax.text(
                                            p.get_x() + p.get_width() / 2.0,  # X позиция размещения текста
                                            height + pad,  # Y позиция размещения текста
                                            number_of_images,  # Текст
                                            ha = 'center',  # Выравнивание
                                            fontdict = {
                                                'fontsize': 14,  # Размер заголовка
                                                'color': '#000000'  # Цвет заголовка
                                            }
                                        )

                                # Изменение внешнего вида меток
                                ax.tick_params(
                                    axis = 'x',  # Ось
                                    direction = 'out',  # Расположение линий меток
                                    length = 10,  # Длина линий меток
                                    width = 1,  # Ширина линий меток
                                    color = '#999A99',  # Цвет линий меток
                                    pad = 5,  # Расстояние между линиями меток и метками
                                    labelsize = 14,  # Размер метки
                                    labelcolor = '#000000',  # Цвет метки
                                    bottom = True,  # Рисование линий меток
                                )
                                ax.tick_params(
                                    axis = 'y',  # Ось
                                    direction = 'out',  # Расположение линий меток
                                    length = 10,  # Длина линий меток
                                    width = 1,  # Ширина линий меток
                                    color = '#999A99',  # Цвет линий меток
                                    pad = 5,  # Расстояние между линиями меток и метками
                                    labelsize = 14,  # Размер метки
                                    labelcolor = '#000000',  # Цвет метки
                                    left = True  # Рисование линий меток
                                )

                                # DataFrames
                                if len(df) < 2: label_name = self._('Сбалансированность классов')
                                else: label_name = self._keys_folds[cnt_df % len(self._keys_folds)]

                                # Заголовок осей
                                ax.set_title(
                                    label = label_name,  # Заголовок
                                    fontdict = {
                                        'fontsize': 18,  # Размер заголовка
                                        'color': '#000000'  # Цвет заголовка
                                    },
                                    pad = 10  # Отступ заголовка от вершины осей
                                )

                                # Изменение внешнего вида меток данных
                                ax.set_xlabel(
                                    self._('ID класса'),
                                    fontsize = 14,  # Размер метки
                                    fontdict = {
                                        'color': '#000000'  # Цвет метки
                                    },
                                    labelpad = 10  # Отступ
                                )
                                ax.set_ylabel(
                                    self._('Количество экземпляров в каждом классе'),
                                    fontsize = 14,  # Размер метки
                                    fontdict = {
                                        'color': '#000000'  # Цвет метки
                                    },
                                    labelpad = 5  # Отступ
                                )

                                plt.setp(ax.spines.values(), color = '#999A99')  # Цвет рамки

                                ax.yaxis.set_major_locator(MaxNLocator(integer = True))

                                xticklabels = ax.get_xticklabels()  # Метки X

                                # Словарь из ID и названий классов
                                labels = dict(zip(curr_df[self.keys_dataset[2]], curr_df[self.keys_dataset[1]]))

                                labels = [labels[int(h.get_text())] for h in xticklabels]

                                # DataFrames
                                if len(df) < 2: self._stats_files[self.keys_stats[1]] = labels

                                handles = [(h.get_text(), c.get_fc()) for h, c in zip(xticklabels, ax.patches)]

                                try:
                                    # Значения для размера фигуры не валидные
                                    if self.bbox_to_anchor[0] < 1 or self.bbox_to_anchor[1] < 1: raise ValueError

                                    leg = ax.legend(
                                        handles,
                                        labels,
                                        handler_map = {tuple: TextHandler()},
                                        bbox_to_anchor = self.bbox_to_anchor,
                                        borderaxespad = 0,
                                        frameon = False,
                                        fontsize = 16,
                                        title_fontsize = 16,
                                        prop = {
                                            'size': 16,
                                            'weight': 'bold'
                                        }
                                    )
                                except (TypeError, ValueError):
                                    plt.close(fig); self._other_error(self._som_ww, out = out); return False
                                except Exception:
                                    plt.close(fig); self._other_error(self._unknown_err, out = out); return False
                                else:
                                    leg.set_visible(show_legend)

                                    try: ax.set_ymargin(self.ymargin)  # Y отступ от ряда до рамки
                                    except (ValueError, TypeError):
                                        plt.close(fig); self._other_error(self._som_ww, out = out); return False
                                    except Exception:
                                        plt.close(fig); self._other_error(self._unknown_err, out = out); return False
                                    else:
                                        # Цвета
                                        for h, t in zip(leg.legendHandles, ax.xaxis.get_ticklabels()):
                                            t.set_color(h.get_color())
                                        for h, t in zip(leg.legendHandles, leg.get_texts()):
                                            t.set_color(h.get_color())

                                        cnt_df += 1  # Увеличение счетчика
                # DataFrames
                if len(df) > 1:
                    try:
                        # Отступы
                        plt.subplots_adjust(wspace = self.subplots_adjust[0], hspace = self.subplots_adjust[1])
                    except (TypeError, IndexError):
                        plt.close(fig); self._other_error(self._som_ww, out = out); return False
                    except Exception: plt.close(fig); self._other_error(self._unknown_err, out = out); return False
                    else:
                        try:
                            if type(self.suptitle_y) is not float and type(self.suptitle_y) is not int: raise TypeError
                        except TypeError: plt.close(fig); self._other_error(self._som_ww, out = out); return False
                        except Exception: plt.close(fig); self._other_error(self._unknown_err, out = out); return False
                        else:
                            sublabel = self._('Сбалансированность классов выборки')

                            if self._title_label_for_df_1 is False: sublabel += ' - {}'.format(self._curr_n_splits)

                            plt.suptitle(
                                sublabel,  # Заголовок
                                fontsize = 20,  # Размер заголовка
                                fontdict = {
                                    'color': '#000000'  # Цвет заголовка
                                },
                                y = self.suptitle_y  # Отступ заголовка от вершины осей
                            )

                if out: plt.show()  # Отображение фигуры

                return True

    # ------------------------------------------------------------------------------------------------------------------
    # Внешние методы
    # ------------------------------------------------------------------------------------------------------------------

    # Формирование DataFrame для статистики
    def generate_df(self, depth: int = 1,
                    func_for_class_name: FunctionType = lambda class_name: Path(class_name).name,
                    runtime: bool = True, logs: bool = True, out: bool = True, run: bool = True):
        """
        Формирование DataFrame для статистики

        Аргументы:
            depth - Глубина иерархии для извлечения классов
            func_for_class_name - Функция для приведения названий классов в необходимый вид
            runtime - Подсчет времени выполнения
            logs - При необходимости формировать LOG файл
            out - Отображение
            run - Блокировка выполнения
        """

        self._clear_notebook_history_output()  # Очистка истории вывода сообщений в ячейке Jupyter

        # Сброс
        self._df_files = pd.DataFrame()  # Пустой DataFrame с данными
        self._df_files_without_annotated = pd.DataFrame()  # Пустой DataFrame с данными без аннотации

        try:
            # Проверка аргументов
            if (type(depth) is not int or depth < 1 or not isinstance(func_for_class_name, FunctionType)
                    or type(runtime) is not bool or type(logs) is not bool or type(out) is not bool
                    or type(run) is not bool): raise TypeError
        except TypeError: self._inv_args(__class__.__name__, self.generate_df.__name__, out = out)
        else:
            if run is False: self._error(self._lock_user, out = out); return None  # Блокировка выполнения

            if runtime: self._r_start()

            try:
                # Получение директорий где хранятся данные
                path_to_classes = self._get_paths(self.path_to_dataset, depth)

                if type(path_to_classes) is bool: return None

                if type(self.keys_dataset) is not list: raise TypeError

                # Словарь для DataFrame набора данных с данными
                self._dict_of_files = dict(zip(self.keys_dataset, [[] for _ in range(0, len(self.keys_dataset))]))
                # Словарь для DataFrame набора данных с данными без аннотации
                self._dict_of_files_without_annotated = dict(zip([self.keys_dataset[0]], [[]]))
            except (TypeError, FileNotFoundError):
                self._other_error(self._folder_not_found.format(self._info_wrapper(self.path_to_dataset)), out = out)
            except Exception: self._other_error(self._unknown_err, out = out); return None
            else:
                all_empty = True  # По умолчанию все каталоги пустые
                # Распознавание объектов
                if self.__obj_det is True: with_annotated = False  # По умолчанию все файлы с аннотацией

                # Установка списка с директориями входящими в выборку
                self.filter_dirs = [v.lower().replace(' ', '_').capitalize().strip() for v in
                    self.filter_dirs if type(v) is str]

                # Проход по всем именам классов
                for curr_path in path_to_classes:
                    if len(self.filter_dirs) > 0 and (Path(curr_path).name in self.filter_dirs) is False: continue

                    empty = True  # По умолчанию каталог пустой

                    # Формирование словаря для DataFrame
                    for p in Path(curr_path).rglob('*'):
                        # Добавление ID каждому классу
                        try:
                            if type(self.ext) is not list or len(self.ext) < 1: raise TypeError

                            self.ext = [x.lower() for x in self.ext]
                        except TypeError: self._other_error(self._som_ww, out = out); return None
                        except Exception: self._other_error(self._unknown_err, out = out); return None
                        else:
                            # Расширение файла соответствует расширению искомых файлов
                            if p.suffix.lower() in self.ext:
                                valid_annotated = True  # По умолчанию разметка валидная

                                # Распознавание объектов
                                if self.__obj_det is True:
                                    file_xml = os.path.join(p.parent, p.stem + self._ext_annotated)  # Файла с разметкой

                                    # Получение аннотаций для распознавания объектов
                                    classes = self.__get_annotated_classes(file_xml)

                                    if len(classes) == 0:
                                        if self.__append_to_list_of_files_without_annotated(p.resolve(), out) is False:
                                            return None

                                        # Минимум 1 файл без аннотации
                                        if with_annotated is False: with_annotated = True
                                        valid_annotated = False  # Разметка не валидная

                                if empty is True: empty = False  # Каталог не пустой
                                if all_empty is True: all_empty = False  # Все каталоги не пустые

                                # Разметка валидная
                                if valid_annotated is True:
                                    # Добавление значений в словарь для DataFrame
                                    if self.__append_to_list_of_files(
                                            p.resolve(),
                                            classes if self.__obj_det else [func_for_class_name(curr_path)],
                                            out
                                    ) is False: return None

                    # В каталоге нет файлов
                    if empty is True:
                        # Добавление значений в словарь для DataFrame
                        if self.__append_to_list_of_files(np.nan, [func_for_class_name(curr_path)], out) is False:
                            return None
                # Во всех каталогах нет файлов
                try:
                    if all_empty is True: raise TypeError
                except TypeError: self._other_error(self._files_not_found, out = out); return None
                except Exception: self._other_error(self._unknown_err, out = out)
                else:
                    # Отображение в DataFrame с данными
                    self._df_files = pd.DataFrame.from_dict(data = self._dict_of_files, orient = 'index').transpose()
                    self._df_files.index.name = self._keys_id
                    self._df_files.index += 1

                    # Минимум 1 файл без аннотации
                    if self.__obj_det is True and with_annotated is True:
                        # Отображение в DataFrame с данными без аннотации
                        self._df_files_without_annotated = pd.DataFrame.from_dict(
                            data = self._dict_of_files_without_annotated, orient = 'index').transpose()
                        self._df_files_without_annotated.index.name = self._keys_id
                        self._df_files_without_annotated.index += 1

                    # Добавление ID каждому классу
                    try:
                        self._df_files[self.keys_dataset[2]] = \
                            self._df_files[self.keys_dataset[1]].astype('category').cat.codes + 1
                    except IndexError: self._other_error(self._som_ww, out = out)
                    except Exception: self._other_error(self._unknown_err, out = out)
                    else:
                        self._df_files.index = self._df_files.index.map(str)

                        # Распознавание объектов
                        if self.__obj_det is True:
                            # Информационное сообщение
                            self._info(self._all_find_files_with_annotated.format(
                                self._info_wrapper(self._ext_annotated.replace('.', '')),
                                self._info_wrapper(', '.join(x.lower().replace('.', '') for x in self.ext)),
                                self._info_wrapper(len(self._df_files)),
                                self._info_wrapper(len(self._df_files) + len(self._df_files_without_annotated))
                            ), last = False, out = False)
                        else:
                            # Информационное сообщение
                            self._info(self._all_find_files.format(self._info_wrapper(len(self._df_files)),
                                self._info_wrapper(', '.join(x.lower().replace('.', '') for x in self.ext))
                            ), last = False, out = False)

                        # Отображение
                        if out is True:
                            self._add_notebook_history_output(self._df_files.iloc[0:self.num_to_df_display, :])

                        # Распознавание объектов
                        if self.__obj_det is True:
                            # Минимум 1 файл без аннотации
                            if with_annotated is True:
                                # Информационное сообщение
                                self._error(self._all_find_files_without_annotated.format(
                                    self._info_wrapper(len(self._df_files_without_annotated))
                                ), last = False, out = False)

                                # Отображение
                                if out is True:
                                    self._add_notebook_history_output(
                                        self._df_files_without_annotated.iloc[0:self.num_to_df_display, :])
                            else:
                                # Информационное сообщение
                                self._info_true(self._all_find_files_is_annotated.format(
                                    self._info_wrapper(', '.join(x.lower().replace('.', '') for x in self.ext))
                                ), last = False, out = False)

                        # Отображение истории вывода сообщений в ячейке Jupyter
                        if out is True: self.show_notebook_history_output()

                        if logs is True:
                            # Текущее время для лог файла
                            # см. datetime.fromtimestamp()
                            curr_ts = str(datetime.now().timestamp()).replace('.', '_')

                            # Распознавание объектов
                            if self.__obj_det is True: name_logs_file = self.generate_df_obj_det.__name__
                            else: name_logs_file = self.generate_df.__name__

                            # Сохранение LOG
                            res_save_logs = self._save_logs(
                                self._df_files, name_logs_file + ('_with_annotated_' if self.__obj_det else '')
                                + curr_ts)

                            # Сохранение LOG с не аннотированными файлами
                            if self.__obj_det is True and with_annotated is True:
                                res_saved_logs = self._save_logs(
                                    self._df_files_without_annotated, name_logs_file
                                    + ('_without_annotated_' if self.__obj_det else '') + curr_ts)

                            if res_save_logs is True:
                                # Сохранение LOG файла/файлов
                                if self.__obj_det is True and with_annotated is True:
                                    if res_saved_logs is False: return None

                                    logs_s = self._logs_saves_true
                                else: logs_s = self._logs_save_true

                                self._info_true(logs_s, out = out)
            finally:
                if runtime: self._r_end(out = out)

    # Формирование DataFrame для статистики (распознавание объектов)
    def generate_df_obj_det(self, depth: int = 1,
                            func_for_class_name: FunctionType = lambda class_name: Path(class_name).name,
                            runtime: bool = True, logs: bool = True, out: bool = True, run: bool = True):
        """
        Формирование DataFrame для статистики (распознавание объектов)

        Аргументы:
            depth - Глубина иерархии для извлечения классов
            func_for_class_name - Функция для приведения названий классов в необходимый вид
            runtime - Подсчет времени выполнения
            logs - При необходимости формировать LOG файл
            out - Отображение
            run - Блокировка выполнения
        """

        self.__obj_det = True

        self.generate_df(depth = depth, func_for_class_name = func_for_class_name, runtime = runtime, logs = logs,
                         out = out, run = run)

        self.__obj_det = False

    # Получение пустых классов
    def get_empty_classes(self, runtime: bool = True, logs: bool = True, out: bool = True, run: bool = True):
        """
        Получение пустых классов

        Аргументы:
            runtime - Подсчет времени выполнения
            logs - При необходимости формировать LOG файл
            out - Отображение
            run - Блокировка выполнения
        """

        self._clear_notebook_history_output()  # Очистка истории вывода сообщений в ячейке Jupyter

        try:
            # Проверка аргументов
            if type(runtime) is not bool or type(logs) is not bool or type(out) is not bool or type(run) is not bool:
                raise TypeError
        except TypeError: self._inv_args(__class__.__name__, self.get_empty_classes.__name__, out = out)
        else:
            if runtime: self._r_start()

            try:
                # DataFrame c данными не создан или пустой
                if self.df_files.empty: raise ValueError
            except ValueError: self._other_error(self._df_files_is_empty, out = out)
            else:
                # Удаление дубликатов
                df_files_nan = self._df_files[
                    self._df_files.isnull().any(axis = 1)
                ].drop_duplicates(subset = [self.keys_dataset[1]])

                nan = df_files_nan[self.keys_dataset[1]].isin(
                    self._df_files.dropna()[self.keys_dataset[1]].unique().tolist())

                df_files_delete = df_files_nan[nan].index.tolist() # Индексы которые необходимо удалить
                self._df_files.drop(index = df_files_delete, inplace = True)  # Удаление индексов

                # Удаление классов в которых уже имеются значения но в другом объекте
                df_files_nan = df_files_nan[~nan]

                self._labels_nan = df_files_nan[self.keys_dataset[2]].tolist()  # Список с ID пустых классов

                # Пустые классы не найдены
                if len(self._labels_nan) == 0:
                    # Информационное сообщение
                    self._info_true(self._df_files_not_empty_classes, last = False, out = False)
                    # Отображение истории вывода сообщений в ячейке Jupyter
                    if out: self.show_notebook_history_output()
                else:
                    # Информационное сообщение
                    self._info(self._all_find_empty_classes.format(
                        self._info_wrapper(len(self._labels_nan))
                    ), last = False, out = False)
                    # Отображение истории вывода сообщений в ячейке Jupyter
                    if out: self.show_notebook_history_output()

                    # Отображение
                    if out is True:
                        # Отображение первых N строк
                        display(df_files_nan[[
                            self.keys_dataset[1], self.keys_dataset[2]
                        ]].iloc[0:self.num_to_df_display, :].style.hide_index())

                    if logs is True:
                        # Текущее время для лог файла
                        # см. datetime.fromtimestamp()
                        curr_ts = str(datetime.now().timestamp()).replace('.', '_')

                        # Сохранение LOG
                        res_save_logs = self._save_logs(df_files_nan[[
                            self.keys_dataset[1], self.keys_dataset[2]
                        ]], self.get_empty_classes.__name__ + '_' + curr_ts)

                        if res_save_logs is True: self._info_true(self._logs_save_true, out = out)
            finally:
                if runtime: self._r_end(out = out)

    # Визуализация сбалансированности данных
    def data_balance_visualization(self, show_df: bool = True, show_legend: bool = True, runtime: bool = True,
                                   logs: bool = True, out: bool = True, run: bool = True):
        """
        Визуализация сбалансированности данных

        Аргументы:
            show_df - Отображение DataFrame co статистикой
            show_legend - Отображение легенды
            runtime - Подсчет времени выполнения
            logs - При необходимости формировать LOG файл
            out - Отображение
            run - Блокировка выполнения
        """

        self._clear_notebook_history_output()  # Очистка истории вывода сообщений в ячейке Jupyter

        # Сброс
        self._df_stats_files = pd.DataFrame()  # Пустой DataFrame

        try:
            # Проверка аргументов
            if (type(show_df) is not bool or type(show_legend) is not bool or type(runtime) is not bool
                or type(logs) is not bool or type(out) is not bool or type(run) is not bool): raise TypeError
        except TypeError: self._inv_args(__class__.__name__, self.data_balance_visualization.__name__, out = out)
        else:
            if run is False: self._error(self._lock_user, out = out); return None  # Блокировка выполнения

            if runtime: self._r_start()

            try: self.keys_stats.insert(0, self.keys_dataset[2])
            except (AttributeError, IndexError, TypeError): self._other_error(self._som_ww, out = out)
            except Exception: self._other_error(self._unknown_err, out = out)
            else:
                self._stats_files = dict(zip(self.keys_stats, [[] for _ in range(0, len(self.keys_stats))]))

                # График подсчета количества экземпляров в каждом классе
                if self._countplot(1, 1, show_legend, out, self._df_files) is True:
                    self._df_stats_files = pd.DataFrame.from_dict(
                        data = self._stats_files, orient = 'index'
                    ).transpose()
                    self._df_stats_files.set_index([self.keys_dataset[2]], inplace = True)  # Установка индекса

                    try:
                        # Минимальное допустимое значение для train_size
                        self._min_train_size = int(self._df_stats_files.query(
                            '{} > 0'.format(self.keys_stats[2])
                        )[self.keys_stats[2]].min() - 2)
                    except KeyError: self._other_error(self._som_ww, out = out)
                    except Exception: self._other_error(self._unknown_err, out = out)
                    else:
                        # Отображение
                        if show_df and out: display(self._df_stats_files.iloc[0:self.num_to_df_display, :])

                        if logs is True:
                            # Текущее время для лог файла
                            # см. datetime.fromtimestamp()
                            curr_ts = str(datetime.now().timestamp()).replace('.', '_')

                            # Сохранение LOG
                            res_save_logs = self._save_logs(
                                self._df_stats_files,
                                self.data_balance_visualization.__name__ + '_' + curr_ts)

                            if res_save_logs is True: self._info_true(self._logs_save_true, out = out)
            finally:
                if runtime: self._r_end(out = out)

# ######################################################################################################################
# Для легенд
# ######################################################################################################################
class TextHandler(HandlerBase):
    def create_artists(self, legend, tup, xdescent, ydescent, width, height, fontsize, trans):
        tx = Text(
            width / 1.3, height / 3, tup[0], fontsize = fontsize, ha = 'center', va = 'center', color = tup[1],
            fontweight = 'bold'
        )

        return [tx]