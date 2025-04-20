import streamlit as st
import requests
import json
import time
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid
import os
import base64
from typing import Dict, List, Tuple, Optional, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set page configuration
st.set_page_config(
    page_title="API Tester Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        font-weight: 700;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        font-weight: 500;
    }
    .response-container {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .metrics-container {
        background-color: #e3f2fd;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .json-viewer {
        font-family: 'Courier New', Courier, monospace;
        white-space: pre-wrap;
        overflow-x: auto;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'request_history' not in st.session_state:
    st.session_state.request_history = []

if 'collections' not in st.session_state:
    st.session_state.collections = {}

if 'environment_variables' not in st.session_state:
    st.session_state.environment_variables = {}

if 'test_results' not in st.session_state:
    st.session_state.test_results = []

if 'active_collection' not in st.session_state:
    st.session_state.active_collection = None

class APITester:
    """Core API testing functionality"""
    
    @staticmethod
    def send_request(method: str, url: str, headers: Dict, params: Dict, 
                    body: str, auth: Optional[Tuple] = None, timeout: int = 30) -> Dict:
        """Send an HTTP request and return the response details."""
        start_time = time.time()
        
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            # Process the body based on content type
            parsed_body = None
            if body:
                content_type = next((h for h in headers.keys() if h.lower() == 'content-type'), None)
                if content_type and 'application/json' in headers[content_type].lower():
                    try:
                        parsed_body = json.loads(body)
                    except json.JSONDecodeError:
                        parsed_body = body
                else:
                    parsed_body = body
            
            # Prepare request parameters
            kwargs = {
                'headers': headers,
                'params': params,
                'timeout': timeout
            }
            
            # Add authentication if provided
            if auth and all(auth):
                kwargs['auth'] = auth
                
            # Add request body if provided
            if parsed_body is not None:
                if isinstance(parsed_body, dict):
                    kwargs['json'] = parsed_body
                else:
                    kwargs['data'] = parsed_body
            
            # Send the request
            response = requests.request(method, url, **kwargs)
            elapsed_time = time.time() - start_time
            
            # Process response
            try:
                response_json = response.json()
                is_json = True
            except:
                response_json = None
                is_json = False
            
            # Create response object
            response_data = {
                'status_code': response.status_code,
                'elapsed_time': round(elapsed_time * 1000, 2),  # Convert to ms
                'headers': dict(response.headers),
                'size': len(response.content),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'is_json': is_json,
                'content': response_json if is_json else response.text
            }
            
            return response_data
            
        except requests.exceptions.RequestException as e:
            elapsed_time = time.time() - start_time
            return {
                'status_code': None,
                'elapsed_time': round(elapsed_time * 1000, 2),
                'headers': {},
                'size': 0,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'is_json': False,
                'content': str(e),
                'error': True
            }
    
    @staticmethod
    def run_test(response_data: Dict, assertions: List[Dict]) -> List[Dict]:
        """Run tests against a response using provided assertions."""
        test_results = []
        
        for assertion in assertions:
            test_type = assertion.get('type')
            expected = assertion.get('expected')
            actual = None
            passed = False
            
            if test_type == 'status_code':
                actual = response_data.get('status_code')
                passed = str(actual) == str(expected)
            
            elif test_type == 'response_time':
                actual = response_data.get('elapsed_time')
                passed = actual <= float(expected)
            
            elif test_type == 'header_exists':
                actual = expected in response_data.get('headers', {})
                passed = actual
            
            elif test_type == 'header_value':
                header_name, expected_value = expected.split(':', 1)
                header_name = header_name.strip()
                expected_value = expected_value.strip()
                actual = response_data.get('headers', {}).get(header_name)
                passed = actual == expected_value
            
            elif test_type == 'json_path':
                path, expected_value = expected.split('==', 1)
                path = path.strip()
                expected_value = expected_value.strip()
                
                if response_data.get('is_json') and isinstance(response_data.get('content'), dict):
                    try:
                        # Simple dot notation path resolution
                        parts = path.split('.')
                        value = response_data.get('content')
                        for part in parts:
                            if part.endswith(']'):
                                array_part, idx_part = part.split('[')
                                idx = int(idx_part[:-1])
                                value = value.get(array_part, [])[idx]
                            else:
                                value = value.get(part)
                        
                        actual = str(value)
                        passed = str(value) == expected_value
                    except (KeyError, IndexError, AttributeError):
                        actual = "Path not found"
                        passed = False
                else:
                    actual = "Not JSON response"
                    passed = False
            
            test_results.append({
                'type': test_type,
                'expected': expected,
                'actual': actual,
                'passed': passed
            })
        
        return test_results
    
    @staticmethod
    def resolve_variables(text: str, variables: Dict) -> str:
        """Replace variable placeholders in text with their values."""
        if not text:
            return text
            
        for name, value in variables.items():
            placeholder = f"{{{{${name}}}}}"
            text = text.replace(placeholder, str(value))
        
        return text

class UI:
    """UI components for the application"""
    
    @staticmethod
    def render_sidebar():
        """Render the sidebar with collections and environments."""
        st.sidebar.markdown("<div class='main-header'>API Tester Pro</div>", unsafe_allow_html=True)
        
        # Environment variables section
        st.sidebar.markdown("<div class='sub-header'>🌍 Environment Variables</div>", unsafe_allow_html=True)
        
        # Display current variables
        if st.session_state.environment_variables:
            st.sidebar.dataframe(
                pd.DataFrame(
                    [(k, v) for k, v in st.session_state.environment_variables.items()],
                    columns=["Variable", "Value"]
                ),
                hide_index=True,
                use_container_width=True
            )
        
        # Add new variable form
        with st.sidebar.expander("Add/Edit Variable"):
            var_name = st.text_input("Variable Name", key="new_var_name")
            var_value = st.text_input("Variable Value", key="new_var_value")
            
            if st.button("Save Variable"):
                if var_name:
                    st.session_state.environment_variables[var_name] = var_value
                    st.rerun()
        
        # Collections section
        st.sidebar.markdown("<div class='sub-header'>📁 Collections</div>", unsafe_allow_html=True)
        
        # Create new collection
        with st.sidebar.expander("Create New Collection"):
            collection_name = st.text_input("Collection Name", key="new_collection_name")
            if st.button("Create Collection"):
                if collection_name and collection_name not in st.session_state.collections:
                    st.session_state.collections[collection_name] = []
                    st.session_state.active_collection = collection_name
                    st.rerun()
        
        # Display collections
        if st.session_state.collections:
            collection_names = list(st.session_state.collections.keys())
            selected_collection = st.sidebar.selectbox(
                "Select Collection", 
                collection_names,
                index=collection_names.index(st.session_state.active_collection) if st.session_state.active_collection in collection_names else 0
            )
            
            if selected_collection != st.session_state.active_collection:
                st.session_state.active_collection = selected_collection
                st.rerun()
            
            # Display requests in the selected collection
            if st.session_state.active_collection:
                saved_requests = st.session_state.collections[st.session_state.active_collection]
                if saved_requests:
                    request_names = [req.get('name', 'Unnamed Request') for req in saved_requests]
                    selected_request_index = st.sidebar.selectbox("Saved Requests", range(len(request_names)), format_func=lambda i: request_names[i])
                    
                    if st.sidebar.button("Load Request"):
                        selected_request = saved_requests[selected_request_index]
                        # Set form values for the selected request
                        st.session_state.request_name = selected_request.get('name', '')
                        st.session_state.request_url = selected_request.get('url', '')
                        st.session_state.request_method = selected_request.get('method', 'GET')
                        st.session_state.request_headers = json.dumps(selected_request.get('headers', {}), indent=2)
                        st.session_state.request_params = json.dumps(selected_request.get('params', {}), indent=2)
                        st.session_state.request_body = selected_request.get('body', '')
                        st.session_state.request_auth_username = selected_request.get('auth', ['', ''])[0]
                        st.session_state.request_auth_password = selected_request.get('auth', ['', ''])[1]
                        st.rerun()
                        
                    if st.sidebar.button("Delete Request"):
                        saved_requests.pop(selected_request_index)
                        st.rerun()
        
        # Import/Export section
        st.sidebar.markdown("<div class='sub-header'>🔄 Import/Export</div>", unsafe_allow_html=True)
        
        # Export functionality
        if st.session_state.collections:
            export_data = {
                'collections': st.session_state.collections,
                'environment_variables': st.session_state.environment_variables
            }
            
            export_json = json.dumps(export_data, indent=2)
            b64 = base64.b64encode(export_json.encode()).decode()
            href = f'<a href="data:application/json;base64,{b64}" download="api_tester_export.json">Download Export File</a>'
            st.sidebar.markdown(href, unsafe_allow_html=True)
        
        # Import functionality
        uploaded_file = st.sidebar.file_uploader("Import Configuration", type=["json"])
        if uploaded_file is not None:
            try:
                import_data = json.loads(uploaded_file.getvalue().decode())
                if 'collections' in import_data:
                    st.session_state.collections.update(import_data['collections'])
                if 'environment_variables' in import_data:
                    st.session_state.environment_variables.update(import_data['environment_variables'])
                st.sidebar.success("Import successful!")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Import failed: {str(e)}")
    
    @staticmethod
    def render_request_form():
        """Render the main request form."""
        st.markdown("<div class='main-header'>API Request</div>", unsafe_allow_html=True)
        
        # Initialize form session state variables if they don't exist
        if 'request_name' not in st.session_state:
            st.session_state.request_name = ""
        if 'request_url' not in st.session_state:
            st.session_state.request_url = ""
        if 'request_method' not in st.session_state:
            st.session_state.request_method = "GET"
        if 'request_headers' not in st.session_state:
            st.session_state.request_headers = "{}"
        if 'request_params' not in st.session_state:
            st.session_state.request_params = "{}"
        if 'request_body' not in st.session_state:
            st.session_state.request_body = ""
        if 'request_auth_username' not in st.session_state:
            st.session_state.request_auth_username = ""
        if 'request_auth_password' not in st.session_state:
            st.session_state.request_auth_password = ""
        
        # Request form
        col1, col2 = st.columns([3, 1])
        with col1:
            request_name = st.text_input("Request Name", value=st.session_state.request_name, key="input_request_name")
        with col2:
            request_method = st.selectbox("Method", 
                                         ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
                                         index=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"].index(st.session_state.request_method),
                                         key="input_request_method")
        
        request_url = st.text_input("URL", value=st.session_state.request_url, key="input_request_url")
        
        # Tabs for different request components
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Headers", "Params", "Body", "Auth", "Tests"])
        
        with tab1:
            st.text_area(
                "Headers (JSON format)", 
                value=st.session_state.request_headers,
                height=200,
                key="input_request_headers",
                help="Enter headers in JSON format. Example: {\"Content-Type\": \"application/json\"}"
            )
        
        with tab2:
            st.text_area(
                "Query Parameters (JSON format)", 
                value=st.session_state.request_params,
                height=200,
                key="input_request_params",
                help="Enter query parameters in JSON format. Example: {\"page\": \"1\", \"limit\": \"10\"}"
            )
        
        with tab3:
            st.text_area(
                "Request Body", 
                value=st.session_state.request_body,
                height=300,
                key="input_request_body"
            )
        
        with tab4:
            auth_col1, auth_col2 = st.columns(2)
            with auth_col1:
                auth_username = st.text_input(
                    "Username", 
                    value=st.session_state.request_auth_username,
                    key="input_request_auth_username"
                )
            with auth_col2:
                auth_password = st.text_input(
                    "Password", 
                    value=st.session_state.request_auth_password,
                    type="password",
                    key="input_request_auth_password"
                )
        
        with tab5:
            # Test assertions definition
            if 'test_assertions' not in st.session_state:
                st.session_state.test_assertions = []
            
            # Display current assertions
            if st.session_state.test_assertions:
                for i, assertion in enumerate(st.session_state.test_assertions):
                    cols = st.columns([3, 1])
                    with cols[0]:
                        st.text(f"{assertion['type']}: {assertion['expected']}")
                    with cols[1]:
                        if st.button("Remove", key=f"remove_test_{i}"):
                            st.session_state.test_assertions.pop(i)
                            st.rerun()
            
            # Add new assertion
            with st.expander("Add Test Assertion"):
                test_type = st.selectbox(
                    "Test Type",
                    ["status_code", "response_time", "header_exists", "header_value", "json_path"],
                    key="new_test_type"
                )
                
                if test_type == "status_code":
                    expected = st.text_input("Expected Status Code (e.g., 200)", key="expected_status")
                elif test_type == "response_time":
                    expected = st.number_input("Max Response Time (ms)", min_value=1, value=1000, key="expected_time")
                elif test_type == "header_exists":
                    expected = st.text_input("Header Name", key="expected_header")
                elif test_type == "header_value":
                    expected = st.text_input("Header:Value (e.g., Content-Type: application/json)", key="expected_header_val")
                elif test_type == "json_path":
                    expected = st.text_input("Path == Value (e.g., data.id == 123)", key="expected_json_path")
                
                if st.button("Add Test"):
                    if expected:
                        st.session_state.test_assertions.append({
                            'type': test_type,
                            'expected': expected
                        })
                        st.rerun()
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            send_button = st.button("Send Request", type="primary", use_container_width=True)
        with col2:
            save_button = st.button("Save Request", use_container_width=True)
        with col3:
            clear_button = st.button("Clear Form", use_container_width=True)
        
        return {
            'name': request_name,
            'method': request_method,
            'url': request_url,
            'headers': UI.parse_json_input(st.session_state.input_request_headers),
            'params': UI.parse_json_input(st.session_state.input_request_params),
            'body': st.session_state.input_request_body,
            'auth': (
                st.session_state.input_request_auth_username,
                st.session_state.input_request_auth_password
            ) if st.session_state.input_request_auth_username or st.session_state.input_request_auth_password else None,
            'send_button': send_button,
            'save_button': save_button,
            'clear_button': clear_button,
            'test_assertions': st.session_state.test_assertions
        }
    
    @staticmethod
    def parse_json_input(json_str: str) -> Dict:
        """Parse JSON string input, handling errors."""
        try:
            if not json_str.strip():
                return {}
            return json.loads(json_str)
        except json.JSONDecodeError:
            st.error(f"Invalid JSON: {json_str}")
            return {}
    
    @staticmethod
    def render_response(response_data: Dict, test_results: List[Dict] = None):
        """Render the API response and test results."""
        if not response_data:
            return
        
        st.markdown("<div class='main-header'>Response</div>", unsafe_allow_html=True)
        
        # Response metrics
        col1, col2, col3, col4 = st.columns(4)
        
        status_color = "green" if response_data.get('status_code', 0) and 200 <= response_data['status_code'] < 300 else "red"
        
        with col1:
            st.metric("Status", response_data.get('status_code', 'Error'))
        with col2:
            st.metric("Time", f"{response_data.get('elapsed_time', 0)} ms")
        with col3:
            st.metric("Size", f"{response_data.get('size', 0) / 1024:.2f} KB")
        with col4:
            st.metric("Timestamp", response_data.get('timestamp', 'N/A'))
        
        # Response content tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Body", "Headers", "Tests", "Visualize"])
        
        with tab1:
            if response_data.get('error', False):
                st.error(response_data.get('content', 'Unknown error'))
            elif response_data.get('is_json', False):
                st.json(response_data.get('content', {}))
            else:
                st.text(response_data.get('content', ''))
        
        with tab2:
            if response_data.get('headers'):
                headers_df = pd.DataFrame(
                    [(k, v) for k, v in response_data['headers'].items()],
                    columns=["Header", "Value"]
                )
                st.dataframe(headers_df, hide_index=True, use_container_width=True)
        
        with tab3:
            if test_results:
                # Show test summary
                passed = sum(1 for test in test_results if test['passed'])
                failed = len(test_results) - passed
                
                st.metric("Tests", f"{passed}/{len(test_results)} Passed")
                
                # Show individual test results
                for i, test in enumerate(test_results):
                    result_color = "green" if test['passed'] else "red"
                    expander_label = f"{'✅' if test['passed'] else '❌'} {test['type']}"
                    with st.expander(expander_label):
                        st.write(f"**Type:** {test['type']}")
                        st.write(f"**Expected:** {test['expected']}")
                        st.write(f"**Actual:** {test['actual']}")
                        st.write(f"**Result:** {'Passed' if test['passed'] else 'Failed'}")
        
        with tab4:
            if response_data.get('is_json', False):
                content = response_data.get('content', {})
                
                # Try to detect if the content has a plottable structure
                if isinstance(content, list) and len(content) > 0 and isinstance(content[0], dict):
                    st.subheader("Data Visualization")
                    
                    # Convert to DataFrame
                    try:
                        df = pd.json_normalize(content)
                        
                        # Show dataframe
                        st.dataframe(df.head(), use_container_width=True)
                        
                        # Basic visualizations if numerical columns exist
                        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                        if numeric_cols:
                            st.subheader("Quick Visualizations")
                            
                            chart_type = st.selectbox(
                                "Chart Type",
                                ["Bar Chart", "Line Chart", "Scatter Plot", "Histogram"],
                                key="viz_chart_type"
                            )
                            
                            if chart_type == "Bar Chart" and len(numeric_cols) > 0:
                                x_col = st.selectbox("X-Axis", df.columns.tolist(), key="viz_x_col")
                                y_col = st.selectbox("Y-Axis", numeric_cols, key="viz_y_col")
                                
                                fig = px.bar(df.head(20), x=x_col, y=y_col, title=f"{y_col} by {x_col}")
                                st.plotly_chart(fig, use_container_width=True)
                                
                            elif chart_type == "Line Chart" and len(numeric_cols) > 0:
                                x_col = st.selectbox("X-Axis", df.columns.tolist(), key="viz_x_col")
                                y_col = st.selectbox("Y-Axis", numeric_cols, key="viz_y_col")
                                
                                fig = px.line(df.head(50), x=x_col, y=y_col, title=f"{y_col} over {x_col}")
                                st.plotly_chart(fig, use_container_width=True)
                                
                            elif chart_type == "Scatter Plot" and len(numeric_cols) > 1:
                                x_col = st.selectbox("X-Axis", numeric_cols, key="viz_x_col")
                                y_col = st.selectbox("Y-Axis", [c for c in numeric_cols if c != x_col] or numeric_cols, key="viz_y_col")
                                
                                fig = px.scatter(df, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")
                                st.plotly_chart(fig, use_container_width=True)
                                
                            elif chart_type == "Histogram" and len(numeric_cols) > 0:
                                col = st.selectbox("Column", numeric_cols, key="viz_hist_col")
                                
                                fig = px.histogram(df, x=col, title=f"Distribution of {col}")
                                st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.error(f"Could not visualize data: {str(e)}")
    
    @staticmethod
    def render_history():
        """Render the request history section."""
        if not st.session_state.request_history:
            return
        
        st.markdown("<div class='main-header'>Request History</div>", unsafe_allow_html=True)
        
        # Create dataframe for history
        history_data = []
        for i, item in enumerate(st.session_state.request_history):
            req = item['request']
            res = item['response']
            
            status_code = res.get('status_code', 'Error')
            status_class = ''
            if isinstance(status_code, int):
                if 200 <= status_code < 300:
                    status_class = 'success'
                elif 400 <= status_code < 600:
                    status_class = 'error'
            
            history_data.append({
                'ID': i,
                'Method': req['method'],
                'URL': req['url'],
                'Status': status_code,
                'Time (ms)': res.get('elapsed_time', 0),
                'Timestamp': res.get('timestamp', '')
            })
        
        # Display history table
        history_df = pd.DataFrame(history_data)
        selected_indices = st.multiselect(
            "Select requests to compare or view",
            options=history_df.index.tolist(),
            format_func=lambda i: f"{history_df.iloc[i]['Method']} {history_df.iloc[i]['URL']} ({history_df.iloc[i]['Status']})"
        )
        
        if selected_indices:
            if len(selected_indices) == 1:
                # Display single request details
                idx = selected_indices[0]
                request_data = st.session_state.request_history[idx]['request']
                response_data = st.session_state.request_history[idx]['response']
                
                st.subheader("Request Details")
                st.json(request_data)
                
                st.subheader("Response Details")
                UI.render_response(response_data)
            
            else:
                # Compare multiple requests
                st.subheader("Response Comparison")
                
                comparison_data = []
                for idx in selected_indices:
                    req = st.session_state.request_history[idx]['request']
                    res = st.session_state.request_history[idx]['response']
                    
                    comparison_data.append({
                        'Request': f"{req['method']} {req['url']}",
                        'Status': res.get('status_code', 'Error'),
                        'Time (ms)': res.get('elapsed_time', 0),
                        'Size (KB)': res.get('size', 0) / 1024
                    })
                
                comparison_df = pd.DataFrame(comparison_data)
                st.dataframe(comparison_df, hide_index=True, use_container_width=True)
                
                # Visualize comparison
                fig = px.bar(
                    comparison_df, 
                    x='Request', 
                    y='Time (ms)',
                    title='Response Time Comparison'
                )
                st.plotly_chart(fig, use_container_width=True)

def main():
    """Main application entry point."""
    
    # Render sidebar
    UI.render_sidebar()
    
    # Render main request form
    request_data = UI.render_request_form()
    
    # Process form actions
    if request_data['send_button']:
        # Apply environment variables to request data
        url = APITester.resolve_variables(request_data['url'], st.session_state.environment_variables)
        headers = {k: APITester.resolve_variables(v, st.session_state.environment_variables) 
                  for k, v in request_data['headers'].items()}
        params = {k: APITester.resolve_variables(v, st.session_state.environment_variables) 
                 for k, v in request_data['params'].items()}
        body = APITester.resolve_variables(request_data['body'], st.session_state.environment_variables)
        
        # Send the request
        response_data = APITester.send_request(
            method=request_data['method'],
            url=url,
            headers=headers,
            params=params,
            body=body,
            auth=request_data['auth']
        )
        
        # Run tests if any assertions are defined
        test_results = []
        if request_data['test_assertions']:
            test_results = APITester.run_test(response_data, request_data['test_assertions'])
            st.session_state.test_results = test_results
        
        # Save request and response to history
        st.session_state.request_history.insert(0, {
            'request': request_data,
            'response': response_data,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # Render response
        UI.render_response(response_data, test_results)
    
    elif request_data['save_button']:
        # Save request to collection
        if st.session_state.active_collection:
            # Check if request has a name
            if not request_data['name']:
                st.error("Please provide a name for the request before saving")
            else:
                # Add request to active collection
                st.session_state.collections[st.session_state.active_collection].append({
                    'name': request_data['name'],
                    'method': request_data['method'],
                    'url': request_data['url'],
                    'headers': request_data['headers'],
                    'params': request_data['params'],
                    'body': request_data['body'],
                    'auth': [request_data['auth'][0], request_data['auth'][1]] if request_data['auth'] else ['', ''],
                    'test_assertions': request_data['test_assertions']
                })
                st.success(f"Request '{request_data['name']}' saved to collection '{st.session_state.active_collection}'")
        else:
            st.error("Please create or select a collection before saving requests")
    
    elif request_data['clear_button']:
        # Clear form
        st.session_state.request_name = ""
        st.session_state.request_url = ""
        st.session_state.request_method = "GET"
        st.session_state.request_headers = "{}"
        st.session_state.request_params = "{}"
        st.session_state.request_body = ""
        st.session_state.request_auth_username = ""
        st.session_state.request_auth_password = ""
        st.session_state.test_assertions = []
        st.rerun()
    
    # Render request history
    UI.render_history()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        logging.error(f"Application error: {str(e)}", exc_info=True)