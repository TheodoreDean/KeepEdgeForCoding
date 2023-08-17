Java.perform(function () {
//var be= Java.use("com.tuya.smart.sdk.platformtools.by");
//var instance = Java.use('com.vimin.hookClass').$new();

var be= Java.use("com.tuya.smart.home.sdk.bean.ActiveDmDeviceBean").$new();

//var FridaActivity3 = Java.use("com.github.androiddemo.Activity.FridaActivity3");
//console.log("static_bool_var:", FridaActivity3.static_bool_var.value);


send(typeof(be));
send("start")

console.log("start")
console.log("local key is ",be.localKey);


be.getLocalKey.implementation = function(){
    var localkey = this.localKey;
    console.log("enter")
    console.log("local key is ",localKey);
    return this.localKey;
};
send("end")
});
