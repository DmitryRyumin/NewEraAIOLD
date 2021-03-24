# NewEraAI - New Era Artificial Intelligence

## March 24, 2021

> `1.0.0-rc2`

<h4><span style="color:#008000;">What's new</span></h4>

- Added warning suppression (`UserWarning`, `FutureWarning`)
- Added arguments (`type_encode`, `crf_value` `presets_crf_encode`) to the `vad` method of the [Audio](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/audio.py) class

<h4><span style="color:#247CB4;">Changes</span></h4>

- The progress bar inside the `vad` method of the [Audio](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/audio.py) class displays both the overall progress of the analysis of audio tracks, and the progress of the formation video clips by time stamps, which were obtained using VAD

<h4><span style="color:#DB534F;">Fixed bugs</span></h4>

- Fixed a bug in the `vad` method of the [Audio](https://github.com/DmitryRyumin/NewEraAI/blob/main/neweraai/modules/lab/audio.py) class which generated video fragments with empty frames at the end

> First version of the package `1.0.0-rc1`