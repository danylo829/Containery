document.querySelectorAll('.prune-btn').forEach(button => {
    button.addEventListener('click', function() {
        url = `/dashboard/api/prune`;
        method = 'POST';
        message = 'Are you sure you want to delete all unused data and build cache? This cannot be undone.';
        return_url = '/dashboard/info';
        
        openModal(url, method, message, return_url);
    });
});