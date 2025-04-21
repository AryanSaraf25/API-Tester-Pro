# API-Tester-Pro
A web-based API testing tool built with Streamlit and Python. Features include HTTP methods, custom headers, environment variables, test assertions, response visualization, collections, history, and import/export. Uses Requests, Pandas, and Plotly for a powerful yet simple experience.
# API Tester Pro

![API Tester Pro Banner](https://via.placeholder.com/800x200?text=API+Tester+Pro)

A comprehensive, user-friendly Streamlit application for testing, debugging, and documenting API endpoints. API Tester Pro helps developers streamline their API workflows by providing a powerful interface for sending requests, validating responses, and organizing collections.

## 🌟 Features

- **Modern UI**: Clean, intuitive interface built with Streamlit
- **Request Management**: Save, organize, and reuse API requests in collections
- **Environment Variables**: Use variables for different environments and dynamic values
- **Comprehensive Testing**: Define assertions for validating API responses
- **Response Visualization**: Analyze API responses with data visualization tools
- **Import/Export**: Share configurations with team members
- **Request History**: Track and compare previous API calls
- **Authentication Support**: Basic auth and custom headers for secured endpoints

## 📋 Table of Contents

- [Installation](#installation)
- [Getting Started](#getting-started)
- [Core Functions](#core-functions)
  - [Sending API Requests](#sending-api-requests)
  - [Working with Collections](#working-with-collections)
  - [Environment Variables](#environment-variables)
  - [Testing API Responses](#testing-api-responses)
  - [Visualizing Responses](#visualizing-responses)
  - [Request History](#request-history)
  - [Import/Export](#importexport)
- [Advanced Usage](#advanced-usage)
- [Contributing](#contributing)
- [License](#license)

## 🚀 Installation

### Prerequisites

- Python 3.7+
- pip

### Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/api-tester-pro.git
cd api-tester-pro
```

2. Create and activate a virtual environment (optional but recommended):

```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

The requirements.txt file should include:

```
streamlit
requests
pandas
plotly
```

## 🏁 Getting Started

1. Launch the application:

```bash
streamlit run app.py
```

2. The application will open in your default web browser, typically at `http://localhost:8501`.

3. You're ready to start testing APIs!

## 💻 Core Functions

### Sending API Requests

1. **Create a Request**:
   - Enter a name for your request (optional but recommended for saving)
   - Select an HTTP method (GET, POST, PUT, DELETE, etc.)
   - Enter the URL for your API endpoint
   - Fill in headers, query parameters, and request body as needed

2. **Configure Headers**:
   - Navigate to the Headers tab
   - Enter headers in JSON format, example:
   ```json
   {
     "Content-Type": "application/json",
     "Authorization": "Bearer token123"
   }
   ```

3. **Configure Query Parameters**:
   - Navigate to the Params tab
   - Enter parameters in JSON format, example:
   ```json
   {
     "page": "1",
     "limit": "10",
     "sort": "desc"
   }
   ```

4. **Add Request Body**:
   - Navigate to the Body tab
   - Enter your request body (JSON, text, etc.)
   - For JSON bodies, ensure proper formatting

5. **Add Authentication**:
   - Navigate to the Auth tab
   - Enter username and password for Basic Authentication
   - For other auth types, use appropriate headers

6. **Send Request**:
   - Click the "Send Request" button
   - View the response in the Response section

### Working with Collections

Collections help you organize related API requests.

1. **Create a Collection**:
   - In the sidebar, click "Create New Collection"
   - Enter a name for your collection
   - Click "Create Collection"

2. **Save Requests to Collections**:
   - Fill out your request details
   - Enter a name for the request
   - Click "Save Request"
   - The request will be added to the currently active collection

3. **Load a Saved Request**:
   - In the sidebar, select a collection
   - Choose a request from the dropdown
   - Click "Load Request"
   - The request details will populate the form

4. **Delete a Request**:
   - Select the request from the dropdown
   - Click "Delete Request"

### Environment Variables

Environment variables allow you to use dynamic values across requests.

1. **Add Environment Variables**:
   - In the sidebar, expand "Add/Edit Variable"
   - Enter a variable name and value
   - Click "Save Variable"

2. **Use Environment Variables**:
   - In any request field (URL, headers, params, body), use the syntax `{{$variableName}}`
   - Example URL: `https://api.example.com/{{$apiVersion}}/users`
   - Variables will be replaced with their values when sending the request

### Testing API Responses

Create assertions to validate API responses automatically.

1. **Add Test Assertions**:
   - Navigate to the Tests tab
   - Click "Add Test Assertion"
   - Choose a test type:
     - **Status Code**: Verify response status code (e.g., 200)
     - **Response Time**: Check if response time is below threshold (in ms)
     - **Header Exists**: Verify a specific header exists
     - **Header Value**: Check if a header has a specific value
     - **JSON Path**: Validate a value in the JSON response

2. **JSON Path Syntax**:
   - Use dot notation to access nested properties
   - Example: `data.user.id == 123`
   - For array access: `data.items[0].name == "Product"`

3. **View Test Results**:
   - After sending a request, go to the Tests tab in the Response section
   - View passed/failed tests and detailed results

### Visualizing Responses

Analyze JSON response data visually.

1. **View Response Data**:
   - After receiving a JSON response, go to the Visualize tab
   - The system will attempt to convert the JSON to a DataFrame

2. **Create Visualizations**:
   - Select a chart type (Bar Chart, Line Chart, Scatter Plot, Histogram)
   - Choose columns for X and Y axes
   - View the generated chart

3. **Customize Visualizations**:
   - Different chart types work best for different data structures
   - Experiment with different columns and chart types

### Request History

Keep track of previous requests and compare their responses.

1. **View History**:
   - All sent requests are automatically saved to the history
   - Scroll down to the Request History section

2. **Examine Past Requests**:
   - Select a single request to view its details
   - The complete request and response information will be displayed

3. **Compare Requests**:
   - Select multiple requests using the multi-select dropdown
   - View a comparison table and chart of response times
   - Useful for performance testing and debugging

### Import/Export

Share your API configurations with team members.

1. **Export Configuration**:
   - In the sidebar, find the Import/Export section
   - Click "Download Export File"
   - This will download a JSON file containing all your collections and environment variables

2. **Import Configuration**:
   - Click "Browse files" in the Import section
   - Select a previously exported JSON file
   - Your collections and environment variables will be imported

## 🔍 Advanced Usage

### Working with Large JSON Responses

For large JSON responses:
1. Use the visualize tab to get a quick overview
2. Filter and sort data using the dataframe view
3. Create targeted visualizations to extract insights

### Testing API Performance

To benchmark API performance:
1. Send the same request multiple times
2. Use the history comparison to analyze response times
3. Create test assertions for maximum response time

### Handling Authentication

For OAuth and other authentication methods:
1. Get your token through the appropriate means
2. Add it as an environment variable
3. Use the variable in your Authorization header

## 📝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Made with ❤️ by [Aryan]

---

## 📸 Screenshots

![Main Interface]
![Response Visualization](https://via.placeholder.com/800x450?text=Response+Visualization)
![Collections and Environment](https://via.placeholder.com/800x450?text=Collections+and+Environment)
!["Main Page]{}