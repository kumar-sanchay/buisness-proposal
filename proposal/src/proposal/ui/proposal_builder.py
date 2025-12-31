import time
import streamlit as st

from proposal.core.graph_state import UserRequirement, GraphState, ClientInfo
from proposal.graph.graph import run_graph


st.set_page_config(
    page_title="AI Consulting Proposal Builder",
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

    with st.form("proposal_form"):
        st.markdown("### 🧠 Problem Definition")

        problem_statement = st.text_area(
            "Problem Statement * (max 50 words)",
            placeholder="Describe the business or technical problem",
            height=120
        )

        proposal_goal = st.text_area(
            "Proposal Goal * (max 50 words)",
            placeholder="Objective of this proposal",
            height=120
        )

        st.markdown("### 🏢 Client Details")

        client_name = st.text_input(
            "Client Company Name * (max 10 words)",
            placeholder="e.g. ABC Corp"
        )

        industry = st.selectbox(
            "Industry *",
            [
                "Banking & Financial Services",
                "Insurance",
                "Investment & Asset Management",
                "Healthcare & Life Sciences",
                "Retail & E-Commerce",
                "Manufacturing & Industrial",
                "Supply Chain & Logistics",
                "Technology & SaaS"
            ]
        )

        st.markdown("### 🛠 Optional Inputs")

        approach = st.text_area(
            "Approach (max 50 words)",
            placeholder="High-level approach or methodology",
            height=120
        )

        timeline = st.text_input(
            "Timeline (max 5 words)",
            placeholder="e.g. 12 weeks"
        )

        scope_exclusions = st.text_area(
            "Scope & Exclusions (max 20 words)",
            placeholder="What is out of scope?",
            height=120
        )

        budget_range = st.text_input(
            "Budget Range (max 5 words)",
            placeholder="e.g. $50k - $100k"
        )

        technical_depth = st.selectbox(
            "Technical Depth",
            ["High-level", "Medium", "Deep Technical"]
        )

        st.markdown("### 📦 Sections to Generate")

        sections = []

        if st.checkbox("Executive Summary"):
            sections.append("Executive Summary")

        if st.checkbox("Scope of Work"):
            sections.append("Scope of Work")

        if st.checkbox("Approach"):
            sections.append("Approach")

        if st.checkbox("Methodology"):
            sections.append("Methodology")

        if st.checkbox("Pricing"):
            sections.append("Pricing")

        if st.checkbox("Timeline"):
            sections.append("Timeline")

        if st.checkbox("Deliverables"):
            sections.append("Deliverables")

        if st.checkbox("Assumptions"):
            sections.append("Assumptions")

        if st.checkbox("Risks"):
            sections.append("Risks")

        submit = st.form_submit_button("🚀 Generate Proposal")


with right_col:

    st.subheader("📊 Proposal Generation Pipeline")

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

                run_container = st.container()
                status_container = st.container()

                # Create ONE placeholder for latest status line
                section_status_placeholder = st.empty()

                with st.spinner("Generating proposal..."):
                    previous_node = None

                    runner = run_graph(user_req, sections)

                    try:
                        while True:
                            section, node, event_type = next(runner)

                            # Previous node completed
                            if previous_node:
                                section_status_placeholder.markdown(
                                    f"✅ **{section}** → {previous_node} completed"
                                )

                            # Current node running (replaces same line)
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

                # st.markdown("### ✏️ Review or Proceed")

                # change_request = st.text_area(
                #     "Suggest changes (optional, max 20 words)",
                #     placeholder="E.g. refine executive summary tone",
                #     height=70
                # )

                # col1, col2 = st.columns(2)

                # with col1:
                #     rerun = st.button("🔁 Apply Changes & Re-run")

                # with col2:
                #     proceed = st.button("➡️ Proceed")

                # if rerun:
                #     st.info("♻️ Graph will re-run with requested changes (connect graph here).")

                # if proceed:
                #     st.success("✅ Proceeding to final proposal export.")
            except Exception:
                st.error(f"❌ Graph execution failed: {e}")


    else:
        st.info("👈 Fill the form and click **Generate Proposal** to start.")
