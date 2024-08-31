document.addEventListener('DOMContentLoaded', function() {
    const peopleSelect = document.getElementById('people');
    const paymentLabel = document.querySelector('label[for="voucher"]');

    function updateFields() {
        const numPeople = parseInt(peopleSelect.value);
        const fields = [
            document.getElementById('person-field-1'),
            document.getElementById('person-field-2'),
            document.getElementById('person-field-3')
        ];
        const inputs = [
            document.getElementById('person1'),
            document.getElementById('person2'),
            document.getElementById('person3')
        ];

        // Reset all fields to not required and hide them initially
        fields.forEach(field => {
            field.style.display = 'none';
        });
        inputs.forEach(input => {
            input.required = false;
            input.value = ''; // Optionally clear the field value
        });

        // Show and set required based on the number of people
        if (numPeople >= 2) {
            fields[0].style.display = 'block';
            inputs[0].required = true;
        }
        if (numPeople >= 3) {
            fields[1].style.display = 'block';
            inputs[1].required = true;
        }
        if (numPeople >= 4) {
            fields[2].style.display = 'block';
            inputs[2].required = true;
        }

        // Update the payment label based on the number of people
        const amount = numPeople * 500;
        if (paymentLabel) {
            paymentLabel.textContent = `Pago de $${amount}`;
        }
    }

    // Initial call to update the fields based on the default value
    updateFields();

    // Add event listener to update fields when the selection changes
    peopleSelect.addEventListener('change', updateFields);
});
