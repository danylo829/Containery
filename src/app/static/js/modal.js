function createModal() {
    const modal = document.createElement('div');
    modal.id = 'confirmationModal';
    modal.className = 'modal';

    const modalContent = document.createElement('div');
    modalContent.className = 'modal-content';

    const question = document.createElement('p');
    question.id = 'modalQuestion';
    question.textContent = 'Are you sure you want to perform this action?';

    const buttonGroup = document.createElement('div');
    buttonGroup.className = 'button-group';

    const cancelBtn = document.createElement('button');
    cancelBtn.id = 'cancelBtn';
    cancelBtn.className = 'btn cancel';
    cancelBtn.textContent = 'Cancel';

    const confirmBtn = document.createElement('button');
    confirmBtn.id = 'confirmBtn';
    confirmBtn.className = 'btn delete';
    confirmBtn.textContent = 'Confirm';

    // Build hierarchy
    buttonGroup.appendChild(cancelBtn);
    buttonGroup.appendChild(confirmBtn);
    modalContent.appendChild(question);
    modalContent.appendChild(buttonGroup);
    modal.appendChild(modalContent);

    return modal;
}

function closeModal() {
    const modal = document.getElementById('confirmationModal');
    if (modal) {
        modal.remove();
    }
}

function openModal(url, method, question, returnUrl) {
    const confirmationModal = createModal();
    const confirmBtn = confirmationModal.querySelector('#confirmBtn');
    const cancelBtn = confirmationModal.querySelector('#cancelBtn');
    const modalQuestion = confirmationModal.querySelector('#modalQuestion');

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

    cancelBtn.addEventListener('click', closeModal);

    window.addEventListener('click', function (event) {
        if (event.target === confirmationModal) {
            closeModal();
        }
    });

    document.body.appendChild(confirmationModal);
}