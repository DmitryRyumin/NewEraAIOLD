# NewEraAI - New Era Artificial Intelligence

## April 10, 2021

> `1.0.0-rc4`

<h4><span style="color:#008000;">What's new</span></h4>

- Added the ability to block the execution of all external methods (argument `run`)
- New method `_neai.show_notebook_history_output()` to display the last result from the output history in Jupyter cells
- New method `_neai.media_info(...)` for get and display meta data from media files
- Added custom [exceptions](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/core/exceptions.py) for certain errors that may occur during work
- New class [Download](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/download.py) for download files from URL
- New class [Unzip](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/unzip.py) for unzipping archives

<h4><span style="color:#247CB4;">Changes</span></h4>

- Speech recognition class [Speech](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/speech.py) can function separately from the class [Audio](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/audio.py)
- Improved the functionality of the [Audio](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/audio.py) class by analyzing and processing audio information without first saving it to local storage
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