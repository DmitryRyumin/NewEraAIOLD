# NewEraAI - новая эра искусственного интеллекта 

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