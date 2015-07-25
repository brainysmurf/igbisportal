// Defines classes we'll use on our splash page
(function (Splash) {

'use strict';

var Button = function (first, second, third) {
	var name, link, icon;

	if (second ===undefined && third==undefined) {
		var $sel;		
		if (first instanceof jQuery) {
			$sel = first;
		} else {
			$sel = $(first);
		}
		this.$sel = $sel;
		this.$subSel = $sel.find('ul');
		this.name = $sel.data('name');
		this.link = $sel.data('link');
		this.icon = $sel.data('icon');
		this.count = $sel.data('count');

		// TODO: here, use the templating scheme to determine submenuString
		// Which we'll pass to jbox

	} else if (first && second && third) {
		this.name = first;
		this.link = second;
		this.icon = third;
		this.$sel = undefined;
		this.$subSel = undefined;
		this.submenuString = undefined;
		// What about the count?
	}
}

var Tab = function(first) {
	var $sel;		
	if (first instanceof jQuery) {
		$sel = first;
	} else {
		$sel = $(first);
	}
	this.buttons = [];
	this.$liSelector = $sel;
	this.name = $sel.data('name');
	this.$divSelector = $('#'+this.name);
	this.$gridSelector = this.$divSelector.find('.grid');
	// Now see about the buttons
	var $button;

	this.$gridSelector.find('.buttonContainer').each(function (index, button) {
		var $button = $(button);
		this.loadButton(button);
		$button.remove();
		this.$gridSelector.mustache('buttonContainerTemplate', new Button(button), {method:'append'})
	}.bind(this));
}

Tab.prototype.loadButton = function (button) {
	this.buttons.push(button);
	return this;
}

Tab.prototype.addButton = function (button) {
	this.$gridSelector.mustache('buttonContainerTemplate', button, {method:'append'});
	this.updateGrid();
}

Tab.prototype.updateGrid = function () {
	console.log('updating with gridly');
	this.$gridSelector.gridly(Splash.config.gridly);
	this.$gridSelector.gridly('draggable', 'off');
}

var Tabs = function(first) {
	// reads in any existing tabs (and buttons)	
	console.log(arguments);
	if (first === undefined) {
		console.log('Need to pass in something for tabs...');
	}
	var $sel;
	if (first instanceof jQuery) {
		$sel = first;
	} else {
		$sel = $(first);
	}
	this.$sel = $sel;
	this.tabs = [];
	$sel.find('ul:first').find('li').each(function (index, item) {
		this.loadTab(item);
	}.bind(this));

	// init the grids
	this.forEachTab(function (tab) {
		tab.updateGrid();
	});

	// initing tabs last after grid operations works better
	$(Splash.config.tabsContainer).tabs(Splash.config.tabs);

}

Tabs.prototype.forEachTab = function (callback) {
	this.tabs.forEach(callback);
}

Tabs.prototype.loadTab = function (item) {
	this.tabs.push(new Tab(item));
}

Tabs.prototype.getTabByName = function (name) {
	var index = this.tabs.indexOf();
	return _.findWhere(this.tabs, {name: name});
}

Tabs.prototype.addNewButtonInTab = function(inTabName, buttonName, buttonLink, buttonIcon) {
	var button = new Button(buttonName, buttonLink, buttonIcon);
	this.getTabByName(inTabName).addButton(button);
}

// Actually run the loading mechanism and make it available for reference in other areas
Splash.singletonTabs = new Tabs(Splash.config.tabsContainer);

Splash.tabs = function() {
	return Splash.singletonTabs;
}

}(this.Splash));