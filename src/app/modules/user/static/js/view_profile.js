document.addEventListener('DOMContentLoaded', function () {
    const deleteButton = document.getElementById('delete-btn');
    const deleteUserId = deleteButton.getAttribute('data-id');
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const confirmationModal = document.getElementById('confirmationModal');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const modalQuestion = document.getElementById('modalQuestion');

    const roleList = document.querySelector('.role-list');
    const userId = roleList.getAttribute('data-user-id');

    function openModal() {
        modalQuestion.textContent = `Are you sure you want to delete this user?`;
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
        formData.append('user_id', deleteUserId);
        console.log(deleteUserId);

        fetch('/user/delete', {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken,
                'Accept': 'application/json'
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
                localStorage.setItem('flash_message', message || 'User deleted successfully!');
                localStorage.setItem('flash_type', 'success');
            } else if (status === 403) {
                localStorage.setItem('flash_message', message || 'You do not have permission to delete this user.');
                localStorage.setItem('flash_type', 'error');
            } else {
                localStorage.setItem('flash_message', message || 'Failed to delete user.');
                localStorage.setItem('flash_type', 'error');
            }

        })
        .catch(error => {
            console.error('Error:', error);
            localStorage.setItem('flash_message', 'An error occurred.');
            localStorage.setItem('flash_type', 'error');
        })
        .finally(() => {
            window.location.replace('/user/list');
        });
    });

    cancelBtn.addEventListener('click', closeModal);

    window.addEventListener('click', function (event) {
        if (event.target === confirmationModal) {
            closeModal();
        }
    });

    document.querySelectorAll('.delete-role').forEach(button => {
        button.addEventListener('click', function() {
            const roleId = this.getAttribute('data-role-id');

            const formData = new FormData();
            formData.append('user_id', userId);
            formData.append('role_id', roleId);

            fetch('/user/remove_role', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Accept': 'application/json'
                },
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    localStorage.setItem('flash_message', 'Role deleted successfully!');
                    localStorage.setItem('flash_type', 'success');
                    window.location.reload();
                } else if (response.status === 403) {
                    localStorage.setItem('flash_message', 'You do not have permission to perform this action.');
                    localStorage.setItem('flash_type', 'error');
                } else {
                    localStorage.setItem('flash_message', 'Failed to delete the role.');
                    localStorage.setItem('flash_type', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                localStorage.setItem('flash_message', 'An error occurred.');
                localStorage.setItem('flash_type', 'error');
            })
            .finally(() => {
                window.location.reload();
            });
        });
    });
});