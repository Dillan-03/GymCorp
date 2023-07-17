// Load sessions into the table
function loadSessions(button) {
	// Get activity and facility id
	activityId = button.data("activity-id");
	facilityId = button.data("facility-id");
	// Query activity for sessions
	$.ajax({
		url: "/sessions",
		type: "POST",
		// Send activity data
		data: JSON.stringify({ activity_id: activityId, facility_id: facilityId }), //{ activity: activityData, facility: facilityData }),
		contentType: "application/json; charset=utf-8",
		dataType: "json",
		success: function (response) {
			// Unhighlight other buttons
			$(".activity-button").removeClass("active");
			// Highlight button
			button.addClass("active");
			// Change active facility/activity/session so code knows what table is showing
			sessionStorage.setItem("active-activity", JSON.stringify(response.activity));
			sessionStorage.setItem("active-facility", JSON.stringify(response.facility));
			sessionStorage.setItem("active-sessions", JSON.stringify(response.sessions));
			// Change sessions header
			$("#sessions-header").text(response.facility.name + " - " + response.activity.name + " - " + response.activity.duration + " minutes");
			// Display sessions table
			$("#sessions-table").html(response.rendered);
			// Incase we have items in the basket we must color our items and change the number of people going
			// Loop through all items in basket
			$("#basket-list")
				.children("")
				.each(function () {
					// Get the basket item
					const basketItem = $(this);
					// Get the activity id, date and time from basket items
					const activityId = basketItem.data("activity-id");
					const date = basketItem.data("date");
					const time = basketItem.data("time");
					// If activity id does not match, we can skip
					if (activityId != response.activity.id) return;
					// Get the button element to change color
					const button = $(`.session-button[data-date="${date}"][data-time="${time}"]`);
					button.removeClass("btn-primary");
					button.addClass("btn-success");
					// Change number of people going if not a booking type
					if (response.activity.booking_type != "BookingTypes.BOOKING") changeNumberOfPeople(basketItem.find("input"));
				});
		},
		error: function (error) {
			console.log(error);
		},
	});
}

// Change the number of people going to session
function changeNumberOfPeople(input) {
	// Get active activity
	const activityData = JSON.parse(sessionStorage.getItem("active-activity"));
	// Get data from the parent element
	const basketItem = input.closest(".basket-item");
	const activityId = basketItem.data("activity-id");
	const date = basketItem.data("date");
	const time = basketItem.data("time");
	// Get associated button
	const button = $(`.session-button[data-date="${date}"][data-time="${time}"]`);
	// Incase number of people is changed to zero, remove from basket
	if (input.val() == 0) {
		// If we are on the correct activity, use the predefined method from addSession
		if (activityData.id == activityId) {
			addSession(button);
		}
		// Else just remove the item
		else basketItem.remove();
		return;
	}
	// Calculate the amount of spots left
	const openSpots = input.attr("max") - input.val();
	// Get current open spots text of the basket item
	const openSpotsText = basketItem.find(".open-spots-text");
	// Change the text to the new text
	openSpotsText.text(openSpots);
	// Also want to change the price
	const priceSpan = basketItem.find(".activity-price");
	priceSpan.text("£" + (priceSpan.data("unit-price") * input.val()).toFixed(2));
	// Replace value of the spots left in the table if we are on the same activity
	// Check with active activity
	if (activityData.id == activityId) {
		// Replace value
		button.text(`${openSpots} spots left`);
	}
}

// Add session to the basket
function addSession(button) {
	// Get time and date from button
	const time = button.data("time");
	const date = button.data("date");
	// Hour used for comparing with sessions
	const hour = time.split(":")[0];
	// Get the activity, facility amd sessions data from the active storage item
	const activityData = JSON.parse(sessionStorage.getItem("active-activity"));
	const facilityData = JSON.parse(sessionStorage.getItem("active-facility"));
	const sessionsData = JSON.parse(sessionStorage.getItem("active-sessions"));
	if (button.hasClass("btn-primary")) {
		// Change button colour
		button.removeClass("btn-primary");
		button.addClass("btn-success");
		// Loop through sessions to find correct start time
		let activeSession;
		let openSpots = facilityData.capacity;
		for (const session of sessionsData) {
			// If the start time and date are correct
			if (session.start_time == hour && session.date == date) {
				activeSession = session;
				openSpots -= activeSession.number_of_people;
			}
		}
		// Display in the shopping basket with the data stored
		// If it is a booking type, then the entire facility is booked so we don't care about spots
		if (activityData.booking_type == "BookingTypes.BOOKING") {
			$("#basket-list").append(
				`<li class="list-group-item container-fluid basket-item" data-facility-id=${facilityData.id} data-activity-id=${activityData.id} data-date=${date} data-time=${time}>
					<div class="row justify-content-between">
						<div class="container-fluid row basket-text col-8 col-sm-10 col-xxl-10 p-0">
							<span class="col-12 col-sm-6 col-md-4 col-xxl-3 fw-semibold">${facilityData.name}</span>
							<span class="col-12 col-sm-6 col-md-4 col-xxl-2 fw-semibold">${activityData.name}</span>
							<span class="col-12 col-sm-6 col-md-4 col-xxl-2 fw-semibold basket-date">${date}</span>
							<span class="col-12 col-sm-6 col-md-4 col-xxl-2 fw-semibold">${time}</span>
							<span class="col-12 col-sm-6 col-md-4 col-xxl-3"><span class="fw-semibold">${activityData.duration}</span> minutes</span>
						</div>
						<div class="container-fluid row col-4 col-sm-2 col-xxl-2">
							<button type="button" class="col-12 col-xxl-6 btn btn-danger remove-booking m-0 p-1">Remove</button>
							<span class="col-12 col-xxl-6 m-0 fw-bold text-end activity-price">£${activityData.price}</span>
						</div>
					</div>
				</li>`
			);
		} else {
			// Taking into account the spots remaining and displaying an input where you can change number of people
			$("#basket-list").append(
				`<li class="list-group-item container-fluid basket-item" data-facility-id=${facilityData.id} data-activity-id=${activityData.id} data-date=${date} data-time=${time}>
					<div class="row justify-content-between">
						<div class="container-fluid row basket-text col-8 col-sm-10 col-xxl-10 p-0">
							<span class="col-12 col-sm-6 col-md-4 col-xxl-3 fw-semibold">${facilityData.name}</span>
							<span class="col-12 col-sm-6 col-md-4 col-xxl-2 fw-semibold">${activityData.name}</span>
							<span class="col-12 col-sm-6 col-md-4 col-xxl-2 fw-semibold basket-date">${date}</span>
							<span class="col-12 col-sm-6 col-md-4 col-xxl-2 fw-semibold">${time}</span>
							<span class="col-12 col-sm-6 col-md-4 col-xxl-3"><span class="fw-semibold open-spots-text">${openSpots}</span> spots left</span>
						</div>
						<div class="container-fluid row col-4 col-sm-2 col-xxl-2">
							<input type="number" class="col-12 col-xxl-6 form-control-sm number_of_people m-0" min=0 max=${openSpots} value=1 aria-describedby="number_of_people">
							<span class="col-12 col-xxl-6 m-0 fw-bold text-end activity-price" data-unit-price=${activityData.price}>£${activityData.price}</span>
						</div>
					</div>
				</li>`
			);
			// Change number of people going to 1
			changeNumberOfPeople(
				$(
					`.basket-item[data-facility-id="${facilityData.id}"][data-activity-id="${activityData.id}"][data-date="${date}"][data-time="${time}"]`
				).find("input")
			);
		}
	} else if (button.hasClass("btn-success")) {
		// Change button colour
		button.removeClass("btn-success");
		button.addClass("btn-primary");
		// Change number of open spots back to default
		const basketItem = $(
			`.basket-item[data-facility-id="${facilityData.id}"][data-activity-id="${activityData.id}"][data-date="${date}"][data-time="${time}"]`
		);
		// If type is booking we don't have to change anything
		if (activityData.booking_type != "BookingTypes.BOOKING") button.text(basketItem.find("input").attr("max") + " spots left");
		// Remove from the basket
		basketItem.remove();
	}
}

$(document).ready(function () {
	// Load first button in
	loadSessions($(".activity-button:first"));
});

// Disable typing in number inputs
$("#basket-list").on("keypress", "[type='number']", function (input) {
	input.preventDefault();
});

// On click button event to load sessions
$(".activity-button").on("click", function () {
	loadSessions($(this));
});
// On click button we add session
$(document).on("click", ".session-button", function () {
	addSession($(this));
});

// Bind the inputs to the method
$("#basket-list").on("change", ".number_of_people", function (input) {
	changeNumberOfPeople($(input.target));
});

// Bind the remove booking button
$("#basket-list").on("click", ".remove-booking", function (input) {
	// Get active activity
	const activityData = JSON.parse(sessionStorage.getItem("active-activity"));
	// Get data from the parent element
	const basketItem = $(input.target).closest(".basket-item");
	const activityId = basketItem.data("activity-id");
	const date = basketItem.data("date");
	const time = basketItem.data("time");
	// Get associated button
	const button = $(`.session-button[data-date="${date}"][data-time="${time}"]`);
	// If we are on the correct activity, use the predefined method from addSession
	if (activityData.id == activityId) {
		addSession(button);
	}
	// Else just remove the item
	else basketItem.remove();
	return;
});

// Helper functiont to get distance between two dates
function datediff(first, second) {
	return Math.round((second - first) / (1000 * 60 * 60 * 24));
}

// Detect when the user is eligible for discount off, return dates that are discounted
function discount() {
	// Dates of bookings in basket
	const bookingDates = $(".basket-date")
		.map(function () {
			return $.trim($(this).text());
		})
		.get()
		// Sort the array of dates
		.sort(function (a, b) {
			return new Date(a) - new Date(b);
		});
	if (bookingDates.length == 0) return bookingDates;
	// Members are automatically eligible on all dates
	const membership = $("#customer-membership").data("membership");
	if (membership == "True") {
		// All dates are discounted
		return bookingDates;
	}
	// Map dates to array of distances between each date
	const dayDistances = bookingDates
		.map(function (item, index, array) {
			if (index == array.length - 1) return false;
			const date = new Date(item);
			const nextDate = new Date(array[index + 1]);
			return datediff(date, nextDate);
		})
		.slice(0, bookingDates.length - 1);
	const output = new Set();
	// Loop through distances between dates and if there are 4 dates (3 distances between dates) within 7 days, apply discount
	for (let i = 0; i < dayDistances.length - 2; i++) {
		const total = dayDistances[i] + dayDistances[i + 1] + dayDistances[i + 2];
		// Add to output array if total is less than 7
		if (total <= 7) {
			output.add(bookingDates[i]);
			output.add(bookingDates[i + 1]);
			output.add(bookingDates[i + 2]);
			output.add(bookingDates[i + 3]);
		}
	}
	return Array.from(output);
}

// When the basket changes, update total price
// Create mutation observer to observe basket
const observer = new MutationObserver((mutationList, observer) => {
	for (const mutation of mutationList) {
		// Get discounted dates
		const discountedDates = discount();
		// Get all prices
		let sum = 0.0;
		let discountedSum = 0.0;
		$(".activity-price").each(function () {
			const date = $(this).closest(".basket-item").find(".basket-date").text();
			if (discountedDates.includes(date)) {
				discountedSum += Number($(this).text().replace("£", "")) * $("#discount").data("discount");
			} else discountedSum += Number($(this).text().replace("£", ""));
			sum += Number($(this).text().replace("£", ""));
		});
		// Change the total
		$("#total-price").html("£" + sum.toFixed(2));
		// If we have a discount applied, strike out and show discounted price
		if (discountedDates.length != 0)
			$("#total-price").html(`
  					<span class="fw-semibold text-decoration-line-through fst-italic">
    					£${sum.toFixed(2)}
  					</span>
   					<span class="text-danger">
    					£${discountedSum.toFixed(2)}
  					</span>
			`);
		// Enable/disable the booking button
		bookButton = $("#book-button");
		if (sum == 0.0) bookButton.prop("disabled", true);
		else bookButton.prop("disabled", false);
	}
});

// Pass in the basket list and observe the list of children
observer.observe($("#basket-list")[0], {
	attributes: true,
	childList: true,
	subtree: true,
});
