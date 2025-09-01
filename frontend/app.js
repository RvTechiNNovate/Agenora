document.addEventListener('DOMContentLoaded', function() {
    // Initialize app
    console.log('DOM loaded, initializing app');
    
    // Initialize settings
    initSettings();
    
    // Set up create agent button handlers
    const createAgentBtn = document.getElementById('create-agent-btn');
    if (createAgentBtn) {
        createAgentBtn.addEventListener('click', function() {
            openModal('create');
            return false;
        });
    }
    
    // Set up sidebar toggle
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    // Function to handle sidebar state updates
    function updateSidebarState(isCollapsed) {
        // Update the toggle icon
        const toggleIcon = sidebarToggle.querySelector('i');
        if (toggleIcon) {
            if (isCollapsed) {
                toggleIcon.className = 'fas fa-chevron-right';
            } else {
                toggleIcon.className = 'fas fa-chevron-left';
            }
        }
        
        // Save the sidebar state in localStorage
        localStorage.setItem('sidebarCollapsed', isCollapsed);
    }
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            updateSidebarState(sidebar.classList.contains('collapsed'));
        });
        
        // Check for saved sidebar state
        const savedState = localStorage.getItem('sidebarCollapsed');
        if (savedState === 'true') {
            sidebar.classList.add('collapsed');
            updateSidebarState(true);
        }
    }
    
    // Mobile menu toggle
    if (mobileMenuToggle && sidebar) {
        mobileMenuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
            
            // Update mobile toggle icon
            const mobileIcon = mobileMenuToggle.querySelector('i');
            if (mobileIcon) {
                if (sidebar.classList.contains('active')) {
                    mobileIcon.className = 'fas fa-times';
                } else {
                    mobileIcon.className = 'fas fa-bars';
                }
            }
        });
        
        // Close sidebar when clicking on a nav item on mobile
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', function() {
                if (window.innerWidth <= 768) {
                    sidebar.classList.remove('active');
                    if (mobileMenuToggle.querySelector('i')) {
                        mobileMenuToggle.querySelector('i').className = 'fas fa-bars';
                    }
                }
            });
        });
    }
    
    // Debug click handler for the whole document
    document.addEventListener('click', function(e) {
        console.log('Document clicked:', e.target);
        
        // Check if the clicked element is one of our create buttons by class or text
        if (e.target.classList.contains('primary-button') || 
            (e.target.textContent && e.target.textContent.includes('Create Agent'))) {
            console.log('Possible create button clicked:', e.target);
        }
    });
    
    // Initialize modal elements directly
    console.log('Initializing modal elements');
    const modal = document.getElementById('agent-modal');
    const modalOverlay = document.getElementById('modal-overlay');
    
    console.log('Modal elements found on load:', {
        modal: modal ? true : false,
        modalOverlay: modalOverlay ? true : false,
        modalHTML: modal ? modal.outerHTML : 'null'
    });
    
    // Add global functions for modal operations
    window.showCreateAgentModal = function() {
        console.log('showCreateAgentModal called');
        
        try {
            // Direct approach to show modal
            const modal = document.getElementById('agent-modal');
            const modalOverlay = document.getElementById('modal-overlay');
            const form = document.getElementById('agent-form');
            
            if (modal && modalOverlay) {
                console.log('Found modal elements, showing directly');
                
                // Set form for creation
                if (form) {
                    form.reset();
                    form.setAttribute('data-mode', 'create');
                    document.getElementById('modal-title').textContent = 'Create New Agent';
                    document.getElementById('form-submit-btn').textContent = 'Create Agent';
                }
                
                // Direct style modification
                modal.style.display = 'block';
                modal.style.visibility = 'visible';
                modal.style.opacity = '1';
                
                modalOverlay.style.display = 'block';
                modalOverlay.style.visibility = 'visible';
                modalOverlay.style.opacity = '1';
                
                // Add classes
                modal.classList.add('show');
                modalOverlay.classList.add('show');
                document.body.classList.add('modal-open');
                
                // Update models list
                try {
                    updateModelsForProvider('openai');
                } catch (e) {
                    console.error('Error updating models:', e);
                }
                
                return true;
            } else {
                console.error('Modal elements not found, falling back to openModal');
                openModal('create');
            }
        } catch (error) {
            console.error('Error in showCreateAgentModal:', error);
            try {
                openModal('create');
            } catch (e) {
                console.error('Fallback also failed:', e);
            }
        }
    };
    
    // Add direct onclick handlers to HTML elements if they exist
    const createAgentBtns = document.querySelectorAll('.nav-item');
    createAgentBtns.forEach(btn => {
        if (btn.textContent && btn.textContent.trim().includes('Create Agent')) {
            btn.setAttribute('onclick', 'showCreateAgentModal(); return false;');
            console.log('Added direct onclick to button:', btn);
        }
    });
    
    initNavigation();
    initFormHandlers();
    initPlayground();
});

function initSettings() {
    // Add click handler for save settings button
    const saveBtn = document.getElementById('save-settings-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveSettings);
    }
    
    // Toggle password visibility
    const toggleBtns = document.querySelectorAll('.toggle-password');
    toggleBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const input = this.previousElementSibling;
            const icon = this.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });
    
    // Load existing settings
    loadSettings();
}

async function saveSettings() {
    const settings = {
        openai_api_key: document.getElementById('openai-api-key').value,
        azure_api_key: document.getElementById('azure-api-key').value,
        groq_api_key: document.getElementById('groq-api-key').value
    };
    
    try {
        const response = await fetch('/api/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        });
        
        if (response.ok) {
            showNotification('Settings saved successfully!', 'success');
        } else {
            const error = await response.text();
            showNotification(`Failed to save settings: ${error}`, 'error');
        }
    } catch (error) {
        showNotification(`Error saving settings: ${error.message}`, 'error');
    }
}


async function loadSettings() {
    try {
        const response = await fetch('/api/settings');
        if (response.ok) {
            const settings = await response.json();
            
            // Populate form fields
            if (settings.openai_api_key) {
                document.getElementById('openai-api-key').value = settings.openai_api_key;
            }
            if (settings.anthropic_api_key) {
                document.getElementById('anthropic-api-key').value = settings.anthropic_api_key;
            }
            if (settings.google_api_key) {
                document.getElementById('google-api-key').value = settings.google_api_key;
            }
        }
    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.classList.add('notification', type);
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Remove notification after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Navigation Functions
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const pages = document.querySelectorAll('.page');
    
    // Handle page navigation
    navItems.forEach(item => {
        if (item.getAttribute('data-page')) { // Only for items that switch pages
            item.addEventListener('click', function(e) {
                const targetPage = this.getAttribute('data-page');
                console.log(`Navigating to page: ${targetPage}`);
                
                // Hide all pages and remove active class from nav items
                pages.forEach(page => {
                    page.classList.remove('active');
                    page.classList.add('hidden');
                });
                navItems.forEach(item => item.classList.remove('active'));
                
                // Show target page and set active class
                const targetPageElement = document.getElementById(targetPage + '-page');
                if (targetPageElement) {
                    targetPageElement.classList.remove('hidden');
                    targetPageElement.classList.add('active');
                    this.classList.add('active');
                    
                    // If navigating to agents page, refresh the agents list
                    if (targetPage === 'agents') {
                        fetchAgents();
                    }
                } else {
                    console.error(`Target page element not found: ${targetPage}-page`);
                }
            });
        }
    });
    
    // Handle create agent button click
    console.log('Checking for create-agent-btn element');
    const createAgentBtn = document.getElementById('create-agent-btn');
    if (createAgentBtn) {
        console.log('create-agent-btn found, adding click handler');
        createAgentBtn.addEventListener('click', (event) => {
            event.preventDefault();
            console.log('Create agent button clicked');
            console.log('Button element:', event.target);
            try {
                openModal('create');
            } catch (error) {
                console.error('Error in openModal from create-agent-btn:', error);
            }
        });
        
        // Add direct onclick attribute as backup
        createAgentBtn.setAttribute('onclick', 'try { openModal("create"); } catch(e) { console.error(e); }');
    } else {
        console.error('create-agent-btn element not found!');
        // Try to find by class or other attribute
        const possibleButtons = document.querySelectorAll('.nav-item');
        console.log('Found nav-items:', possibleButtons.length);
        possibleButtons.forEach(btn => {
            console.log('Nav item:', btn.outerHTML);
        });
    }
    
    // Handle create agent button in agents page
    console.log('Checking for agents-create-btn element');
    const agentsCreateBtn = document.getElementById('agents-create-btn');
    if (agentsCreateBtn) {
        console.log('agents-create-btn found, adding click handler');
        agentsCreateBtn.addEventListener('click', (event) => {
            event.preventDefault();
            console.log('Agents page create button clicked');
            console.log('Button element:', event.target);
            try {
                openModal('create');
            } catch (error) {
                console.error('Error in openModal from agents-create-btn:', error);
            }
        });
        
        // Add direct onclick attribute as backup
        agentsCreateBtn.setAttribute('onclick', 'try { openModal("create"); } catch(e) { console.error(e); }');
    } else {
        console.error('agents-create-btn element not found!');
    }
    
    // Set default active page
    document.getElementById('playground-page').classList.add('active');
    document.getElementById('playground-page').classList.remove('hidden');
}

// Modal Functions
function openModal(mode, agentId = null) {
    console.log('Opening modal:', mode, agentId);
    const modal = document.getElementById('agent-modal');
    const modalOverlay = document.getElementById('modal-overlay');
    
    console.log('Modal elements:', {
        modal: modal,
        modalOverlay: modalOverlay,
        modalHTML: modal ? modal.outerHTML : 'null'
    });
    
    if (!modal || !modalOverlay) {
        console.error('Modal elements not found:', {modal, modalOverlay});
        return;
    }
    
    const form = document.getElementById('agent-form');
    const title = document.getElementById('modal-title');
    const submitButton = document.getElementById('form-submit-btn');
    
    if (!form || !title || !submitButton) {
        console.error('Modal child elements not found:', {form, title, submitButton});
        // Continue anyway, the modal should still be shown
    }
    
    try {
        // Reset form if it exists
        if (form) {
            form.reset();
            
            if (mode === 'create') {
                title.textContent = 'Create New Agent';
                submitButton.textContent = 'Create Agent';
                form.setAttribute('data-mode', 'create');
                form.removeAttribute('data-agent-id');
                
                // Set default values
                const frameworkElement = document.getElementById('framework');
                if (frameworkElement) {
                    frameworkElement.value = 'crewai';
                }
                
                // Initialize provider dropdown and models
                initProviderSelect().then(() => {
                    // Default to openai provider
                    const providerSelect = document.getElementById('provider');
                    if (providerSelect) {
                        for (let i = 0; i < providerSelect.options.length; i++) {
                            if (providerSelect.options[i].value === 'openai') {
                                providerSelect.selectedIndex = i;
                                break;
                            }
                        }
                        updateModelsForProvider('openai');
                    } else {
                        console.error('Provider select not found when initializing default provider');
                    }
                });
                
            } else if (mode === 'edit') {
                title.textContent = 'Edit Agent';
                submitButton.textContent = 'Update Agent';
                form.setAttribute('data-mode', 'edit');
                form.setAttribute('data-agent-id', agentId);
                
                // Load agent data
                loadAgentData(agentId);
            }
        }
    } catch (error) {
        console.error('Error setting up form:', error);
    }
    
    // Try different approaches to make the modal visible
    try {
        // 1. Add classes
        console.log('Adding visibility classes to modal');
        modal.classList.add('show');
        modal.classList.add('active');
        modalOverlay.classList.add('show');
        modalOverlay.classList.add('active');
        document.body.classList.add('modal-open');
        
        // 2. Force inline style
        console.log('Setting inline styles');
        modal.style.display = 'block';
        modal.style.visibility = 'visible';
        modal.style.opacity = '1';
        modal.style.zIndex = '1000';
        
        modalOverlay.style.display = 'block';
        modalOverlay.style.visibility = 'visible';
        modalOverlay.style.opacity = '1';
        modalOverlay.style.zIndex = '999';
        
        // Log the result
        console.log('Modal display style:', modal.style.display);
        console.log('Modal visibility:', modal.style.visibility);
        console.log('Modal element after changes:', modal.outerHTML);
    } catch (error) {
        console.error('Error making modal visible:', error);
    }
}

function closeModal() {
    console.log('Closing modal');
    const modal = document.getElementById('agent-modal');
    const modalOverlay = document.getElementById('modal-overlay');
    
    if (!modal || !modalOverlay) {
        console.error('Modal elements not found when closing');
        return;
    }
    
    // Remove both classes
    modal.classList.remove('show');
    modal.classList.remove('active');
    modalOverlay.classList.remove('show');
    modalOverlay.classList.remove('active');
    document.body.classList.remove('modal-open');
    
    // Reset inline styles
    modal.style.display = '';
    modalOverlay.style.display = '';
}

// Form Handlers
function initFormHandlers() {
    console.log('Initializing form handlers');
    
    // Initialize provider select with available options
    initProviderSelect();
    
    // Provider change handler - updates model list
    const providerSelect = document.getElementById('provider');
    if (providerSelect) {
        providerSelect.addEventListener('change', function() {
            updateModelsForProvider(this.value);
        });
    } else {
        console.error('Provider select element not found');
    }
    
    // Temperature slider handler
    const tempSlider = document.getElementById('temperature');
    const tempValue = document.getElementById('temperature-value');
    if (tempSlider && tempValue) {
        tempSlider.addEventListener('input', function() {
            tempValue.textContent = this.value;
        });
    } else {
        console.error('Temperature slider elements not found');
    }
    
    // Close modal button
    const closeModalBtn = document.querySelector('.close-modal');
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeModal);
    } else {
        console.error('Close modal button not found');
    }
    
    // Modal overlay click to close
    const modalOverlay = document.getElementById('modal-overlay');
    if (modalOverlay) {
        modalOverlay.addEventListener('click', closeModal);
    } else {
        console.error('Modal overlay element not found');
    }
    
    // Form submission
    const agentForm = document.getElementById('agent-form');
    if (agentForm) {
        agentForm.addEventListener('submit', handleFormSubmit);
    } else {
        console.error('Agent form not found');
    }
    
    // Initialize models for default provider
    updateModelsForProvider('openai');
}

// Initialize provider select dropdown with available options
async function initProviderSelect() {
    try {
        // Get the provider select element
        const providerSelect = document.getElementById('provider');
        
        // Clear existing options
        providerSelect.innerHTML = '';
        
        // Fetch available providers
        console.log('Fetching available LLM providers');
        const response = await fetch('/api/llm/providers');
        if (response.ok) {
            const data = await response.json();
            console.log('Available providers:', data);
            
            // Check if we have providers from the API
            if (data.providers && data.providers.length > 0) {
                // Track provider IDs to prevent duplicates
                const addedProviders = new Set();
                
                // Add each provider as an option, avoiding duplicates
                data.providers.forEach(provider => {
                    // Skip if we've already added this provider
                    if (addedProviders.has(provider.id)) {
                        console.warn(`Duplicate provider ${provider.id} found, skipping`);
                        return;
                    }
                    
                    const option = document.createElement('option');
                    option.value = provider.id;
                    option.textContent = provider.name;
                    
                    if (provider.model_count) {
                        option.textContent += ` (${provider.model_count} models)`;
                    }
                    
                    providerSelect.appendChild(option);
                    addedProviders.add(provider.id);
                });
                
                console.log('Populated provider select with', addedProviders.size, 'options');
                
                // No need for fallback if we got providers from API
                return;
            }
            
            // Fallback options if no providers returned
            console.warn('No providers returned from API, using defaults');
        } else {
            // Fallback if API fails
            console.error('Failed to fetch providers, status:', response.status);
        }
        
        // Add default providers as fallback
        addDefaultProviders(providerSelect);
    } catch (error) {
        console.error('Error initializing provider select:', error);
        // Fallback to default providers
        addDefaultProviders(document.getElementById('provider'));
    }
}

// Add default provider options if API fails
function addDefaultProviders(selectElement) {
    if (!selectElement) return;
    
    // First, check if we already have options to avoid duplicates
    if (selectElement.options.length > 0) {
        console.log('Provider select already has options, skipping defaults');
        return;
    }
    
    const providers = [
        { id: 'openai', name: 'OpenAI' },
        { id: 'azure', name: 'Azure OpenAI' },
        { id: 'groq', name: 'Groq' }
    ];
    
    console.log('Adding default providers:', providers);
    
    providers.forEach(provider => {
        const option = document.createElement('option');
        option.value = provider.id;
        option.textContent = provider.name;
        selectElement.appendChild(option);
    });
}

async function updateModelsForProvider(provider) {
    try {
        console.log(`Fetching models for provider: ${provider}`);
        const response = await fetch(`/api/llm/models?provider=${provider}`);
        const data = await response.json();
        console.log('Models data:', data);
        
        const modelSelect = document.getElementById('model');
        modelSelect.innerHTML = '';
        
        if (data.models && data.models.length > 0) {
            data.models.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model;
                modelSelect.appendChild(option);
            });
            
            // Select first model as default
            modelSelect.value = data.models[0];
        } else {
            // Add fallback option if no models returned
            modelSelect.innerHTML = '<option value="">No models available</option>';
        }
        
    } catch (error) {
        console.error('Error loading models:', error);
        
        // Add fallback option
        const modelSelect = document.getElementById('model');
        modelSelect.innerHTML = '<option value="">Unable to load models</option>';
    }
}

async function handleFormSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const mode = form.getAttribute('data-mode');
    const submitButton = document.getElementById('form-submit-btn');
    
    // Disable submit button to prevent multiple submissions
    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
    
    try {
        // Get selected framework
        const framework = document.getElementById('framework').value;
        console.log('Selected framework:', framework);
        
        // Debug LangGraph fields if selected
        if (framework === 'langgraph') {
            const promptField = document.getElementById('langgraph_prompt');
            console.log('LangGraph prompt field value at submission:', promptField ? promptField.value : 'not found');
        }
        
        // Get form data based on selected framework
        const formData = collectFrameworkSpecificFormData(framework);
        
        // Ensure LangGraph required fields are included
        if (framework === 'langgraph') {
            if (!formData.prompt) {
                formData.prompt = document.getElementById('langgraph_prompt')?.value || 'Default ReAct agent prompt';
            }
            if (!formData.tools) {
                const toolsInput = document.getElementById('langgraph_tools')?.value || '';
                formData.tools = toolsInput ? toolsInput.split(',').map(tool => tool.trim()) : [];
            }
        }
        
        // Log the form data for debugging
        console.log('Form data being sent:', JSON.stringify(formData));
        
        let response;
        
        if (mode === 'create') {
            const payload = JSON.stringify(formData);
            console.log('Final JSON payload:', payload);
            
            response = await fetch('/api/agent', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: payload
            });
        } else if (mode === 'edit') {
            const agentId = form.getAttribute('data-agent-id');
            const payload = JSON.stringify(formData);
            console.log('Final JSON payload for edit:', payload);
            
            response = await fetch(`/api/agent/${agentId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: payload
            });
        }
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Something went wrong');
        }
        
        // Close modal and refresh agents
        closeModal();
        fetchAgents();
        
    } catch (error) {
        console.error('Error submitting agent:', error);
        alert(`Error: ${error.message}`);
    } finally {
        // Re-enable submit button
        submitButton.disabled = false;
        submitButton.textContent = mode === 'create' ? 'Create Agent' : 'Update Agent';
    }
}

function formatModelWithProvider() {
    const provider = document.getElementById('provider').value;
    const model = document.getElementById('model').value;
    
    if (!model) return '';
    
    // If model already has provider prefix, return as is
    if (model.includes(':')) {
        return model;
    }
    
    return `${provider}:${model}`;
}

// Agent Management Functions
async function fetchAgents() {
    try {
        console.log('Fetching agents...');
        const res = await fetch('/api/agents');
        const agents = await res.json();
        console.log('Agents fetched:', agents);
        
        // Update agents grid view
        updateAgentsGrid(agents);
        
        // Update playground agent selector
        updatePlaygroundAgentSelector(agents);
        
    } catch (error) {
        console.error('Error fetching agents:', error);
    }
}

function updateAgentsGrid(agents) {
    const agentsGrid = document.getElementById('agents-grid');
    
    // Clear current content
    agentsGrid.innerHTML = '';
    
    if (!agents || Object.keys(agents).length === 0) {
        agentsGrid.innerHTML = `
            <div class="no-agents">
                <p>No agents created yet. Create your first agent!</p>
                <button class="primary-button" id="create-first-agent-btn">
                    <i class="fas fa-plus"></i> Create Agent
                </button>
            </div>
        `;
        
        // Add event listener to the newly created button
        const createFirstAgentBtn = document.getElementById('create-first-agent-btn');
        if (createFirstAgentBtn) {
            createFirstAgentBtn.addEventListener('click', function() {
                console.log('Create first agent button clicked');
                openModal('create');
            });
        }
        return;
    }
    
    // Create cards for each agent
    Object.entries(agents).forEach(([id, agent]) => {
        const card = document.createElement('div');
        card.className = 'agent-card';
        
        // Create card content
        card.innerHTML = `
            <div class="agent-header">
                <h3>${agent.name}</h3>
                <span class="tag status ${agent.status}">${agent.status}</span>
                <span class="tag version">v${agent.version || 1}</span>
            </div>
            <p class="agent-description">${agent.description}</p>
            <div class="agent-details">
                <p><span class="tag framework">${agent.framework.charAt(0).toUpperCase() + agent.framework.slice(1)}</span></p>
                <p><strong>Model:</strong> ${agent.model}</p>
            </div>
            <div class="agent-controls">
                ${agent.status === 'stopped' ? 
                    `<button class="primary-button start-btn" data-id="${id}" title="Start Agent"><i class="fas fa-play"></i><span class="btn-text"> Start</span></button>` : 
                    `<button class="secondary-button stop-btn" data-id="${id}" title="Stop Agent"><i class="fas fa-stop"></i><span class="btn-text"> Stop</span></button>`
                }
                <button class="edit-btn" data-id="${id}" title="Edit Agent"><i class="fas fa-edit"></i><span class="btn-text"> Edit</span></button>
                <button class="history-btn" data-id="${id}" title="Version History"><i class="fas fa-history"></i><span class="btn-text"> History</span></button>
                <button class="delete-btn" data-id="${id}" title="Delete Agent"><i class="fas fa-trash"></i><span class="btn-text"> Delete</span></button>
            </div>
        `;
        
        // Add event listeners to buttons
        agentsGrid.appendChild(card);
    });
    
    // Add event listeners to the newly created buttons
    document.querySelectorAll('.start-btn').forEach(btn => {
        btn.addEventListener('click', () => startAgent(btn.getAttribute('data-id')));
    });
    
    document.querySelectorAll('.stop-btn').forEach(btn => {
        btn.addEventListener('click', () => stopAgent(btn.getAttribute('data-id')));
    });
    
    // /* Add event listeners to the newly created buttons
    document.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', () => openModal('edit', btn.getAttribute('data-id')));
    });
    
    document.querySelectorAll('.history-btn').forEach(btn => {
        btn.addEventListener('click', () => showVersionHistory(btn.getAttribute('data-id')));
    });
    
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', () => deleteAgent(btn.getAttribute('data-id')));
    });
}

function updatePlaygroundAgentSelector(agents) {
    const selector = document.getElementById('playground-agent');
    selector.innerHTML = '';
    
    let runningAgentsExist = false;
    
    // Add option for each running agent
    Object.entries(agents).forEach(([id, agent]) => {
        if (agent.status === 'running') {
            runningAgentsExist = true;
            const option = document.createElement('option');
            option.value = id;
            option.textContent = agent.name;
            selector.appendChild(option);
        }
    });
    
    // Set currentAgentId if we have a running agent
    if (runningAgentsExist && selector.options.length > 0) {
        currentAgentId = selector.value;
        document.getElementById('send-message').disabled = false;
    } else {
        // No running agents available
        const option = document.createElement('option');
        option.textContent = '-- No running agents available --';
        option.disabled = true;
        selector.appendChild(option);
        selector.selectedIndex = 0;
        
        currentAgentId = null;
        document.getElementById('send-message').disabled = true;
    }
    
    // Add change handler to update currentAgentId when selection changes
    selector.addEventListener('change', () => {
        currentAgentId = selector.value;
    });
}

async function startAgent(agentId) {
    try {
        const startBtn = document.querySelector(`.start-btn[data-id="${agentId}"]`);
        if (startBtn) {
            startBtn.disabled = true;
            startBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Starting...';
        }
        
        const response = await fetch(`/api/agent/${agentId}/start`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('Failed to start agent');
        }
        
        // Refresh agents list
        fetchAgents();
        
    } catch (error) {
        console.error('Error starting agent:', error);
        alert(`Error starting agent: ${error.message}`);
        
        // Reset button state
        const startBtn = document.querySelector(`.start-btn[data-id="${agentId}"]`);
        if (startBtn) {
            startBtn.disabled = false;
            startBtn.innerHTML = '<i class="fas fa-play"></i> Start';
        }
    }
}

async function stopAgent(agentId) {
    try {
        const stopBtn = document.querySelector(`.stop-btn[data-id="${agentId}"]`);
        if (stopBtn) {
            stopBtn.disabled = true;
            stopBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Stopping...';
        }
        
        const response = await fetch(`/api/agent/${agentId}/stop`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('Failed to stop agent');
        }
        
        // Refresh agents list
        fetchAgents();
        
    } catch (error) {
        console.error('Error stopping agent:', error);
        alert(`Error stopping agent: ${error.message}`);
        
        // Reset button state
        const stopBtn = document.querySelector(`.stop-btn[data-id="${agentId}"]`);
        if (stopBtn) {
            stopBtn.disabled = false;
            stopBtn.innerHTML = '<i class="fas fa-stop"></i> Stop';
        }
    }
}

async function deleteAgent(agentId) {
    // Confirm deletion
    if (!confirm('Are you sure you want to delete this agent? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/agent/${agentId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete agent');
        }
        
        // Refresh agents list
        fetchAgents();
        
    } catch (error) {
        console.error('Error deleting agent:', error);
        alert(`Error deleting agent: ${error.message}`);
    }
}

async function loadAgentData(agentId) {
    try {
        const response = await fetch(`/api/agent/${agentId}`);
        
        if (!response.ok) {
            throw new Error('Failed to load agent data');
        }
        
        const agent = await response.json();
        
        // Fill form fields with agent data
        document.getElementById('name').value = agent.name || '';
        document.getElementById('description').value = agent.description || '';
        document.getElementById('role').value = agent.role || '';
        document.getElementById('backstory').value = agent.backstory || '';
        document.getElementById('task').value = agent.task || '';
        
        // Set framework
        const frameworkSelect = document.getElementById('framework');
        for (let i = 0; i < frameworkSelect.options.length; i++) {
            if (frameworkSelect.options[i].value === agent.framework) {
                frameworkSelect.selectedIndex = i;
                break;
            }
        }
        
        // Handle model and provider
        let provider = 'openai';
        let modelName = agent.model;
        
        // Check if model has provider prefix
        if (agent.model && agent.model.includes(':')) {
            const parts = agent.model.split(':');
            provider = parts[0];
            modelName = parts[1];
        }
        
        // Set provider and update models list
        const providerSelect = document.getElementById('provider');
        for (let i = 0; i < providerSelect.options.length; i++) {
            if (providerSelect.options[i].value === provider) {
                providerSelect.selectedIndex = i;
                break;
            }
        }
        
        // Update models for the selected provider and then set the model
        await updateModelsForProvider(provider);
        
        // Set model after models are loaded (with short delay)
        setTimeout(() => {
            const modelSelect = document.getElementById('model');
            for (let i = 0; i < modelSelect.options.length; i++) {
                if (modelSelect.options[i].value === modelName || modelSelect.options[i].value === agent.model) {
                    modelSelect.selectedIndex = i;
                    break;
                }
            }
        }, 300);
        
        // Set temperature
        if (agent.model_config && agent.model_config.temperature !== undefined) {
            const temp = agent.model_config.temperature;
            document.getElementById('temperature').value = temp;
            document.getElementById('temperature-value').textContent = temp;
        }
        
    } catch (error) {
        console.error('Error loading agent data:', error);
        alert(`Error loading agent data: ${error.message}`);
        closeModal();
    }
}

// Playground Chat Functions
let currentAgentId = null;
let chatHistory = {};

// Initialize chat history for an agent if not already created
function initAgentChatHistory(agentId) {
    if (!chatHistory[agentId]) {
        chatHistory[agentId] = [];
    }
}

function displayChatHistory(agentId) {
    const chatContainer = document.getElementById('chat-messages');
    chatContainer.innerHTML = ''; // Clear current messages
    
    if (!chatHistory[agentId] || chatHistory[agentId].length === 0) {
        // Show welcome message if no chat history
        chatContainer.innerHTML = `
            <div class="welcome-message">
                <h2>Start a conversation</h2>
                <p>Send a message to begin interacting with the selected agent.</p>
            </div>
        `;
        return;
    }
    
    // Display all messages for this agent
    chatHistory[agentId].forEach(msg => {
        const messageElement = createMessageElement(msg);
        chatContainer.appendChild(messageElement);
    });
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function createMessageElement(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${message.role === 'user' ? 'user-message' : 'agent-message'}`;
    
    if (message.role === 'user') {
        messageDiv.innerHTML = `
            <div class="message-header">
                <span class="message-sender"><i class="fas fa-user"></i> You</span>
                <span class="message-time">${formatTime(message.timestamp)}</span>
            </div>
            <div class="message-content">${formatMessage(message.content)}</div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="message-header">
                <span class="message-sender"><i class="fas fa-robot"></i> Agent</span>
                <span class="message-time">${formatTime(message.timestamp)}</span>
            </div>
            <div class="message-content">${formatMessage(message.content)}</div>
        `;
    }
    
    return messageDiv;
}

function formatMessage(content) {
    // Convert URLs to links
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    content = content.replace(urlRegex, url => `<a href="${url}" target="_blank">${url}</a>`);
    
    // Handle markdown-like formatting
    content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>'); // Bold
    content = content.replace(/\*(.*?)\*/g, '<em>$1</em>'); // Italic
    
    // Handle code blocks
    content = content.replace(/```([^`]+)```/g, '<pre><code>$1</code></pre>');
    content = content.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Convert line breaks to <br>
    content = content.replace(/\n/g, '<br>');
    
    return content;
}

function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

async function sendMessage() {
    if (!currentAgentId) {
        alert('Please select an agent first');
        return;
    }
    
    const messageInput = document.getElementById('user-message');
    const message = messageInput.value.trim();
    
    if (!message) return;
    
    // Clear input
    messageInput.value = '';
    
    // Initialize agent's chat history if needed
    initAgentChatHistory(currentAgentId);
    
    // Add user message to history
    const userMessage = {
        role: 'user',
        content: message,
        timestamp: new Date().toISOString()
    };
    chatHistory[currentAgentId].push(userMessage);
    
    // Display updated chat
    displayChatHistory(currentAgentId);
    
    // Show typing indicator
    const chatContainer = document.getElementById('chat-messages');
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.innerHTML = '<span></span><span></span><span></span>';
    chatContainer.appendChild(typingIndicator);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    try {
        console.log(`Sending query to agent ${currentAgentId}: ${message}`);
        // Send message to API
        const response = await fetch(`/api/agent/${currentAgentId}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: message })
        });
        
        if (!response.ok) {
            throw new Error(`Server responded with ${response.status}`);
        }
        
        const data = await response.json();
        
        // Remove typing indicator
        typingIndicator.remove();
        
        console.log('Agent response data:', data);
        
        // Add agent response to history
        const agentMessage = {
            role: 'assistant',
            content: data.response || data.result || 'No response from agent',
            timestamp: new Date().toISOString()
        };
        chatHistory[currentAgentId].push(agentMessage);
        
        // Update display
        displayChatHistory(currentAgentId);
        
    } catch (error) {
        console.error('Error sending message:', error);
        
        // Remove typing indicator
        typingIndicator.remove();
        
        // Add error message
        const errorMessage = {
            role: 'assistant',
            content: `Error: ${error.message}. Please try again later.`,
            timestamp: new Date().toISOString()
        };
        chatHistory[currentAgentId].push(errorMessage);
        
        // Update display
        displayChatHistory(currentAgentId);
    }
}

function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Helper function for quick prompts
function setMessage(text) {
    const messageInput = document.getElementById('user-message');
    messageInput.value = text;
    messageInput.focus();
}

// Initialize templates for agent creation
function loadTemplate(templateType) {
    let name, description, role, backstory, task;
    let provider = 'openai';
    let model = 'gpt-3.5-turbo';
    let temperature = 0.7;
    
    switch(templateType) {
        case 'research':
            name = 'Research Assistant';
            description = 'A helpful AI assistant that can research topics and provide detailed analysis';
            role = 'Senior Research Analyst';
            backstory = 'You are a highly experienced research analyst with expertise in data analysis, market research, and information synthesis. You have worked for top consulting firms and have a knack for finding patterns and insights in complex information.';
            task = 'Analyze user queries, conduct thorough research, and provide comprehensive, well-structured responses with actionable insights and recommendations.';
            provider = 'openai';
            model = 'gpt-4';
            temperature = 0.3; // Lower temperature for more factual responses
            break;
        case 'writer':
            name = 'Content Writer';
            description = 'Creative AI writer that produces engaging content on various topics';
            role = 'Professional Content Creator';
            backstory = 'You are an accomplished writer with years of experience in content creation across multiple industries. You have a talent for crafting engaging narratives and clear, compelling copy.';
            task = 'Create high-quality content based on user specifications, adapting to different tones, styles, and formats as required.';
            provider = 'groq';
            model = 'llama3-70b-8192'; // Using Groq for creative writing
            temperature = 0.8; // Higher temperature for more creative responses
            break;
        case 'analyst':
            name = 'Business Analyst';
            description = 'AI assistant for business analytics and strategic planning';
            role = 'Strategic Business Consultant';
            backstory = 'You are a seasoned business analyst with experience in multiple industries. You excel at analyzing market trends, identifying opportunities, and developing strategic recommendations.';
            task = 'Analyze business scenarios, market data, and competitive landscapes to provide actionable insights and strategic recommendations.';
            provider = 'openai';
            model = 'gpt-4-turbo';
            temperature = 0.5;
            break;
        case 'coach':
            name = 'Personal Coach';
            description = 'Supportive AI coach for personal development and goal achievement';
            role = 'Personal Development Expert';
            backstory = 'You are an experienced life coach who has helped hundreds of clients achieve their personal and professional goals. You are empathetic, encouraging, and skilled at asking the right questions.';
            task = 'Guide users in their personal development journey, help them clarify goals, identify obstacles, and develop actionable plans for progress.';
            provider = 'groq';
            model = 'mixtral-8x7b-32768'; // Good for conversational responses
            temperature = 0.7;
            break;
    }
    
    // Set basic agent information
    document.getElementById('name').value = name;
    document.getElementById('description').value = description;
    document.getElementById('role').value = role;
    document.getElementById('backstory').value = backstory;
    document.getElementById('task').value = task;
    
    // Set LLM provider and update temperature
    setProviderAndModel(provider, model, temperature);
}

// Set provider and model with proper UI updates
async function setProviderAndModel(provider, model, temperature) {
    // Set temperature
    const tempSlider = document.getElementById('temperature');
    const tempValue = document.getElementById('temperature-value');
    if (tempSlider && tempValue) {
        tempSlider.value = temperature;
        tempValue.textContent = temperature;
    }
    
    // Set provider
    const providerSelect = document.getElementById('provider');
    if (providerSelect) {
        // Find provider in dropdown
        for (let i = 0; i < providerSelect.options.length; i++) {
            if (providerSelect.options[i].value === provider) {
                providerSelect.selectedIndex = i;
                break;
            }
        }
        
        // Update models for selected provider
        await updateModelsForProvider(provider);
        
        // Set the specified model after models are loaded (with short delay)
        setTimeout(() => {
            const modelSelect = document.getElementById('model');
            if (modelSelect) {
                for (let i = 0; i < modelSelect.options.length; i++) {
                    if (modelSelect.options[i].value === model) {
                        modelSelect.selectedIndex = i;
                        break;
                    }
                }
            }
        }, 300);
    }
}

// Clear form helper
function clearForm() {
    document.getElementById('agent-form').reset();
}

// Initialize playground
function initPlayground() {
    // Set up agent selector change handler
    const selector = document.getElementById('playground-agent');
    selector.addEventListener('change', function() {
        currentAgentId = this.value;
        
        if (currentAgentId) {
            initAgentChatHistory(currentAgentId);
            displayChatHistory(currentAgentId);
            document.getElementById('send-message').disabled = false;
        } else {
            document.getElementById('send-message').disabled = true;
        }
    });
    
    // Set up send button handler
    document.getElementById('send-message').addEventListener('click', sendMessage);
    
    // Set up enter key handler
    document.getElementById('user-message').addEventListener('keypress', handleKeyPress);
    
    // Fetch agents to populate selector
    fetchAgents();
}
