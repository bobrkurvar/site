const form = document.getElementById('tile-form');

// Поля, которые всегда необязательные при добавлении
const optionalForAdd = ['color_feature', 'surface', 'images'];

document.getElementById('add-btn').addEventListener('click', () => {
    form.action = "/admin/tiles/create";

    // Все input/textarea/file поля кроме optionalForAdd делаем обязательными
    form.querySelectorAll('input, textarea, select').forEach(el => {
        if (optionalForAdd.includes(el.id) || el.id === 'article') {
            el.required = false;
        } else {
            el.required = true;
        }
    });
});

document.getElementById('update-btn').addEventListener('click', () => {
    form.action = "/admin/tiles/update";

    form.querySelectorAll('input, textarea, select').forEach(el => {
        if (el.id === 'article') {
            el.required = true;
        } else {
            el.required = false;
        }
    });
});

const collectionForm = document.getElementById('collection-form');
const imageInput = document.getElementById('collection_image');
const categorySelect = document.getElementById('category_name');

document.getElementById('create-collection-btn').addEventListener('click', () => {
    collectionForm.action = "/admin/tiles/collections/create";

    imageInput.required = true;
    categorySelect.required = true;
});

document.getElementById('delete-collection-btn').addEventListener('click', () => {
    collectionForm.action = "/admin/tiles/collections/delete";
    imageInput.required = false;
    categorySelect.required = false;
});