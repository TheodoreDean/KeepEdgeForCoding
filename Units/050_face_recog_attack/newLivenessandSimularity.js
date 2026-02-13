/**
 * KbyAI FaceSDK 深度拦截脚本 (自动化重试版)
 * 解决问题：无需手动保存二次，脚本自动等待类加载并注入
 */

Java.perform(function () {
    console.log("[+] 脚本启动：正在潜伏等待 FaceSDK 类加载...");

    var targetSDK = "com.kbyai.facesdk.FaceSDK";
    var targetBox = "com.kbyai.facesdk.FaceBox";
    
    var sdkHooked = false;
    var boxHooked = false;

    // --- 核心 Hook 逻辑函数 ---

    function hookFaceBox(loader) {
        try {
            Java.classFactory.loader = loader;
            var FaceBox = Java.use(targetBox);
            
            FaceBox.$init.overloads.forEach(function (overload) {
                overload.implementation = function () {
                    this.$init.apply(this, arguments);
                    try {
                        this.liveness.value = 1.0;
                        console.log("[✓] FaceBox 实例创建：liveness 已锁定为 1.0");
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
            console.log("[+++] FaceBox 活体拦截注入成功！");
        } catch (e) { }
    }

    function hookFaceSDK(loader) {
        try {
            Java.classFactory.loader = loader;
            var FaceSDK = Java.use(targetSDK);
            
            // 劫持相似度计算的所有重载
            var simOverloads = FaceSDK.similarityCalculation.overloads;
            simOverloads.forEach(function (overload) {
                overload.implementation = function () {
                    var originalScore = this.similarityCalculation.apply(this, arguments);
                    console.log("[!] Similarity 拦截！原始分: " + originalScore.toFixed(4) + " -> 强制修改为: 1.0");
                    return 1.0;
                };
            });

            // 劫持检测回调（可选）
            FaceSDK.faceDetection.implementation = function (bitmap, param) {
                return this.faceDetection(bitmap, param);
            };

            sdkHooked = true;
            console.log("[+++] FaceSDK 比对拦截注入成功！");
        } catch (e) { }
    }

    // --- 自动化探测逻辑 ---

    var checkTimer = setInterval(function () {
        if (sdkHooked && boxHooked) {
            console.log("[*] 所有目标已成功 Hook，停止探测。");
            clearInterval(checkTimer);
            return;
        }

        // 遍历所有类加载器
        Java.enumerateClassLoaders({
            onMatch: function (loader) {
                try {
                    // 检查当前加载器是否能看到目标类
                    if (!boxHooked && loader.findClass(targetBox)) {
                        hookFaceBox(loader);
			console.log("[*]  Hook box");

                    }
                    if (!sdkHooked && loader.findClass(targetSDK)) {
                        hookFaceSDK(loader);
			console.log("[*]  Hook similiarity");

                    }
                } catch (e) { }
            },
            onComplete: function () { }
        });
    }, 1000); // 每秒检查一次内存，直到找到类为止

});