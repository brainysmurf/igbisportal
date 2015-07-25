// Defines classes we'll use on our splash page
(function (Splash) {

'use strict';

// Actually run the loading mechanism and make it available for reference in other areas
Splash.config = {
	tabsContainer: '#tabs_holder',

	gridly: {
	    base: 40,
	    gutter: 10,
	    columns: 18,
	    draggable: {
	    	zIndex: 10,
	    	selector: '> .buttonContainer'
	    }
	},

	tabs: {
		active: 0,
		collapsible: false,
		disabled:false,
		// event: "mouseover",
		show: { effect: "fade", duration: 200 }
	}
},

Splash.utils = {
	// various javascript-specific functions we need

	hexc: function (colorval) {
	    var parts = colorval.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
	    delete(parts[0]);
	    for (var i = 1; i <= 3; ++i) {
	        parts[i] = parseInt(parts[i]).toString(16);
	        if (parts[i].length == 1) parts[i] = '0' + parts[i];
	    }
	    return '#' + parts.join('').toUpperCase();
	},

	isValidURL: function (url) {
	    try {
	        var uri = new URI(url);
	        // URI has a scheme and a host
	        return (!!uri.scheme() && !!uri.host());
	    }
	    catch (e) {
	        // Malformed URI
	        return false;
	    }
	}

}

// Initializations

$.Mustache.addFromDom();



}(this.Splash = {} ));