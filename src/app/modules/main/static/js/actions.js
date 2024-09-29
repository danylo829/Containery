document.querySelectorAll('.start-btn').forEach(button => {
    button.addEventListener('click', function() {
        const containerId = this.getAttribute('data-id');
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

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
        .catch(error => handleError());
    });
});

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
        .then(response => handleResponse(response, 'restarted'))
        .catch(error => handleError());
    });
});

document.querySelectorAll('.stop-btn').forEach(button => {
    button.addEventListener('click', function() {
        const containerId = this.getAttribute('data-id');
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

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
        .catch(error => handleError());
    });
});

document.querySelectorAll('.delete-btn').forEach(button => {
    button.addEventListener('click', function() {
        const containerId = this.getAttribute('data-id');
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

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
        .catch(error => handleError());
    });
});

function handleResponse(response, action) {
    if (response.status === 204) {
        localStorage.setItem('flash_message', `Container ${action} successfully!`);
        localStorage.setItem('flash_type', 'success');
    } else if (response.status === 403) {
        localStorage.setItem('flash_message', `You do not have permission to ${action} containers.`);
        localStorage.setItem('flash_type', 'error');
    } else {
        localStorage.setItem('flash_message', 'Failed to perform action.');
        localStorage.setItem('flash_type', 'error');
    }
    if (action != 'deleted') {
        window.location.reload();   
    } else {
        window.location.href = '/container/list';
    }
}

function handleError() {
    localStorage.setItem('flash_message', 'An error occurred.');
    localStorage.setItem('flash_type', 'error');
    window.location.reload();
}

