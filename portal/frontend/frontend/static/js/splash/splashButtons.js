// Defines classes we'll use on our splash page
(function (Splash) {

'use strict';

var Button = function (first, second, third) {
	var name, link, icon;
	if (arguments.length == 1) {
		var $sel;		
		if (first instanceof jQuery) {
			$sel = first;
		} else {
			$sel = $(first);
		}
		this.$sel = $sel;
		this.$subSel = $sel.find('ul');
		this.name = $sel.data('name');
		this.id = 'splashButton'+Button.counter++;
		this.link = $sel.data('link');
		this.icon = $sel.data('icon');
		this.count = $sel.data('count');

		// Loop through all the submenus, making items array
		var items = [];

		$sel.find('.splashSubMenu').each(function (index, liItem) {
			var $liItem = $(liItem);
			var item = {isKindDiver:false, isKindNormal:false, isKindPlaceholer:false};
			item.display = $liItem.data('display');
			var url = $liItem.data('url');
			if (item.display === 'hr') {
				item.isKindDivider = true;
			} else if (item.display === 'placeholder') {
				item.isKindPlaceholder = true;
			} else {
				item.isKindNormal = true;
			}
			items.push(item);
		});

		if (items.length > 0) {
			var subMenuItems = $.Mustache.render('submenuItemTemplate', {items:items});
			
			// Save it for retrieval later
			var thisTitle = '<a class="submenuTitle" href="'+ this.link + '">&nbsp;' + this.name + '</a>';
			var jbox = {
				content: subMenuItems, 
				selector: '#' + this.id,
				title:thisTitle
			};

	    	Splash.JBoxes.push(jbox);
	    }

	} else if (arguments.length == 3) {
		this.name = first;
		this.link = second;
		this.icon = third;
		this.$sel = undefined;
		this.$subSel = undefined;
		this.submenuString = undefined;
		// What about the count?
	}
}

Button.counter = 0;

Button.prototype.left = function () {
	return parseInt($(this.selector).css("left"),10);
}

Button.prototype.right = function () {
	return parseInt($(this.selector).css("right"),10);
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
	this.$gridSelector.gridly(Splash.config.gridly);
	this.$gridSelector.gridly('draggable', 'off');
}

var Tabs = function(first) {
	// reads in any existing tabs (and buttons)	
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

	this.processJBoxes();
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

Tabs.prototype.processJBoxes = function () {
	$.each(Splash.JBoxes, function (index, item) {
		item.jbox = $(item.selector).jBox('Tooltip', {
			position: {
				y: item.left,
				x: item.right,
			},
			delayOpen: 400,
			outside: 'x',
			title: item.title,
			closeOnMouseleave: true,
			content: item.content
		});
	});
}

Tabs.prototype.disableJBoxes = function () {
	$.each(Splash.JBoxes, function (index, item) {
		item.jbox.disable();
	});
}

Tabs.prototype.enableJBoxes = function () {
	$.each(Splash.JBoxes, function (index, item) {
		item.jbox.enable();
	});
}

// Actually run the loading mechanism and make it available for reference in other areas
Splash.singletonTabs = new Tabs(Splash.config.tabsContainer);

Splash.tabs = function() {
	return Splash.singletonTabs;
}

}(this.Splash));