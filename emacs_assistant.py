from typing import Dict, List

from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Chroma

PROMPT_TEMPLATE = """
You are an Emacs learning assistant for non-technical users.

Rules:
- Start with a plain-language explanation first.
- Avoid jargon unless needed, and define it when used.
- Give practical steps the user can try in Emacs.
- If the question is advanced, still explain what problem the feature solves.
- If the answer is uncertain, say what is missing.

User skill level: {skill_level}

Context:
{context}

Question:
{question}

Helpful answer:
""".strip()


def _build_chain() -> RetrievalQA:
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(persist_directory="emacs_db", embedding_function=embeddings)

    llm = Ollama(model="deepseek-r1")

    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "question", "skill_level"],
    )

    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
        chain_type="stuff",
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )


def ask_emacs(query: str, skill_level: str = "beginner") -> Dict[str, List[str]]:
    qa_chain = _build_chain()
    result = qa_chain.invoke({"query": query, "skill_level": skill_level})

    sources = []
    for doc in result.get("source_documents", []):
        source = doc.metadata.get("resource_path") or doc.metadata.get("source")
        if source and source not in sources:
            sources.append(source)

    return {
        "answer": result.get("result", ""),
        "sources": sources,
    }
