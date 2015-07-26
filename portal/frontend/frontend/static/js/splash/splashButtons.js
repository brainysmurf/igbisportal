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
		this.$subSel = $sel.find('ul'); // unused...
		this.name = $sel.data('name');
		this.id = 'splashButton'+Button.counter++;
		this.idSelector = '#'+this.id;
		this.link = $sel.data('link');
		this.icon = $sel.data('icon');
		this.count = $sel.data('count');

		// Loop through all the submenus, making items array
		var items = [];
		var $liItem, item;

		$sel.find('.splashSubMenu').each(function (index, liItem) {
			$liItem = $(liItem);
			item = {isKindDivider:false, isKindNormal:false, isKindPlaceholer:false};
			item.display = $liItem.data('display');
			item.url = $liItem.data('url');
			if (item.display === 'hr') {
				item.isKindDivider = true;
			} else if (item.display === 'placeholder') {
				item.isKindPlaceholder = true;
			} else {
				item.isKindNormal = true;
			}
			items.push(item);
		});

		this.subMenuItems = items;


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

Button.prototype.processJBox = function () {
	if (this.subMenuItems.length > 0) {
		$(this.idSelector).mustache('submenuItemTemplate', {items:this.subMenuItems}, {method:'append'});
		var thisTitle = '<a class="submenuTitle" href="'+ this.link + '">' + this.name + '</a>';

		// attach jbox to the target element and save in the button object
		this.jbox = $(this.idSelector).jBox('Tooltip', {
			constructOnInit: true,
			position: {
				y: $(this.idSelector).left,
				x: $(this.idSelector).right,
			},
			delayOpen: 400,
			outside: 'x',
			title: thisTitle,
			closeOnMouseleave: true,
			content: $(this.idSelector).find('ul'),
		});
    } else {
    	this.jbox = undefined;
    }
}

Button.counter = 0;

Button.prototype.left = function () {
	return parseInt(this.$idSelector.css("left"), 10);
}

Button.prototype.right = function () {
	return parseInt(this.$idSelector.css("right"), 10);
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
		// Make new button object with existing data
		var newButton = new Button(button);

		// Remove the old button from the DOM
		$(button).remove();

		// Add newButton to our object structure
		this.loadButton(newButton);

		// Add newButton to the DOM
		this.$gridSelector.mustache('buttonContainerTemplate', newButton, {method:'append'});

		// Read in submenu information, jbox processing
		newButton.processJBox();
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

	// initing tabs last aftetr grid operations works better
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

// Tabs.prototype.processJBoxes = function () {
// 	$.each(Splash.JBoxes, function (index, item) {
// 		console.log(item);
// 		item.jbox = item.selector.jBox('Tooltip', {
// 			position: {
// 				y: item.left,
// 				x: item.right,
// 			},
// 			delayOpen: 400,
// 			outside: 'x',
// 			title: item.title,
// 			closeOnMouseleave: true,
// 			content: this.content,
// 		});
// 	});
// }

Tabs.prototype.disableJBoxes = function () {
	$.each(this.tabs, function (index, tab) {
		$.each(tab.buttons, function (index, button) {
			if (button.jbox != undefined) {
				button.jbox.disable();
			}
		});
	});
}

Tabs.prototype.enableJBoxes = function () {
	$.each(this.tabs, function (index, tab) {
		$.each(tab.buttons, function (index, button) {
			if (button.jbox != undefined) {
				button.jbox.enable();
			}
		});
	});
}

// Actually run the loading mechanism and make it available for reference in other areas
Splash.singletonTabs = new Tabs(Splash.config.tabsContainer);

Splash.tabs = function() {
	return Splash.singletonTabs;
}

}(this.Splash));