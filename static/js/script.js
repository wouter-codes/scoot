// Add hover effect to clickable ride cards
document.addEventListener("DOMContentLoaded", function () {
    const cardLinks = document.querySelectorAll(".card-link-wrapper");
    cardLinks.forEach(function (link) {
        // Find the parent .card element
        let card = link.closest(".card");
        // If not found, try child .card (for my_rides)
        if (!card) card = link.querySelector(".card");
        if (!card) return;
        link.addEventListener("mouseenter", function () {
            card.classList.add("shadow-lg", "card-hover");
        });
        link.addEventListener("mouseleave", function () {
            card.classList.remove("shadow-lg", "card-hover");
        });
    });
});

// JavaScript to handle the delete confirmation modal

document.addEventListener("DOMContentLoaded", function () {
    handleRideModal();
    handleRideRequestModal();
});

function handleRideRequestModal() {
    const rideRequestModal = document.getElementById("rideRequestModal");
    if (!rideRequestModal) return;
    rideRequestModal.addEventListener("show.bs.modal", function (event) {
        const button = event.relatedTarget;
        const actionUrl = button.getAttribute("data-cancel-url");
        const form = document.getElementById("rideRequestForm");
        if (form && actionUrl) {
            form.action = actionUrl;
        }

        // Set modal title, body, and confirm button text dynamically
        const modalTitle = rideRequestModal.querySelector(".modal-title");
        const modalBody = rideRequestModal.querySelector(".modal-body");
        const confirmBtn = rideRequestModal.querySelector(
            ".modal-footer .btn.btn-danger",
        );
        if (button && modalTitle && modalBody && confirmBtn) {
            const actionText = button.textContent.trim(); // "Delete" or "Cancel"
            if (actionText === "Delete") {
                modalTitle.textContent = "Confirm Delete";
                modalBody.textContent =
                    "Are you sure you want to delete this ride request?";
                confirmBtn.textContent = "Yes, delete";
            } else {
                modalTitle.textContent = "Confirm Cancellation";
                modalBody.textContent =
                    "Are you sure you want to cancel this ride request?";
                confirmBtn.textContent = "Yes, cancel";
            }
        }
    });
}

function handleRideModal() {
    const rideModal = document.getElementById("rideModal");
    if (!rideModal) return;
    rideModal.addEventListener("show.bs.modal", function (event) {
        const button = event.relatedTarget;
        const deleteUrl = button.getAttribute("data-delete-url");
        const form = document.getElementById("rideForm");
        if (form && deleteUrl) {
            form.action = deleteUrl;
        }
    });
}
