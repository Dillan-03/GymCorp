// Book button clicked
$("#book-button").on("click", function () {
	const bookings = [];
	// Fill bookings from basket
	$(".basket-item").each(function () {
		const basketItem = $(this);
		const booking = {
			activity_id: basketItem.data("activity-id"),
			date: basketItem.data("date"),
			time: basketItem.data("time"),
		};
		// If booking has number field then we need to add number of people
		const number_of_people = basketItem.find(".number_of_people");
		if (number_of_people.length != 0) {
			booking.number_of_people = Number(number_of_people.val());
		}
		// Add it to bookings array
		bookings.push(booking);
	});
	// If an employee is sending this request, send a customer id with it
	data = { bookings };
	if ($("#customer-id").length != 0) {
		data.customer_id = Number($("#customer-id").data("customer-id"));
	}
	// Book the sessions
	$.ajax({
		url: "/book",
		type: "POST",
		// Send booking data
		data: JSON.stringify(data),
		contentType: "application/json; charset=utf-8",
		dataType: "json",
		success: function (response) {
			// Redirect if payment page loads
			if (response.redirect) window.location.href = response.redirect;
			else {
				$("#alerts").html(`<div class="alert alert-success mt-4 p-4">Your sessions have been booked.</div>`);
				// Refresh sessions
				loadSessions($(".activity-button:first"));
				// Wipe basket
				$("#basket-list").empty();
			}
		},
		error: function (response) {
			// If we have an error response, display alert
			errors = response.responseJSON.errors;
			if (errors) {
				$("#alerts").html(`<ul class="alert alert-warning mt-4 p-4" id="alerts-errors"></ul>`);
				for (let i = 0; i < errors.length; i++) {
					$("#alerts-errors").append(`<li>Basket item ${i + 1}: ${errors[i]}</li>`);
				}
				// Else we have failed responses
			} else $("#alerts").html(`<ul class="alert alert-danger mt-4 p-4">There seems to have been an error, please try again later</ul>`);
		},
	});
});
