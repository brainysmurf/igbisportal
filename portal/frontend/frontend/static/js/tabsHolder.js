console.log('tabsHolder here');
// show: { effect: "fade", duration: 300 }		
(function () {
	$('#tab_container').tabs({
		heightStyle: 'content',  //  calculate on resizes
		show: function (event, ui) { console.log('show');}
	});

	console.log($(".js-packery"));
	$(".js-packery").on('tabsshow', function(event, ui) {
		console.log('tabsshow');
	});
})();
