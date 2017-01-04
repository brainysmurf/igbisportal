
(function () {
	// When the update button is clicked,
	//	Initiate on the portal the scraping procedure
	//	And poll the database until it has been completed
	//  TODO: A 'last update' date feature
	$(document).on('click', '#update_button', function () {
		$('#update_button').prop('disabled', true);
		$.ajax({
			url: "/update_report_internal?student_id=" + $('#student_id').text(),
			type: "GET",
			dataType: "json",
			timeout: 2000,
			success: function successHandler(data) {
				if (data.error==true) { console.log(data); return }
				var uniq_id = data.uniq_id;
				// Start the gui process to
				$('#wrapper').css("opacity", 0.5).fadeOut("slow", function() {
					$('#progress_dialog').dialog({
						position: { my: "center", at: "center", of: window },
						dialogClass: 'no-close',
						draggable: false,
					});
				});

				(function poll() {
				    setTimeout(function() {
				        $.ajax({
				            url: "/update_report_poll?uniq_id=" + uniq_id,
				            type: "get",
				            success: function(data) {
				            	if (data.error) console.log(data.message);
				                else if (data.done) {
									$('#update_button').prop('disabled', true);
				                	location.reload();
				                }
				                else console.log("polling");   // maybe do some sort of UI update?
				            },
				            dataType: "json",
				            complete: poll,
				            timeout: 2000
				        });
				    }, 5000);
				})();
			},
		})
	});

	$(document).on('click', '#updateAll', function () {
		$('#updateAll').prop('disabled', true);
		$.ajax({
			url: "/update_report_internal?student_id=all",
			type: "GET",
			dataType: "json",
			timeout: 2000,
			success: function successHandler(data) {
				if (data.error==true) { console.log(data); return }
				var uniq_id = data.uniq_id;
				// Start the gui process to
				$('#wrapper').css("opacity", 0.5).fadeOut("slow", function() {
					$('#progress_dialog').dialog({
						position: { my: "center", at: "center", of: window },
						dialogClass: 'no-close',
						draggable: false,
					});
				});

				(function poll() {
				    setTimeout(function() {
				        $.ajax({
				            url: "/update_report_poll?uniq_id=" + uniq_id,
				            type: "get",
				            success: function(data) {
				            	if (data.error) console.log(data.message);
				                else if (data.done) {
									$('#update_button').prop('disabled', true);
				                	location.reload();
				                }
				                else console.log("polling");   // maybe do some sort of UI update?
				            },
				            dataType: "json",
				            complete: poll,
				            timeout: 2000
				        });
				    }, 5000);
				})();
			},
		})
	});
})();
