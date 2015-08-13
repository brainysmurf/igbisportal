// Defines classes we'll use on our splash page
(function (Splash) {

'use strict';

Splash.config.gridly.callbacks = {
	// reordering: function ($elements) {

	// },
	reordered: function ($elements) {
		var id, element, button;

		// Loop through each element and update our model information
		// Only set dirty to any positions that changed
		for (var position = 0; position < $elements.length; position++) {
			element = $($elements[position]);
			id = element.data('id');
			button = Splash.tabs.getButtonById(id);
			if (button.position != position + 1) {
				button.position = position + 1;
				button.dirty = true;
			}
		}
		Splash.changeMade();
	}
};

Splash.config.sortable.start = function (event, ui) {
	Splash.state.tabOrder = $('#tabs_titlebar').sortable("toArray", {attribute:'data-position'});
};

Splash.config.sortable.stop = function (event, ui) {
	var newOrder = $('#tabs_titlebar').sortable("toArray", {attribute:'data-position'});
	if (Splash.state.tabOrder != newOrder) {
		Splash.changeMade();
		var dataPositions = $('#tabs_titlebar').sortable("toArray", {attribute:'data-position'});
		var Ids = $('#tabs_titlebar').sortable("toArray", {attribute:'id'});
		var tab, position;
		// Go through the data and change the positions as appropriate
		var howManyToPrepend = Splash.tabs.tabs.length - $('#tabs_titlebar').sortable("toArray").length
		for (var i=0; i<howManyToPrepend; i++) {
			dataPositions.splice(0, 0, "");
		}
		_.zip(Splash.tabs.tabs, dataPositions).forEach(function (item, index) {
			tab = item[0];
			position = item[1];
			tab.position = parseInt(position);
		});
	}
};

Splash.JBoxes = [];

// TODO: Update position when adding manually
var Button = function (name, color, url, icon) {

	// We do not want to put any objects on here except for values
	// If user needs jquery obj, use $(button.idSelector)
	var $sel = undefined;
	this.editButton = ""; 

	if (arguments.length == 1) {

		if (name instanceof HTMLElement || name instanceof jQuery) {
			if (name instanceof jQuery) {
				$sel = name;
			} else {
				$sel = $(name);
			}
			this.name = $sel.data('name');
			if (!$sel.attr('id')) {
				this.id = 'splashButton'+Button.counter++;
			} else {
				this.id = $sel.attr('id');
			}
			this.idSelector = '#'+this.id;
			this.url = $sel.data('url');
			this.icon = $sel.data('icon');
			this.count = $sel.data('count');
			this.color = $sel.data('color');
			this.externalid = $sel.data('externalid');
			this.size = $sel.data('size');
			this.dirty = false;
			this.position = undefined;
			this.kind = $sel.data('kind');

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
		}

		else if (typeof name === 'object') {
			for (var property in name) {
				this[property] = name[property];
			}
			if (!this.subMenuItems) {
				this.subMenuItems = [];
			}
			// We override in case of deletions
			this.id = 'splashButton'+Button.counter++;
			this.idSelector = '#' + this.id;

		}

	} else if (arguments.length == 4) {
		// It's spelled out, must be a new one
		this.name = name;
		this.color = color;
		this.url = url;
		this.icon = icon;
		$sel = undefined;
		this.submenuString = undefined;
		this.externalid = undefined;
		this.id = 'splashButton'+Button.counter++;
		this.idSelector = '#'+this.id;
		this.dirty = false;
		this.position = undefined;
		this.kind = 'userButton';
	}
};

Button.prototype.toJson = function () {
	return JSON.stringify({
		name: this.name,
		icon: this.icon,
		url: this.url,
		position: this.position,
		color: this.color
	});
};

Button.prototype.processJBox = function () {
	var jbox;

	if (this.subMenuItems.length > 0) {
		$(this.idSelector).mustache('submenuItemTemplate', {items:this.subMenuItems}, {method:'append'});
		var thisTitle = '<a class="submenuTitle" href="'+ this.url + '">' + this.name + '</a>';

		// attach jbox to the target element and save in the button object
		jbox = $(this.idSelector).jBox('Tooltip', {
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
		jbox.splashIdSelector = this.idSelector;
		jbox.indexInArray = Splash.JBoxes.length;
		Splash.JBoxes.push(jbox);
    } else {
    	jbox = undefined;
    }

    return jbox;
};

Button.counter = 0;

Button.prototype.left = function () {
	return parseInt($(this.idSelector).css("left"), 10);
};

Button.prototype.right = function () {
	return parseInt($(this.idSelector).css("right"), 10);
};

Button.prototype.updateDom = function () {
	$(this.idSelector).find('.buttonTitle').text(this.name);
	$(this.idSelector).find('a').attr('href', this.url);
	$(this.idSelector).alterClass('color*', 'color'+this.color);
	$(this.idSelector).find('.buttonIcon > i').alterClass('fa-*', 'fa-'+this.icon);
};

Button.prototype.updateWithValues = function (name, color, url, icon) {
	this.name = name;
	this.color = color;
	this.url = url;
	this.icon = icon;
	this.dirty = true;
	this.updateDom();
};

var Tab = function(name) {
	var $sel = undefined;
	this.buttons = [];

	if (name instanceof HTMLElement || name instanceof jQuery) {
		// We get here when we are looping through our initial markup and see the system-provided buttons and tabs

		if (name instanceof jQuery) {
			$sel = name;
		} else {
			$sel = $(name);
		}
		this.name = $sel.data('name');
		// FIXME: Don't depend on the names!
		this.kind = $sel.data('kind');
		$sel.addClass(this.kind);
		this.id = this.name.replace(/ /g, '_');

		this.idSelector = '#'+this.id;
		this.gridSelector = this.idSelector + ' > .grid';

		this.dirty = false;
		this.position = Tab.counter++;  // not the same as position below!
		$sel.data('position', this.position);

		var position = 1;  // use 1 as starting point because we use length to calculate on new button
		$(this.gridSelector).find('.buttonContainer').each(function (index, button) {
			// Make new button object with existing data
			var newButton = new Button(button);
			newButton.position = position++;

			// Remove the old button from the DOM
			$(button).remove();

			// Add newButton to our object structure
			this.loadButton(newButton);

			// Add newButton to the DOM
			$(this.gridSelector).mustache('buttonContainerTemplate', newButton, {method:'append'});

			// Read in submenu information, jbox processing
			newButton.processJBox();
		}.bind(this));

	} else if (typeof name === "string") {
		// We get here when we create a string from scratch
		this.name = name;
		this.id = this.name.replace(/ /g, '_');
		this.idSelector = '#'+this.id;
		this.gridSelector = this.idSelector + ' > .grid';
		if (this.name == 'Secondary_Teachers' || this.name == 'Elementary_Teachers' || this.name == 'Students') {
			this.kind = 'systemTab';
		} else {
			this.kind = 'userTab';
		}

		this.dirty = false;
		this.position = Tab.counter++;

	} else if (typeof name === 'object') {
		// We get here when we load up user-saved tabs that are available to us as objects (from serialization)
		// Ironic, we are essentially rebuiliding
		for (var property in name) {
			this[property] = name[property];
		}
		this.buttons = []; // reset this because we'll build it up later
		this.position = Tab.counter++;
	}
};

Tab.counter = 0;

Tab.prototype.numButtons = function () {
	return this.buttons.length;
}

Tab.prototype.loadButton = function (button) {
	this.buttons.push(button);
	return this;
};

Tab.prototype.addButton = function (name, color, url, icon) {
	var button;
	if (arguments == 1) {
		button = name;
	} else {
		button = new Button(name, color, url, icon)
	}
	$(this.gridSelector).mustache('buttonContainerTemplate', button, {method:'append'});
	this.loadButton(button);
	this.updateGrid();
};

Tab.prototype.initGrid = function () {
	$(this.gridSelector).gridly(Splash.config.gridly);
	$(this.gridSelector).gridly('draggable', 'off');
};

Tab.prototype.updateGrid = function () {
	$(this.gridSelector).gridly('layout');	
};

// This class effectively loads up all the buttons and tabs
// We don't want any jquery objects on this class for serialization purposes
var Tabs = function() {

	this.tabsSelector = Splash.config.tabsContainer;
	this.tabs = [];
	$(this.tabsSelector).find('ul:first').find('li').each(function (index, item) {
		this.loadTab(new Tab(item));
	}.bind(this));

    $.ajax({
        type:'GET',
        url: 'getButtons',
        contentType: 'application/json; charset=utf-8',
        success: function(fromServer) {
			var fromLocal = localStorage.getItem(Splash.config.localStorageKey);

			if (fromServer != fromLocal) {
				// delete the other stuff from dom and the model...
				//this.process.Storage();
				console.log('server and local do NOT match');
				var tab;
				for (var i = 0; i < fromServer.length; i++) {
					tab = fromServer[i];
					if (tab.kind === 'userTab') {
						$(tab.idSelector).remove();   // removes from the DOM, if exists
						this.tabs.splice(i, 1);       // removes from the model if it's there
					}
				}
				this.processStorage(fromServer);

			} else {
				this.processStorage(fromLocal);
			}
        }.bind(this),

        complete: function (ignore, ignore2) {
        	this.finalInit();
        }.bind(this)
    });

	// initing tabs last aftetr grid operations works better
};

Tabs.JBoxes = [];

Tabs.prototype.finalInit = function () {
	this.forEachTab(function (tab) {
		tab.initGrid();
	});
	$(Splash.config.tabsContainer).tabs(Splash.config.tabs);
	var currentTab = localStorage.getItem(Splash.config.currentTabKey);
	if (currentTab != "null" && currentTab != "") {
		$(Splash.config.tabsContainer).tabs({active: parseInt(currentTab)});
	}
}

Tabs.prototype.processStorage = function (storage) {
	var newTab;
	var userTabs = JSON.parse(storage);
	_.sortBy(userTabs, function (t) { return t.position; }).forEach(function (tab, index) {
		if (tab.kind === 'userTab') {
			newTab = new Tab(tab);

			var $lastLi = $(this.tabsSelector).find('ul > li:last-child');
		  	$lastLi.mustache('newTabLiTemplate', newTab, {method:'after'});

		  	var $lastDiv = $(this.tabsSelector).children('div:last-child');
		  	$lastDiv.mustache('newTabTemplate', newTab, {method:'after'});

			this.loadTab(newTab);

			// Load them up in order of position.
			_.sortBy(tab.buttons, function (b) { return b.position;} ).forEach(function (button, index) {
				var newButton = new Button(button);

				newTab.loadButton(newButton);

				$(newTab.gridSelector).mustache('buttonContainerTemplate', newButton, {method:'append'});

				newButton.processJBox();				
			});
		}
	}.bind(this));
};

Tabs.prototype.toJson = function() {
	var ret = "";
};

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

Tabs.prototype.getButtonById = function (id) {
	var ret = undefined;
	var button = undefined;
	this.tabs.forEach(function (tab, index) {
		if (button =_.findWhere(tab.buttons, {id:id})) {
			ret = button;
		}
	});
	return ret;
};

Tabs.prototype.addNewButtonInTab = function(inTabName, buttonName, buttonColor, buttonLink, buttonIcon) {
	var button = new Button(buttonName, buttonColor, buttonLink, buttonIcon);
	this.getTabByName(inTabName).addButton(buttonName, buttonColor, buttonLink, buttonIcon);
};

Tabs.prototype.disableJBoxes = function () {
	Splash.JBoxes.forEach(function (jbox, index) {
		jbox.disable();
	});
};

Tabs.prototype.enableJBoxes = function () {
	Splash.JBoxes.forEach(function (jbox, index) {
		jbox.enable();
	});
};

Tabs.prototype.addTab = function (name) {
	// Adds to the model and the DOM
	
  	// TODO: Add target depending on user setting? to be consistent?
  	// Make this a template, too, right?
  	// Add the tab in the tab list to the DOM
  	var newTab = new Tab(name);

	var $lastLi = $(this.tabsSelector).find('ul > li:last-child');
  	var $save = $lastLi.mustache('newTabLiTemplate', newTab, {method:'after'}).next();

  	var $lastDiv = $(this.tabsSelector).children('div:last-child');
  	var $thisOne = $lastDiv.mustache('newTabTemplate', newTab, {method:'after'});

  	$save.addClass('editButton');
  	$save.find('*').addClass('editButton');
    $save.find('*:not(.onButton)').animate({opacity: 0.4});
    $save.animate({opacity: 1}, {
          done: function () {
              $save.find('.onButton').removeClass('js-avoidClicks');
          },
    });

  	$(this.tabsSelector).tabs("refresh");

	newTab.initGrid();
	this.loadTab(newTab);
};

Tabs.prototype.addButtonToCurrentTab = function (name, color, url, icon) {
	// Adds to the current tab...

	var button = new Button(name, color, url, icon);
	button.dirty = true;
	var tab = this.getCurrentTab();
	button.position = tab.numButtons() + 1;
	button.editButton = 'editButton';
	$(tab.gridSelector).mustache('buttonContainerTemplate', button, {method:'append'});
	$(button.idSelector).hide().toggle('highlight');	
	tab.loadButton(button);

	// TODO: Make this a trigger instead
    $(button.idSelector).find('*').addClass('editButton');
    $(button.idSelector).find('*:not(.onButton)').css('opacity', 0.4);
    $(button.idSelector).addClass('noBorder');
	$(button.idSelector).find('*:not(.onButton)').addClass('js-avoidClicks')
	$(button.idSelector).find('.onButton').css('opacity', 1);

	tab.updateGrid();

};

Tabs.prototype.getCurrentTab = function () {
	// this needs to change to position
  	var index = $(this.tabsSelector).tabs('option', 'active');
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

Tabs.prototype.isAnythingDirty = function () {
	var tabsDirty = false;
	this.tabs.forEach(function (index, tab) {
		if (tab.dirty) {
			tabsDirty = true;
		}
	});
	if (tabsDirty) {
		return true;
	}
	return this.tabs.some(function (tab) { 
		return tab.buttons.some(function (button) {
			return button.dirty; 
		}); 
	});
};

Tabs.prototype.buttonsNotDirty = function () {
	this.tabs.forEach(function (tab) {
		tab.buttons.forEach(function (button) {
			button.dirty = false;
		});
	});
};

// TODO: These looping functions could be faster...

// returns dirty buttons and resets flag
Tabs.prototype.dirtyButtons = function () {
	var ret = [];
	this.tabs.forEach(function (tab) {
		tab.buttons.forEach(function (button) {
			if (button.dirty) {
				ret.push(button);
				button.dirty = false;
			}
		});
	});
	return ret;
}

// This kicks off the start up code 
Splash.singletonTabs = new Tabs();

Splash.tabs = Splash.singletonTabs;

Splash.state = {
	isEditing: false,
	changeMade: false,
};

}(this.Splash));