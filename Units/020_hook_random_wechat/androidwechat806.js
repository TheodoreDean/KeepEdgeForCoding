Java.perform(function () {
var util= Java.use("com.tencent.mm.sdk.platformtools.Util");
send(typeof(util));
send(typeof(util.getIntRandom));
send("start")
util.getIntRandom.implementation = function(){
    var type = arguments[0];
    send("start")
    send("type="+type);
    return 5;
};
send("end")
});
