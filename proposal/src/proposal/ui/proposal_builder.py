import streamlit as st

from proposal.core.graph_state import UserRequirement, GraphState
from proposal.graph.graph import build_graph


st.set_page_config(page_title="AI Consulting Proposal Builder", layout="wide")

st.title("AI Consulting Proposal Builder")

left_col, right_col = st.columns(2)

with left_col:
    st.subheader("Client & Requirement Details")

    with st.form("proposal_form"):
        # Required fields
        problem_statement = st.text_area(
            "Problem Statement *",
            placeholder="Describe the business or technical problem"
        )

        client_name = st.text_input(
            "Client Company Name *",
            placeholder="e.g. ABC Corp"
        )

        industry = st.text_input(
            "Industry *",
            placeholder="e.g. Banking, Retail, Healthcare"
        )

        proposal_goal = st.text_area(
            "Proposal Goal *",
            placeholder="What is the objective of this proposal?"
        )

        # Optional fields
        approach = st.text_area(
            "Approach",
            placeholder="High-level approach or methodology"
        )

        timeline = st.text_input(
            "Timeline",
            placeholder="e.g. 12 weeks"
        )

        scope_exclusions = st.text_area(
            "Scope & Exclusions",
            placeholder="What is out of scope?"
        )

        budget_range = st.text_input(
            "Budget Range",
            placeholder="e.g. $50k - $100k"
        )

        technical_depth = st.selectbox(
            "Technical Depth",
            ["High-level", "Medium", "Deep Technical"]
        )

        submit = st.form_submit_button("Generate Proposal")


with right_col:
    st.subheader("Generated Consulting Proposal")

    if submit:
        # Validation for required fields
        if not all([problem_statement, client_name, industry, proposal_goal]):
            st.error("Please fill all required fields marked with *")
        else:
            user_requirement: UserRequirement = {
                "problem_statement": problem_statement,
                "client_info": {
                    "client_name": client_name,
                    "industry": industry,
                },
                "proposal_goal": proposal_goal,
                "approach": approach,
                "timeline": timeline,
                "scope_exclusions": scope_exclusions,
                "budget_range": budget_range,
                "technical_depth": technical_depth,
            }

            with st.spinner("Generating proposal..."):
                generated_section = build_graph(user_requirement=user_requirement)

            st.markdown(generated_section)
    else:
        st.info("Fill the form and click **Generate Proposal**")
