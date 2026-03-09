document.getElementById('filtersForm').addEventListener('submit', function(event) {
    const form = event.target;
    const inputs = Array.from(form.elements);
    inputs.forEach(input => {
        if ((input.tagName === 'INPUT' || input.tagName === 'SELECT') && !input.value) {
            input.disabled = true;
        }
    });
});