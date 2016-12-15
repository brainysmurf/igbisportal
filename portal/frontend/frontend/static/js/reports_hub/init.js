
(function () {

	$('#userEnter').autocomplete({
		delay: 0,
		autoFocus: true,
		minLength: 3,
		source: $('#userEnter').data('autocomplete-source'),

		// focus: function (event, ui) {
		// 	$('#userEnter').val(ui.item.value);
		// },

		select: function (event, ui) {
			console.log(ui.item);
			$('#studentID').val(ui.item.id);
			//$('#userSubmit').removeAttr('disabled');
			var url = "students/" + $('#studentID').val() + "/pyp_report?api_token=" + $('#api_token').text();
			window.location.href = url;
		},

		// search: function (event, ui) {
		// 	$('#userSubmit').attr('disabled', 'disabled');
		// }

	});

})();
