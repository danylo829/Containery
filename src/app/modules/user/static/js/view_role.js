document.addEventListener('DOMContentLoaded', function () {
    const deleteButton = document.getElementById('delete-role-btn');
    const roleId = deleteButton.getAttribute('data-role-id');
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const confirmationModal = document.getElementById('confirmationModal');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const modalQuestion = document.getElementById('modalQuestion');

    function openModal() {
        modalQuestion.textContent = `Are you sure you want to delete this role?`;
        confirmDeleteBtn.textContent = `Delete`;
        confirmationModal.style.display = 'block';
    }

    function closeModal() {
        confirmationModal.style.display = 'none';
    }
    
    deleteButton.addEventListener('click', function () {
        openModal();
    });

    confirmDeleteBtn.addEventListener('click', function () {
        const formData = new FormData();
        formData.append('role_id', roleId);

        fetch('/user/role/delete', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData
        })
        .then(response => {
            return response.json().then(data => ({
                status: response.status,
                message: data.message
            }));
        })
        .then(result => {
            const { status, message } = result;
            if (status === 200) {
                localStorage.setItem('flash_message', message || 'Role deleted successfully!');
                localStorage.setItem('flash_type', 'success');
            } else {
                localStorage.setItem('flash_message', message || 'Failed to delete the role.');
                localStorage.setItem('flash_type', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            localStorage.setItem('flash_message', 'An error occurred.');
            localStorage.setItem('flash_type', 'error');
        })
        .finally(() => {
            window.location.replace('/user/role/list');
        });
    });

    cancelBtn.addEventListener('click', closeModal);

    confirmationModal.querySelector('.close').addEventListener('click', closeModal);

    window.addEventListener('click', function (event) {
        if (event.target === confirmationModal) {
            closeModal();
        }
    });
});
