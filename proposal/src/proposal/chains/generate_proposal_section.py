from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def generate_proposal_section(llm: BaseChatModel):

    system_prompt = """
        You are an expert consulting proposal writer.

        CRITICAL RULES (must follow strictly):
        - Generate ONLY the requested proposal section and just only 1 output (No section heading or explaination).
        - Use ONLY the information explicitly provided in the input.
        - Do NOT invent client details, metrics, timelines, or pricing.
        - Do NOT assume facts not present in the state.
        - Do NOT reference or mention other proposal sections.
        - If required information is missing, mark it as indicative.
        - Use retrieved documents and web search results ONLY as inspiration for structure and wording,
          not as factual truth unless they directly align with the provided state.
        - Only use those information from provided details which are required to generate the section.
          For example, you don't have to use budget, timeline, etc while generating text for "executive summary" section.
        - The “client” refers to the organization to whom this consulting proposal will be submitted.
          Generate all statements using client-specific web search results and align them with the client’s industry and domain.

        Your output must be professional, clear, and aligned with consulting standards.
        """
    
    human_prompt = """
        PROPOSAL SECTION TO GENERATE:
        {section_name}

        --------------------
        USER REQUIREMENT
        --------------------
        Problem Statement:
        {problem_statement}

        Proposal Goal:
        {proposal_goal}

        Approach (if provided):
        {approach}

        Timeline:
        {timeline}

        Scope Exclusions:
        {scope_exclusions}

        Budget Range:
        {budget_range}

        Technical Depth:
        {technical_depth}

        --------------------
        CLIENT INFORMATION
        --------------------
        Client Name:
        {client_name}

        Industry:
        {industry}

        --------------------
        RETRIEVED CONTEXT (REFERENCE ONLY)
        --------------------
        Vector DB Documents:
        {documents}

        Client Web Search Results:
        {client_websearch}
        --------------------
        TASK
        --------------------
        Generate ONLY the "{section_name}" section of a consulting proposal.

        Requirements:
        - Ground all statements in the USER REQUIREMENT.
        - Align tone and detail with the requested technical depth.
        - If budget or timeline is unclear, mark them as indicative.
        - Do not include headings for other sections.
        - Do not introduce facts not present in the input.

        Begin the "{section_name}" section below.
    """

    query_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", human_prompt)
        ]
    )

    return query_prompt | llm
    