// Defines classes we'll use on our splash page
(function (Splash) {

'use strict';

var Button = function (name, color, link, icon) {
	if (arguments.length == 1) {
		if (name instanceof jQuery) {
			this.$sel = name;
		} else {
			this.$sel = $(name);
		}
		this.name = this.$sel.data('name');
		if (!this.$sel.attr('id')) {
			this.id = 'splashButton'+Button.counter++;			
		} else {
			this.id = this.$sel.attr('id');
		}
		this.idSelector = '#'+this.id;
		this.link = this.$sel.data('link');
		this.icon = this.$sel.data('icon');
		this.count = this.$sel.data('count');
		this.color = this.$sel.data('color');

		// Loop through all the submenus, making items array
		var items = [];
		var $liItem, item;

		this.$sel.find('.splashSubMenu').each(function (index, liItem) {
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

	} else if (arguments.length == 4) {
		// It's spelled out, must be a new one
		this.name = name;
		this.color = color;
		this.link = link;
		this.icon = icon;
		this.$sel = undefined;
		this.submenuString = undefined;
		this.id = 'splashButton'+Button.counter++;
		this.idSelector = '#'+this.id
	}
};

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
};

Button.counter = 0;

Button.prototype.left = function () {
	return parseInt(this.$idSelector.css("left"), 10);
};

Button.prototype.right = function () {
	return parseInt(this.$idSelector.css("right"), 10);
};

Button.prototype.updateDom = function () {
	$(this.idSelector).find('.buttonTitle').text(this.name);
	$(this.idSelector).find('a').attr('href', this.link);
	$(this.idSelector).alterClass('color*', 'color'+this.color);
	$(this.idSelector).find('.buttonIcon > i').alterClass('fa-*', 'fa-'+this.icon);
};

Button.prototype.updateWithValues = function (name, color, link, icon) {
	this.name = name;
	this.color = color;
	this.link = link;
	this.icon = icon;
	this.updateDom();
};

var Tab = function(name) {
	this.buttons = [];

	if (typeof name != "string") {
		if (name instanceof jQuery) {
			$sel = name;
		} else {
			$sel = $(name);
		}
		this.name = $sel.data('name');
		this.id = this.name.replace(/ /g, '_');
		this.becameDom();

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

	} else {
		var $sel = undefined;
		this.name = name;
		this.id = this.name.replace(/ /g, '_');		
	}

};

Tab.prototype.becameDom = function () {
	// Called when ensured that we are in the dom
	this.$divSelector = $('#'+this.name);
	this.$gridSelector = this.$divSelector.find('.grid');
};

Tab.prototype.loadButton = function (button) {
	this.buttons.push(button);
	return this;
};

Tab.prototype.addButton = function (name, color, link, icon) {
	var button;
	if (arguments == 1) {
		button = name;
	} else {
		button = new Button(name, color, link, icon)
	}
	this.$gridSelector.mustache('buttonContainerTemplate', button, {method:'append'});
	this.loadButton(button);
	this.updateGrid();
};

Tab.prototype.initGrid = function () {
	this.$gridSelector.gridly(Splash.config.gridly);
	this.$gridSelector.gridly('draggable', 'off');
};

Tab.prototype.updateGrid = function () {
	this.$gridSelector.gridly('layout');	
};

var Tabs = function(first) {

	// Constructor for Tabs. Kicks off the process of loading up tabs and buttons

	var $sel;
	if (first instanceof jQuery) {
		$sel = first;
	} else {
		$sel = $(first);
	}
	this.$tabsContainer = $sel;
	this.tabs = [];
	$sel.find('ul:first').find('li').each(function (index, item) {
		this.loadTab(new Tab(item));
	}.bind(this));

	// init the grids
	this.forEachTab(function (tab) {
		tab.initGrid();
	});

	// initing tabs last aftetr grid operations works better
	$(Splash.config.tabsContainer).tabs(Splash.config.tabs);
};

Tabs.currentTabId = undefined;  // have to do something at init time to get this

Tabs.prototype.forEachTab = function (callback) {
	this.tabs.forEach(callback);
};

Tabs.prototype.loadTab = function (item) {
	this.tabs.push(item);
};

Tabs.prototype.getTabByName = function (name) {
	var index = this.tabs.indexOf();
	return _.findWhere(this.tabs, {name: name});
};

Tabs.prototype.addNewButtonInTab = function(inTabName, buttonName, buttonColor, buttonLink, buttonIcon) {
	var button = new Button(buttonName, buttonColor, buttonLink, buttonIcon);
	this.getTabByName(inTabName).addButton(buttonName, buttonColor, buttonLink, buttonIcon);
};

Tabs.prototype.disableJBoxes = function () {
	$.each(this.tabs, function (index, tab) {
		$.each(tab.buttons, function (index, button) {
			if (button.jbox != undefined) {
				button.jbox.disable();
			}
		});
	});
};

Tabs.prototype.enableJBoxes = function () {
	$.each(this.tabs, function (index, tab) {
		$.each(tab.buttons, function (index, button) {
			if (button.jbox != undefined) {
				button.jbox.enable();
			}
		});
	});
};

Tabs.prototype.addTab = function (name) {
	// Adds to the model and the DOM
	

  	// TODO: Add target depending on user setting? to be consistent?
  	// Make this a template, too, right?
  	// Add the tab in the tab list to the DOM
  	var newTab = new Tab(name);

	var $lastLi = this.$tabsContainer.find('ul > li:last-child');
  	$lastLi.mustache('newTabLiTemplate', newTab, {method:'after'});

  	var $lastDiv = this.$tabsContainer.children('div:last-child');
  	$lastDiv.mustache('newTabTemplate', newTab, {method:'after'});

  	newTab.becameDom();

  	this.$tabsContainer.tabs("refresh");
  	// var index = $('#tabs_holder a[href="#'+ newTabNameIndex + '"]').parent().index();
  	// $tabs.tabs('option', 'active', index);

	//$newTab.find('.grid').gridly(Splash.config.gridly);  //initGrid?
	newTab.initGrid();
	this.loadTab(newTab);
};

Tabs.prototype.addButtonToCurrentTab = function (name, color, link, icon) {
	// Adds to the current tab...
	var button = new Button(name, color, link, icon);
	var tab = this.getCurrentTab();
	tab.$gridSelector.mustache('buttonContainerTemplate', button, {method:'append'});
	tab.loadButton(button);
	tab.updateGrid();
};

Tabs.prototype.getCurrentTab = function () {
  	var index = this.$tabsContainer.tabs('option', 'active');
  	return this.tabs[index];
};

Tabs.prototype.getButton = function ($sel) {
	var selection = new Button($sel);
	// return the button that is in the model given the jquery obj
	var button = undefined;
	$.each(this.tabs, function (index, tab) {
		if (!button) {
			button = _.findWhere(tab.buttons, {id:selection.id})
		}
	});
	return button;
};


// Actually run the loading mechanism and make it available for reference in other areas
Splash.singletonTabs = new Tabs(Splash.config.tabsContainer);

Splash.tabs = Splash.singletonTabs;

}(this.Splash));