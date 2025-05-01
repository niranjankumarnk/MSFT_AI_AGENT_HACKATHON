from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage, AnyMessage
from langgraph.graph import  StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key and Langsmith tracing variables from environment variables 
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
# os.environ["LANGSMITH_TRACING_V2"] = os.getenv("LANGSMITH_TRACING_V2")
# os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")

# Define the LLM (Language Model) to be used
llm = ChatOpenAI(temperature=0, model="gpt-4o")

# Define the state of the messages using TypedDict
class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    

def blog_graph():
    # Define the nodes of the graph
    def title_generator(state:MessagesState)->str:
        """Generates a blog title based on the given topic.

        Args:
            topic (str): The topic for which to generate a blog title.

        Returns:
            str: A generated blog title.
        """
        messages = state.get("messages", [])  # Ensure messages exist
        if not messages:
            return {"messages": [AIMessage(content="Error: No topic provided.")]}
        topic = messages[-1].content
        prompt = f"Generate a blog title for the topic: {topic}"
        response = llm.invoke([HumanMessage(content=prompt)])
        return {"messages": messages + [AIMessage(content=response.content)]} 
        
        
    

    def content_generator(state:MessagesState)->str:
        """Generates blog content based on the generated title.

        Args:
            topic (str): The topic for which to generate blog content.

        Returns:
            str: Generated blog content.
        """
        messages = state.get("messages", [])
        if not messages or len(messages) < 2:
            return {"messages": [AIMessage(content="Error: No valid title provided.")]}

        title = messages[-1].content  # Extract the generated title
        prompt = f"Write an engaging blog post based on the title: '{title}'"
        response = llm.invoke([HumanMessage(content=prompt)])  # Invoke LLM 
        content=response.content
        print(f"Generated Content: {content[:100]}...") 
        return {"messages": messages + [AIMessage(content=content)]}  
        
    # Define the graph structure
    
    graph = StateGraph(MessagesState)
    graph.add_node("Title creator", title_generator)
    graph.add_node("Content creator", content_generator)
    graph.add_edge(START, "Title creator")
    graph.add_edge("Title creator", "Content creator")
    graph.add_edge("Content creator", END)
    
    overall_graph = graph.compile()
    return overall_graph

agent = blog_graph()


    