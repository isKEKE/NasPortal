async function loadUsers() {
    // document.getElementById('dashboard-content').style.display = 'none';
    document.getElementById('website-data').style.display = 'none';
    document.getElementById('user-data').style.display = 'block';
    document.getElementById('user-list-container').innerHTML = '<p class="loading-message">Loading users...</p>';

    try {
        const response = await fetch('/admin/user/list');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const users = await response.json();
        displayUsers(users);
    } catch (error) {
        document.getElementById('user-list-container').innerHTML = `<p class="error-message">Error loading users: ${error}</p>`;
    }
}

function displayUsers(users) {
    let html = '<table class="data-table"><thead><tr><th>ID</th><th>Username</th><th>Created At</th><th>Actions</th></tr></thead><tbody>';
    if (users && users.length > 0) {
        users.forEach(user => {
            const deleteDisabled = user.is_active ? '' : 'disabled style="background-color: gray; cursor: not-allowed;"';
            html += `<tr>
                        <td>${user.id}</td>
                        <td>${user.username}</td>
                        <td>${user.created_at}</td>
                        <td class="action-buttons">
                            <button class="edit-button" onclick="openEditUserModal(${user.id}, '${user.username}', '${user.is_active}')"><i class="fas fa-edit"></i> Edit</button>
                            <button class="delete-button" onclick="deleteUser('${user.username}')" ${deleteDisabled}>
                                <i class="fas fa-trash-alt"></i> Delete
                            </button>
                        </td>
                    </tr>`;
        });
    } else {
        html += '<tr><td colspan="4">No users found.</td></tr>';
    }
    html += '</tbody></table>';
    document.getElementById('user-list-container').innerHTML = html;
}


async function loadWebsites() {
    document.getElementById('dashboard-content').style.display = 'none';
    document.getElementById('user-data').style.display = 'none';
    document.getElementById('website-data').style.display = 'block';
    document.getElementById('website-list-container').innerHTML = '<p class="loading-message">Loading websites...</p>';

    try {
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

function displayWebsites(websites) {
    let html = '<table class="data-table"><thead><tr><th>ID</th><th>Title</th><th>URL</th><th>Description</th></tr></thead><tbody>';
    if (websites && websites.length > 0) {
        websites.forEach(website => {
            html += `<tr><td>${website.id}</td><td>${website.title}</td><td><a href="${website.url}" target="_blank">${website.url}</a></td><td>${website.description || ''}</td></tr>`;
        });
    } else {
        html += '<tr><td colspan="4">No websites found.</td></tr>';
    }
    html += '</tbody></table>';
    document.getElementById('website-list-container').innerHTML = html;
}

// Add User Modal Functions
function openAddUserModal() {
    document.getElementById('addUserModal').style.display = 'block';
    document.getElementById('add-user-error').style.display = 'none';
    document.getElementById('addUserForm').reset();
}

function closeAddUserModal() {
    document.getElementById('addUserModal').style.display = 'none';
}

document.getElementById('addUserForm').addEventListener('submit', async function (event) {
    event.preventDefault();
    const formData = new FormData(this);
    const errorDiv = document.getElementById('add-user-error');
    errorDiv.style.display = 'none';

    try {
        const response = await fetch('/admin/user/add', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            errorDiv.textContent = errorData.detail || `HTTP error! status: ${response.status}`;
            errorDiv.style.display = 'block';
        } else {
            closeAddUserModal();
            loadUsers();
        }
    } catch (error) {
        errorDiv.textContent = `Error adding user: ${error}`;
        errorDiv.style.display = 'block';
    }
});


// Edit User Modal Functions
let currentEditUserId = null;
let currentUserIsActive = null;

function openEditUserModal(userId, username, is_active) {
    currentEditUserId = userId;
    currentUserIsActive = is_active;
    document.getElementById('edit_user_id').value = userId;
    document.getElementById('edit_username').value = username;
    document.getElementById('edit_password').value = '';
    document.getElementById('editUserModal').style.display = 'block';
    document.getElementById('edit-user-error').style.display = 'none';
    document.getElementById('edit_is_active').value = is_active.toString();
}

function closeEditUserModal() {
    document.getElementById('editUserModal').style.display = 'none';
}

document.getElementById('editUserForm').addEventListener('submit', async function (event) {
    event.preventDefault();
    const formData = new FormData();
    formData.append("user_id", this.user_id.value);
    formData.append("new_password", this.new_password.value);
    formData.append("is_active", this.is_active.value);


    try {
        const response = await fetch(`/admin/user/edit`, {
            method: 'PUT', // Keep as POST if your backend expects form data this way
            body: formData
        });

        const errorDiv = document.getElementById('edit-user-error');
        errorDiv.style.display = 'none';

        if (!response.ok) {
            const errorData = await response.json();
            errorDiv.textContent = errorData.detail || `HTTP error! status: ${response.status}`;
            errorDiv.style.display = 'block';
        } else {
            closeEditUserModal();
            loadUsers();
        }
    } catch (error) {
        const errorDiv = document.getElementById('edit-user-error');
        errorDiv.textContent = `Error editing user: ${error}`;
        errorDiv.style.display = 'block';
    }
});

// Delete User Function
async function deleteUser(username) {
    if (confirm('Are you sure you want to delete this user?')) {
        const formData = new FormData();
        formData.append('username', username);

        try {
            const response = await fetch(`/admin/user/delete`, {
                method: 'DELETE',
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                alert(`Status: ${response.status}. ` + errorData.detail);
            } else {
                loadUsers();
            }
        } catch (error) {
            alert(`Error deleting user: ${error}`);
        }
    }
}


