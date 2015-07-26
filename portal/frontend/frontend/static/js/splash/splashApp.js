(function (Splash) {
	'use strict';

	Splash.app = function () {
		// set up the app as necessary
		Splash.tabs();
		Splash.defineTriggers();
		Splash.defineExtentions();
	}

}(this.Splash));

this.Splash.app();