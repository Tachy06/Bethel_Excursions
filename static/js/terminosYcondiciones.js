document.addEventListener('DOMContentLoaded', function () {
    const checkbox = document.getElementById('accept');
    const submitButton = document.getElementById('submit-button');

    // Inicialmente deshabilitar el botón
    submitButton.disabled = true;

    checkbox.addEventListener('change', function() {
        submitButton.disabled =! checkbox.checked;
    });
});