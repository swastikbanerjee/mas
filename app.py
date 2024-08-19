import streamlit as st
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from crewai import Agent, Task, Crew, Process
from crewai_tools import ScrapeWebsiteTool
import warnings

warnings.filterwarnings("ignore")
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
groq_model = ChatGroq(model="llama-3.1-70b-versatile", api_key=GROQ_API_KEY)
st.set_page_config(page_title="Threat Intelligence Digest Generator", layout="wide")
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        width: 100%;
        background-color: #03C03C;
        color: white;
        height: 3em;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #00ff00;   
    }
    .stTextArea>div>div>textarea {
        background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)
st.title("🛡️ Threat Intelligence Digest Generator")
st.markdown("""
    This application generates a comprehensive threat intelligence digest based on the URLs you provide. 
    It uses multi agent framework of crewAI to extract, analyze, and format the information into a professional report.
""")
st.header("📥 Input URLs")
threat_urls = st.text_area(
    "Enter Threat Intelligence URLs (one per line)",
    height=150,
    help="Enter the URLs of threat intelligence sources you want to analyze."
)

def generate_digest(urls):
    scrape_tool = ScrapeWebsiteTool()
    extractor_agent = Agent(
        role="Content Extractor",
        goal="Extract threat intelligence data from the provided URLs",
        backstory="You're an expert at gathering threat data from various online sources.",
        tools=[scrape_tool],
        allow_delegation=False,
        llm=groq_model,
        verbose=True
    )
    editor_agent = Agent(
        role="Content Editor",
        goal="Edit and refine the extracted threat intelligence data",
        backstory="You're an expert at improving and organizing raw threat intelligence data.",
        allow_delegation=False,
        llm=groq_model,
        verbose=True
    )
    formatter_agent = Agent(
        role="Professional Formatter",
        goal="Format the edited content to resemble professional threat intelligence reports",
        backstory="You specialize in presenting threat intelligence in a clear, professional format.",
        allow_delegation=False,
        llm=groq_model,
        verbose=True
    )
    extract_task = Task(
        description="Extract threat intelligence data from the following URLs:\n{urls}",
        expected_output="Raw extracted threat intelligence data",
        agent=extractor_agent
    )
    edit_task = Task(
        description="Edit and refine the following raw threat intelligence data",
        expected_output="Edited and refined threat intelligence data",
        agent=editor_agent,
        context=[extract_task]
    )
    format_task = Task(
        description="Format the edited threat intelligence data into a professional report",
        expected_output="Professional comprehensive threat intelligence report for each url separately.",
        agent=formatter_agent,
        context=[edit_task]
    )
    crew = Crew(
        agents=[extractor_agent, editor_agent, formatter_agent],
        tasks=[extract_task, edit_task, format_task],
        process=Process.sequential,
        verbose=True
    )
    result = crew.kickoff(inputs={"urls": urls})
    return result
if st.button("🚀 Generate Threat Intelligence Digest"):
    if threat_urls:
        with st.spinner("Generating Threat Intelligence Digest..."):
            urls = threat_urls.splitlines()
            result = generate_digest(urls)

        st.success("✅ Threat Intelligence Digest Generated!")
        st.header("📊 Threat Intelligence Digest")
        st.markdown(str(result))  
        st.download_button(
            label="📥 Download Threat Intelligence Digest",
            data=str(result),  
            file_name="threat_intelligence_digest.txt",
            mime="text/plain"
        )
    else:
        st.error("Please enter at least one URL to generate the digest.")
st.markdown("---")
st.markdown("Developed with ❤️")

