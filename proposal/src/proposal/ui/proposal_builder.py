from dotenv import load_dotenv
from proposal.core.logging_setup import setup_logging
load_dotenv()
setup_logging()

import streamlit as st
from proposal.core.graph_state import UserRequirement, ClientInfo
from proposal.graph.graph import run_graph

st.set_page_config(
    page_title="AI Consulting Proposal Builder (Beta)",
    layout="wide",
    page_icon="📑"
)

st.markdown("""
<style>
.block-container {
    padding-top: 1.5rem;
}

.section-card {
    background: white;
    padding: 1rem;
    border-radius: 10px;
    border-left: 5px solid #4F46E5;
    margin-bottom: 1rem;
}

.node-running {
    color: #2563EB;
    font-weight: 600;
}

.node-done {
    color: #16A34A;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

def word_limit(text, max_words):
    return len(text.split()) <= max_words

st.title("🤖 AI Consulting Proposal Builder")

left_col, right_col = st.columns(2)

with left_col:

    st.subheader("🧾 Client & Requirement Details")

    
    
    if st.button("📥 Load Sample Data"):
        st.session_state["problem_statement"] = "The client's legacy system cannot handle real-time transaction analysis efficiently."
        st.session_state["proposal_goal"] = "Deploy an AI-powered platform to automate proposal generation with high accuracy."
        st.session_state["client_name"] = "Infosys"
        st.session_state["industry"] = "Technology & SaaS"
        st.session_state["approach"] = "Use agentic AI with RAG architecture for document retrieval and section-wise proposal generation."
        st.session_state["timeline"] = "6 weeks"
        st.session_state["scope_exclusions"] = "Excludes client-side integration and post-deployment training."
        st.session_state["budget_range"] = "$50k - $100k"
        st.session_state["technical_depth"] = "Deep Technical"
        st.session_state["sections"] = ["Executive Summary", "Scope of Work"]

    with st.form("proposal_form"):

        st.markdown("### 🧠 Problem Definition")
        problem_statement = st.text_area(
            "Problem Statement * (max 50 words)",
            placeholder="Describe the business or technical problem",
            height=120,
            value=st.session_state.get("problem_statement", "")
        )

        proposal_goal = st.text_area(
            "Proposal Goal * (max 50 words)",
            placeholder="Objective of this proposal",
            height=120,
            value=st.session_state.get("proposal_goal", "")
        )

        st.markdown("### 🏢 Client Details")
        client_name = st.text_input(
            "Client Company Name * (max 10 words)",
            placeholder="e.g. ABC Corp",
            value=st.session_state.get("client_name", "")
        )

        industry_options = [
            "Banking & Financial Services",
            "Insurance",
            "Investment & Asset Management",
            "Healthcare & Life Sciences",
            "Retail & E-Commerce",
            "Manufacturing & Industrial",
            "Supply Chain & Logistics",
            "Technology & SaaS"
        ]

        industry = st.selectbox(
            "Industry *",
            industry_options,
            index=industry_options.index(st.session_state.get("industry", "Banking & Financial Services"))
        )

        st.markdown("### 🛠 Optional Inputs")
        approach = st.text_area(
            "Approach (max 50 words)",
            placeholder="High-level approach or methodology",
            height=120,
            value=st.session_state.get("approach", "")
        )

        timeline = st.text_input(
            "Timeline (max 5 words)",
            placeholder="e.g. 12 weeks",
            value=st.session_state.get("timeline", "")
        )

        scope_exclusions = st.text_area(
            "Scope & Exclusions (max 20 words)",
            placeholder="What is out of scope?",
            height=120,
            value=st.session_state.get("scope_exclusions", "")
        )

        budget_range = st.text_input(
            "Budget Range (max 5 words)",
            placeholder="e.g. $50k - $100k",
            value=st.session_state.get("budget_range", "")
        )

        technical_depth = st.selectbox(
            "Technical Depth",
            ["High-level", "Medium", "Deep Technical"],
            index=["High-level", "Medium", "Deep Technical"].index(st.session_state.get("technical_depth", "High-level"))
        )

        st.markdown("### 📦 Sections to Generate")
        sections = []
        default_sections = st.session_state.get("sections", [])

        if st.checkbox("Executive Summary", value="Executive Summary" in default_sections):
            sections.append("Executive Summary")
        if st.checkbox("Scope of Work", value="Scope of Work" in default_sections):
            sections.append("Scope of Work")
        if st.checkbox("Approach", value="Approach" in default_sections):
            sections.append("Approach")
        if st.checkbox("Methodology", value="Methodology" in default_sections):
            sections.append("Methodology")
        if st.checkbox("Pricing", value="Pricing" in default_sections):
            sections.append("Pricing")
        if st.checkbox("Timeline", value="Timeline" in default_sections):
            sections.append("Timeline")
        if st.checkbox("Deliverables", value="Deliverables" in default_sections):
            sections.append("Deliverables")
        if st.checkbox("Assumptions", value="Assumptions" in default_sections):
            sections.append("Assumptions")
        if st.checkbox("Risks", value="Risks" in default_sections):
            sections.append("Risks")

        submit = st.form_submit_button("🚀 Generate Proposal")

with right_col:

    st.subheader("📊 Proposal Generation Pipeline")

    node_msg_map = {
        "retrieve": "Checking if we already have similar proposal in our database",
        "grade_documents": "Analyzing Collected Data from web",
        "generate": "Generating Proposal Section",
        "websearch_client": "Searching about Client on web",
        "websearch_document": "Searching for similar industry and problem proposal on web",
        "summarize_problem": "Summarizing your problem statement"
    }

    if submit:
        validations = [
            (problem_statement, 50),
            (proposal_goal, 50),
            (client_name, 10),
            (approach, 50),
            (scope_exclusions, 20)
        ]

        if not all([problem_statement, proposal_goal, client_name, industry]):
            st.error("❗ Please fill all required fields.")
        elif not all(word_limit(text, limit) for text, limit in validations if text):
            st.error("❗ One or more fields exceed the word limit.")
        elif not sections:
            st.warning("⚠️ Please select at least one section to generate.")
        else:
            running_header = st.empty()
            running_header.markdown("### ⚙️ Running AI Agent")

            try:
                user_req = UserRequirement()
                user_req["problem_statement"] = problem_statement
                user_req["approach"] = approach
                user_req["budget_range"] = budget_range
                user_req["proposal_goal"] = proposal_goal
                user_req["scope_exclusions"] = scope_exclusions
                user_req["technical_depth"] = technical_depth
                user_req["timeline"] = timeline

                client_info = ClientInfo()
                client_info["client_name"] = client_name
                client_info["industry"] = industry

                user_req["client_info"] = client_info

                section_status_placeholder = st.empty()

                with st.spinner("Your proposal is being generated. Grab a coffee while we work on it!"):
                    previous_node = None
                    runner = run_graph(user_req, sections)
                    try:
                        while True:
                            section, node, event_type = next(runner)
                            if previous_node:
                                section_status_placeholder.markdown(
                                    f"✅ **{section}** → {previous_node} completed"
                                )
                            section_status_placeholder.markdown(
                                f"🔄 **{section}** → {node} running"
                            )
                            previous_node = node
                    except StopIteration as e:
                        if previous_node:
                            section_status_placeholder.markdown(
                                f"✅ **{section}** → {previous_node} completed"
                            )
                        section_results = e.value

                section_status_placeholder.empty()
                running_header.empty()

                if section_results:
                    st.markdown("## 📄 Generated Proposal")
                    for section, content in section_results.items():
                        st.markdown(f"### {section}")
                        st.write(content)

            except Exception as e:
                st.error(f"❌ Graph execution failed: {e}")

    else:
        st.info("👈 Fill the form and click **Generate Proposal** to start.")
