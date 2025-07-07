document.querySelectorAll('.prune-btn').forEach(button => {
    button.addEventListener('click', function() {
        openModal(`/image/api/prune`, 'POST', 'Are you sure you want to delete all unused images?', '/image/list');
    });
});
