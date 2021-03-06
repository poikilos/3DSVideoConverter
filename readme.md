# 3DSVideoConverter
<https://github.com/poikilos/3DSVideoConverter>

Convert side-by-side stereoscopic videos to 3DS stereoscopic video format!


## Related Projects
This is a fork of <https://github.com/jhheo/3DSVideoConverter>.

### 3DS homebrew apps
- https://github.com/Lectem/3Damnesic
- https://github.com/halcy/nordlicht19 (This demo has several uses of
  the 3DS screen but they are mostly related to realtime 3D rendering).

## Developer Notes

### Original Author's Notes

I made this SW after trying some converters for 3DS but i failed to
convert side by side videos to view stereoscopic with 3DS.

This software is a simple front end for FFMPEG.

Internally, It executes the following FFMPEG commands to convert a side
by side video clip:
```
ffmpeg -y -i original.mp4 -vcodec mjpeg -q:v 1 -r 20 -vf "scale=960:240, crop=480:240:0:0" -aspect 2:1 -acodec adpcm_ima_wav -ac 2 left.avi
ffmpeg -y -i original.mp4 -vcodec mjpeg -q:v 1 -r 20 -vf "scale=960:240, crop=480:240:480:0" -aspect 2:1 -acodec adpcm_ima_wav -ac 2 right.avi
ffmpeg -y -i left.avi -i right.avi -ss 00:00:00 -t 00:10:00 -vcodec mjpeg  -q:v 1 -r 20 -acodec adpcm_ima_wav -ac 2 -map 0:0 -map 0:1 -map 1:0 result.avi
```

If the video is not  side by side, then just:
```
ffmpeg -y -i original.mp4  -ss 00:00:00 -t 00:10:00 -vcodec mjpeg -q:v 1 -r 20  -vf scale=480:240 -aspect 2:1 -acodec adpcm_ima_wav -ac 2 result.avi
```

The converter writes output files NIN_0001.AVI ~ NIN_00XX.AVI under the
folder having the same name  with the input file name. the output files
cropped to have only 10 minutes, because 3DS can't play wrong video
clip.
