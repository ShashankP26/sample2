// ------------------------------- AMC Table Functions ------------------------------

// Function to add new AMC row in AMC table
function addAMCRow() {
    const table = document.getElementById("amcTable");
    if (!table) return; // Table not present, do nothing
    const tableBody = table.getElementsByTagName("tbody")[0];
    if (!tableBody) return; // tbody not present, do nothing

    const newRowIndex = tableBody.rows.length + 1;

    const newRow = document.createElement("tr");
    newRow.setAttribute("id", "amc_row_" + newRowIndex);

    newRow.innerHTML = `
        <td>
            <input type="hidden" name="select_amc_${newRowIndex}" value="0">
            <input type="checkbox" name="select_amc_check_${newRowIndex}" class="form-check-input" value="1">
        </td>
        <td>
            <input type="text" name="pd_name_${newRowIndex}" class="form-control" placeholder="Enter product name">
        </td>
        <td>
            <input type="text" name="capacity_${newRowIndex}" class="form-control" placeholder="Enter capacity">
        </td>
        <td>
            <input type="text" name="total_needed_capacity_${newRowIndex}" class="form-control" placeholder="Enter total needed capacity">
        </td>
        <td>
            <input type="text" name="waste_water_type_${newRowIndex}" class="form-control" placeholder="Enter wastewater type">
        </td>
        <td>
            <input type="text" name="total_no_machines_${newRowIndex}" class="form-control" placeholder="Enter number of machines">
        </td>
    `;

    tableBody.appendChild(newRow);
    toggleAMCRemoveButton(); // Enable/Disable Remove button for AMC Table
}

// Function to remove AMC row from AMC table
function removeAMCRow() {
    const tableBody = document.getElementById("amcTable").getElementsByTagName("tbody")[0];
    // Ensure we do not remove the default row
    if (tableBody.rows.length > 1) {
        tableBody.deleteRow(tableBody.rows.length - 1);
    }
    toggleAMCRemoveButton(); // Enable/Disable Remove button for AMC Table
}

// Toggle remove button for AMC Table based on row count
function toggleAMCRemoveButton() {
    const removeButton = document.getElementById("removeAMCButton");
    const tableBody = document.getElementById("amcTable").getElementsByTagName("tbody")[0];

    if (tableBody.rows.length > 1) {
        removeButton.disabled = false;
    } else {
        removeButton.disabled = true;
    }
}
    // ------------------------------- Content Section Functions ------------------------------

    // Function to add new content line
    function addContent() {
        const lastContent = document.querySelector("#contentsSection .form-check-inline:last-child");
        const newIndex = (lastContent ? parseInt(lastContent.id.split('_')[1]) + 1 : 1);

        const newContentDiv = document.createElement("div");
        newContentDiv.classList.add("form-check-inline", "mb-2");
        newContentDiv.setAttribute("id", "content_" + newIndex);

        // Hidden input for select content
        const hiddenInput = document.createElement("input");
        hiddenInput.type = "hidden";
        hiddenInput.name = "content_select_" + newIndex;
        hiddenInput.value = "0";

        // Checkbox input
        const checkboxInput = document.createElement("input");
        checkboxInput.type = "checkbox";
        checkboxInput.name = "content_select_" + newIndex;
        checkboxInput.classList.add("form-check-input");
        checkboxInput.value = "1";

        // Text input for content
        const textInput = document.createElement("input");
        textInput.type = "text";
        textInput.name = "content_" + newIndex;
        textInput.classList.add("form-control");
        textInput.placeholder = "Enter new content...";

        // Remove button for content
        const removeButton = document.createElement("button");
        removeButton.type = "button";
        removeButton.classList.add("btn", "btn-danger", "ms-2");
        removeButton.textContent = "Remove";
        removeButton.onclick = function () {
            removeContent(newContentDiv);
        };

        // Append inputs to newContentDiv
        newContentDiv.appendChild(hiddenInput);
        newContentDiv.appendChild(checkboxInput);
        newContentDiv.appendChild(textInput);
        newContentDiv.appendChild(removeButton);

        // Append the new content div to the contents section
        document.getElementById("contentsSection").appendChild(newContentDiv);
    }

    // Function to remove content line
    function removeContent(contentDiv) {
        document.getElementById("contentsSection").removeChild(contentDiv);
    }
// ------------------------------- Maintenance Support Functions ------------------------------

// Function to add new Maintenance Support field
function addMaintenanceSupportField() {
    const section = document.getElementById('maintenanceSupportSection');
    const lastElement = section.lastElementChild;
    const newIndex = section.children.length + 1; // Use current count to index the new field

    const newField = document.createElement('div');
    newField.classList.add('form-check', 'mb-2');
    newField.setAttribute('id', 'maintenanceSupport_' + newIndex);

    newField.innerHTML = `
        <div class="d-flex align-items-center mb-2">
            <input type="hidden" name="maintenance_support_check_${newIndex}" value="0">
            <input type="checkbox" name="maintenance_support_check_${newIndex}" class="form-check-input me-2" value="1">
            <input type="text" name="maintenance_support_${newIndex}" class="form-control me-2" placeholder="Enter maintenance support details">
            <button type="button" class="btn btn-danger" onclick="removeMaintenanceSupportField(${newIndex})">Remove</button>
        </div>
    `;


    section.appendChild(newField);
}

// Function to remove a Maintenance Support field
function removeMaintenanceSupportField(index) {
    const section = document.getElementById('maintenanceSupportSection');
    const field = document.getElementById('maintenanceSupport_' + index);
    section.removeChild(field);
}


// ------------------------------- Yearly Maintenance Functions ------------------------------

// Function to add new Yearly Maintenance field
function addYearlyMaintenanceField() {
    const section = document.getElementById('yearlyMaintenanceSection');
    const lastElement = section.lastElementChild;
    const newIndex = section.children.length + 1; // Use current count to index the new field

    const newField = document.createElement('div');
    newField.classList.add('form-check', 'mb-2');
    newField.setAttribute('id', 'yearlyMaintenance_' + newIndex);

    newField.innerHTML = `
        <div class="d-flex align-items-center mb-2">
            <input type="hidden" name="yearly_maintenance_check_${newIndex}" value="0">
            <input type="checkbox" name="yearly_maintenance_check_${newIndex}" class="form-check-input me-2" value="1">
            <input type="text" name="yearly_maintenance_${newIndex}" class="form-control me-2" placeholder="Enter yearly maintenance details">
            <button type="button" class="btn btn-danger" onclick="removeYearlyMaintenanceField(${newIndex})">Remove</button>
        </div>
    `;

    section.appendChild(newField);
}

// Function to remove a Yearly Maintenance field
function removeYearlyMaintenanceField(index) {
    const section = document.getElementById('yearlyMaintenanceSection');
    const field = document.getElementById('yearlyMaintenance_' + index);
    section.removeChild(field);
}


// ------------------------------- Running Consumables Functions ------------------------------

// Function to add new Running Consumables field
function addRunningConsumablesField() {
    const section = document.getElementById('runningConsumablesSection');
    const lastElement = section.lastElementChild;
    const newIndex = section.children.length + 1; // Use current count to index the new field

    const newField = document.createElement('div');
    newField.classList.add('form-check', 'mb-2');
    newField.setAttribute('id', 'runningConsumables_' + newIndex);

    newField.innerHTML = `
        <div class="d-flex align-items-center mb-2">
            <input type="hidden" name="running_consumables_check_${newIndex}" value="0">
            <input type="checkbox" name="running_consumables_check_${newIndex}" class="form-check-input me-2" value="1">
            <input type="text" name="running_consumables_${newIndex}" class="form-control me-2" placeholder="Enter running consumables details">
            <button type="button" class="btn btn-danger" onclick="removeRunningConsumablesField(${newIndex})">Remove</button>
        </div>
    `;

    section.appendChild(newField);
}

// Function to remove a Running Consumables field
function removeRunningConsumablesField(index) {
    const section = document.getElementById('runningConsumablesSection');
    const field = document.getElementById('runningConsumables_' + index);
    section.removeChild(field);
}


// ------------------------------- Exclusions Functions ------------------------------

// Function to add new Exclusions field
function addExclusionsField() {
    const section = document.getElementById('exclusionsSection');
    const lastElement = section.lastElementChild;
    const newIndex = section.children.length + 1; // Use current count to index the new field

    const newField = document.createElement('div');
    newField.classList.add('form-check', 'mb-2');
    newField.setAttribute('id', 'exclusions_' + newIndex);

newField.innerHTML = `
    <div class="d-flex align-items-center mb-2">
        <input type="hidden" name="exclusions_check_${newIndex}" value="0">
        <input type="checkbox" name="exclusions_check_${newIndex}" class="form-check-input me-2" value="1">
        <input type="text" name="exclusions_${newIndex}" class="form-control me-2" placeholder="Enter exclusions details">
        <button type="button" class="btn btn-danger" onclick="removeExclusionsField(${newIndex})">Remove</button>
    </div>
`;

    section.appendChild(newField);
}

// Function to remove an Exclusions field
function removeExclusionsField(index) {
    const section = document.getElementById('exclusionsSection');
    const field = document.getElementById('exclusions_' + index);
    section.removeChild(field);
}
// ------------------------------- AMC Pricing Table Functions ------------------------------
// Function to add new AMC row in AMC Pricing table
function addAMCPricingRow() {
    const table = document.getElementById("amcpTable");
    if (!table) return;
    const tableBody = table.getElementsByTagName("tbody")[0];
    if (!tableBody) return;

    const newRowIndex = tableBody.rows.length + 1;

    const newRow = document.createElement("tr");
    newRow.setAttribute("id", "amcp_row_" + newRowIndex);

    newRow.innerHTML = `
        <td>
            <input type="hidden" name="select_amcp_${newRowIndex}" value="0">
            <input type="checkbox" name="select_amcp_check_${newRowIndex}" class="form-check-input" value="1">
        </td>
        <td>
            <input type="text" name="pd_namep_${newRowIndex}" class="form-control" placeholder="Enter product name">
        </td>
        <td>
            <input type="text" name="capacityp_${newRowIndex}" class="form-control" placeholder="Enter capacity">
        </td>
        <td>
            <input type="text" name="total_needed_capacityp_${newRowIndex}" class="form-control" placeholder="Enter total needed capacity">
        </td>
        <td>
            <input type="text" name="waste_water_typep_${newRowIndex}" class="form-control" placeholder="Enter wastewater type">
        </td>
        <td>
            <input type="text" name="total_no_machinesp_${newRowIndex}" class="form-control" placeholder="Enter number of machines">
        </td>
    `;

    tableBody.appendChild(newRow);
    toggleAMCPricingRemoveButton();
}


// Function to remove AMC row from AMC Pricing table
function removeAMCPricingRow() {
    const table = document.getElementById("amcpTable");
    if (!table) return;
    const tableBody = table.getElementsByTagName("tbody")[0];
    if (!tableBody) return;
    if (tableBody.rows.length > 1) {
        tableBody.deleteRow(tableBody.rows.length - 1);
    }
    toggleAMCPricingRemoveButton();
}

function toggleAMCPricingRemoveButton() {
    const removeButton = document.getElementById("removeAMCPricingButton");
    const table = document.getElementById("amcpTable");
    if (!removeButton || !table) return;
    const tableBody = table.getElementsByTagName("tbody")[0];
    if (!tableBody || tableBody.rows.length <= 1) {
        removeButton.disabled = true;
    } else {
        removeButton.disabled = false;
    }
}



// Function to add new AMC Particular row in AMC Particulars Table
function addAMCParticularRow() {
    const table = document.getElementById("amcParticularsTable");
    if (!table) return;
    const tableBody = table.getElementsByTagName("tbody")[0];
    if (!tableBody) return;
    const newRowIndex = tableBody.rows.length + 1;

    const newRow = document.createElement("tr");
    newRow.setAttribute("id", "particular_row_" + newRowIndex);
    newRow.innerHTML = `
        <td>
            <input type="hidden" name="select_per_${newRowIndex}" value="0">
            <input type="checkbox" name="select_per_check_${newRowIndex}" class="form-check-input" value="1">
        </td>
        <td>
            <input type="text" name="particulars_${newRowIndex}" class="form-control" placeholder="Enter particulars">
        </td>
        <td>
            <input type="text" name="first_year_exgst_${newRowIndex}" class="form-control first-year-exgst" placeholder="Enter 1st year cost (Excluding GST)">
        </td>
    `;
    tableBody.appendChild(newRow);

    // Attach listeners to recalculate totals
    const newCheckbox = newRow.querySelector('.form-check-input');
    if (newCheckbox) {
        newCheckbox.addEventListener('change', calculateTotals);
    }
    const newInput = newRow.querySelector('.first-year-exgst');
    if (newInput) {
        newInput.addEventListener('input', calculateTotals);
    }

    toggleAMCParticularRemoveButton();
}


// Function to remove AMC Particular row from AMC Particulars Table
function removeAMCParticularRow() {
    console.log('Removing AMC Particular row');
    const tableBody = document.getElementById("amcParticularsTable").getElementsByTagName("tbody")[0];

    // Ensure we do not remove the default row
    if (tableBody.rows.length > 1) {
        tableBody.deleteRow(tableBody.rows.length - 1);
    }
    toggleAMCParticularRemoveButton(); // Enable/Disable Remove button for AMC Particulars Table
}

// Toggle remove button for AMC Particulars Table based on row count
function toggleAMCParticularRemoveButton() {
    console.log('Toggling remove AMC Particular button');
    const removeButton = document.getElementById("removeAMCParticularButton");
    const tableBody = document.getElementById("amcParticularsTable").getElementsByTagName("tbody")[0];

    if (tableBody.rows.length > 1) {
        removeButton.disabled = false;
    } else {
        removeButton.disabled = true;
    }
}
// -----------------------Terms and Conditions -------------------------
// Function to add new term line
function addTerm() {
    const lastTerm = document.querySelector("#termsSection .form-check-inline:last-child");
    const newIndex = (lastTerm ? parseInt(lastTerm.id.split('_')[1]) + 1 : 1);

    const newTermDiv = document.createElement("div");
    newTermDiv.classList.add("form-check-inline", "mb-2");
    newTermDiv.setAttribute("id", "term_" + newIndex);

    // Hidden input for select term
    const hiddenInput = document.createElement("input");
    hiddenInput.type = "hidden";
    hiddenInput.name = "terms_check_" + newIndex;
    hiddenInput.value = "0";

    // Checkbox input for terms
    const checkboxInput = document.createElement("input");
    checkboxInput.type = "checkbox";
    checkboxInput.name = "terms_check_" + newIndex;
    checkboxInput.classList.add("form-check-input");
    checkboxInput.value = "1";

    // Text input for term description
    const textInput = document.createElement("input");
    textInput.type = "text";
    textInput.name = "terms_" + newIndex;
    textInput.classList.add("form-control");
    textInput.placeholder = "Enter new term...";

    // Remove button for term
    const removeButton = document.createElement("button");
    removeButton.type = "button";
    removeButton.classList.add("btn", "btn-danger", "ms-2");
    removeButton.textContent = "Remove";
    removeButton.onclick = function () {
        removeTerm(newTermDiv);
    };

    // Append inputs to newTermDiv
    newTermDiv.appendChild(hiddenInput);
    newTermDiv.appendChild(checkboxInput);
    newTermDiv.appendChild(textInput);
    newTermDiv.appendChild(removeButton);

    // Append the new term div to the terms section
    document.getElementById("termsSection").appendChild(newTermDiv);
}

// Function to remove term line
function removeTerm(termDiv) {
    document.getElementById("termsSection").removeChild(termDiv);
}


