document.addEventListener('DOMContentLoaded', function() {
    // Fetch predefined queries from the API
    fetchPredefinedQueries();
    
    // Add event listener for custom query button
    document.getElementById('run-custom-query').addEventListener('click', function() {
        const customQuery = document.getElementById('custom-query-input').value.trim();
        if (customQuery) {
            processQuery(customQuery);
        } else {
            showError('Please enter a query');
        }
    });
});

// Fetch predefined queries from the API
function fetchPredefinedQueries() {
    fetch('/api/predefined_queries')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            populateQueryButtons('employee-buttons', data.employee_info);
            populateQueryButtons('attendance-buttons', data.attendance_info);
            populateQueryButtons('payroll-buttons', data.payroll_info);
        })
        .catch(error => {
            console.error('Error fetching predefined queries:', error);
            showError('Failed to load predefined queries. Please try refreshing the page.');
        });
}

// Populate query buttons in the UI
function populateQueryButtons(containerId, queries) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    
    queries.forEach(query => {
        const button = document.createElement('button');
        button.className = 'btn query-btn';
        button.textContent = query.name;
        button.addEventListener('click', function() {
            processQuery(query.query);
        });
        container.appendChild(button);
    });
}

// Process a query by sending it to the API
function processQuery(query) {
    // Show the current query
    document.getElementById('current-query').textContent = query;
    document.getElementById('current-query-container').classList.remove('hidden');
    
    // Hide previous results and show loading spinner
    document.getElementById('sql-query-container').classList.add('hidden');
    document.getElementById('query-results-container').classList.remove('hidden');
    document.getElementById('loading-spinner').classList.remove('hidden');
    document.getElementById('query-results').innerHTML = '';
    document.getElementById('initial-message').classList.add('hidden');
    document.getElementById('error-message').classList.add('hidden');
    
    // Send the query to the API
    fetch('/api/process_query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Hide loading spinner
        document.getElementById('loading-spinner').classList.add('hidden');
        
        // Display the SQL query
        document.getElementById('sql-query').textContent = data.sql_query;
        document.getElementById('sql-query-container').classList.remove('hidden');
        
        // Display the results
        if (data.success) {
            displayQueryResults(data.result);
        } else {
            showError(data.error || 'An error occurred while processing the query');
        }
    })
    .catch(error => {
        document.getElementById('loading-spinner').classList.add('hidden');
        showError('Failed to process query: ' + error.message);
    });
}

// Display query results in the UI
function displayQueryResults(result) {
    const resultsContainer = document.getElementById('query-results');
    
    // Check if result is already in HTML format (like a table)
    if (typeof result === 'string' && result.trim().startsWith('<table')) {
        resultsContainer.innerHTML = result;
        return;
    }
    
    // If result is an array of objects (like rows from a database)
    if (Array.isArray(result)) {
        if (result.length === 0) {
            resultsContainer.innerHTML = '<p>No results found.</p>';
            return;
        }
        
        // Create a table to display the results
        const table = document.createElement('table');
        
        // Create table header
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        
        // Get column names from the first result object
        const columns = Object.keys(result[0]);
        columns.forEach(column => {
            const th = document.createElement('th');
            th.textContent = formatColumnName(column);
            headerRow.appendChild(th);
        });
        
        thead.appendChild(headerRow);
        table.appendChild(thead);
        
        // Create table body
        const tbody = document.createElement('tbody');
        
        // Add data rows
        result.forEach(row => {
            const tr = document.createElement('tr');
            
            columns.forEach(column => {
                const td = document.createElement('td');
                td.textContent = row[column] !== null ? row[column] : '';
                tr.appendChild(td);
            });
            
            tbody.appendChild(tr);
        });
        
        table.appendChild(tbody);
        resultsContainer.appendChild(table);
    } else if (typeof result === 'object') {
        // If result is a single object
        const table = document.createElement('table');
        
        // Create table body
        const tbody = document.createElement('tbody');
        
        // Add data rows
        Object.entries(result).forEach(([key, value]) => {
            const tr = document.createElement('tr');
            
            const keyCell = document.createElement('th');
            keyCell.textContent = formatColumnName(key);
            tr.appendChild(keyCell);
            
            const valueCell = document.createElement('td');
            valueCell.textContent = value !== null ? value : '';
            tr.appendChild(valueCell);
            
            tbody.appendChild(tr);
        });
        
        table.appendChild(tbody);
        resultsContainer.appendChild(table);
    } else {
        // If result is a simple string or other type
        resultsContainer.innerHTML = `<p>${result}</p>`;
    }
}

// Format column names for better display (e.g., "first_name" -> "First Name")
function formatColumnName(name) {
    return name
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

// Show error message
function showError(message) {
    const errorElement = document.getElementById('error-message');
    errorElement.textContent = message;
    errorElement.classList.remove('hidden');
}
