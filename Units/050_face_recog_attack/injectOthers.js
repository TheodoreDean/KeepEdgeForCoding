/**
 * 合并版脚本：视频注入 + 活体拦截 + 相似度劫持
 * 适用场景：KbyAI FaceSDK
 */

Java.perform(function () {
    // ===== 1. 配置项 =====
    const CONFIG = {
        width: 1280,
        height: 720,
        yuvPath: "/data/local/tmp/test10.yuv",
        forceRotation: 270 
    };

    var targetSDK = "com.kbyai.facesdk.FaceSDK";
    var targetBox = "com.kbyai.facesdk.FaceBox";
    var targetProcessor = "com.kbyai.facerecognition.CameraActivityKt$FaceFrameProcessor";

    var sdkHooked = false;
    var boxHooked = false;
    var videoHooked = false;
    var fakeFrame = null;

    console.log("[+] 脚本启动：正在预加载 YUV 数据并等待类加载...");

    // ===== 2. 预加载 YUV 数据 (使用标准 Java 类) =====
    function preloadYuvData() {
        try {
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
            console.log("[+] YUV 数据预加载成功。");
            return true;
        } catch (e) {
            console.log("[!] YUV 预加载失败: " + e);
            return false;
        }
    }

    // ===== 3. 核心 Hook 逻辑函数 =====

    // Hook 活体分值 (FaceBox)
    function hookFaceBox(loader) {
        try {
            Java.classFactory.loader = loader;
            var FaceBox = Java.use(targetBox);
            FaceBox.$init.overloads.forEach(function (overload) {
                overload.implementation = function () {
                    this.$init.apply(this, arguments);
                    try {
                        this.liveness.value = 1.0;
                        console.log("[✓] FaceBox 活体已锁定: 1.0");
                    } catch (e) {
                        // 混淆兜底逻辑
                        var fields = this.getClass().getDeclaredFields();
                        for (var i = 0; i < fields.length; i++) {
                            fields[i].setAccessible(true);
                            if (fields[i].getType().toString() === "float") {
                                var name = fields[i].getName();
                                if (name.includes("live") || name.includes("score")) {
                                    fields[i].setFloat(this, 1.0);
                                }
                            }
                        }
                    }
                };
            });
            boxHooked = true;
        } catch (e) { }
    }

    // Hook 相似度计算 (FaceSDK)
    function hookFaceSDK(loader) {
        try {
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
            sdkHooked = true;
        } catch (e) { }
    }

    // Hook 视频注入 (FaceFrameProcessor)
    function hookVideoInjection(loader) {
        try {
            Java.classFactory.loader = loader;
            var FaceFrameProcessor = Java.use(targetProcessor);
            var processMethod = FaceFrameProcessor.process.overload("io.fotoapparat.preview.Frame");

            processMethod.implementation = function (originalFrame) {
                try {
                    var activity = this.this$0.value;
                    var isRecognized = false;
                    
                    // 状态检查
                    if (activity.getRecognized) {
                        isRecognized = activity.getRecognized();
                    } else if (activity.recognized) {
                        isRecognized = activity.recognized.value;
                    }

                    if (isRecognized === true) return;

                    // 注入预加载的 fakeFrame
                    if (fakeFrame) {
                        processMethod.call(this, fakeFrame);
                    } else {
                        processMethod.call(this, originalFrame);
                    }
                } catch (err) {
                    processMethod.call(this, fakeFrame || originalFrame);
                }
            };
            videoHooked = true;
            console.log("[+++] 视频注入逻辑已挂载。");
        } catch (e) { }
    }

    // ===== 4. 自动化探测循环 =====
    
    // 首先执行一次预加载
    preloadYuvData();

    var checkTimer = setInterval(function () {
        if (sdkHooked && boxHooked && videoHooked) {
            console.log("[*] 所有目标 (Video/Liveness/Similarity) 已成功 Hook，停止探测。");
            clearInterval(checkTimer);
            return;
        }

        Java.enumerateClassLoaders({
            onMatch: function (loader) {
                try {
                    if (!boxHooked && loader.findClass(targetBox)) {
                        hookFaceBox(loader);
                        console.log("[*] 找到 FaceBox 类并注入。");
                    }
                    if (!sdkHooked && loader.findClass(targetSDK)) {
                        hookFaceSDK(loader);
                        console.log("[*] 找到 FaceSDK 类并注入。");
                    }
                    if (!videoHooked && loader.findClass(targetProcessor)) {
                        hookVideoInjection(loader);
                        console.log("[*] 找到 FaceFrameProcessor 类并注入。");
                    }
                } catch (e) { }
            },
            onComplete: function () { }
        });
    }, 1000); 
});
