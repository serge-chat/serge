export async function apiFetch(endpoint: string, options: RequestInit = {}) {
    const token = localStorage.getItem('token');
  
    if (token) {
      options.headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json' // Ensure content type is JSON for POST/PUT requests
      };
    }
  
    const response = await fetch(endpoint, options);
    
    if (!response.ok) {
      if (response.status === 401) {
        // Handle unauthorized access, possibly redirect to login
        localStorage.removeItem('token');
        location.href = '/login'; // Redirect to login page
      }
      throw new Error(`Error: ${response.statusText}`);
    }
  
    return response.json();
  }
  