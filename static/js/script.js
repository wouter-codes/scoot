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
