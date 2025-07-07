document.querySelectorAll('.prune-btn').forEach(button => {
    button.addEventListener('click', function() {
        openModal(`/volume/api/prune`, 'POST', 'Are you sure you want to delete all unused volumes?', '/volume/list');
    });
});
