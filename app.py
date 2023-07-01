import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader 
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from htmlTemplate import css, bot_template, user_template

# css_file_path = "static/style.css"
# local_css(css_file_path)


def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator='\n',
        chunk_size=1000,
        chunk_overlap = 200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunk):
    embeddings = OpenAIEmbeddings() # It will take API and work 
    # embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl") # Need computaional power & free to use
    vectorstore = FAISS.from_texts(texts=text_chunk, embedding=embeddings)
    return vectorstore

def get_conversation_chain(vector_store):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm = llm,
        retriever=vector_store.as_retriver,
        memory = memory
    )
    return conversation_chain



def main():
    load_dotenv()
    st.set_page_config( page_title='Chat with multiple PDFs', 
                        page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None


    st.header("Chat with multiple PDFs books:")
    st.text_input("Ask a question about your Documents:")
    
    st.write(user_template.replace("{{MSG}}", "Hello Bot"), unsafe_allow_html=True)
    st.write(bot_template.replace("{{MSG}}", "Hello pankaj"), unsafe_allow_html=True)

    with st.sidebar:
        st.subheader("Your Documents")
        pdf_docs = st.file_uploader("upload your pdfs here click on 'Process'", accept_multiple_files=True)
        if st.button("Process"):
            with st.spinner("Processing... "):
                # Get the PDF text
                raw_text = get_pdf_text(pdf_docs)
                # st.write(raw_text)

                # Get the text chunks
                text_chunks = get_text_chunks(raw_text)
                # st.write(text_chunks)

                # Create vector store
                vector_store = get_vector_store(text_chunks)

                # Create Conversatioon chain
                st.session_state.conversation = get_conversation_chain(vector_store)


if __name__=="__main__":
    main()