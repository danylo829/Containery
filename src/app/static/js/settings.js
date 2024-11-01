function resetSetting(fieldName) {
    const csrfToken = document.querySelector('input[name="csrf_token"]').value;
    const spinner = document.querySelector('.loading-spinner');
    spinner.style.display = 'flex';
    spinner.style.animation = 'spin 1s linear infinite';

    const formData = new FormData();
    formData.append('csrf_token', csrfToken);
    formData.append('field_name', fieldName);

    fetch(`/settings/reset`, {
        method: 'POST',
        body: formData
    })
    .then(response => handleResetResponse(response))
    .catch(error => handleResetError(error))
    .finally(() => {
        spinner.style.display = 'none';
    });
}

function handleResetResponse(response) {
    if (response.ok) {
        localStorage.setItem('flash_message', 'Setting reset successfully');
        localStorage.setItem('flash_type', 'success');
        window.location.reload();
    } else if (response.status === 403) {
        localStorage.setItem('flash_message', 'Permission denied');
        localStorage.setItem('flash_type', 'error');
        window.location.reload();
    } else {
        response.json().then(data => {
            const errorMessage = data.error || 'Failed to reset setting';
            localStorage.setItem('flash_message', errorMessage);
            localStorage.setItem('flash_type', 'error');
            window.location.reload();
        }).catch(() => {
            // Fallback in case parsing fails
            localStorage.setItem('flash_message', 'An unknown error occurred.');
            localStorage.setItem('flash_type', 'error');
            window.location.reload();
        });
    }
}

function handleResetError(error) {
    localStorage.setItem('flash_message', `An error occurred: ${error}`);
    localStorage.setItem('flash_type', 'error');
    window.location.reload();
}
