const upload = document.querySelector('input[type="file"][multiple]');
if (upload) upload.addEventListener('change', () => {
    document.getElementById('selected-files').textContent = Array.from(upload.files, file => file.name).join('، ');
    document.getElementById('upload-status').textContent = upload.files.length ? `تم اختيار ${upload.files.length} ملفات` : 'لا توجد ملفات مختارة';
});

const deleteDialog = document.getElementById('delete-dialog');
if (deleteDialog && document.querySelector('[data-delete-open]')) {
    document.querySelector('[data-delete-open]').addEventListener('click', () => {
        deleteDialog.showModal();
        deleteDialog.querySelector('[data-delete-close]').focus();
    });
    deleteDialog.querySelectorAll('[data-delete-close]').forEach(button => button.addEventListener('click', () => deleteDialog.close()));
    deleteDialog.addEventListener('click', event => {
        if (event.target === deleteDialog) {
            const box = deleteDialog.getBoundingClientRect();
            if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) deleteDialog.close();
        }
    });
}
