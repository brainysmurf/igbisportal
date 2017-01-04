
(function () {
	// register the format used for "human"
	//$.fn.dataTable.moment( "dddd, MMMM Do YYYY @ h:mm a" );

	$('#individual').autocomplete({
		delay: 0,
		autoFocus: true,
		minLength: 3,
		source: $('#individual').data('autocomplete-source'),

		// focus: function (event, ui) {
		// 	$('#userEnter').val(ui.item.value);
		// },

		select: function (event, ui) {
			$('#studentID').val(ui.item.id);
			//$('#userSubmit').removeAttr('disabled');
			// var url = "students/" + $('#studentID').val() + "/pyp_report?api_token=" + $('#api_token').text();
			// window.location.href = url;
		},

		// search: function (event, ui) {
		// 	$('#userSubmit').attr('disabled', 'disabled');
		// }

	});

	$('#pyp_classroom').autocomplete({
		delay: 0,
		autoFocus: true,
		minLength: 3,
		source: $('#pyp_classroom').data('autocomplete-source'),

		// focus: function (event, ui) {
		// 	$('#userEnter').val(ui.item.value);
		// },

		select: function (event, ui) {
			$('#courseID').val(ui.item.id);
			//$('#userSubmit').removeAttr('disabled');
			// var url = "students/" + $('#studentID').val() + "/pyp_report?api_token=" + $('#api_token').text();
			// window.location.href = url;
		},

		// search: function (event, ui) {
		// 	$('#userSubmit').attr('disabled', 'disabled');
		// }

	});

	$('#individualSubmit').on('click', function () {
		var url = "students/" + $('#studentID').val() + "/pyp_report?api_token=" + $('#api_token').text();
		window.location.href = url;
	});

	$('#courseView').on('click', function () {
		var url = "student_enrollments_by_course_id/" + $('#courseID').val();
		$.ajax({
				url: url,
				type: "GET",
				dataType: "json",
				timeout: 2000,
				success: function successHandler(data) {
					data.students.forEach(function (student_id) {
						newWindowUrl = "students/" + student_id + "/pyp_report?api_token=" + $('#api_token').text();
						window.open(newWindowUrl);
					});
				}
		});
	});

	$('#lastUpdatedTable').DataTable({
		ajax: '/lastupdated',
		order: [
			[ 1, "asc" ],
		],
		columns: [
	 	   { 
	 	     type: "html", 
	 	     data: "name",
	 	     render: function (data, type, row) {
	 	     	return '<a class="updateLink" target="_blank" href="/students/' +  row.id + '/pyp_report">' + row.name + "</a>";
	 	     }
	 	   }, {
		     type: "num", 
		     data: "grade" 
		   }, { 
		   	 type: "date", 
		     data: "date",
		     render: function (data, type, row) {
		     	return row.human;
		     }

		   }
    	],
	});  	//	# 


})();
