document.addEventListener('DOMContentLoaded', function () {
    const profileTable = document.getElementById('profileTable').getElementsByTagName('tbody')[0];
    const addProfileModal = new bootstrap.Modal(document.getElementById('addProfileModal'));
    const editProfileModal = new bootstrap.Modal(document.getElementById('editProfileModal'));

    // Search functionality
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('searchInput');

    searchForm.addEventListener('submit', function (event) {
        event.preventDefault();
        const searchTerm = searchInput.value.toLowerCase();
        window.location.href = `/?search=${searchTerm}`;
    });

    // Show Add Profile Modal
    document.getElementById('addProfileBtn').addEventListener('click', function () {
        document.getElementById('addProfileForm').reset();
        addProfileModal.show();
    });

    // Add Profile functionality
    document.getElementById('addProfileForm').addEventListener('submit', function (event) {
        event.preventDefault();
        const formData = new FormData(this);

        fetch('/add/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.id) {
                // Add new row to the table
                const newRow = profileTable.insertRow();
                newRow.setAttribute('data-id', data.id);
                newRow.innerHTML = `
                    <td>${data.name}</td>
                    <td>${data.email}</td>
                    <td>${data.age}</td>
                    <td>${data.qualification}</td>
                    <td>${data.salary}</td>
                    <td>
                        <button class="editBtn btn btn-warning btn-sm">Edit</button>
                        <button class="deleteBtn btn btn-danger btn-sm">Delete</button>
                    </td>
                `;
                addProfileModal.hide();
            }
        })
        .catch(error => console.error('Error:', error));
    });

    // Event delegation for edit buttons
    profileTable.addEventListener('click', function (event) {
        if (event.target.classList.contains('editBtn')) {
            const row = event.target.closest('tr');
            const profileId = row.dataset.id;

            fetch(`/edit/${profileId}/`, { method: 'GET' })
            .then(response => response.json())
            .then(data => {
                console.log('Profile Data:', data);  // Log data to check if it's correct
                if (data && data.id) {
                    // Populate the form fields with the data
                    document.getElementById('editProfileId').value = data.id;
                    document.getElementById('editName').value = data.name || '';
                    document.getElementById('editEmail').value = data.email || '';
                    document.getElementById('editAge').value = data.age || '';
                    document.getElementById('editQualification').value = data.qualification || '';
                    document.getElementById('editSalary').value = data.salary || '';
        
                    // Show the edit profile modal
                    editProfileModal.show();
                } else {
                    console.error('Profile data is invalid or not found.');
                }
            })
            .catch(error => console.error('Error fetching profile data:', error));
        }
    });

    // Edit Profile functionality
    document.getElementById('editProfileForm').addEventListener('submit', function (event) {
        event.preventDefault();  // Prevent the form from submitting normally
        const formData = new FormData(this);
        const profileId = document.getElementById('editProfileId').value;  // Get the profile ID from the form

        fetch(`/edit/${profileId}/`, {
            method: 'POST',  // Sending a POST request to update the profile
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),  // Add CSRF token for security
            },
        })
        .then(response => response.json())  // Parse the JSON response
        .then(data => {
            if (data.id) {
                // Find the row in the table to update
                const row = profileTable.querySelector(`tr[data-id="${data.id}"]`);
                // Update the table row with the new values from the response
                row.cells[0].textContent = data.name;
                row.cells[1].textContent = data.email;
                row.cells[2].textContent = data.age;
                row.cells[3].textContent = data.qualification;
                row.cells[4].textContent = data.salary;

                // Hide the edit modal after successful update
                editProfileModal.hide();
            } else {
                console.error('Error updating profile:', data);
            }
        })
        .catch(error => console.error('Error:', error));
    });

    // Event delegation for delete buttons (with confirmation)
    profileTable.addEventListener('click', function (event) {
        if (event.target.classList.contains('deleteBtn')) {
            const row = event.target.closest('tr');
            const profileIdToDelete = row.dataset.id;  // Store profile ID when delete button is clicked
    
            // Confirm before deleting
            const confirmation = window.confirm("Are you sure you want to delete this profile?");
            
            if (confirmation) {
                // If confirmed, send the delete request
                fetch(`/delete/${profileIdToDelete}/`, {
                    method: 'DELETE',  // Use DELETE method for deletion
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),  // Make sure this function is defined
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Find the row for the deleted profile and remove it from the table
                        row.remove();  // More explicit than deleting by index
                    } else {
                        console.error('Failed to delete profile:', data.error);
                    }
                })
                .catch(error => console.error('Error:', error));
            }
        }
    });
    

    // Utility function to get CSRF token from cookies (for Django)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
