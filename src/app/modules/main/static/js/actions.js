document.querySelectorAll('.restart-btn').forEach(button => {
    button.addEventListener('click', function() {
        const containerId = this.getAttribute('data-id');
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

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
        .then(response => {
            if (response.status === 204) {
                localStorage.setItem('flash_message', 'Container restarted successfully!');
                localStorage.setItem('flash_type', 'success');
            } else if (response.status === 403) {
                localStorage.setItem('flash_message', 'You do not have permission to restart containers.');
                localStorage.setItem('flash_type', 'error');
            } else {
                localStorage.setItem('flash_message', 'Failed to restart container.');
                localStorage.setItem('flash_type', 'error');
            }
            window.location.reload();
        })
        .catch(error => {
            localStorage.setItem('flash_message', 'An error occurred.');
            localStorage.setItem('flash_type', 'error');
            window.location.reload();
        });
    });
});
