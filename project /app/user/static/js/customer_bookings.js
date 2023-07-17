modalActions = {
	// Cancel booking modal
	cancelBooking: function (bookingId) {
		$.ajax({
			url: "/delete_booking",
			type: "POST",
			data: JSON.stringify({ booking_id: bookingId }),
			contentType: "application/json; charset=utf-8",
			dataType: "json",
			success: function (response) {
				window.location = response.url;
			},
		});
	},
	// Delete account modal
	deleteAccount: function (customerId) {
		$.ajax({
			url: "/delete_account",
			type: "POST",
			data: JSON.stringify({ customer_id: customerId }),
			contentType: "application/json; charset=utf-8",
			dataType: "json",
			success: function (response) {
				window.location = response.url;
			},
		});
	},
};

$(".btn-ok").click(function () {
	// Call the action
	action = $("#confirm-modal").data("action");
	argument = $("#confirm-modal").data("argument");
	modalActions[action](argument);
});

$(".requires-confirm").click(function () {
	const action = $(this).data("action");
	const argument = $(this).data("argument");
	// Set the modal action
	$("#confirm-modal").data("action", action).data("argument", argument);
});

function changePeople(button, increment) {
	// Get booking data
	const bookingId = $(button).data("booking-id");
	// Get the number of people
	const change = $(`#booking-${bookingId}, #collapse-edit-${bookingId}`).find(".booking-number_of_people");
	const costItem = $(`#booking-${bookingId}`).find(".booking-cost");
	const price = $(button).data("price");
	$.ajax({
		url: "/change_people",
		type: "POST",
		data: JSON.stringify({ booking_id: bookingId, increment }),
		contentType: "application/json; charset=utf-8",
		dataType: "json",
		success: function (response) {
			// Update the number of people and cost
			change.html(response.number_of_people);
			costItem.html("£" + parseFloat(response.cost).toFixed(2));
		},
		error: function (error) {
			console.log(error);
		},
	});
}

// Change number of people based on increment button
$(".increment").click(function () {
	changePeople(this, true);
});
$(".decrement").click(function () {
	changePeople(this, false);
});

$(".date-time-button").click(function () {
	const bookingId = $(this).data("booking-id");
	// Query activity for sessions
	$.ajax({
		url: "/sessions",
		type: "POST",
		// Send booking id
		data: JSON.stringify({ booking_id: bookingId }),
		contentType: "application/json; charset=utf-8",
		dataType: "json",
		success: function (response) {
			// Display sessions table
			$(`.sessions-table[data-booking-id="${bookingId}"]`).html(response.rendered);
		},
		error: function (error) {
			console.log(error);
		},
	});
});

$(".sessions-table").on("click", ".session-button", function () {
	const bookingId = $(this).closest(".sessions-table").data("booking-id");
	const date = $(this).data("date");
	const time = $(this).data("time");
	$.ajax({
		url: "/change_date_time",
		type: "POST",
		// Send activity booking data
		data: JSON.stringify({ booking_id: bookingId, date, time }),
		contentType: "application/json; charset=utf-8",
		dataType: "json",
		success: function (response) {
			// Display new date and time
			$(`#booking-${bookingId}`).children(".booking-date").text(date);
			$(`#booking-${bookingId}`).children(".booking-time").text(time);
			// Close out of date time window
			$(`.date-time-button[data-booking-id="${bookingId}"]`).attr("aria-expanded", "false").addClass("collapsed");
			$(`#edit-date-time-${bookingId}`).removeClass("show");
		},
		error: function (error) {
			console.log(error);
		},
	});
});
