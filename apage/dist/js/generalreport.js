document.getElementById('add-note-btn').addEventListener('click', function() {
    // Get the container for the notes
    var container = document.getElementById('notes-container');
    
    // Create a new input field
    var newInput = document.createElement('input');
    newInput.type = 'text';
    newInput.name = 'observation[]';
    newInput.placeholder = 'Observation ' + (container.children.length + 1); // Increment the placeholder
    newInput.classList.add('form-control', 'mb-2');
    
    // Append the new input field to the container
    container.appendChild(newInput);
  });