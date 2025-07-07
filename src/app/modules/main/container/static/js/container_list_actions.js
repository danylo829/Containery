document.querySelectorAll('.prune-btn').forEach(button => {
    button.addEventListener('click', function() {
        openModal(`/container/api/prune`, 'POST', 'Are you sure you want to delete all stopped containers?', '/container/list');
    });
});