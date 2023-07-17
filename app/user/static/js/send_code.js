function isValidEmail(email) {
	// Regular expression for email validation
	const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

	// Test the email against the regular expression and return true or false
	return emailRegex.test(email);
}

function isValidPhoneNumber(phoneNumber) {
	// Regular expression for phone number validation
	const phoneNumberRegex = /^[0-9]+$/;

	// Test the phone number against the regular expression and return true or false
	return phoneNumberRegex.test(phoneNumber) && phoneNumber.length == 10;
}

// Handle code 500 errors
function verifyError(response) {
	$(".verify-alert").remove();
	$("#verify_form").append(`
		<div class="alert alert-danger mt-4 p-4 verify-alert" role="alert">
			${response.responseJSON.status}
  		</div>
  	`);
}

$("#verify-email").on("click", function () {
	const email = $("#email").val();
	if (!isValidEmail(email)) return;
	$.ajax({
		url: "/verify_email",
		type: "POST",
		data: JSON.stringify({ email }),
		contentType: "application/json; charset=utf-8",
		dataType: "json",
		success: function (response) {
			// Remove any existing alerts
			$(".verify-alert").remove();
			// Display success alert
			$("#verify_form").append(`
				<div class="alert alert-success mt-4 p-4 verify-alert" role="alert">
					Email code has been sent.
		  		</div>
		  	`);
		},
		error: verifyError,
	});
});

$("#verify-sms").on("click", function () {
	const phoneNumber = $("#phone_number").val();
	if (!isValidPhoneNumber(phoneNumber)) return;
	$.ajax({
		url: "/verify_sms",
		type: "POST",
		data: JSON.stringify({ phone_number: phoneNumber }),
		contentType: "application/json; charset=utf-8",
		dataType: "json",
		success: function (response) {
			// Remove any existing alerts
			$(".verify-alert").remove();
			// Display success alert
			$("#verify_form").append(`
				<div class="alert alert-success mt-4 p-4 verify-alert" role="alert">
					SMS code has been sent.
		  		</div>
		  	`);
		},
		error: verifyError,
	});
});

$("#submit").on("click", function () {
	$(".verify-alert").remove();
});
