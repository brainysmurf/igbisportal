(function($) {
	$.fn.skinableTabs = function(options) {
		var opts = $.extend({}, $.fn.skinableTabs.defaults, options);
		return new TabSkinsClass($(this), opts);
	};
	$.fn.skinableSkins = function(options) {
		return $(this).skinableTabs(options);
	};
	$.fn.skinableTabs.defaults = {
		skin: 		'skin1',
		position: 	'top',
		effect: 	'simple_fade',
		persist_tab: 	1,
		skin_path:	''
	};

	var TabSkinsClass = function (el, opts) {
		el.hide();
	this.showTooltip = function (text) {
		global_showTooltip(text);
	}
	this.showTab = function (name) {
//		console.log('showing tab with ID: '+name);
		global_showOne(name);
	}
        var global_container = el;
        var global_opts = opts;
		var global_tabs = [];
		var global_selectedTab = false;
		var global_htmlSelectedTab = false;
		var global_step = 0; // possible values: 0, 1, 2

		var __global_construct = function() {
			// GTFHRCPH
			global_container.children('.content_holder').wrapInner('<div class="content_holder_inner" style="overflow: hidden; position: relative; z-index: 1; padding: 10px 0px;" />');
			global_container.css('overflow', 'hidden'); // useful for vertical tabs
			global_container.css('position', 'relative'); // useful for vertical tabs
			global_container.addClass('tabs_wrapper').addClass(global_opts.skin).addClass(global_opts.position); // useful for vertical tabs
			global_container.children('ul').each(function() {
				// load skin
				global_loadSkinCss(global_opts.skin, global_opts.position);
				$(this).addClass('tabs_header');
				global_createHeader(this);
				global_showOne();
			});
			$(global_container).append('<div style="height: 0px; font-size: 1px; line-height: 1px; clear: both;"></div>');
		};
		var myRC = function (name) {
			var nameEQ = name + "=";
			var ca = document.cookie.split(';');
			for(var i=0;i < ca.length;i++) {
				var c = ca[i];
				while (c.charAt(0)==' ') c = c.substring(1,c.length);
				if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
			}
			return null;
		};
		var setRC = function (c_name, value, exdays) {
			var exdate = new Date();
			exdate.setDate(exdate.getDate() + exdays);
			var c_value = escape(value) + ((exdays==null) ? "" : "; expires="+exdate.toUTCString());
			document.cookie = c_name + "=" + c_value;
		};
		var global_loadSkinCss = function(skin_name, position) {
			var url = global_opts.skin_path+'skins/'+skin_name+'/'+position+'.css';
			if (document.createStyleSheet) {
				document.createStyleSheet(url);
			}
			else {
				$('<link rel="stylesheet" type="text/css" href="' + url + '" />').appendTo('head'); 
			}
		};
		var global_createHeader = function(list_obj) {
			$(list_obj).children('li').each(function() {
				var $_this = $(this);
				$_this.addClass('tab_header_item');
				$_this.prepend('<span class="header_item_before"></span>');
				$_this.append('<span class="header_item_after"></span>');
				$_this.children('a').each(function() {
					var $_a_this = $(this);
					var	tab_id = global_getHref($_a_this.attr('href'));
					$_a_this.addClass(global_getHeaderClass(tab_id));
					if ($_a_this.parent().hasClass('tab_selected')) {// tab header is selected in HTML
						global_htmlSelectedTab = {id:tab_id,a_href:$_a_this}; 
					}
					global_createTabContent(tab_id, $_a_this);
					$_a_this.click(function(ev) {
						if (!$_a_this.parent().hasClass('tab_selected')) {
							global_showTabContent(tab_id, false, $_a_this);
						}
						ev.preventDefault();
						return false;
					});
				});
			});
			var loaded_tabs 	= global_tabs;
			var first_tab 		= global_tabs[0].id;
			var last_tab 		= global_tabs[global_tabs.length - 1].id;
			$('a[href$="'+first_tab+'"]').parent().addClass('first_tab');
			$('a[href$="'+last_tab+'"]').parent().addClass('last_tab');
		};
		var global_getHref 		= function (loc) {
			if (loc.match('#')) {
				loc = '#'+loc.split('#')[1];
			}
			return loc;
		};
		var global_showTooltip = function(text) {
			var $_tooltip = $('#tooltip');
			var b = new Boolean($_tooltip);
			if (b) {
				$_tooltip.html(text).show(500).delay(3000).hide(800);
			}
		};
		var global_showTabContent = function(tab_id, no_effect, a_href) {
			if (global_opts.persist_tab) {
//				console.log('selecting: '+tab_id);
				setRC('skinableTabs_sel', tab_id.replace('#', ''), 10);
			}
			var ajax_rel = a_href.attr('rel');
			if (ajax_rel != undefined) {
				var ajax_loaded = a_href.attr('ajax_loaded');
				ajax_loaded = typeof(ajax_loaded) != 'undefined' ? ajax_loaded : 0;
				if (ajax_loaded == 0) {
					a_href.attr('ajax_loaded', 1);
					$.get(ajax_rel, function(data) {
						$(tab_id).html(data);
					});
				}
			}
			if (global_step != 0) {
				global_showTooltip('There is an animation in progress.<br /> To prevent animation overlapping, you should wait until it\'s finished.');
				return false;
			}
			else {
				global_step++;
			}
			no_effect = typeof(no_effect) != 'undefined' ? no_effect : false;
			global_hideSelectedTab();
			if (!no_effect) {
				global_animateEffect(tab_id, global_opts.effect, 'show');
			}
			else {
				$(tab_id).show();
				global_step = 0;
			}
			$('.'+global_getHeaderClass(tab_id)).parent().addClass('tab_selected');
			global_registerSelected(tab_id);
		};
		var global_getHeaderClass = function(tab_id) {
			var string = tab_id.replace('#', '')+'-tab_header';
			return string;
		};
		var global_hideSelectedTab = function() {
			if (global_selectedTab) {
				global_animateEffect(global_selectedTab, global_opts.effect, 'hide');

				$('.'+global_getHeaderClass(global_selectedTab)).parent().removeClass('tab_selected');
			}
		};
		var global_registerSelected = function(tab_id) {
			global_selectedTab = tab_id;
		};
		var global_stopInAnimation = function() {
			global_inAnimation = false;
		};
		var effectDone = function() {
			if (global_step == 2) {
				global_step = 0;
			}
			else {
				global_step++;
			}
		};
		var global_animateEffect = function(tab_id, effect, do_show) {
			global_inAnimation = true;
			var to_show = tab_id;
			var to_hide = tab_id;

			var $_to_show = $(tab_id);
			var $_to_hide = $_to_show;
			switch (effect) {
				case 'basic_display':
					if (do_show == 'show') {
						$_to_show.css('display', 'block');
						effectDone();
					}
					else {
						$_to_hide.css('display', 'none');				
						effectDone();
					}
				break;
				case 'simple_fade':
					if (do_show == 'show') {
						$_to_show.css('position', 'relative').effect('fade', {mode: 'show', times: 2, direction: 'right', distance: 50}, 1000, effectDone);
					}
					else {
						$_to_hide.css('position', 'absolute').effect('fade', {mode: 'hide', times: 2, direction: 'right', distance: 50}, 1000, effectDone);
					}
				break;
				case 'hide_and_seek':
					if (do_show == 'show') {
						$_to_show.css('position', 'relative').effect('fold', {mode: 'show', times: 2, direction: 'right', distance: 50}, 1000, effectDone);
					}
					else {
						$_to_hide.css('position', 'relative').effect('fold', {mode: 'hide', times: 2, direction: 'right', distance: 50}, 1000, effectDone);
					}
				break;
				case 'evanescence':
					if (do_show == 'show') {
						$_to_show.toggle('slideRight', null,  2500);
						setTimeout(function(){effectDone();}, 1500);
					}	
					else {
						$_to_hide.effect('slideRight', {mode: 'hide'}, 1500, effectDone);
					}
				break;
				case 'transfading_down':
					if (do_show == 'show') {
						$_to_show.show(500);
						setTimeout(function(){effectDone();}, 500);
					}
					else {
						$_to_hide.effect('slideRight', {mode: 'hide', times: 2, direction: 'up', distance: 50}, 500, effectDone);
					}
				break;
				case 'transfading_up':
					if (do_show == 'show') {
						$_to_show.show(500);
						setTimeout(function(){effectDone();}, 500);
					}
					else {
						$_to_hide.hide(500);
						setTimeout(function(){effectDone();}, 500);
					}
				break;
				case 'overlapping':
					if (do_show == 'show') {
						$_to_show.toggle('blind', null,  1500);
						setTimeout(function(){effectDone();}, 1000);
					}
					else {
						$_to_hide.effect('blind', {mode: 'hide'}, 1000, effectDone);
					}
				break;
				case 'horizontal_bouncer':
					if (do_show == 'show') {
						$_to_show.toggle('bounce', {mode: 'show', times: 2, direction: 'right', distance: 100}, 1000);
						setTimeout(function(){effectDone();}, 2500);
					}
					else {
						$_to_hide.effect('slideRight', {mode: 'hide', times: 2, direction: 'up', distance: 50}, 500, effectDone);
					}
				break;
				case 'vertical_bouncer':
					if (do_show == 'show') {
						$_to_show.slideDown(500).effect('bounce', {times: 2, direction: 'up', distance: 30}, 500, effectDone);
					}
					else {
						$_to_hide.hide(500, effectDone);
					}
				break;
				case 'slide_right':
					if (do_show == 'show') {
						$_to_show.css('position', 'relative').effect('slide', {mode: 'show', direction: 'left'}, 1000, effectDone);
					}
					else {
						$_to_hide.css('position', 'absolute').effect('slide', {mode: 'hide', direction: 'right'}, 1000, effectDone);
					}
				break;
				case 'slide_left':
					if (do_show == 'show') {
						$_to_show.css('position', 'relative').effect('slide', {mode: 'show', direction: 'right'}, 1000, effectDone);
					}
					else {
						$_to_hide.css('position', 'absolute').effect('slide', {mode: 'hide', direction: 'left'}, 1000, effectDone);
					}
				break;
				case 'slide_up':
					if (do_show == 'show') {
						$_to_show.css('position', 'relative').effect('clip', {mode: 'show'}, 500, effectDone);
					}
					else {
						$_to_hide.css('position', 'absolute').hide(500, effectDone);
					}
				break;
				case 'fade_slide_left':
					if (do_show == 'show') {
						$_to_show.css('position', 'relative').effect('drop', {mode: 'show', times: 2, direction: 'right', distance: 100}, 1000, effectDone);
					}
					else {
						$_to_hide.css('position', 'relative').hide(5, effectDone);
					}
				break;
				case 'fade_slide_right':
					if (do_show == 'show') {
						$_to_show.css('position', 'relative').effect('drop', {mode: 'show', times: 2, direction: 'left', distance: 100}, 1000, effectDone);
					}
					else {
						$_to_hide.css('position', 'absolute').effect('drop', {mode: 'hide', times: 2, direction: 'right', distance: 50}, 500, effectDone);
					}
				break;
				case 'fade_slide_up':
					if (do_show == 'show') {
						$_to_show.css('position', 'relative').effect('drop', {mode: 'show', times: 2, direction: 'down', distance: 100}, 1000, effectDone);
					}
					else {
						$_to_hide.css('position', 'absolute').effect('drop', {mode: 'hide', times: 2, direction: 'up', distance: 50}, 500, effectDone);
					}
				break;
				case 'fade_slide_down':
					if (do_show == 'show') {
						$_to_show.css('position', 'relative').effect('drop', {mode: 'show', times: 2, direction: 'up', distance: 100}, 1000, effectDone);
					}
					else {
						$_to_hide.css('position', 'absolute').effect('drop', {mode: 'hide', times: 2, direction: 'down', distance: 50}, 500, effectDone);
					}
				break;
				case 'fireworks':
					if (do_show == 'show') {
						$_to_show.css('position', 'relative').css('display', 'block');
						effectDone();
					}
					else {
						$_to_hide.css('position', 'absolute').effect('explode', {mode: 'hide', times: 2, direction: 'right', distance: 50}, 1000, effectDone);
					}
				break;
				case 'puff':
					if (do_show == 'show') {
						$_to_show.css('position', 'relative').effect('slide', {mode: 'show', times: 2, direction: 'right', distance: 50}, 1000, effectDone);
					}
					else {
						$_to_hide.css('position', 'absolute').effect('puff', {mode: 'hide', times: 2, direction: 'right', distance: 50}, 300, effectDone);
					}
				break;
					default:
					if (do_show == 'show') {
						$_to_show.css('position', 'relative').effect('fade', {mode: 'show', times: 2, direction: 'right', distance: 50}, 1000, effectDone);
					}
					else {
						$_to_hide.css('position', 'absolute').effect('fade', {mode: 'hide', times: 2, direction: 'right', distance: 50}, 1000, effectDone);
					}
				break;
			}
		};
		var global_getTabFromUrl = function() {
			var url = document.location.toString();
			var tab = false;
			if (url.match('#')) {
				var tmp = '#'+url.split('#')[1];
				tab = global_getTabFromId(tmp);
			}
			return tab;
		};
		var global_getTabFromId = function (tab_id) {
			var tab = false;
			for (var i=0;i<global_tabs.length;i++) {
				if (global_tabs[i].id == tab_id) {
					tab = global_tabs[i];
					break;
				}
			}
			return tab;
		}
		var global_showOne = function(tab_id) {
			var a_href = '';
			var tab = false;
			if (global_htmlSelectedTab) {
				global_htmlSelectedTab.a_href.parent().removeClass('tab_selected');
			}
			if (typeof tab_id != 'undefined') {
				var tab = global_getTabFromId(tab_id);
			}
			else {
				tab_id = '';
			}
			if (tab != false) {
				tab_id = tab.id;
				a_href = tab.a_href;
			}
			else {
				// search for #anchor reference to tabs
				var tab_in_url = global_getTabFromUrl();

				if (tab_in_url != false) { // from URL
					tab_id = tab_in_url.id;
					a_href = tab_in_url.a_href;
	//				console.log('from URL', tab_id);
				}
				else if (global_opts.persist_tab && tab_id == '') { // from cookie
					var temp_tab_id = '';
					temp_tab_id = '#'+myRC('skinableTabs_sel');
					$.each(global_tabs, function(index, item) {
						if (item.id == temp_tab_id) {
							tab_id = item.id;
							a_href = item.a_href;
	//						console.log('from cookie', tab_id);
						}
					});
				}
				if (tab_id == '' && global_htmlSelectedTab) { // from HTML
					tab_id = global_htmlSelectedTab.id;
					a_href = global_htmlSelectedTab.a_href;
	//				console.log('from HTML', tab_id);
				}
				else if (tab_id == '') { // simply show the first
					tab_id = global_tabs[0].id;
					a_href = global_tabs[0].a_href;
	//				console.log('the first one', tab_id);
				}



			}
			global_showTabContent(tab_id, true, a_href);
		};
		var global_createTabContent = function(tab_id, a_href) {
			var $tab_id = $(tab_id);
			$tab_id.addClass('tab_content');
			$tab_id.wrapInner('<div class="inner_content" />');
			$tab_id.hide();
			global_tabs.push({id:tab_id,a_href:a_href});
		};
		// added for on page hash location
		var onHashChange = function(event) {
			//get hash function
			var getHashValue = function() {
				var arr = window.location.hash.split("#");
				var hasValue = arr[1];
				//sets default
				if (typeof hasValue == "undefined") {
				    return false;
				}
				if (hasValue.search('-inpage') > 0) {
					window.location = arr[0]+'#'+hasValue.replace('-inpage', '');
				}
				var hashLen = hasValue.indexOf("?");
				if(hashLen>0){
				    hasValue = hasValue.substring(0,hashLen);
				}
				return hasValue;
			}
			//last hash
			var lastHash = getHashValue();
			//checker
			(function watchHash() {
				var hash = getHashValue();
				if (hash !== lastHash) {
				    event();
				    lastHash = hash;
				}
				var t = setTimeout(watchHash, 100);
			})();
		} 
		onHashChange(function() {
			global_showOne();
		});
		// calling the constructor
		__global_construct();
		el.show();
	};
})(jQuery);