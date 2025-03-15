from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool, wiki_tool, save_tool
import sys
import re
import json

load_dotenv()

class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]
    
try:
    print("Initializing LLM...")
    llm = ChatOpenAI(model="gpt-4o")
    print("LLM initialized successfully:", llm)
    
    print("Setting up parser...")
    parser = PydanticOutputParser(pydantic_object=ResearchResponse)
    
    print("Setting up prompt template...")
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
    
    print("Setting up tools...")
    tools = [search_tool, wiki_tool, save_tool]
    
    print("Creating agent...")
    agent = create_tool_calling_agent(
        llm=llm,
        prompt=prompt,
        tools=tools
    )
    
    print("Setting up agent executor...")
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    print("Ready to receive query...")
    query = input("What can i help you research? ")
    
    print("Executing query:", query)
    raw_response = agent_executor.invoke({"query": query})
    
    try:
        print("Parsing response...")
        response_text = raw_response.get("output")
        print("Response type:", type(response_text))
        
        # The response contains JSON inside a code block
        if isinstance(response_text, str) and "```json" in response_text:
            # Extract JSON from markdown code block
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                print("Extracted JSON from code block")
                # Parse JSON directly into ResearchResponse
                json_data = json.loads(json_str)
                structured_response = ResearchResponse(**json_data)
            else:
                structured_response = parser.parse(response_text)
        else:
            # Try using the regular parser
            structured_response = parser.parse(response_text)
        
        print(structured_response)
    except Exception as e:
        print("Error parsing response", e, "Raw Response - ", raw_response)
except Exception as e:
    print(f"Error occurred: {e}", file=sys.stderr)