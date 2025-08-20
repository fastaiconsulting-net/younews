// Test script to verify API endpoints
const API_BASE_URL = 'https://8a17q933pb.execute-api.eu-west-2.amazonaws.com';

async function testApiEndpoint(endpoint, method = 'GET', body = null) {
    const url = `${API_BASE_URL}${endpoint}`;
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
    };
    
    if (body) {
        options.body = JSON.stringify(body);
    }
    
    console.log(`Testing ${method} ${url}`);
    
    try {
        const response = await fetch(url, options);
        console.log(`Status: ${response.status}`);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            console.error('Error Response:', errorData);
            return { success: false, error: errorData };
        }
        
        const data = await response.json();
        console.log('Success Response:', data);
        return { success: true, data: data };
    } catch (error) {
        console.error('Network Error:', error);
        return { success: false, error: error.message };
    }
}

async function runTests() {
    console.log('=== Testing YouNews API Endpoints ===\n');
    
    // Test 1: Health check
    console.log('1. Testing health check...');
    await testApiEndpoint('/healthz', 'GET');
    console.log('');
    
    // Test 2: Subscribe (this will send a confirmation email)
    console.log('2. Testing subscribe endpoint...');
    await testApiEndpoint('/subscriptions/subscribe', 'POST', {
        email: 'test@example.com'
    });
    console.log('');
    
    // Test 3: Get all subscriptions
    console.log('3. Testing get all subscriptions...');
    await testApiEndpoint('/subscriptions', 'GET');
    console.log('');
    
    console.log('=== Tests completed ===');
}

// Run tests if this script is executed directly
if (typeof window === 'undefined') {
    // Node.js environment
    const fetch = require('node-fetch');
    runTests();
} else {
    // Browser environment
    runTests();
}
