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
    handleDeleteModal();
});

function handleDeleteModal() {
    const deleteModal = document.getElementById("deleteModal");
    if (!deleteModal) return;
    deleteModal.addEventListener("show.bs.modal", function (event) {
        const button = event.relatedTarget;
        const deleteUrl = button.getAttribute("data-delete-url");
        const form = document.getElementById("deleteRideForm");
        form.action = deleteUrl;
    });
}
