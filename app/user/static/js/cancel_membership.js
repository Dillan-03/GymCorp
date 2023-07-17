modalActions = {
	// Cancel membership modal
	cancelMembership: function () {
		$.ajax({
			url: "/cancel_subscription",
			type: "POST",
			success: function (response) {
				window.location = response.url;
			},
		});
	},
	// Renew membership modal
	renewMembership: function () {
		$.ajax({
			url: "/renew_subscription",
			type: "POST",
			success: function (response) {
				window.location = response.url;
			},
		});
	},
};

$(".btn-ok").click(function () {
	console.log("hi");
	action = $("#confirm-modal").data("action");
	// Call the action
	modalActions[action]();
});

$(".requires-confirm").click(function () {
	// Set the modal action
	const action = $(this).data("action");
	$("#confirm-modal").data("action", action);
});
