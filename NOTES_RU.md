# NewEraAI - новая эра искусственного интеллекта 

## 17 апреля 2021 года

> `1.0.3`

<h4><span style="color:#008000;">Что нового</span></h4>

- Добавлена возможность фильтрации директорий, которые не будут включены в выборку сбалансированности (настройка ядра: `ignore_dirs`)

> `1.0.2`

<h4><span style="color:#008000;">Что нового</span></h4>

- Добавлена возможность фильтрации директорий, которые будут включены в выборку сбалансированности (настройка ядра: `filter_dirs`)

> `1.0.1`

<h4><span style="color:#008000;">Что нового</span></h4>

- Добавлено отображение библиотеки `seaborn` в методе `libs_vers` класса [Core](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/core/core.py)

> `1.0.0`

<h4><span style="color:#008000;">Что нового</span></h4>

- Метод `media_info` [Core](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/core/core.py) отображает дополнительные meta данные (`minimum_frame_rate`, `maximum_frame_rate`) из медиафайлов
- Расширены собственные [исключения](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/core/exceptions.py) для определенных ошибок, которые могут возникнуть в процессе работы
- Добавлена возможность обработки видео с разных ракурсов
- Новый класс [Statistics](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/statistics.py) для отображения статистических данных

<h4><span style="color:#247CB4;">Изменения</span></h4>

- Обновлены зависимости

<h4><span style="color:#DB534F;">Исправления</span></h4>

- Исправлены опечатки

## 10 апреля 2021 года

> `1.0.0-rc5`

<h4><span style="color:#008000;">Что нового</span></h4>

- Добавлена возможность распознавания английского языка
- Добавлена возможность автоматического создания директорий под фильтр распознавания речи (аргумент `create_folder_filter_sr` в методе `vad` класса [Audio](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/audio.py))

> `1.0.0-rc4`

<h4><span style="color:#008000;">Что нового</span></h4>

- Добавлена возможность блокировки выполнения всех внешних методов (аргумент `run`)
- Новый метод `show_notebook_history_output` класса [Core](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/core/core.py) для отображения последнего результата из истории вывода в ячейках Jupyter
- Новый метод `media_info` [Core](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/core/core.py) для получения и отображения meta данных из медиафайлов
- Добавлены собственные [исключения](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/core/exceptions.py) для определенных ошибок, которые могут возникнуть в процессе работы
- Новый класс [Download](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/download.py) для загрузки файлов из URL
- Новый класс [Unzip](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/unzip.py) для разархивирования архивов

<h4><span style="color:#247CB4;">Изменения</span></h4>

- Класс распознавания речи [Speech](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/speech.py) может функционировать отдельно от класса [Audio](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/audio.py)
- Улучшена функциональность класса [Audio](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/audio.py) за счет анализа и обработки аудиоинформации без ее предварительного сохранения на локальном хранилище
- Язык по умолчанию изменен с `русский` на `английский`
- Обновлены зависимости

<h4><span style="color:#DB534F;">Исправления</span></h4>

- Исправлены опечатки

## 24 марта 2021 года

> `1.0.0-rc3`

<h4><span style="color:#DB534F;">Исправления</span></h4>

- Исправлена ошибка в методе `vad` класса [Audio](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/audio.py), которая вызывала исключение `ZeroDivisionError` при некорректном вводе значения аргумента `trig_sum`

> `1.0.0-rc2`

<h4><span style="color:#008000;">Что нового</span></h4>

- Добавлено подавление предупреждений (`UserWarning`, `FutureWarning`)
- Добавлены аргументы (`type_encode`, `crf_value`, `presets_crf_encode`) в метод `vad` класса [Audio](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/audio.py)

<h4><span style="color:#247CB4;">Изменения</span></h4>

- Индикатор выполнения внутри метода `vad` класса [Audio](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/audio.py) отображает, как общий прогресс анализа аудиодорожек, так и прогресс формирования видеофрагментов по временным меткам, которые получены с помощью VAD

<h4><span style="color:#DB534F;">Исправления</span></h4>

- Исправлена ошибка в методе `vad` класса [Audio](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/audio.py), которая формировала видеофрагменты с пустыми кадрами в конце

> Первая версия пакета `1.0.0-rc1`