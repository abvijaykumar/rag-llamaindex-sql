import streamlit as st
import os
import os.path

from dotenv import load_dotenv
from llama_index import VectorStoreIndex, SimpleDirectoryReader, load_index_from_storage, ServiceContext
from llama_index.storage import StorageContext
from llama_index.response.pprint_utils import pprint_response
from llama_index.llms import OpenAI
from llama_index import SQLDatabase, ServiceContext
from llama_index.indices.struct_store.sql_query import NLSQLTableQueryEngine

from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    select,
)


load_dotenv()

storage_path = "./vectorstore"
db_url = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"

llm = OpenAI(temperature=0.1, model="gpt-4-turbo-preview")
service_context = ServiceContext.from_defaults(llm=llm)

engine = create_engine(db_url)
sql_database = SQLDatabase(engine, include_tables=["product_master", "inventory"])

query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database,
    tables=["product_master", "inventory"],
)

def queryDB(query_str):
    response = query_engine.query(query_str)
    return response


# @st.cache_resource(show_spinner=False)
# def initialize(): 
#     if not os.path.exists(storage_path):
#         print("Index and Vector Store does not exisit, Creating a new store...")
#         documents = SimpleDirectoryReader(documents_path).load_data()
#         print("Documents: ")
#         print(documents)
#         index = VectorStoreIndex.from_documents(documents)
#         index.storage_context.persist(persist_dir=storage_path)
#     else:
#         storage_context = StorageContext.from_defaults(persist_dir=storage_path)
#         index = load_index_from_storage(storage_context)
#     return index
# index = initialize()

st.title("Query the database - TEXT to SQL")
if "messages" not in st.session_state.keys(): 
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question !"}
    ]

# chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

if prompt := st.chat_input("Your question"): 
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: 
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = queryDB(prompt) #chat_engine.chat(prompt)
            st.write(response.response)
            pprint_response(response, show_source=True)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) 