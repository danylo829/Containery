const saveBtn = document.getElementById('save-btn');
const deleteBtn = document.getElementById('delete-btn');

saveBtn.addEventListener('click', function (e) {
    e.preventDefault();
    document.getElementById('role-form').submit();
});

if (deleteBtn) {
    deleteBtn.addEventListener('click', function() {
        const id = this.getAttribute('data-id');
        openModal(`role/delete?id=${id}`, 'DELETE', 'Are you sure you want to delete this role?', 'role/list');
    });
}

document.querySelectorAll('.toggle-category').forEach(toggleCheckbox => {
    toggleCheckbox.addEventListener('change', () => {
    const category = toggleCheckbox.getAttribute('data-category');
    const checkboxes = document.querySelectorAll(`.category-checkbox[data-category="${category}"]`);
    
    checkboxes.forEach(checkbox => {
        checkbox.checked = toggleCheckbox.checked;
    });
    });
});