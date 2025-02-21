# UI Generator Agent

This project generates UI components based on text descriptions using OpenAI's GPT model.

## Installation and Setup

### 1. Clone the Repository
```bash
git clone https://github.com/omghumre/ui-generator-agent.git
cd ui-generator-agent
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate    # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
streamlit run app.py
```

## Project Structure
```
ui-generator-agent/
│── main.py             # Main application entry point
│── requirements.txt    # Dependencies required for the project
│── README.md           # Documentation and setup instructions
│── .gitignore          # Files and directories to be ignored by Git
│── venv/               # Virtual environment (excluded from Git)
│── test.py             # Testing generated code
```

## Features
- Generate UI components from text descriptions
- Supports multiple UI frameworks
- User-friendly interface

## Contributing
Feel free to fork this repository and submit pull requests for improvements!

## License
This project is licensed under the MIT License.


---
Developed by [Om Ghumre](https://github.com/omghumre) 

