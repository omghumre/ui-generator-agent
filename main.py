import streamlit as st
import requests
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import json
from pathlib import Path
import re

class GitHubRepoExtractor:
    def __init__(self):
        self.base_url = "https://api.github.com"
        
    def get_repo_contents(self, owner, repo, path=""):
        """Fetch repository contents from GitHub API"""
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        headers = {'Accept': 'application/vnd.github.v3+json'}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"GitHub API Error: {response.json().get('message', 'Unknown error')}")
        return response.json()
    
    def get_file_content(self, download_url):
        """Fetch file content from GitHub"""
        response = requests.get(download_url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch file content: {response.status_code}")
        return response.text
    
    def extract_frontend_files(self, repo_url):
        """Extract frontend-related files from the repository"""
        try:
            # Parse owner and repo from URL
            parts = repo_url.split('github.com/')[-1].split('/')
            owner, repo_name = parts[0], parts[1]
            
            frontend_files = []
            to_process = [("", [])]  # (path, files) tuples
            processed_paths = set()
            
            # Frontend file extensions to look for
            frontend_extensions = ('.html', '.css', '.js', '.jsx', '.tsx', '.vue', '.py')
            
            while to_process:
                current_path, current_files = to_process.pop(0)
                if current_path in processed_paths:
                    continue
                    
                processed_paths.add(current_path)
                
                try:
                    contents = self.get_repo_contents(owner, repo_name, current_path)
                    
                    # Handle both single file and directory responses
                    if not isinstance(contents, list):
                        contents = [contents]
                    
                    for item in contents:
                        if item['type'] == 'dir':
                            to_process.append((item['path'], []))
                        elif item['type'] == 'file':
                            if Path(item['name']).suffix in frontend_extensions:
                                try:
                                    file_content = self.get_file_content(item['download_url'])
                                    frontend_files.append({
                                        'path': item['path'],
                                        'content': file_content,
                                        'type': Path(item['name']).suffix
                                    })
                                    
                                    # Progress update
                                    st.sidebar.write(f"Found: {item['path']}")
                                except Exception as e:
                                    st.warning(f"Couldn't fetch content for {item['path']}: {str(e)}")
                
                except Exception as e:
                    st.warning(f"Error processing {current_path}: {str(e)}")
                    continue
            
            if not frontend_files:
                st.warning("No frontend files found in the repository")
                return None
            
            return frontend_files
            
        except Exception as e:
            st.error(f"Error extracting repository: {str(e)}")
            return None
    
    def get_repo_info(self, repo_url):
        """Get basic repository information"""
        try:
            parts = repo_url.split('github.com/')[-1].split('/')
            owner, repo_name = parts[0], parts[1]
            
            url = f"{self.base_url}/repos/{owner}/{repo_name}"
            headers = {'Accept': 'application/vnd.github.v3+json'}
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                repo_data = response.json()
                return {
                    'name': repo_data['name'],
                    'description': repo_data.get('description', ''),
                    'language': repo_data.get('language', ''),
                    'stars': repo_data.get('stargazers_count', 0),
                    'forks': repo_data.get('forks_count', 0)
                }
            else:
                st.error(f"Failed to fetch repository information: {response.json().get('message', '')}")
                return None
                
        except Exception as e:
            st.error(f"Error getting repository information: {str(e)}")
            return None

class UIGenerator:
    def __init__(self, openai_api_key):
        self.llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
        self.chat_model = ChatOpenAI(
            temperature=0.7,
            openai_api_key=openai_api_key,
            model_name="gpt-3.5-turbo"
        )
        
    def generate_ui(self, frontend_files):
        prompt_template = """You are an AI agent specialized in creating user interfaces.
        
        Repository files:
        {frontend_files}
        
        Create a modern, responsive Streamlit UI for this repository that includes:
        1. A clean and professional layout
        2. Necessary input components and forms
        3. Data visualization sections if needed
        4. Interactive elements and navigation
        5. Error handling and user feedback
        
        The UI should match the repository's functionality and purpose.
        Generate complete, runnable Streamlit code.
        
        Important: Include all necessary imports and make sure the code is self-contained.
        Use modern Streamlit features like st.tabs(), st.columns(), etc.
        """
        
        prompt = PromptTemplate(
            input_variables=["frontend_files"],
            template=prompt_template
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        initial_code = chain.run(frontend_files=json.dumps(frontend_files, indent=2))
        
        return self.extract_code(initial_code)
    
    def improve_code(self, code, feedback):
        """Improve code based on human feedback"""
        prompt = f"""
        Original Code:
        ```python
        {code}
        ```
        
        Human Feedback:
        {feedback}
        
        Please improve the code based on the feedback provided.
        Ensure the code is complete and ready to run.
        """
        
        response = self.chat_model.predict(prompt)
        return self.extract_code(response)
    
    def extract_code(self, content):
        code_match = re.search(r'```python\n(.*?)\n```', content, re.DOTALL)
        return code_match.group(1) if code_match else content

def main():
    st.set_page_config(
        page_title="GitHub UI Generator",
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .stButton>button {
            width: 100%;
        }
        .feedback-section {
            margin-top: 1rem;
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #f0f2f6;
        }
        .code-improvement {
            margin-top: 1rem;
            padding: 1rem;
            border: 1px solid #e0e0e0;
            border-radius: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'generated_code' not in st.session_state:
        st.session_state.generated_code = None
    if 'feedback_history' not in st.session_state:
        st.session_state.feedback_history = []
    if 'current_version' not in st.session_state:
        st.session_state.current_version = 0
    
    # Main content
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("GitHub UI Generator")
        st.write("Transform your GitHub repository into a Streamlit UI")
    
    # Sidebar
    with st.sidebar:
        st.header("Configuration")
        # openai_api_key = st.text_input("OpenAI API Key", type="password")
        openai_api_key = st.text_input("OpenAI API Key", type="password")
        if st.session_state.feedback_history:
            st.markdown("### Feedback History")
            for i, feedback in enumerate(st.session_state.feedback_history):
                with st.expander(f"Version {i + 1}"):
                    st.write(feedback)
    
    # Main form
    with st.form("repo_form"):
        repo_url = st.text_input(
            "GitHub Repository URL",
            placeholder="https://github.com/username/repository"
        )
        generate_button = st.form_submit_button("Generate UI")
        
        if generate_button and repo_url and openai_api_key:
            with st.spinner("Analyzing repository and generating UI..."):
                try:
                    extractor = GitHubRepoExtractor()
                    frontend_files = extractor.extract_frontend_files(repo_url)
                    
                    if frontend_files:
                        generator = UIGenerator(openai_api_key)
                        generated_code = generator.generate_ui(frontend_files)
                        st.session_state.generated_code = generated_code
                        st.session_state.current_version += 1
                        st.success("Initial UI generated! Please review and provide feedback.")
                    else:
                        st.error("No suitable files found in the repository.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # Code review and improvement section
    if st.session_state.generated_code:
        st.markdown("---")
        st.header(f"Generated UI Code (Version {st.session_state.current_version})")
        
        tabs = st.tabs(["Code", "Review & Improve", "Preview"])
        
        with tabs[0]:
            st.code(st.session_state.generated_code, language="python")
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="Download Code",
                    data=st.session_state.generated_code,
                    file_name=f"generated_ui_v{st.session_state.current_version}.py",
                    mime="text/plain"
                )
            with col2:
                if st.button("Start Over"):
                    st.session_state.generated_code = None
                    st.session_state.feedback_history = []
                    st.session_state.current_version = 0
                    st.rerun()
        
        with tabs[1]:
            st.markdown("### Code Review")
            
            feedback_options = st.multiselect(
                "What aspects need improvement?",
                [
                    "Layout and Design",
                    "Functionality",
                    "Error Handling",
                    "Performance",
                    "Code Organization",
                    "Documentation",
                    "Other"
                ]
            )
            
            detailed_feedback = st.text_area(
                "Provide detailed feedback and suggestions",
                height=150,
                placeholder="Describe what needs to be improved..."
            )
            
            if st.button("Submit Feedback and Improve"):
                if detailed_feedback:
                    with st.spinner("Improving code based on feedback..."):
                        # Store feedback
                        feedback_entry = {
                            "version": st.session_state.current_version,
                            "categories": feedback_options,
                            "details": detailed_feedback
                        }
                        st.session_state.feedback_history.append(feedback_entry)
                        
                        # Generate improved code
                        generator = UIGenerator(openai_api_key)
                        improved_code = generator.improve_code(
                            st.session_state.generated_code,
                            detailed_feedback
                        )
                        
                        # Update session state
                        st.session_state.generated_code = improved_code
                        st.session_state.current_version += 1
                        
                        st.success("Code improved! Please review the new version.")
                        st.rerun()
                else:
                    st.warning("Please provide detailed feedback for improvement.")
        
        with tabs[2]:
            st.warning("Preview functionality is limited for security reasons")
            if st.button("Try Preview"):
                try:
                    with st.spinner("Loading preview..."):
                        exec(st.session_state.generated_code)
                except Exception as e:
                    st.error(f"Preview Error: {str(e)}")

if __name__ == "__main__":
    main()