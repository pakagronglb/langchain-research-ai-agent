import streamlit as st
import time
import re
import json
import io
from contextlib import redirect_stdout
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool, wiki_tool, save_tool

# MUST BE THE FIRST STREAMLIT COMMAND - nothing before this!
st.set_page_config(
    page_title="Research AI Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Now we can run other Streamlit commands
load_dotenv()

# Define the response model
class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

# Apply CSS for responsive design and proper spacing/justification
st.markdown("""
<style>
    /* Base styles with proper text justification */
    p, li {
        text-align: justify;
        line-height: 1.6;
    }
    
    /* Container widths for better responsiveness */
    .container {
        width: 100%;
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 15px;
    }
    
    /* Responsive grid system */
    .row {
        display: flex;
        flex-wrap: wrap;
        margin: 0 -15px;
    }
    
    .col {
        flex: 1;
        padding: 0 15px;
        min-width: 300px; /* Minimum width before wrapping */
    }
    
    /* Responsive header */
    .header-container {
        display: flex;
        align-items: center;
        padding: 1.5rem;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, rgba(67,97,238,0.1) 0%, rgba(42,54,189,0.2) 100%);
        border-radius: 10px;
        border: 1px solid rgba(67,97,238,0.2);
        flex-wrap: wrap;
    }
    
    .header-icon {
        font-size: min(3rem, 10vw);
        margin-right: 20px;
        color: #4361ee;
    }
    
    .header-title {
        color: white;
        margin: 0;
        font-size: min(2.2rem, 7vw);
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    
    /* Description box with proper text justification */
    .desc-box {
        padding: 1.2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        background: rgba(30, 33, 43, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        text-align: justify;
    }
    
    /* Research card with justification */
    .research-card {
        background: rgba(30, 33, 43, 0.7);
        border-radius: 12px;
        padding: clamp(1rem, 3vw, 1.5rem);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(67, 97, 238, 0.3);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: fit-content;
    }
    
    .research-card h2 {
        color: #4361ee;
        margin-bottom: 1rem;
        font-weight: 600;
        border-bottom: 1px solid rgba(67, 97, 238, 0.3);
        padding-bottom: 0.5rem;
        text-align: left;
    }
    
    .research-card p {
        text-align: justify;
        color: #e2e8f0;
        line-height: 1.7;
        font-size: clamp(0.9rem, 2vw, 1rem);
    }
    
    /* Source links with proper spacing */
    .sources-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-top: 1rem;
    }
    
    .source-link {
        background-color: rgba(67, 97, 238, 0.15);
        border-radius: 8px;
        padding: 10px 15px;
        display: block;
        transition: all 0.2s ease;
        border: 1px solid rgba(67, 97, 238, 0.2);
        word-break: break-all;
    }
    
    .source-link:hover {
        background-color: rgba(67, 97, 238, 0.25);
        transform: translateX(5px);
    }
    
    .source-link a {
        color: #a5b4fc !important;
        text-decoration: none !important;
        display: block;
        width: 100%;
    }
    
    /* Tool tags container for proper justification */
    .tool-tags-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        justify-content: flex-start;
        margin-top: 0.5rem;
    }
    
    /* Tool tags */
    .tool-tag {
        background: linear-gradient(135deg, rgba(67, 97, 238, 0.2) 0%, rgba(58, 12, 163, 0.2) 100%);
        border-radius: 20px;
        padding: 6px 12px;
        display: inline-block;
        font-size: 0.85em;
        color: #a5b4fc;
        border: 1px solid rgba(67, 97, 238, 0.3);
        transition: all 0.2s ease;
    }
    
    .tool-tag:hover {
        background: linear-gradient(135deg, rgba(67, 97, 238, 0.3) 0%, rgba(58, 12, 163, 0.3) 100%);
        transform: scale(1.05);
    }
    
    /* Thinking process styling with proper spacing */
    .thinking-process {
        background: rgba(30, 33, 43, 0.5);
        border-radius: 10px;
        padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .thinking-step {
        border-left: 3px solid #4361ee;
        padding-left: 15px;
        margin: 15px 0;
        padding-bottom: 5px;
    }
    
    .tool-call {
        background: rgba(67, 97, 238, 0.15);
        border-radius: 8px;
        padding: 12px;
        margin: 12px 0;
        transition: all 0.2s ease;
    }
    
    .tool-result {
        background: rgba(46, 139, 87, 0.15);
        border-radius: 8px;
        padding: 12px;
        margin: 12px 0 12px 20px;
        border-left: 2px solid #2e8b57;
        transition: all 0.2s ease;
    }
    
    /* Input field styling */
    .input-container {
        max-width: 800px;
        margin: 0 auto 2rem auto;
    }
    
    .stTextInput input {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(67, 97, 238, 0.3) !important;
        border-radius: 8px !important;
        color: white !important;
        padding: 15px !important;
        font-size: clamp(0.9rem, 2vw, 1.1rem) !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
    }
    
    /* Button styling */
    .button-container {
        max-width: 400px;
        margin: 0 auto 2rem auto;
    }
    
    .stButton button {
        background: linear-gradient(90deg, #4361ee 0%, #3a0ca3 100%) !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        padding: clamp(10px, 3vw, 15px) clamp(15px, 5vw, 30px) !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 10px rgba(67, 97, 238, 0.3) !important;
        width: 100% !important;
    }
    
    /* Section headings with proper alignment */
    .section-header {
        color: #4361ee;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 1px solid rgba(67, 97, 238, 0.3);
        padding-bottom: 0.5rem;
        text-align: left;
    }
    
    /* Footer with proper centering */
    .footer {
        text-align: center;
        padding: 1.5rem;
        margin-top: 2rem;
        background: rgba(30, 33, 43, 0.7);
        border-radius: 10px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Media queries for better responsiveness */
    @media (max-width: 768px) {
        .row {
            flex-direction: column;
        }
        
        .col {
            width: 100%;
            min-width: 100%;
            padding: 0;
        }
        
        .research-card, .thinking-process {
            margin-bottom: 1rem;
        }
        
        .header-container {
            flex-direction: column;
            text-align: center;
            padding: 1rem;
        }
        
        .header-icon {
            margin-right: 0;
            margin-bottom: 10px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Main container for proper spacing and centering
st.markdown('<div class="container">', unsafe_allow_html=True)

# Header with icon
st.markdown("""
<div class="header-container">
    <div class="header-icon">🔍</div>
    <h1 class="header-title">Research AI Assistant</h1>
</div>
""", unsafe_allow_html=True)

# Enhanced description with justified text
st.markdown("""
<div class="desc-box">
    <p style="margin: 0; font-size: 1.1em; color: #e2e8f0;">
        Enter any topic and the AI will create comprehensive research using web search and Wikipedia. 
        Get detailed summaries with cited sources and a transparent research process.
    </p>
</div>
""", unsafe_allow_html=True)

# Initialize the LLM and tools
@st.cache_resource
def initialize_agent():
    llm = ChatOpenAI(model="gpt-4o")
    
    parser = PydanticOutputParser(pydantic_object=ResearchResponse)
    
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                You are a research assistant that will help generate a research paper.
                Answer the user query and use neccessary tools. 
                Wrap the output in this format and provide no other text\n{format_instructions}
                """,
            ),
            ("placeholder", "{chat_history}"),
            ("human", "{query}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    ).partial(format_instructions=parser.get_format_instructions())
    
    tools = [search_tool, wiki_tool, save_tool]
    
    agent = create_tool_calling_agent(
        llm=llm,
        prompt=prompt,
        tools=tools
    )
    
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    return agent_executor, parser

# Input container for centered and responsive input
st.markdown('<div class="input-container">', unsafe_allow_html=True)
st.markdown('<p class="section-header">What would you like to research?</p>', unsafe_allow_html=True)
query = st.text_input("Research topic", placeholder="Enter your research topic here...", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# Button container for proper centering
st.markdown('<div class="button-container">', unsafe_allow_html=True)
search_button = st.button("🔍 Start Research", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Results section
if query and (search_button or 'structured_response' in st.session_state):
    try:
        if search_button or 'structured_response' not in st.session_state:
            # Initialize progress indicators
            progress_container = st.container()
            with progress_container:
                progress_bar = st.progress(0)
                status = st.empty()
            
            # Show a spinner while processing
            with st.spinner("Researching..."):
                status.info("Initializing research agent...")
                progress_bar.progress(10)
                
                # Initialize agent
                agent_executor, parser = initialize_agent()
                
                status.info("Beginning research on: " + query)
                progress_bar.progress(30)
                
                # Capture the agent's verbose output for display
                agent_output = io.StringIO()
                
                # Redirect stdout to capture the verbose output
                with redirect_stdout(agent_output):
                    raw_response = agent_executor.invoke({"query": query})
                
                # Process the output to get thinking steps
                output_text = agent_output.getvalue()
                
                # Create a function to capture and format the thinking process
                def process_agent_output(output_text):
                    # Extract tool calls and results
                    thinking_steps = []
                    
                    # Look for tool invocations
                    tool_invocations = re.findall(r'Invoking: `([^`]+)` with `([^`]+)`', output_text)
                    tool_results = re.split(r'Invoking: `[^`]+` with `[^`]+`', output_text)
                    
                    if len(tool_results) > 0 and tool_results[0].strip():
                        thinking_steps.append(("thinking", tool_results[0].strip()))
                    
                    # Match invocations with their results
                    for i, (tool, query) in enumerate(tool_invocations):
                        thinking_steps.append(("tool_call", (tool, query)))
                        if i+1 < len(tool_results):
                            result = tool_results[i+1].strip()
                            if result:
                                thinking_steps.append(("tool_result", result))
                    
                    return thinking_steps
                
                thinking_steps = process_agent_output(output_text)
                
                progress_bar.progress(70)
                status.info("Processing results...")
                
                # Parse the response
                response_text = raw_response.get("output")
                
                # The response contains JSON inside a code block
                if isinstance(response_text, str) and "```json" in response_text:
                    # Extract JSON from markdown code block
                    json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                        # Parse JSON directly into ResearchResponse
                        json_data = json.loads(json_str)
                        structured_response = ResearchResponse(**json_data)
                    else:
                        structured_response = parser.parse(response_text)
                else:
                    # Try using the regular parser
                    structured_response = parser.parse(response_text)
                
                # Store in session state for persistence
                st.session_state.structured_response = structured_response
                st.session_state.thinking_steps = thinking_steps
                
                progress_bar.progress(100)
                status.success("Research complete!")
                time.sleep(0.5)
                progress_container.empty()
        else:
            # Retrieve from session state if already processed
            structured_response = st.session_state.structured_response
            thinking_steps = st.session_state.thinking_steps

        # Responsive row layout
        st.markdown('<div class="row">', unsafe_allow_html=True)
        
        # First column - Research summary
        st.markdown('<div class="col">', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="research-card">
            <h2>{structured_response.topic}</h2>
            <p>{structured_response.summary}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sources
        st.markdown('<p class="section-header">Sources</p>', unsafe_allow_html=True)
        st.markdown('<div class="sources-container">', unsafe_allow_html=True)
        for source in structured_response.sources:
            st.markdown(f"""
            <div class="source-link">
                <a href="{source}" target="_blank">📚 {source}</a>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Save button
        if st.button("💾 Save Research Results", use_container_width=True):
            filename = f"research_{structured_response.topic.replace(' ', '_').lower()}_{time.strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"RESEARCH ON: {structured_response.topic}\n\n")
                f.write(f"SUMMARY:\n{structured_response.summary}\n\n")
                f.write("SOURCES:\n")
                for source in structured_response.sources:
                    f.write(f"- {source}\n")
                f.write("\nRESEARCH METHODS:\n")
                for tool in structured_response.tools_used:
                    f.write(f"- {tool}\n")
            
            st.success(f"Research saved to {filename}")
            
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Second column - Tools and thinking process
        st.markdown('<div class="col">', unsafe_allow_html=True)
        
        # Research methods/tools
        st.markdown('<p class="section-header">Research Methods</p>', unsafe_allow_html=True)
        st.markdown('<div class="tool-tags-container">', unsafe_allow_html=True)
        for tool in structured_response.tools_used:
            tool_name = tool.replace("functions.", "")
            icon = "🔍" if "search" in tool_name else "📖" if "wiki" in tool_name else "💾" if "save" in tool_name else "🔧"
            st.markdown(f"""
            <span class="tool-tag">{icon} {tool_name}</span>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Thinking process
        with st.expander("🧠 View Research Process", expanded=False):
            st.markdown('<div class="thinking-process">', unsafe_allow_html=True)
            st.markdown('<p class="section-header">How I Researched This Topic</p>', unsafe_allow_html=True)
            
            for step_type, content in thinking_steps:
                if step_type == "thinking":
                    st.markdown(f"""
                    <div class="thinking-step">
                        <p style="color: #e2e8f0;">🤔 <strong>Thinking:</strong> Analyzing the request and planning my research approach...</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                elif step_type == "tool_call":
                    tool, query = content
                    icon = "🔍" if "search" in tool else "📖" if "wiki" in tool else "💾" if "save" in tool else "🔧"
                    st.markdown(f"""
                    <div class="tool-call">
                        <p style="color: #e2e8f0;">{icon} <strong>Using {tool}:</strong> Researching "{query}"</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                elif step_type == "tool_result":
                    # Truncate very long results
                    if len(content) > 300:
                        display_content = content[:300] + "... (truncated)"
                    else:
                        display_content = content
                        
                    st.markdown(f"""
                    <div class="tool-result">
                        <p style="color: #e2e8f0;">📊 <strong>Found information:</strong> {display_content}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="thinking-step">
                <p style="color: #e2e8f0;">✅ <strong>Finalizing:</strong> Compiling all information into a comprehensive summary...</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Close the row
        st.markdown('</div>', unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        if 'raw_response' in locals():
            st.write("Raw response:", raw_response)

# Footer
st.markdown("""
<div class="footer">
    <p style="color: #a5b4fc;">Research AI Assistant powered by LangChain and OpenAI</p>
    <p style="color: #a5b4fc; font-size: 0.8em; margin-top: 5px;">Get comprehensive research on any topic with just a few clicks.</p>
</div>
""", unsafe_allow_html=True)

# Close the main container
st.markdown('</div>', unsafe_allow_html=True) 