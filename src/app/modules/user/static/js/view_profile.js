document.addEventListener('DOMContentLoaded', function () {
    const roleList = document.querySelector('.role-list');
    const userId = roleList.getAttribute('data-user-id');
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    document.querySelectorAll('.delete-role').forEach(button => {
        button.addEventListener('click', function() {
            const roleId = this.getAttribute('data-role-id');

            const formData = new FormData();
            formData.append('user_id', userId);
            formData.append('role_id', roleId);

            fetch('/user/remove_role', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
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