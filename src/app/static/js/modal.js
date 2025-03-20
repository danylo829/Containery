function closeModal() {
    confirmationModal.style.display = 'none';
}

function openModal(url, method, question, returnUrl) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const confirmationModal = document.getElementById('confirmationModal');
    const confirmBtn = document.getElementById('confirmBtn');
    const modalQuestion = document.getElementById('modalQuestion');

    const actions = document.querySelector('.actions');

    modalQuestion.textContent = question;
    confirmationModal.style.display = 'block';

    confirmBtn.addEventListener('click', function () {
        const spinner = document.querySelector('.loading-spinner');
        spinner.classList.remove('hidden');

        if (actions) {
            actions.classList.add('disabled');
        }

        closeModal();

        fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
        })
        .then(response => handleResponse(response, returnUrl))
        .catch(error => handleError(error));
    });
}

document.addEventListener('DOMContentLoaded', function () {
    const confirmationModal = document.getElementById('confirmationModal');
    const cancelBtn = document.getElementById('cancelBtn');

    cancelBtn.addEventListener('click', closeModal);
    window.addEventListener('click', function (event) {
        if (event.target === confirmationModal) {
            closeModal();
        }
    });
});