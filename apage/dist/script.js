// script.js

function toggleFields() {
    var paymentCategory = document.getElementById('payment_category').value;
    
    if (paymentCategory === 'bill') {
        document.getElementById('bill_fields').style.display = 'block';
        document.getElementById('voucher_fields').style.display = 'none';
    } else if (paymentCategory === 'voucher') {
        document.getElementById('voucher_fields').style.display = 'block';
        document.getElementById('bill_fields').style.display = 'none';
    } else {
        document.getElementById('bill_fields').style.display = 'none';
        document.getElementById('voucher_fields').style.display = 'none';
    }
}

window.onload = function() {
    toggleFields(); // Call once to set initial state
}