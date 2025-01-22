document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.toggle-category').forEach(toggleCheckbox => {
        toggleCheckbox.addEventListener('change', () => {
        const category = toggleCheckbox.getAttribute('data-category');
        const checkboxes = document.querySelectorAll(`.category-checkbox[data-category="${category}"]`);
        
        checkboxes.forEach(checkbox => {
            checkbox.checked = toggleCheckbox.checked;
        });
        });
    });
});