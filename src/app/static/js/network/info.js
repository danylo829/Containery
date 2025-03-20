document.addEventListener('DOMContentLoaded', function () {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const confirmationModal = document.getElementById('confirmationModal');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const modalQuestion = document.getElementById('modalQuestion');
    let networkId = null;

    function openModal(id) {
        networkId = id;
        modalQuestion.textContent = `Are you sure you want to delete this image?`;
        confirmDeleteBtn.textContent = `Delete`;
        confirmationModal.style.display = 'block';
    }

    function closeModal() {
        confirmationModal.style.display = 'none';
        networkId = null;
    }
    
    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            openModal(id);
        });
    });

    confirmDeleteBtn.addEventListener('click', function () {
        const spinner = document.querySelector('.loading-spinner');
        spinner.classList.remove('hidden');
        actions.classList.add('disabled');

        fetch(`/network/${networkId}/delete`, {
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
        if (response.status === 204) {
            localStorage.setItem('flash_message', 'Network deleted successfully');
            localStorage.setItem('flash_type', 'success');
            window.location.href = '/network/list'; 
        } else if (response.status === 403) {
            localStorage.setItem('flash_message', 'Docker or permissions error');
            localStorage.setItem('flash_type', 'error');
            window.location.reload();
        } else {
            localStorage.setItem('flash_message', 'Failed to perform action');
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