document.addEventListener('DOMContentLoaded', () => {
    // Get all forms
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        // Get all inputs, textareas, and select elements in this form
        const inputs = form.querySelectorAll('input, textarea, select');
        const bottomRow = form.querySelector('#action-bar');

        // Skip if this is the reload form at the top
        if (!bottomRow) return;

        inputs.forEach(input => {
            input.addEventListener('change', () => {
                bottomRow.classList.remove('hidden');
            });

            // For textarea and text inputs, also listen for keyup
            if (input.type === 'text' || input.tagName.toLowerCase() === 'textarea') {
                input.addEventListener('keyup', () => {
                    bottomRow.classList.remove('hidden');
                });
            }
        });
    });
});
