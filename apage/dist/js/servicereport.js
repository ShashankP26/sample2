let runCycleCount = 1;

// When the "Add More" button is clicked
document.getElementById('addRunCycleBtn').addEventListener('click', function () {
  runCycleCount++;
  // Add new row for the new run cycle
  const newRow = document.createElement('tr');
  newRow.id = `run_cycle_${runCycleCount}`;

  newRow.innerHTML = `
        <td>Run cycle ${runCycleCount}</td>
        <td><input type="time" name="run_time_${runCycleCount}"></td>
        <td><input type="time" name="end_time_${runCycleCount}"></td>
        <td><input type="checkbox" name="checked_${runCycleCount}"></td>
        <td><input type="checkbox" name="pass_${runCycleCount}"></td>
        <td><input type="checkbox" name="fail_${runCycleCount}"></td>
        <td><textarea class="form-control" name="remark_${runCycleCount}" rows="2" placeholder="Remark"></textarea></td>
    `;

  // Append the new row to the table body
  document.getElementById('runCycleRows').appendChild(newRow);

  // Update the hidden field for the run cycle count
  document.getElementById('runCycleCount').value = runCycleCount;
});

  let remarkCount = 3;

  document.getElementById('add-remark-btn').addEventListener('click', () => {
    remarkCount++;
    const table = document.getElementById('remarks-table').getElementsByTagName('tbody')[0];
    const row = table.insertRow();
    const cell1 = row.insertCell(0);
    const cell2 = row.insertCell(1);

    cell1.textContent = remarkCount;
    cell2.innerHTML = `
      <div class="mb-3">
        <textarea class="form-control" name="remark_${remarkCount}" rows="2" placeholder="Remark"></textarea>
      </div>
    `;
  });





   let spareCount = 3;

  document.getElementById('add-spare-btn').addEventListener('click', () => {
    spareCount++;
    const table = document.getElementById('spares-table').getElementsByTagName('tbody')[0];
    const row = table.insertRow();
    const cell1 = row.insertCell(0);
    const cell2 = row.insertCell(1);

    cell1.textContent = spareCount;
    cell2.innerHTML = `
      <div class="mb-3">
        <textarea class="form-control" name="spare_${spareCount}" rows="2" placeholder="Enter spare details"></textarea>
      </div>
    `;
  });





  document.getElementById('add-spare-btn').addEventListener('click', () => {
    spareCount++;
    const table = document.getElementById('spares-table').getElementsByTagName('tbody')[0];
    const row = table.insertRow();
    const cell1 = row.insertCell(0);
    const cell2 = row.insertCell(1);

    cell1.textContent = spareCount;
    cell2.innerHTML = `
      <div class="mb-3">
        <textarea class="form-control" name="spare_${spareCount}" rows="2" placeholder="Enter spare details"></textarea>
      </div>
    `;
  });









