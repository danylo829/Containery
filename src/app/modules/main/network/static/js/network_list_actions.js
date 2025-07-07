document.querySelectorAll('.prune-btn').forEach(button => {
    button.addEventListener('click', function() {
        openModal(`/network/api/prune`, 'POST', 'Are you sure you want to delete all unused networks?', '/network/list');
    });
});
