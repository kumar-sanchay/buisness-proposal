from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def generate_proposal_section(llm: BaseChatModel):

    system_prompt = """
      You are a senior consulting proposal writer.

      You must follow ALL rules below strictly:

      OUTPUT RULES:
      - Generate ONLY the requested proposal section.
      - Produce ONLY ONE continuous output.
      - Do NOT include section headings or labels.
      - Do NOT include explanations, notes, or meta commentary.

      GROUNDING RULES:
      - Use ONLY information explicitly provided in the user input.
      - Do NOT invent client details, metrics, timelines, pricing, tools, or outcomes.
      - Do NOT assume facts not present in the input.
      - If required information is missing or unclear, explicitly mark it as "indicative".
      - Do NOT reference or imply other proposal sections.

      REFERENCE RULES:
      - Retrieved documents and web search results may be used ONLY for structure and wording style.
      - They must NOT be treated as factual unless they directly align with the provided user input.

      CLIENT CONTEXT RULE:
      - The term "client" always refers to the organization to whom this proposal is being submitted.
      - All statements must align with the client’s stated industry and domain only.

      SECTION LENGTH CONTROL (MANDATORY):
      Decide the length and depth of the output based on section criticality:
      - High criticality sections (e.g., Solution, Approach, Methodology, Technical Architecture):
        → Produce detailed, multi-paragraph, implementation-level content.
      - Medium criticality sections (e.g., Executive Summary, Problem Statement, Risks):
        → Produce structured, explanatory content with sufficient detail.
      - Low criticality sections (e.g., Timeline, Budget, Scope Exclusions):
        → Produce concise, precise content without unnecessary elaboration.

      Failure to follow these rules is considered an incorrect response.
      """

    human_prompt = """
      PROPOSAL SECTION:
      {section_name}

      USER REQUIREMENTS:
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

      CLIENT INFORMATION:
      Client Name:
      {client_name}

      Industry:
      {industry}

      REFERENCE CONTEXT (STYLE ONLY):
      Vector DB Documents:
      {documents}

      Client Web Search Results:
      {client_websearch}

      TASK:
      Generate ONLY the "{section_name}" section of the consulting proposal.
      Ground every statement in the user requirements and align with the requested technical depth.
      """


    query_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", human_prompt)
        ]
    )

    return query_prompt | llm
    