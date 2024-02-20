#To test AstraDB Connection, run this file with the following command: python3 integrate.py

import os

from llama_index.vector_stores.astra import AstraDBVectorStore
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext

from dotenv import load_dotenv

load_dotenv()

ASTRA_DB_APPLICATION_TOKEN = os.environ.get("ASTRA_DB_APPLICATION_TOKEN")
ASTRA_DB_API_ENDPOINT = os.environ.get("ASTRA_DB_API_ENDPOINT")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

documents = SimpleDirectoryReader("./data").load_data()

astra_db_store = AstraDBVectorStore(
    token=ASTRA_DB_APPLICATION_TOKEN,
    api_endpoint=ASTRA_DB_API_ENDPOINT,
    collection_name="test4",
    embedding_dimension=1536,
)

storage_context = StorageContext.from_defaults(vector_store=astra_db_store)

index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context
)

query_engine = index.as_query_engine()
query_string_1 = "how can trevor project help LGBTQ+ youth?"
response = query_engine.query(query_string_1)

print(query_string_1)
print(response.response)