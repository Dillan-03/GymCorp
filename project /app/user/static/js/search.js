$(document).ready(function() {
	// Check if data is entered in search bar
	$('#search-bar').keyup(function(event) {
		// Save the data
		var query = $(this).val();
		// Respond to data by altering the customer table
		$.ajax({
			url: '/respond_search',
			type: 'GET',
			data: {'query': query},
			success: function(response){
				$('#customer-table').html(response);
			},
			error: function(error){
                console.log(error);
            }
		});
	});
});