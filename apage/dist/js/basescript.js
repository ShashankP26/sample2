
        function updateFormFields() {
            var selectBox = document.getElementById('selectOption');
            var selectedValue = Array.from(selectBox.selectedOptions).map(option => option.value);
            var fileInput = document.getElementById('fileInput');
            var voucherInput = document.getElementById('voucherInput');
            
            // Hide both fields by default
            fileInput.style.display = 'none';
            voucherInput.style.display = 'none';

            // Show relevant input field based on selection
            if (selectedValue.includes('1')) { // Bill is selected
                fileInput.style.display = 'block';
            } else if (selectedValue.includes('2')) { // Voucher is selected
                voucherInput.style.display = 'block';
            }
        }
