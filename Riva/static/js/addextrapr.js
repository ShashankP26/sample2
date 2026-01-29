// Function to add new content line
function addContent() {
    const lastContent = document.querySelector("#contentsSection .d-flex:last-child");
    const newIndex = (lastContent ? parseInt(lastContent.id.split('_')[1]) + 1 : 1);

    const newContentDiv = document.createElement("div");
    newContentDiv.classList.add("d-flex", "align-items-center", "mb-2");
    newContentDiv.setAttribute("id", "content_" + newIndex);

    // Checkbox input
    const checkboxInput = document.createElement("input");
    checkboxInput.type = "checkbox";
    checkboxInput.name = "content_select_" + newIndex;
    checkboxInput.classList.add("form-check-input", "me-2");
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
    newContentDiv.appendChild(checkboxInput);
    newContentDiv.appendChild(textInput);
    newContentDiv.appendChild(removeButton);

    // Append the new content div to the contents section
    document.getElementById("contentsSection").appendChild(newContentDiv);
}

// Function to remove content line
function removeContent(contentDiv) {
    contentDiv.remove();
}

// --------------------------table1---------------------------------------------
// Function to add a new row to the Table1
function addTable1Row() {
    const tableBody = document.getElementById("table1").getElementsByTagName("tbody")[0];
    const newRowIndex = tableBody.rows.length + 1; // Determine the new row index

    const newRow = document.createElement("tr");
    newRow.setAttribute("id", "row_t1_" + newRowIndex);

    newRow.innerHTML = `
        <td>
            <input type="hidden" name="select_row_t1_${newRowIndex}" value="0">
            <input type="checkbox" class="select-row" name="select_row_t1_${newRowIndex}" value="1" data-row="${newRowIndex}">
        </td>
        <td>
            <input type="text" name="sl_no_value_t1_${newRowIndex}" class="form-control" placeholder="Enter sl. no">
        </td>
        <td>
            <input type="text" name="raw_sewage_characteristics_value_t1_${newRowIndex}" class="form-control" placeholder="Enter characteristics">
        </td>
        <td>
            <input type="text" name="unit_value_t1_${newRowIndex}" class="form-control" placeholder="Enter unit">
        </td>
        <td>
            <input type="text" name="value_value_t1_${newRowIndex}" class="form-control" placeholder="Enter value">
        </td>
    `;

    tableBody.appendChild(newRow);
}

// Function to remove the last row from Table1
function removeTable1Row() {
    const tableBody = document.getElementById("table1").getElementsByTagName("tbody")[0];
    // Ensure we do not remove the default row
    if (tableBody.rows.length > 1) {
        tableBody.deleteRow(tableBody.rows.length - 1);
    }
}
// ------------------------------treatment Process----------------------------------
// Function to add a new row to the "Treatment Processes" table
function addTreatmentProcessRow() {
    const tableBody = document.getElementById("treatmentProcessTable").getElementsByTagName("tbody")[0];
    const newRowIndex = tableBody.rows.length + 1; // Determine the new row index

    const newRow = document.createElement("tr");
    newRow.setAttribute("id", "treatment_process_row_" + newRowIndex);

    newRow.innerHTML = `
        <td>
            <input type="hidden" name="standard_select_${newRowIndex}" value="0">
            <input type="checkbox" name="standard_select_${newRowIndex}" value="1" class="form-check-input">
        </td>
        <td>
            <input type="text" name="principal_purpose_${newRowIndex}" class="form-control" placeholder="Enter principal purpose">
        </td>
        <td>
            <input type="text" name="unit_processes_${newRowIndex}" class="form-control" placeholder="Enter unit processes">
        </td>
    `;

    tableBody.appendChild(newRow);
}

// Function to remove the last row from the "Treatment Processes" table
function removeTreatmentProcessRow() {
    const tableBody = document.getElementById("treatmentProcessTable").getElementsByTagName("tbody")[0];
    // Ensure we do not remove the default row
    if (tableBody.rows.length > 2) {
        tableBody.deleteRow(tableBody.rows.length - 1);
    }
}
// ----------------------------------------------SPecs Table -------------------------------
// Function to add a new row to the "Specs" table
function addSpecsRow() {
    const tableBody = document.getElementById("specsTable").getElementsByTagName("tbody")[0];
    const newRowIndex = tableBody.rows.length + 1; // Determine the new row index

    const newRow = document.createElement("tr");
    newRow.setAttribute("id", "spec_row_" + newRowIndex);

    newRow.innerHTML = `
        <td>
            <input type="hidden" name="spec_select_${newRowIndex}" value="0">
            <input type="checkbox" name="spec_select_${newRowIndex}" value="1" class="form-check-input">
        </td>
        <td>
            <input type="text" name="specs_for_25kld_${newRowIndex}" class="form-control" placeholder="Enter specs for 25 KLD">
        </td>
        <td>
            <input type="text" name="hidrec_${newRowIndex}" class="form-control" placeholder="Enter HIDREC">
        </td>
    `;

    tableBody.appendChild(newRow);
}

// Function to remove the last row from the "Specs" table
function removeSpecsRow() {
    const tableBody = document.getElementById("specsTable").getElementsByTagName("tbody")[0];
    // Ensure we do not remove the default row
    if (tableBody.rows.length > 2) {
        tableBody.deleteRow(tableBody.rows.length - 1);
    }
}

// -------------------------------------------------output water table ----------------------------------
// Function to add a new row to the "Output Treated Water Quality" table
function addOutputRow() {
    const tableBody = document.getElementById("outputTable").getElementsByTagName("tbody")[0];
    const newRowIndex = tableBody.rows.length + 1; // Determine the new row index

    const newRow = document.createElement("tr");
    newRow.setAttribute("id", "output_row_" + newRowIndex);

    newRow.innerHTML = `
        <td>
            <input type="hidden" name="select_row_op_${newRowIndex}" value="0">
            <input type="checkbox" name="select_row_op_${newRowIndex}" value="1" class="form-check-input">
        </td>
        <td>
            <input type="text" name="sl_no_value_op_${newRowIndex}" class="form-control" placeholder="Enter sl no">
        </td>
        <td>
            <input type="text" name="treated_water_characteristics_value_op_${newRowIndex}" class="form-control" placeholder="Enter characteristics">
        </td>
        <td>
            <input type="text" name="unit_value_op_${newRowIndex}" class="form-control" placeholder="Enter unit">
        </td>
        <td>
            <input type="text" name="standard_value_op_${newRowIndex}" class="form-control" placeholder="Enter standard value">
        </td>
    `;

    tableBody.appendChild(newRow);
}

// Function to remove the last row from the "Output Treated Water Quality" table
function removeOutputRow() {
    const tableBody = document.getElementById("outputTable").getElementsByTagName("tbody")[0];
    // Ensure we do not remove the default row
    if (tableBody.rows.length > 1) {
        tableBody.deleteRow(tableBody.rows.length - 1);
    }
}
// -----------------------Machine Specification ------------------------
// Function to add a new row to the "Machine Specifications" table
function addMachineSpecRow() {
    const tableBody = document.getElementById("machineSpecTable").getElementsByTagName("tbody")[0];
    const newRowIndex = tableBody.rows.length + 1; // Determine the new row index

    const newRow = document.createElement("tr");
    newRow.setAttribute("id", "machine_spec_row_" + newRowIndex);

    newRow.innerHTML = `
        <td>
            <input type="hidden" name="select_row_spe_${newRowIndex}" value="0">
            <input type="checkbox" name="select_row_spe_${newRowIndex}" value="1" class="form-check-input">
        </td>
        <td>
            <input type="text" name="product_name_spe_${newRowIndex}" class="form-control" placeholder="Enter product name">
        </td>
        <td>
            <input type="text" name="capacity_value_spe_${newRowIndex}" class="form-control" placeholder="Enter capacity">
        </td>
        <td>
            <input type="text" name="total_needed_capacity_value_spe_${newRowIndex}" class="form-control" placeholder="Enter total needed capacity">
        </td>
        <td>
            <input type="text" name="waste_water_type_value_spe_${newRowIndex}" class="form-control" placeholder="Enter waste water type">
        </td>
        <td>
            <input type="text" name="total_no_machines_value_spe_${newRowIndex}" class="form-control" placeholder="Enter total number of machines">
        </td>
    `;

    tableBody.appendChild(newRow);
}

// Function to remove the last row from the "Machine Specifications" table
function removeMachineSpecRow() {
    const tableBody = document.getElementById("machineSpecTable").getElementsByTagName("tbody")[0];
    // Ensure we do not remove the default row
    if (tableBody.rows.length > 1) {
        tableBody.deleteRow(tableBody.rows.length - 1);
    }
}
// ---------------------------Detailed Specs row ----------------------------
// Function to add a new row to the "Detailed Specifications" table
function addDetailedSpecRow() {
    const tableBody = document.getElementById("detailedSpecTable").getElementsByTagName("tbody")[0];
    const newRowIndex = tableBody.rows.length + 1; // Determine the new row index

    const newRow = document.createElement("tr");
    newRow.setAttribute("id", "detailed_spec_row_" + newRowIndex);

    newRow.innerHTML = `
        <td>
            <input type="hidden" name="select_row_det_${newRowIndex}" value="0">
            <input type="checkbox" name="select_row_det_${newRowIndex}" value="1" class="form-check-input">
        </td>
        <td>
            <input type="text" name="sl_no_value_det_${newRowIndex}" class="form-control" placeholder="Enter Sl. No">
        </td>
        <td>
            <input type="text" name="specification_value_det_${newRowIndex}" class="form-control" placeholder="Enter Specification">
        </td>
        <td>
            <input type="text" name="qnty_value_det_${newRowIndex}" class="form-control" placeholder="Enter Quantity">
        </td>
        <td>
            <input type="text" name="unit_value_det_${newRowIndex}" class="form-control" placeholder="Enter Unit">
        </td>
        <td>
            <input type="text" name="unit_rate_value_det_${newRowIndex}" class="form-control" placeholder="Enter Unit Rate">
        </td>
        <td>
            <input type="text" name="price_exgst_value_det_${newRowIndex}" class="form-control" placeholder="Enter Price (Excluding GST)">
        </td>
        <td>
            <input type="text" name="total_value_det_${newRowIndex}" class="form-control" placeholder="Enter Total">
        </td>
    `;

    tableBody.appendChild(newRow);
}

// Function to remove the last row from the "Detailed Specifications" table
function removeDetailedSpecRow() {
    const tableBody = document.getElementById("detailedSpecTable").getElementsByTagName("tbody")[0];
    // Ensure we do not remove the default row
    if (tableBody.rows.length > 1) {
        tableBody.deleteRow(tableBody.rows.length - 1);
    }
}

// ----------------------------------------optional hadware table -----------------------------------
// Function to add a new row to the "Optional Hardware Specification" table
function addOptionalHardwareRow() {
    const tableBody = document.getElementById("optionalHardwareTable").getElementsByTagName("tbody")[0];
    const newRowIndex = tableBody.rows.length + 1; // Determine the new row index

    const newRow = document.createElement("tr");
    newRow.setAttribute("id", "optional_hardware_row_" + newRowIndex);

    newRow.innerHTML = `
        <td>
            <input type="hidden" name="select_row_opt_${newRowIndex}" value="0">
            <input type="checkbox" name="select_row_opt_${newRowIndex}" value="1" class="form-check-input">
        </td>
        <td>
            <input type="text" name="sl_no_value_opt_${newRowIndex}" class="form-control" placeholder="Enter Sl. No">
        </td>
        <td>
            <input type="text" name="optional_hardware_value_opt_${newRowIndex}" class="form-control" placeholder="Enter Optional Hardware">
        </td>
        <td>
            <input type="text" name="qnty_value_opt_${newRowIndex}" class="form-control" placeholder="Enter Quantity">
        </td>
        <td>
            <input type="text" name="unit_value_opt_${newRowIndex}" class="form-control" placeholder="Enter Unit">
        </td>
        <td>
            <input type="text" name="unit_rate_value_opt_${newRowIndex}" class="form-control" placeholder="Enter Unit Rate">
        </td>
        <td>
            <input type="text" name="price_exgst_value_opt_${newRowIndex}" class="form-control" placeholder="Enter Price (Excluding GST)">
        </td>
        <td>
            <input type="text" name="total_value_opt_${newRowIndex}" class="form-control" placeholder="Enter Total">
        </td>
    `;

    tableBody.appendChild(newRow);
}

// Function to remove the last row from the "Optional Hardware Specification" table
function removeOptionalHardwareRow() {
    const tableBody = document.getElementById("optionalHardwareTable").getElementsByTagName("tbody")[0];
    // Ensure we do not remove the default row
    if (tableBody.rows.length > 1) {
        tableBody.deleteRow(tableBody.rows.length - 1);
    }
}




