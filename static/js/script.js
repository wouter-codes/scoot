/* global document */
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
        // Set modal title, body, and confirm button text dynamically
        const modalTitle = rideModal.querySelector(".modal-title");
        const modalBody = document.getElementById("rideModalBody");
        const confirmBtn = document.getElementById("rideModalConfirmBtn");
        if (button && modalTitle && modalBody && confirmBtn) {
            const actionText = button.textContent.trim(); // "Delete" or "Cancel"
            if (actionText === "Delete") {
                modalTitle.textContent = "Confirm Delete";
                modalBody.textContent =
                    "Are you sure you want to delete this ride?";
                confirmBtn.textContent = "Yes, delete";
            } else {
                modalTitle.textContent = "Confirm Cancellation";
                modalBody.innerHTML = `
                    <p>Are you sure you want to cancel this ride? If cancelled:</p>
                    <ul>
                        <li>All passengers with existing ride requests will be notified</li>
                        <li>Ride will be removed from active listings</li>
                    </ul>
                `;
                confirmBtn.textContent = "Yes, cancel";
            }
        }
    });
}

document.addEventListener("DOMContentLoaded", function () {
    handleRideModal();
    handleRideRequestModal();
});

// Handle publish modal for edit ride form
document.addEventListener("DOMContentLoaded", function () {
    const openPublishModalBtn = document.getElementById("openPublishModalBtn");
    const confirmPublishBtn = document.getElementById("confirmPublishBtn");
    const publishHiddenInput = document.getElementById("publishHiddenInput");
    // Support both create and edit forms
    const rideForm =
        document.getElementById("editRideForm") ||
        document.getElementById("createRideForm");
    if (
        openPublishModalBtn &&
        confirmPublishBtn &&
        rideForm &&
        publishHiddenInput
    ) {
        // Publish: set hidden input and submit
        confirmPublishBtn.addEventListener("click", function () {
            publishHiddenInput.value = "1";
            rideForm.submit();
        });
        // Save as Draft: clear hidden input before submit
        const saveDraftBtn = document.getElementById("saveDraftBtn");
        if (saveDraftBtn) {
            saveDraftBtn.addEventListener("click", function (e) {
                e.preventDefault();
                publishHiddenInput.value = "0";
                rideForm.submit();
            });
        }
        // Optional: clear hidden input on modal close
        document
            .getElementById("publishModal")
            .addEventListener("hidden.bs.modal", function () {
                publishHiddenInput.value = "";
            });
    }
});
