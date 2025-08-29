// Framework-specific fields handling
document.addEventListener('DOMContentLoaded', function() {
    const frameworkSelect = document.getElementById('framework');
    
    if (frameworkSelect) {
        // Initialize visibility based on current selection
        updateFrameworkFields(frameworkSelect.value);
        
        // Add event listener for changes
        frameworkSelect.addEventListener('change', function(event) {
            updateFrameworkFields(event.target.value);
        });
    }
});

// Function to update form fields based on selected framework
function updateFrameworkFields(framework) {
    console.log('Updating fields for framework:', framework);
    
    // Get framework-specific field containers
    const crewaiFields = document.getElementById('crewai-fields');
    const langchainFields = document.getElementById('langchain-fields');
    const agnoFields = document.getElementById('agno-fields');
    
    // Get framework descriptions
    const crewaiDescription = document.getElementById('crewai-description');
    const langchainDescription = document.getElementById('langchain-description');
    const agnoDescription = document.getElementById('agno-description');
    
    // Hide all framework-specific fields and descriptions first
    if (crewaiFields) crewaiFields.style.display = 'none';
    if (langchainFields) langchainFields.style.display = 'none';
    if (agnoFields) agnoFields.style.display = 'none';
    if (crewaiDescription) crewaiDescription.style.display = 'none';
    if (langchainDescription) langchainDescription.style.display = 'none';
    if (agnoDescription) agnoDescription.style.display = 'none';
    
    // Show the fields and description for the selected framework
    if (framework === 'crewai') {
        if (crewaiFields) crewaiFields.style.display = 'block';
        if (crewaiDescription) crewaiDescription.style.display = 'block';
    } else if (framework === 'langchain') {
        if (langchainFields) langchainFields.style.display = 'block';
        if (langchainDescription) langchainDescription.style.display = 'block';
    } else if (framework === 'agno') {
        if (agnoFields) agnoFields.style.display = 'block';
        if (agnoDescription) agnoDescription.style.display = 'block';
    }
}

// Function to collect form data based on selected framework
function collectFrameworkSpecificFormData(framework) {
    // Common form data
    const formData = {
        name: document.getElementById('name').value,
        description: document.getElementById('description').value,
        framework: framework,
        model: formatModelWithProvider(),
        model_config: {
            temperature: parseFloat(document.getElementById('temperature').value)
        }
    };
    
    // Add framework-specific fields
    if (framework === 'crewai') {
        formData.role = document.getElementById('role').value;
        formData.backstory = document.getElementById('backstory').value;
        formData.task = document.getElementById('task').value;
    } else if (framework === 'langchain') {
        formData.agent_type = document.getElementById('agent_type').value;
        
        // Parse tools as array
        const toolsInput = document.getElementById('tools').value;
        formData.tools = toolsInput ? toolsInput.split(',').map(tool => tool.trim()) : [];
    } else if (framework === 'agno') {
        formData.model_id = document.getElementById('model_id').value;
        
        // Parse tools as array
        const toolsInput = document.getElementById('agno_tools').value;
        formData.tools = toolsInput ? toolsInput.split(',').map(tool => tool.trim()) : [];
        
        // Parse instructions as array
        const instructionsInput = document.getElementById('instructions').value;
        formData.instructions = instructionsInput 
            ? instructionsInput.split('\n').filter(line => line.trim() !== '')
            : [];
        
        // Add checkbox values
        formData.markdown = document.getElementById('markdown').checked;
        formData.stream = document.getElementById('stream').checked;
    }
    
    return formData;
}
