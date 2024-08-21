$(document).ready(function() {
    let selectedDepartureId = null;
    let selectedReturnId = null;

    // Lấy số lượng hành khách từ input
    let numPassengers = $("#num_passengers").val();

    // Khi chọn một chuyến bay đi
    $(".single-booking-item.departure").click(function() {
        $(".single-booking-item.departure").removeClass("selected");
        $(this).addClass("selected");
        selectedDepartureId = $(this).data("flight-ticket-type-id");
        console.log("Selected Departure ID:", selectedDepartureId);
    });

    // Khi chọn một chuyến bay về
    $(".single-booking-item.return").click(function() {
        $(".single-booking-item.return").removeClass("selected");
        $(this).addClass("selected");
        selectedReturnId = $(this).data("flight-ticket-type-id");
        console.log("Selected Return ID:", selectedReturnId);
    });

    // Khi nhấn nút "Booking"
    $(".new-flights-btn").click(function() {
        numPassengers = $("#num_passengers").val();  // Cập nhật giá trị num_passengers
        if (selectedDepartureId) {
            let url = "selectflight/?depatureId=" + selectedDepartureId;
            if (selectedReturnId) {
                url += "&returnId=" + selectedReturnId;
            }
            if (numPassengers) {
                url += "&numPassengers=" + numPassengers;
            }
            console.log("Redirecting to:", url);
            window.location.href = url;
        } else {
            alert('Please select a departure flight.');
        }
    });
});
