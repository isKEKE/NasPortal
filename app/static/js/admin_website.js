// Function to load and display the list of websites
async function loadWebsites() {
    // Hide user data (if it exists) and show website data
    const userDataContainer = document.getElementById('user-data');
    if (userDataContainer) {
        userDataContainer.style.display = 'none';
    }
    document.getElementById('website-data').style.display = 'block';

    // Add active class to Websites link and remove from others (if they exist)
    const usersLink = document.getElementById('users-link');
    const websitesLink = document.getElementById('websites-link');
    if (usersLink) usersLink.classList.remove('active');
    if (websitesLink) websitesLink.classList.add('active');


    document.getElementById('website-list-container').innerHTML = '<p class="loading-message">Loading websites...</p>';

    try {
        // Assuming this endpoint exists and now returns owner_name and is_public
        const response = await fetch('/admin/website/list');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const websites = await response.json();
        displayWebsites(websites);
    } catch (error) {
        document.getElementById('website-list-container').innerHTML = `<p class="error-message">Error loading websites: ${error}</p>`;
    }
}

// Function to display the list of websites in a table
function displayWebsites(websites) {
    // Added 'Is Public' column header
    let html = '<table class="data-table"><thead><tr><th>ID</th><th>Title</th><th>URL</th><th>Description</th><th>Owner Name</th><th>Is Public</th><th>Actions</th></tr></thead><tbody>';
    if (websites && websites.length > 0) {
        websites.forEach(website => {
            // Use data attributes to store website data instead of passing in onclick
            html += `<tr>
                        <td>${website.id}</td>
                        <td>${website.title}</td>
                        <td><a href="${website.url}" target="_blank">${website.url}</a></td>
                        <td>${website.description || ''}</td>
                        <td>${website.owner_username || 'N/A'}</td>
                        <td>${website.is_public ? 'Yes' : 'No'}</td> <td class="action-buttons">
                            <button class="edit-button" data-website-id="${website.id}" data-title="${website.title}" data-url="${website.url}" data-description="${website.description || ''}" data-is-public="${website.is_public}"><i class="fas fa-edit"></i> Edit</button>
                            <button class="delete-button" data-website-id="${website.id}"><i class="fas fa-trash-alt"></i> Delete</button>
                        </td>
                    </tr>`;
        });
    } else {
        // Adjusted colspan for the new column (from 6 to 7)
        html += '<tr><td colspan="7">No websites found.</td></tr>';
    }
    html += '</tbody></table>';
    const websiteListContainer = document.getElementById('website-list-container');
    websiteListContainer.innerHTML = html;

    // Attach event listeners to the buttons after they are added to the DOM
    attachWebsiteButtonListeners();
}

// Function to attach event listeners to website buttons
function attachWebsiteButtonListeners() {
    // Attach edit button listeners
    const editButtons = document.querySelectorAll('.data-table .edit-button');
    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const websiteId = this.dataset.websiteId;
            const title = this.dataset.title;
            const url = this.dataset.url;
            const description = this.dataset.description;
            // Convert data-is-public string to boolean
            const isPublic = this.dataset.isPublic === 'true';
            openEditWebsiteModal(websiteId, title, url, description, isPublic);
        });
    });

    // Attach delete button listeners
    const deleteButtons = document.querySelectorAll('.data-table .delete-button');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const websiteId = this.dataset.websiteId;
            deleteWebsite(websiteId);
        });
    });
}


// Add Website Modal Functions
function openAddWebsiteModal() {
    document.getElementById('addWebsiteModal').style.display = 'block';
    document.getElementById('add-website-error').style.display = 'none';
    document.getElementById('addWebsiteForm').reset();
    // Set the default for is_public to true (Yes)
    document.getElementById('new_website_is_public').value = 'false';
}

function closeAddWebsiteModal() {
    document.getElementById('addWebsiteModal').style.display = 'none';
}

// Event listener for Add Website form submission
// This listener is attached once in the DOMContentLoaded block in the HTML
// or by calling attachWebsiteFormListeners()
const addWebsiteForm = document.getElementById('addWebsiteForm');
if (addWebsiteForm) {
    addWebsiteForm.addEventListener('submit', async function (event) {
        event.preventDefault();
        const formData = new FormData(this);
        // Append is_public to form data
        formData.append('is_public', document.getElementById('new_website_is_public').value);

        const errorDiv = document.getElementById('add-website-error');
        errorDiv.style.display = 'none';

        try {
            const response = await fetch('/admin/website/add', { // Assuming this endpoint exists
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                errorDiv.textContent = errorData.detail || `HTTP error! status: ${response.status}`;
                errorDiv.style.display = 'block';
            } else {
                closeAddWebsiteModal();
                loadWebsites(); // Reload websites list after successful add
            }
        } catch (error) {
            errorDiv.textContent = `Error adding website: ${error}`;
            errorDiv.style.display = 'block';
        }
    });
}


// Edit Website Modal Functions
let currentEditWebsiteId = null;

// Added is_public parameter
function openEditWebsiteModal(websiteId, title, url, description, is_public) {
    currentEditWebsiteId = websiteId;
    document.getElementById('edit_website_id').value = websiteId;
    document.getElementById('edit_website_title').value = title;
    document.getElementById('edit_website_url').value = url;
    document.getElementById('edit_website_description').value = description;
    document.getElementById('editWebsiteModal').style.display = 'block';
    document.getElementById('edit-website-error').style.display = 'none';

    // Set the value of the is_public select list
    document.getElementById('edit_website_is_public').value = is_public ? 'true' : 'false';
}

function closeEditWebsiteModal() {
    document.getElementById('editWebsiteModal').style.display = 'none';
}

// Event listener for Edit Website form submission
// This listener is attached once in the DOMContentLoaded block in the HTML
// or by calling attachWebsiteFormListeners()
const editWebsiteForm = document.getElementById('editWebsiteForm');
if (editWebsiteForm) {
    editWebsiteForm.addEventListener('submit', async function (event) {
        event.preventDefault();
        const formData = new FormData();
        formData.append("website_id", this.website_id.value);
        formData.append("title", this.title.value);
        formData.append("url", this.url.value);
        formData.append("description", this.description.value);
        // Added is_public to form data
        formData.append("is_public", document.getElementById('edit_website_is_public').value);


        try {
            // Assuming the backend expects website_id in the URL or body for PUT/POST
            const response = await fetch(`/admin/website/edit`, { // Assuming this endpoint exists
                method: 'PUT', // Or 'PUT', depending on your backend API design
                body: formData
            });

            const errorDiv = document.getElementById('edit-website-error');
            errorDiv.style.display = 'none';

            if (!response.ok) {
                const errorData = await response.json();
                errorDiv.textContent = errorData.detail || `HTTP error! status: ${response.status}`;
                errorDiv.style.display = 'block';
            } else {
                closeEditWebsiteModal();
                loadWebsites(); // Reload websites list after successful edit
            }
        } catch (error) {
            const errorDiv = document.getElementById('edit-website-error');
            errorDiv.textContent = `Error editing website: ${error}`;
            errorDiv.style.display = 'block';
        }
    });
}


// Delete Website Function
async function deleteWebsite(websiteId) {
    if (confirm('Are you sure you want to delete this website?')) {
        const formData = new FormData();
        formData.append('website_id', websiteId);

        try {
            // Assuming the backend expects website_id in the body or URL for DELETE
            const response = await fetch(`/admin/website/delete`, { // Assuming this endpoint exists
                method: 'DELETE',
                 // For DELETE with body, you might need to use a different approach
                 // like sending JSON body, or sending website_id as query parameter.
                 // Sending FormData with DELETE might not be universally supported.
                 // Assuming your backend handles DELETE with FormData for now.
                body: formData,
            });

            if (!response.ok) {
                 const errorData = await response.json();
                 alert(`Failed to delete website: ${errorData.detail || response.statusText}`);
            } else {
                loadWebsites(); // Reload websites list after successful delete
            }
        } catch (error) {
             alert(`Error deleting website: ${error}`);
        }
    }
}

// Function to attach form listeners (called in DOMContentLoaded)
function attachWebsiteFormListeners() {
    // The form listeners are already attached directly below the form definitions
    // in this script, wrapped in an if check for existence.
    // This function can remain empty or be used for other initializations if needed.
    console.log("Website form listeners are already attached.");
}

