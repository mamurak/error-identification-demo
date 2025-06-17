import logging
import uuid
from os import getenv

from dotenv import load_dotenv
from llama_stack_client import Agent, LlamaStackClient, RAGDocument
from termcolor import cprint

from src.loki import query_loki_logs
from src.utils import step_printer

load_dotenv()


VECTOR_DB_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
VECTOR_DB_EMBEDDING_DIMENSION = 384
VECTOR_DB_CHUNK_SIZE = 512
VDB_PROVIDER = "milvus"

base_url = getenv("REMOTE_BASE_URL")
model_id = "llama32-3b"
temperature = 0.0
doc_urls = [
    ("https://raw.githubusercontent.com/mamurak/error-identification-demo/refs"
     "/heads/main/source_docs/customer-validation-service.pdf", "application/pdf"),
]
sampling_params = {
    "strategy": {"type": "greedy"},
    "max_tokens": 100000,
}
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def get_agentic_rag_client():
    client = LlamaStackClient(base_url=base_url)

    vector_db_id = f"test_vector_db_{uuid.uuid4()}"

    client.vector_dbs.register(
        vector_db_id=vector_db_id,
        embedding_model=VECTOR_DB_EMBEDDING_MODEL,
        embedding_dimension=VECTOR_DB_EMBEDDING_DIMENSION,
        provider_id=VDB_PROVIDER,
    )

    documents = [
        RAGDocument(
            document_id=f"num-{i}",
            content=url,
            mime_type=url_type,
            metadata={},
        )
        for i, (url, url_type) in enumerate(doc_urls)
    ]
    client.tool_runtime.rag_tool.insert(
        documents=documents,
        vector_db_id=vector_db_id,
        chunk_size_in_tokens=VECTOR_DB_CHUNK_SIZE,
    )

    # Get list of registered tools and extract their toolgroup IDs
    registered_tools = client.tools.list()
    registered_toolgroups = [tool.toolgroup_id for tool in registered_tools]

    if "builtin::rag" not in registered_toolgroups:
        client.toolgroups.register(
            toolgroup_id="builtin::rag",
            provider_id=VDB_PROVIDER
        )

    builtin_rag = dict(
        name="builtin::rag",
        args={"vector_db_ids": [vector_db_id]},
    )

    instructions = """
    You are a helpful assistant. You have access to a number of tools.
    Whenever a tool is called, be sure return the response in a friendly and helpful tone.
    If you're asked to retrieve logs, then use the query_loki_logs tool to look up logs from the 'customer-onboarding-service' container in namespace 'customer-onboarding'.
    """

    agent = Agent(
        client,
        model=model_id,
        instructions=instructions,
        tools=[query_loki_logs, builtin_rag],
        sampling_params=sampling_params,
    )
    return agent


def submit_prompts(agent, user_prompts):
    session_id = agent.create_session(session_name="full")
    for i, prompt in enumerate(user_prompts):
        print("\n"+"="*50)
        cprint(f"Processing user query: {prompt}", "blue")
        print("="*50)
        response = agent.create_turn(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            session_id=session_id,
            stream=False
        )
        step_printer(response.steps)


def search_status_for_client(agent, client_id, age_in_minutes=60):
    user_prompts = [
        f"Parse the available logs over the past {age_in_minutes} minutes and identify all entries that reference the customer ID {client_id}. Do not treat the ID as a search query—scan the logs line by line and extract matching entries.",
        "Once extracted, summarize the key events or issues associated with this customer.",
        #"If this customer has passed the validation process, do nothing. Otherwise, use the knowledge search tool to look up the meaning and context of the identified issues.",
        #"Finally, report your findings and provide a clear summary of the customer’s issue.",
    ]
    submit_prompts(agent, user_prompts)