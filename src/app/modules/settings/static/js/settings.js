function resetSetting(fieldName) {
    spinner.classList.remove('hidden');
    actions.classList.add('disabled');

    fetch(`/settings/reset`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            field_name: fieldName
        })
    })
    .then(response => handleResponse(response))
    .catch(error => handleError(error))
}
