Java.perform(function () {
	Java.use('android.app.SharedPreferencesImpl$EditorImpl').putString.overload('java.lang.String', 'java.lang.String').implementation = function(k, v) {
    	console.log('[SharedPreferences putString]', k, '=', v);
    	return this.putString(k, v);
  };
	 Java.use('android.app.SharedPreferencesImpl').getString.overload('java.lang.String', 'java.lang.String').implementation = function(k, v) {
	console.log('[SharedPreferences getString]', k, '=', this.getString(k,v));
        return this.getString(k, v);
  };
});

