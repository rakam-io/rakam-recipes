var api_url = "https://www.google.com/trends/api/autocomplete/";
var cache = {};
var mapper = function(eventHandler, requestParams, sourceAddress, responseHeaders, parameters) {
    var events = eventHandler.events();
    while(events.hasNext()) {
        var event = events.next();
        if(event.collection() != "google_search" || !event.get("search_term")) {
            continue;
        }
      
        var value = cache[event.get("search_term")];
        if(value === undefined) {
          var response = http.get(api_url + event.get("search_term") + "?hl=en-EN&tz=-180").send();
          if(response.getStatusCode() != 200) {
              return;
          }
          var category_value = JSON.parse(response.getResponseBody().substring(6)).default.topics;
          if(category_value && category_value.length > 0) {
            var value = category_value[0];
          } else {
            value = null;
          }
          
          cache[event.get("search_term")] = value;
        }
      
        if(value) {
        	event.set("category_mid", value.mid);
        	event.set("category_title", value.title);
        	event.set("category_type", value.type);
        }
    }
}
