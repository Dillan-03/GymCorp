// Global variables for user details
var email;
var number;

// When page loads then get user details and censor them
$(document).ready(function() {
	$.ajax({
		type: "GET",
        url: "/settings/get-current-user-details",
        success: function(response) {
            email = response.email;
			number = response.phone_number;
			censorDetails();
        },
		error: function() {
            alert("An error occurred while processing your request.");
        }
    });
});

// Censor details function for email and phone number
var censorDetails = function (){
	var censoredEmail = censorEmail(email);
	var censoredPhone = "+44 " + censorWord(number);
	document.getElementById("email").value = censoredEmail;
	document.getElementById("phone_number").value = censoredPhone;
}

// Censors the string that is passed into it
var censorWord = function (str) {
	return str[0] + "*".repeat(str.length - 2) + str.slice(-1);
}
// Censors email appropriately
var censorEmail = function (email){
	var arr = email.split("@");
	return censorWord(arr[0]) + "@" + censorWord(arr[1]);
}

// Change password ajax request
$("#change_password").submit(function(event) {
	event.preventDefault();
	var form = $(this);
	$.ajax({
		type: form.attr("method"),
		url: form.attr("action"),
		data: form.serialize(),
		dataType: "json",
		success: function(response) {
			// If password was changed then reset form and format alert message
			if (response.success) {
				form.trigger("reset");
				var alert = "alert alert-success"
			}
			else{
				var alert = "alert alert-danger"
			}
			// Remove any potential current alerts
			$(".verify-alert").remove();
			form.append(`
				<div class="${alert} mt-4 p-4 verify-alert" role="alert">
					${response.message}
				</div>
			`);
			// Remove alert after time
			setTimeout(function() {
				$(".verify-alert").remove();
			}, 5000);
		},
		error: function() {
			alert("An error occurred while processing your request.");
		}
	});
});

// When button is clicked to confirm password
$(".btn-ok").click(function () {
	$.ajax({
		type: "POST",
		url: "/settings/confirm",
		data: JSON.stringify(document.getElementById("confirm_pass").value),
		contentType: "application/json; charset=utf-8",
		dataType: "json",
		success: function() {
			// Show true user details
			$('#email').val(email);
			$('#phone_number').val("+44 " + number);
			$('#show').hide();
			$('#hide').show();
		},
		error: function() {
			// Show alert to indicate wrong password
			$(".verify-alert").remove();
			$("#details_form").append(`
				<div class="alert alert-danger mt-4 p-4 verify-alert" role="alert">
					Incorrect password
				</div>
			`);
			setTimeout(function() {
				$(".verify-alert").remove();
			}, 5000);
		}
	});
});

// Button to hide user details
$("#hide").click(function () {
	censorDetails();
	$('#hide').hide();
	$('#show').show();
});