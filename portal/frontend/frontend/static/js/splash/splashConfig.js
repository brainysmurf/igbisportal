// Defines classes we'll use on our splash page
(function (Splash) {

'use strict';

// Actually run the loading mechanism and make it available for reference in other areas
Splash.config = {

	tabsContainer: '#tabs_holder',

	gridly: {
	    base: 40,
	    gutter: 20,
	    columns: 16,
	    draggable: {
	    	zIndex: 800,
	    	selector: '> .buttonContainer'
	    }
	},

	tabs: {
		active: 0,
		collapsible: false,
		disabled:false,
		// event: "mouseover",
		show: { effect: "fade", duration: 200 }
	},

	jbox: {}
},

Splash.JBoxes = [],

Splash.utils = {
	// various javascript-specific functions we need

	hexc: function (rgb) {
		rgb = rgb.match(/^rgba?[\s+]?\([\s+]?(\d+)[\s+]?,[\s+]?(\d+)[\s+]?,[\s+]?(\d+)[\s+]?/i);
		return (rgb && rgb.length === 4) ? "#" +
		  ("0" + parseInt(rgb[1],10).toString(16)).slice(-2) +
		  ("0" + parseInt(rgb[2],10).toString(16)).slice(-2) +
		  ("0" + parseInt(rgb[3],10).toString(16)).slice(-2) : '';
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