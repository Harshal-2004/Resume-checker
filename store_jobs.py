import streamlit as st
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from tempfile import NamedTemporaryFile

# Set up the page
st.set_page_config(page_title="Job Description Storage", layout="wide")
st.title("💼 Store Job Descriptions")
st.markdown("Upload job descriptions to create a searchable database")

# Initialize the embedding model
@st.cache_resource
def load_embedding_model():
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    return HuggingFaceEmbeddings(model_name=model_name)

embeddings = load_embedding_model()

# Function to process PDF and extract text
def extract_text_from_pdf(pdf_file):
    try:
        with NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_file.getvalue())
            tmp_file_path = tmp_file.name
        
        loader = PyPDFLoader(tmp_file_path)
        documents = loader.load()
        os.unlink(tmp_file_path)
        
        full_text = " ".join([doc.page_content for doc in documents])
        return full_text
    except Exception as e:
        st.error(f"Error processing {pdf_file.name}: {str(e)}")
        return None

def main():
    # Create database directory if it doesn't exist
    os.makedirs("job_database", exist_ok=True)
    
    st.subheader("📋 Upload Job Descriptions")
    job_desc_files = st.file_uploader("Upload Job Description PDFs", type='pdf', accept_multiple_files=True)
    
    if job_desc_files and st.button("Store Job Descriptions"):
        with st.spinner("Processing and storing job descriptions..."):
            all_chunks = []
            all_metadatas = []
            
            for job_file in job_desc_files:
                job_text = extract_text_from_pdf(job_file)
                if job_text:
                    # Split job description into chunks
                    text_splitter = RecursiveCharacterTextSplitter(
                        chunk_size=300, 
                        chunk_overlap=100
                    )
                    chunks = text_splitter.split_text(job_text)
                    
                    # Create metadata for each chunk
                    job_id = os.path.splitext(job_file.name)[0]  # Use filename as ID
                    metadatas = [{'job_id': job_id, 'filename': job_file.name}] * len(chunks)
                    
                    all_chunks.extend(chunks)
                    all_metadatas.extend(metadatas)
                    
                    st.success(f"Processed: {job_file.name} → {len(chunks)} chunks")
            
            if all_chunks:
                # Create FAISS vectorstore
                vectorstore = FAISS.from_texts(
                    texts=all_chunks,
                    embedding=embeddings,
                    metadatas=all_metadatas
                )
                
                # Save the database to disk
                vectorstore.save_local("job_database")
                
                st.success(f"✅ Database created successfully!")
                st.info(f"Stored {len(all_chunks)} chunks from {len(job_desc_files)} job descriptions")
                st.info("Database saved in: job_database/ folder")
                
                # Show what's stored
                st.subheader("📊 Stored Job Descriptions")
                for job_file in job_desc_files:
                    st.write(f"• {job_file.name}")
            else:
                st.error("No text could be extracted from the files")

if __name__ == "__main__":
    main()