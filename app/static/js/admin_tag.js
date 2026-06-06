// Function to load and display the list of tags
async function loadTags() {
    const tagListContainer = document.getElementById('tag-list-container');
    if (!tagListContainer) return;

    const tagData = document.getElementById('tag-data');
    const userData = document.getElementById('user-data');
    const websiteData = document.getElementById('website-data');

    if (tagData) tagData.style.display = 'block';
    if (userData) userData.style.display = 'none';
    if (websiteData) websiteData.style.display = 'none';

    // 安全地更新导航链接样式
    document.getElementById('users-link')?.classList.remove('active');
    document.getElementById('websites-link')?.classList.remove('active');
    document.getElementById('tags-link')?.classList.add('active');

    tagListContainer.innerHTML = '<p class="loading-message">Loading tags...</p>';

    try {
        const response = await fetch('/admin/tag/list');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        displayTags(await response.json());
    } catch (error) {
        tagListContainer.innerHTML = `<p class="error-message">Error loading tags: ${error}</p>`;
    }
}


// Function to display the list of tags in a table
function displayTags(tags) {
    let html = '<table class="data-table"><thead><tr><th>ID</th><th>Name</th><th>Actions</th></tr></thead><tbody>';
    if (tags && tags.length > 0) {
        tags.forEach(tag => {
            html += `<tr>
                        <td>${tag.id}</td>
                        <td>${tag.name}</td>
                        <td class="action-buttons">
                            <button class="edit-button" data-tag-id="${tag.id}" data-name="${tag.name}"><i class="fas fa-edit"></i> Edit</button>
                            <button class="delete-button" data-tag-id="${tag.id}"><i class="fas fa-trash-alt"></i> Delete</button>
                        </td>
                    </tr>`;
        });
    } else {
        html += '<tr><td colspan="3">No tags found.</td></tr>';
    }
    html += '</tbody></table>';
    document.getElementById('tag-list-container').innerHTML = html;

    // Attach event listeners to the buttons
    attachTagButtonListeners();
}

// Function to attach event listeners to tag buttons
function attachTagButtonListeners() {
    // Edit button listeners
    const editButtons = document.querySelectorAll('.data-table .edit-button');
    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tagId = this.dataset.tagId;
            const name = this.dataset.name;
            openEditTagModal(tagId, name);
        });
    });

    // Delete button listeners
    const deleteButtons = document.querySelectorAll('.data-table .delete-button');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tagId = this.dataset.tagId;
            deleteTag(tagId);
        });
    });
}

// Add Tag Modal Functions
function openAddTagModal() {
    document.getElementById('addTagModal').style.display = 'block';
    document.getElementById('add-tag-error').style.display = 'none';
    document.getElementById('addTagForm').reset();
}

function closeAddTagModal() {
    document.getElementById('addTagModal').style.display = 'none';
}

// Event listener for Add Tag form submission
const addTagForm = document.getElementById('addTagForm');
if (addTagForm) {
    addTagForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        const formData = new FormData(this);
        const errorDiv = document.getElementById('add-tag-error');
        errorDiv.style.display = 'none';

        try {
            const response = await fetch('/admin/tag/add', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                errorDiv.textContent = errorData.detail || `HTTP error! status: ${response.status}`;
                errorDiv.style.display = 'block';
            } else {
                closeAddTagModal();
                loadTags(); // Reload tags list after successful add
            }
        } catch (error) {
            errorDiv.textContent = `Error adding tag: ${error}`;
            errorDiv.style.display = 'block';
        }
    });
}

// Edit Tag Modal Functions
let currentEditTagId = null;

function openEditTagModal(tagId, name) {
    currentEditTagId = tagId;
    document.getElementById('edit_tag_id').value = tagId;
    document.getElementById('edit_tag_name').value = name;
    document.getElementById('editTagModal').style.display = 'block';
    document.getElementById('edit-tag-error').style.display = 'none';
}

function closeEditTagModal() {
    document.getElementById('editTagModal').style.display = 'none';
}

// Event listener for Edit Tag form submission
const editTagForm = document.getElementById('editTagForm');
if (editTagForm) {
    editTagForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        const formData = new FormData();
        formData.append('tag_id', this.tag_id.value);
        formData.append('name', this.name.value);

        const errorDiv = document.getElementById('edit-tag-error');
        errorDiv.style.display = 'none';

        try {
            const response = await fetch('/admin/tag/edit', {
                method: 'PUT',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                errorDiv.textContent = errorData.detail || `HTTP error! status: ${response.status}`;
                errorDiv.style.display = 'block';
            } else {
                closeEditTagModal();
                loadTags(); // Reload tags list after successful edit
            }
        } catch (error) {
            errorDiv.textContent = `Error editing tag: ${error}`;
            errorDiv.style.display = 'block';
        }
    });
}

// Delete Tag Function
async function deleteTag(tagId) {
    if (confirm('Are you sure you want to delete this tag?')) {
        const formData = new FormData();
        formData.append('tag_id', tagId);

        try {
            const response = await fetch('/admin/tag/delete', {
                method: 'DELETE',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                alert(`Failed to delete tag: ${errorData.detail || response.statusText}`);
            } else {
                loadTags(); // Reload tags list after successful delete
            }
        } catch (error) {
            alert(`Error deleting tag: ${error}`);
        }
    }
}

// Function to attach form listeners (called in DOMContentLoaded)
function attachTagFormListeners() {
    // The form listeners are already attached directly below the form definitions
    console.log("Tag form listeners are already attached.");
}