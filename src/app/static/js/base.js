document.addEventListener('DOMContentLoaded', function() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    spinner = document.querySelector('.loading-spinner');
    spinner.style.display = 'none';

    document.querySelector('.user-icon').addEventListener('click', function() {
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

        fetch('/toggle_sidebar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
        });
    });

    const flashMessage = localStorage.getItem('flash_message');
    const flashType = localStorage.getItem('flash_type');

    if (flashMessage) {
        // Create a flash message container if it doesn't exist
        let flashContainer = document.querySelector('.flash-messages');
        if (!flashContainer) {
            flashContainer = document.createElement('div');
            flashContainer.className = 'flash-messages';
            document.body.appendChild(flashContainer);
        }

        // Create the flash message element
        const flashElement = document.createElement('div');
        flashElement.className = `flash-message ${flashType}`;
        flashElement.textContent = flashMessage;

        // Append the flash message to the container
        flashContainer.appendChild(flashElement);

        // Clear the flash message from localStorage
        localStorage.removeItem('flash_message');
        localStorage.removeItem('flash_type');
    }
});