const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
const spinner = document.querySelector('.loading-spinner');
const actions = document.querySelector('.actions');

setTimeout(function() {
    spinner.classList.add('hidden');
}, 300);

function handleResponse(response, returnUrl) {
    if (response.ok) {
        localStorage.setItem('flash_message',  'Action performed successfully!');
        localStorage.setItem('flash_type', 'success');
        if (returnUrl) {
            window.location.href = returnUrl;
            return;
        }
    } else if (response.status === 403) {
        localStorage.setItem('flash_message', 'You do not have permission to perform this action.');
        localStorage.setItem('flash_type', 'error');
    } else {
        localStorage.setItem('flash_message', 'Failed to perform action.');
        localStorage.setItem('flash_type', 'error');
    }
    
    window.location.reload();
}

function handleError(error) {
    localStorage.setItem('flash_message', `An error occurred: ${error}`);
    localStorage.setItem('flash_type', 'error');
    window.location.reload();
}

document.querySelector('#user-icon').addEventListener('click', function() {
    document.querySelector('.user-panel').classList.toggle('open');
});  

document.getElementById('menu-toggle').addEventListener('click', function () {
    const sidebar = document.querySelector('.sidebar');
    const body = document.querySelector('body');
    sidebar.classList.toggle('closed');

    if (sidebar.classList.contains('closed')) {
        body.style.overflow = 'auto';
    } else {
        body.style.overflow = 'hidden';
    }

    fetch('/toggle-sidebar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    });
});

const flashMessage = localStorage.getItem('flash_message');
const flashType = localStorage.getItem('flash_type');

if (flashMessage) {
    let flashContainer = document.querySelector('.flash-messages');
    if (!flashContainer) {
        flashContainer = document.createElement('div');
        flashContainer.className = 'flash-messages';
        document.body.appendChild(flashContainer);
    }

    const flashElement = document.createElement('div');
    flashElement.className = `flash-message ${flashType}`;
    flashElement.textContent = flashMessage;

    flashContainer.appendChild(flashElement);

    localStorage.removeItem('flash_message');
    localStorage.removeItem('flash_type');
}