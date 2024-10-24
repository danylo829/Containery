document.addEventListener('DOMContentLoaded', function () {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const confirmationModal = document.getElementById('confirmationModal');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const modalQuestion = document.getElementById('modalQuestion');
    let containerId = null;

    function openModal(id) {
        containerId = id;
        modalQuestion.textContent = `Are you sure you want to delete this container?`;
        confirmDeleteBtn.textContent = `Delete`;
        confirmationModal.style.display = 'block';
    }

    function closeModal() {
        confirmationModal.style.display = 'none';
        containerId = null;
    }
    
    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            openModal(id);
        });
    });

    document.querySelectorAll('.start-btn').forEach(button => {
        button.addEventListener('click', function() {
            const containerId = this.getAttribute('data-id');
    
            const spinner = document.querySelector('.loading-spinner');
            spinner.style.display = 'flex';
            spinner.style.animation = 'spin 1s linear infinite';
    
            fetch(`/container/api/${containerId}/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
            })
            .then(response => handleResponse(response, 'started'))
            .catch(error => handleError(error));
        });
    });
    
    document.querySelectorAll('.restart-btn').forEach(button => {
        button.addEventListener('click', function() {
            const containerId = this.getAttribute('data-id');
    
            const spinner = document.querySelector('.loading-spinner');
            spinner.style.display = 'flex';
            spinner.style.animation = 'spin 1s linear infinite';
    
            fetch(`/container/api/${containerId}/restart`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
            })
            .then(response => handleResponse(response, 'restarted'))
            .catch(error => handleError(error));
        });
    });
    
    document.querySelectorAll('.stop-btn').forEach(button => {
        button.addEventListener('click', function() {
            const containerId = this.getAttribute('data-id');
    
            const spinner = document.querySelector('.loading-spinner');
            spinner.style.display = 'flex';
            spinner.style.animation = 'spin 1s linear infinite';
    
            fetch(`/container/api/${containerId}/stop`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
            })
            .then(response => handleResponse(response, 'stopped'))
            .catch(error => handleError(error));
        });
    });

    confirmDeleteBtn.addEventListener('click', function () {
        const spinner = document.querySelector('.loading-spinner');
        spinner.style.display = 'flex';
        spinner.style.animation = 'spin 1s linear infinite';

        fetch(`/container/api/${containerId}/delete`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
        })
        .then(response => handleResponse(response, 'deleted'))
        .catch(error => handleError(error));
    });

    function handleResponse(response, action) {
        if (response.status === 204) {
            localStorage.setItem('flash_message', `Container ${action} successfully!`);
            localStorage.setItem('flash_type', 'success');
        } else if (response.status === 403) {
            localStorage.setItem('flash_message', 'You do not have permission to perform this action.');
            localStorage.setItem('flash_type', 'error');
        } else {
            localStorage.setItem('flash_message', 'Failed to perform action.');
            localStorage.setItem('flash_type', 'error');
        }
        
        if (response.status == 204 && action == 'deleted') {
            window.location.href = '/container/list'; 
        } else {
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