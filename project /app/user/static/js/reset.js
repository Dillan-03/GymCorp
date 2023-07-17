$("#reset_form").submit(function (event) {
	event.preventDefault();
	var form = $(this);
	var errors = $("#verify_form");
	$.ajax({
		type: form.attr("method"),
		url: form.attr("action"),
		data: form.serialize(),
		dataType: "json",
		success: function (response) {
			// If password was changed then reset form and format alert message
			if (response.success) {
				form.trigger("reset");
				var alert = "alert alert-success";
			} else {
				var alert = "alert alert-danger";
			}
			// Remove any potential current alerts
			$(".verify-alert").remove();
			errors.append(`
				<div class="${alert} mt-4 p-4 verify-alert" role="alert">
					${response.message}
				</div>
			`);
			// Remove alert after time
			setTimeout(function () {
				$(".verify-alert").remove();
			}, 5000);
		},
		error: function () {
			alert("An error occurred while processing your request.");
		},
	});
});
