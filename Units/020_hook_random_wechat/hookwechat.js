Java.perform(function () {
var be= Java.use("com.tencent.mm.sdk.platformtools.by");
send(typeof(be));
send(typeof(be.jV));
send("start")
be.jV.implementation = function(){
    var type = arguments[0];
    send("start")
    send("type="+type);
    return 5;
};
send("end")
});
