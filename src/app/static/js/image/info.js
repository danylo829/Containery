document.addEventListener('DOMContentLoaded', function () {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const confirmationModal = document.getElementById('confirmationModal');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const modalQuestion = document.getElementById('modalQuestion');
    let imageId = null;

    function openModal(id) {
        imageId = id;
        modalQuestion.textContent = `Are you sure you want to delete this image?`;
        confirmDeleteBtn.textContent = `Delete`;
        confirmationModal.style.display = 'block';
    }

    function closeModal() {
        confirmationModal.style.display = 'none';
        imageId = null;
    }
    
    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            openModal(id);
        });
    });

    confirmDeleteBtn.addEventListener('click', function () {
        const spinner = document.querySelector('.loading-spinner');
        spinner.style.display = 'flex';
        spinner.style.animation = 'spin 1s linear infinite';

        fetch(`/image/${imageId}/delete`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
        })
        .then(response => handleResponse(response))
        .catch(error => handleError(error));
    });

    function handleResponse(response) {
        if (response.status === 200) {
            localStorage.setItem('flash_message', 'Image deleted successfully!');
            localStorage.setItem('flash_type', 'success');
            window.location.href = '/image/list'; 
        } else if (response.status === 403) {
            localStorage.setItem('flash_message', 'You do not have permission to perform this action.');
            localStorage.setItem('flash_type', 'error');
            window.location.reload();
        } else {
            localStorage.setItem('flash_message', 'Failed to perform action.');
            localStorage.setItem('flash_type', 'error');
            window.location.reload();
        }
    }

    function handleError(error) {
        localStorage.setItem('flash_message', `An error occurred: ${error}`);
        localStorage.setItem('flash_type', 'error');
        window.location.reload();
    }

    cancelBtn.addEventListener('click', closeModal);

    window.addEventListener('click', function (event) {
        if (event.target === confirmationModal) {
            closeModal();
        }
    });
});