import streamlit as st
from blog_generation import blog_graph  # your agent import
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage, AnyMessage

def display_blog_creator():
    st.header("✍️ Blog Title & Content Generator")

    topic = st.text_input("Enter a blog topic:")
    if st.button("Generate Blog"):
        if topic:
            graph = blog_graph()
            result = graph.invoke({"messages": [HumanMessage(content=topic)]})
            messages = result.get("messages", [])
            title = messages[1].content if len(messages) > 1 else "No title generated."
            content = messages[2].content if len(messages) > 2 else "No content generated."

            st.subheader("📝 Generated Blog Title")
            st.write(title)

            st.subheader("📄 Blog Content")
            st.markdown(content)
        else:
            st.warning("Please enter a topic to generate the blog.")
