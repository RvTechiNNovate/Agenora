/**
 * Test script to verify provider dropdown fixes
 * 
 * This script simulates the provider selection process and logs
 * the results to help verify that we've fixed the duplicate provider issue.
 */

// Mock DOM elements
const mockProviderSelect = document.createElement('select');
mockProviderSelect.id = 'provider';

// Mock API response
const mockApiProviders = {
    providers: [
        { id: 'openai', name: 'OpenAI', model_count: 10 },
        { id: 'groq', name: 'Groq', model_count: 5 },
        { id: 'azure', name: 'Azure OpenAI', model_count: 8 }
    ]
};

// Test functions
function testProviderPopulation() {
    console.log('=== PROVIDER SELECTION TEST ===');
    
    // Clear any existing options
    mockProviderSelect.innerHTML = '';
    console.log('Initial state:', mockProviderSelect.options.length, 'options');
    
    console.log('Adding API providers...');
    // Add providers from API
    const addedProviders = new Set();
    mockApiProviders.providers.forEach(provider => {
        if (addedProviders.has(provider.id)) {
            console.warn(`Skipping duplicate provider ${provider.id}`);
            return;
        }
        
        const option = document.createElement('option');
        option.value = provider.id;
        option.textContent = provider.name;
        
        if (provider.model_count) {
            option.textContent += ` (${provider.model_count} models)`;
        }
        
        mockProviderSelect.appendChild(option);
        addedProviders.add(provider.id);
    });
    
    console.log('After API providers:', mockProviderSelect.options.length, 'options');
    
    console.log('Testing addDefaultProviders with existing options...');
    // Test addDefaultProviders when options already exist
    addDefaultProviders(mockProviderSelect);
    
    console.log('After addDefaultProviders:', mockProviderSelect.options.length, 'options');
    console.log('Provider options:');
    for (let i = 0; i < mockProviderSelect.options.length; i++) {
        console.log(`- ${mockProviderSelect.options[i].value}: ${mockProviderSelect.options[i].text}`);
    }
    
    console.log('Testing addDefaultProviders with empty select...');
    // Test with empty select
    mockProviderSelect.innerHTML = '';
    console.log('After clearing:', mockProviderSelect.options.length, 'options');
    
    // Now add defaults to empty select
    addDefaultProviders(mockProviderSelect);
    console.log('After addDefaultProviders on empty select:', mockProviderSelect.options.length, 'options');
    console.log('Provider options:');
    for (let i = 0; i < mockProviderSelect.options.length; i++) {
        console.log(`- ${mockProviderSelect.options[i].value}: ${mockProviderSelect.options[i].text}`);
    }
    
    console.log('=== TEST COMPLETE ===');
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

// Run the test
testProviderPopulation();
