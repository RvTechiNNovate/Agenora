// Framework-specific fields handling
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM content loaded for framework-fields.js');
    const frameworkSelect = document.getElementById('framework');
    
    if (frameworkSelect) {
        console.log('Framework select found:', frameworkSelect.value);
        // Initialize visibility based on current selection
        updateFrameworkFields(frameworkSelect.value);
        
        // Add event listener for changes
        frameworkSelect.addEventListener('change', function(event) {
            console.log('Framework changed to:', event.target.value);
            updateFrameworkFields(event.target.value);
        });
    } else {
        console.error('Framework select element not found!');
    }
    
    // Debug: check if LangGraph fields exist in DOM
    const langgraphFields = document.getElementById('langgraph-fields');
    console.log('LangGraph fields container exists:', !!langgraphFields);
});

// Function to update form fields based on selected framework
function updateFrameworkFields(framework) {
    console.log('Updating fields for framework:', framework);
    
    // Get framework-specific field containers
    const crewaiFields = document.getElementById('crewai-fields');
    const langchainFields = document.getElementById('langchain-fields');
    const agnoFields = document.getElementById('agno-fields');
    const langgraphFields = document.getElementById('langgraph-fields');
    
    // Get framework descriptions
    const crewaiDescription = document.getElementById('crewai-description');
    const langchainDescription = document.getElementById('langchain-description');
    const agnoDescription = document.getElementById('agno-description');
    const langgraphDescription = document.getElementById('langgraph-description');
    
    // Hide all framework-specific fields and descriptions first
    if (crewaiFields) crewaiFields.style.display = 'none';
    if (langchainFields) langchainFields.style.display = 'none';
    if (agnoFields) agnoFields.style.display = 'none';
    if (langgraphFields) langgraphFields.style.display = 'none';
    if (crewaiDescription) crewaiDescription.style.display = 'none';
    if (langchainDescription) langchainDescription.style.display = 'none';
    if (agnoDescription) agnoDescription.style.display = 'none';
    if (langgraphDescription) langgraphDescription.style.display = 'none';
    
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
    } else if (framework === 'langgraph') {
        if (langgraphFields) {
            langgraphFields.style.display = 'block';
            console.log('LangGraph fields displayed');
            
            // Debug LangGraph fields
            const promptField = document.getElementById('langgraph_prompt');
            const toolsField = document.getElementById('langgraph_tools');
            
            console.log('LangGraph prompt field exists:', !!promptField);
            console.log('LangGraph tools field exists:', !!toolsField);
        } else {
            console.error('LangGraph fields container not found');
        }
        
        if (langgraphDescription) langgraphDescription.style.display = 'block';
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
    
    // Pre-initialize fields that might be required by backend validations
    if (framework === 'langgraph') {
        formData.prompt = '';  // Will be updated later
        formData.tools = [];   // Will be updated later
    }
    
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
    } else if (framework === 'langgraph') {
        // Parse tools as array
        const toolsInput = document.getElementById('langgraph_tools')?.value || '';
        formData.tools = toolsInput ? toolsInput.split(',').map(tool => tool.trim()) : [];
        
        // Add prompt template with fallback to ensure it's never empty
        const promptElement = document.getElementById('langgraph_prompt');
        let promptValue = 'Default ReAct agent prompt';
        
        if (promptElement) {
            promptValue = promptElement.value || promptValue;
            console.log('LangGraph prompt element found, value:', promptValue);
        } else {
            console.error('LangGraph prompt element not found!');
        }
        
        // Always ensure prompt is included
        formData.prompt = promptValue;
        
        // Log the complete form data for LangGraph
        console.log('LangGraph form data:', formData);
    }
    
    return formData;
}
