# Research AI Assistant 🔍

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.22.0-FF4B4B?style=for-the-badge&logo=streamlit)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3.20-blue?style=for-the-badge)](https://www.langchain.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991?style=for-the-badge&logo=openai)](https://openai.com/)

A powerful AI research assistant built with LangChain and OpenAI that helps you research any topic by searching the web, Wikipedia, and other sources. This project was created following the tutorial by [Tech With Tim](https://www.youtube.com/watch?v=bTMPwUgLZf0).

![Research AI Assistant Screenshot](https://via.placeholder.com/800x400?text=Research+AI+Assistant)

## ✨ Features

- 🌐 **Web Search Integration:** Uses DuckDuckGo to find relevant information on the web
- 📚 **Wikipedia Research:** Searches Wikipedia for authoritative information
- 💾 **Save Research:** Export your research results to a text file
- 🤔 **Transparent Process:** See how the AI thinks and conducts research
- 🎨 **Modern UI:** Beautiful Streamlit interface with intuitive design
- 🔄 **Agent Framework:** Powered by LangChain's agent system for flexible research

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- An OpenAI API key

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/langchain-research-ai-agent.git
   cd langchain-research-ai-agent
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with your API keys:
   ```
   OPENAI_API_KEY="your-openai-api-key"
   ```

### Running the Application

Start the Streamlit app:
```bash
streamlit run app.py
```

The app will open in your browser at http://localhost:8501.

## 🧠 How It Works

The Research AI Assistant uses a combination of techniques to provide comprehensive research on any topic:

1. **User Input:** Enter a research topic in the web interface
2. **Agent Initialization:** LangChain creates a research agent using GPT-4o
3. **Tool Usage:** The agent decides which tools to use for research (web search, Wikipedia, etc.)
4. **Data Collection:** Information is gathered from multiple sources
5. **Summarization:** The agent compiles a concise, informative summary
6. **Citation:** Sources are properly cited for reference

## 🛠️ Project Structure

```
langchain-research-ai-agent/
├── app.py              # Streamlit web application
├── main.py             # Command-line version of the research agent
├── tools.py            # Research tools definition (search, Wikipedia, save)
├── requirements.txt    # Project dependencies
├── .env                # Environment variables (API keys)
└── README.md           # Project documentation
```

## 📋 Dependencies

- **langchain & langchain-openai:** Framework for creating agent-based applications with LLMs
- **streamlit:** Web application framework for creating the UI
- **wikipedia:** Python library for accessing Wikipedia
- **duckduckgo-search:** Python library for searching the web
- **pydantic:** Data validation and settings management
- **python-dotenv:** Loading environment variables from .env files

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/yourusername/langchain-research-ai-agent/issues).

## 📝 License

This project is [MIT](https://choosealicense.com/licenses/mit/) licensed.

## 🙏 Acknowledgements

- This project was created following [Tech With Tim's](https://www.youtube.com/watch?v=bTMPwUgLZf0) excellent tutorial
- [LangChain](https://www.langchain.com/) for the agent framework
- [OpenAI](https://openai.com/) for the GPT-4o model
- [Streamlit](https://streamlit.io/) for the web application framework

## 🔗 Links

- [Tech With Tim Tutorial](https://www.youtube.com/watch?v=bTMPwUgLZf0)
- [LangChain Documentation](https://python.langchain.com/docs/get_started)
- [OpenAI Documentation](https://platform.openai.com/docs/introduction)
- [Streamlit Documentation](https://docs.streamlit.io/) 