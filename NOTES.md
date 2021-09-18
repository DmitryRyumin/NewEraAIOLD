# NewEraAI - New Era Artificial Intelligence

## September 18, 2021

> `1.0.4`

<h4><span style="color:#247CB4;">Changes</span></h4>

- Updated `small` model for Russian language recognition (version: `0.15`)
- Updated require packages

<h4><span style="color:#DB534F;">Fixed bugs</span></h4>

- Fixed a bug in the `vosk_sr` method of the [Speech](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/speech.py) class and the `vad` method of the [Audio](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/audio.py) class, which did not allow speech recognition in cases where the audio or video file lacked information distinguishable from speech (silence, noise, knocking, etc.)
- Fixed typos

## April 17, 2021

> `1.0.3`

<h4><span style="color:#008000;">What's new</span></h4>

- Added the ability to filter directories that will not be included in the balance selection (kernel setting: `ignore_dirs`)

> `1.0.2`

<h4><span style="color:#008000;">What's new</span></h4>

- Added the ability to filter directories that will be included in the balance selection (kernel setting: `filter_dirs`)

> `1.0.1`

<h4><span style="color:#008000;">What's new</span></h4>

- Added display of the `seaborn` library in the `libs_vers` method of the class [Core](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/core/core.py)

> `1.0.0`

<h4><span style="color:#008000;">What's new</span></h4>

- Method `media_info` [Core](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/core/core.py) displays additional meta data (`minimum_frame_rate`, `maximum_frame_rate`) from media files
- Expanded native [exceptions](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/core/exceptions.py) for certain errors that may occur during work
- Added the ability to process videos from different angles
- New class [Statistics](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/statistics.py) to display statistics

<h4><span style="color:#247CB4;">Changes</span></h4>

- Updated require packages

<h4><span style="color:#DB534F;">Fixed bugs</span></h4>

- Fixed typos

## April 10, 2021

> `1.0.0-rc5`

<h4><span style="color:#008000;">What's new</span></h4>

- Added the ability to recognize the English language
- Added the ability to automatically create directories for the speech recognition filter (argument `create_folder_filter_sr` in the `vad` method of the [Audio](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/audio.py) class)

> `1.0.0-rc4`

<h4><span style="color:#008000;">What's new</span></h4>

- Added the ability to block the execution of all external methods (argument `run`)
- New method `show_notebook_history_output` of the [Core](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/core/core.py) class to display the last result from the output history in Jupyter cells
- New method `media_info` of the [Core](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/core/core.py) class for get and display meta data from media files
- Added custom [Exceptions](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/core/exceptions.py) for certain errors that may occur during work
- New class [Download](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/download.py) for download files from URL
- New class [Unzip](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/unzip.py) for unzipping archives

<h4><span style="color:#247CB4;">Changes</span></h4>

- Speech recognition class [Speech](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/speech.py) can function separately from the class [Audio](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/audio.py)
- Improved the functionality of the [Audio](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/audio.py) class by analyzing and processing audio information without first saving it to local storage
- Default language changed from `Russian` to `English`
- Updated require packages

<h4><span style="color:#DB534F;">Fixed bugs</span></h4>

- Fixed typos

## March 24, 2021

> `1.0.0-rc3`

<h4><span style="color:#DB534F;">Fixed bugs</span></h4>

- Fixed a bug in the `vad` method of the [Audio](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/audio.py) class, which generate the `ZeroDivisionError` exception when the argument `trig_sum` value was entered incorrectly

> `1.0.0-rc2`

<h4><span style="color:#008000;">What's new</span></h4>

- Added warning suppression (`UserWarning`, `FutureWarning`)
- Added arguments (`type_encode`, `crf_value`, `presets_crf_encode`) to the `vad` method of the [Audio](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/audio.py) class

<h4><span style="color:#247CB4;">Changes</span></h4>

- The progress bar inside the `vad` method of the [Audio](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/audio.py) class displays both the overall progress of the analysis of audio tracks, and the progress of the formation video clips by time stamps, which were obtained using VAD

<h4><span style="color:#DB534F;">Fixed bugs</span></h4>

- Fixed a bug in the `vad` method of the [Audio](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/audio.py) class which generated video fragments with empty frames at the end

> First version of the package `1.0.0-rc1`