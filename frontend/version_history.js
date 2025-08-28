// Functions for version history management
async function showVersionHistory(agentId) {
    console.log(`Showing version history for agent ${agentId}`);
    
    // Show the modal and overlay
    const versionModal = document.getElementById('version-modal');
    const modalOverlay = document.getElementById('modal-overlay');
    
    if (!versionModal || !modalOverlay) {
        console.error('Version modal elements not found');
        return;
    }
    
    // Show loading state
    document.getElementById('version-list').innerHTML = '<div class="loading-versions">Loading version history...</div>';
    
    // Display the modal
    versionModal.style.display = 'block';
    modalOverlay.style.display = 'block';
    modalOverlay.style.visibility = 'visible';
    modalOverlay.style.opacity = '1';
    
    // Add click event to close button
    const closeBtn = document.getElementById('close-version-modal');
    if (closeBtn) {
        closeBtn.onclick = closeVersionModal;
    }
    
    // Add click event to overlay
    modalOverlay.onclick = closeVersionModal;
    
    try {
        // Fetch version history from API
        const response = await fetch(`/api/agent/${agentId}/versions`);
        
        if (!response.ok) {
            throw new Error(`Failed to fetch version history: ${response.status}`);
        }
        
        const data = await response.json();
        displayVersionHistory(agentId, data.versions);
        
    } catch (error) {
        console.error('Error fetching version history:', error);
        document.getElementById('version-list').innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-circle"></i>
                <p>Failed to load version history: ${error.message}</p>
            </div>
        `;
    }
}

function closeVersionModal() {
    const versionModal = document.getElementById('version-modal');
    const modalOverlay = document.getElementById('modal-overlay');
    
    if (versionModal) {
        versionModal.style.display = 'none';
    }
    
    if (modalOverlay) {
        modalOverlay.style.visibility = 'hidden';
        modalOverlay.style.opacity = '0';
        setTimeout(() => {
            modalOverlay.style.display = 'none';
        }, 300);
    }
}

function displayVersionHistory(agentId, versions) {
    const versionList = document.getElementById('version-list');
    
    if (!versions || versions.length === 0) {
        versionList.innerHTML = '<div class="no-versions">No version history found.</div>';
        return;
    }
    
    // Clear and create version items
    versionList.innerHTML = '';
    
    versions.forEach(version => {
        const versionItem = document.createElement('div');
        versionItem.className = `version-item ${version.is_current ? 'current' : ''}`;
        
        const date = new Date(version.created_at);
        const formattedDate = date.toLocaleString();
        
        versionItem.innerHTML = `
            <div class="version-header">
                <div>
                    <span class="version-badge">v${version.version_number}</span>
                    <strong>${version.name}</strong>
                    ${version.is_current ? '<span class="current-badge"> (Current)</span>' : ''}
                </div>
                <span class="version-date">${formattedDate}</span>
            </div>
            
            <div class="version-details">
                <p>${version.description}</p>
                <p><strong>Model:</strong> ${version.model}</p>
            </div>
            
            ${!version.is_current ? `
                <div class="version-controls">
                    <button class="primary-button restore-btn" data-agent-id="${agentId}" data-version="${version.version_number}">
                        <i class="fas fa-undo"></i> Restore this version
                    </button>
                </div>
            ` : ''}
        `;
        
        versionList.appendChild(versionItem);
    });
    
    // Add event listeners to restore buttons
    document.querySelectorAll('.restore-btn').forEach(btn => {
        btn.addEventListener('click', async function() {
            const agentId = this.getAttribute('data-agent-id');
            const versionNumber = this.getAttribute('data-version');
            await restoreVersion(agentId, versionNumber);
        });
    });
}

async function restoreVersion(agentId, versionNumber) {
    if (!confirm(`Are you sure you want to restore agent to version ${versionNumber}? This will create a new version based on the current state before restoring.`)) {
        return;
    }
    
    try {
        // Show loading state
        const restoreBtn = document.querySelector(`.restore-btn[data-version="${versionNumber}"]`);
        if (restoreBtn) {
            restoreBtn.disabled = true;
            restoreBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Restoring...';
        }
        
        // Call API to restore version
        const response = await fetch(`/api/agent/${agentId}/restore/${versionNumber}`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`Failed to restore version: ${response.status}`);
        }
        
        // Get updated agent data
        const result = await response.json();
        
        // Show success message
        showNotification(`Successfully restored agent to version ${versionNumber}`, 'success');
        
        // Close modal and refresh agents list
        closeVersionModal();
        fetchAgents();
        
    } catch (error) {
        console.error('Error restoring version:', error);
        showNotification(`Failed to restore version: ${error.message}`, 'error');
        
        // Reset button state
        const restoreBtn = document.querySelector(`.restore-btn[data-version="${versionNumber}"]`);
        if (restoreBtn) {
            restoreBtn.disabled = false;
            restoreBtn.innerHTML = '<i class="fas fa-undo"></i> Restore this version';
        }
    }
}
