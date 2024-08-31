document.addEventListener('DOMContentLoaded', function() {
    const peopleSelect = document.getElementById('people');
    const paymentLabel = document.querySelector('label[for="voucher"]');

    function dividirInputs() {
        var divs = document.querySelectorAll('.asientos');
        
        divs.forEach(function(div) {
            var inputs = div.querySelectorAll('input[type="checkbox"]');
            var lis = div.querySelectorAll('li');
            if (inputs.length > 2) {
                var nuevosAsientos = document.createElement('div');
                nuevosAsientos.classList.add('asiento');
                div.parentNode.insertBefore(nuevosAsientos, div.nextSibling);
                
                var contador = 0;
                var nuevoContenedor = null;
                
                inputs.forEach(function(input, index) {
                    if (contador === 0) {
                        nuevoContenedor = document.createElement('div');
                        nuevoContenedor.classList.add('asientos');
                        nuevosAsientos.appendChild(nuevoContenedor);
                    }
                    nuevoContenedor.appendChild(lis[index]);
                    nuevoContenedor.appendChild(input);
                    
                    contador++;
                    
                    if (contador === 2 || index === inputs.length - 1) {
                        contador = 0;
                    }
                });
            }
        });
    }

    function limitarAsientos() {
        var checkboxes = document.querySelectorAll('input[type="checkbox"].bus');
        var maxAsientos = 4;

        checkboxes.forEach(function(checkbox) {
            checkbox.addEventListener('change', function() {
                var selectedCheckboxes = document.querySelectorAll('input[type="checkbox"].bus:checked');
                if (selectedCheckboxes.length > maxAsientos) {
                    this.checked = false;
                    alert('Solo puedes seleccionar un máximo de ' + maxAsientos + ' asientos.');
                }
            });
        });
    }

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
        paymentLabel.textContent = `Pago de $${amount}`;
    }

    // Initial calls to set the fields based on default selection
    dividirInputs();
    limitarAsientos();
    updateFields();

    // Event listeners for changes in the people selection
    peopleSelect.addEventListener('change', function() {
        updateFields();
    });
});
