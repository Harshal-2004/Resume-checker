import streamlit as st
import os
import re
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from tempfile import NamedTemporaryFile
from difflib import SequenceMatcher

# Set up the page
st.set_page_config(page_title="Resume Matcher", layout="wide")
st.title("🔍 Resume Matcher")
st.markdown("Upload resumes to find matching job descriptions")

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

# Function to highlight matching words between two texts
def highlight_matching_words(text1, text2):
    # Convert to lowercase for case-insensitive matching
    text1_lower = text1.lower()
    text2_lower = text2.lower()
    
    # Find common words (more than 3 characters to avoid common words)
    words1 = set(re.findall(r'\b\w{4,}\b', text1_lower))
    words2 = set(re.findall(r'\b\w{4,}\b', text2_lower))
    common_words = words1.intersection(words2)
    
    # Also find common phrases using sequence matching
    matcher = SequenceMatcher(None, text1_lower, text2_lower)
    common_phrases = []
    for match in matcher.get_matching_blocks():
        if match.size > 10:  # Only consider phrases longer than 10 characters
            phrase = text1[match.a:match.a + match.size]
            common_phrases.append(phrase)
    
    # Highlight common words in the original text
    highlighted_text1 = text1
    highlighted_text2 = text2
    
    # Highlight words
    for word in common_words:
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        highlighted_text1 = pattern.sub(f"**{word}**", highlighted_text1)
        highlighted_text2 = pattern.sub(f"**{word}**", highlighted_text2)
    
    # Highlight phrases
    for phrase in common_phrases:
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        highlighted_text1 = pattern.sub(f"<mark>{phrase}</mark>", highlighted_text1)
        highlighted_text2 = pattern.sub(f"<mark>{phrase}</mark>", highlighted_text2)
    
    return highlighted_text1, highlighted_text2, common_words, common_phrases

def main():
    # Check if database exists
    if not os.path.exists("job_database"):
        st.error("❌ No job database found! Please run 'store_jobs.py' first to create a database.")
        return
    
    # Load the FAISS database
    with st.spinner("Loading job database..."):
        vectorstore = FAISS.load_local("job_database", embeddings, allow_dangerous_deserialization=True)
    
    st.success(f"✅ Loaded job database successfully!")
    
    # Upload resumes
    st.subheader("📄 Upload Resumes")
    resume_files = st.file_uploader("Upload Resume PDFs", type='pdf', accept_multiple_files=True)
    
    if resume_files and st.button("Find Matching Jobs"):
        with st.spinner("Analyzing resumes..."):
            results = []
            
            for resume_file in resume_files:
                resume_text = extract_text_from_pdf(resume_file)
                if resume_text:
                    # Split resume into chunks
                    text_splitter = RecursiveCharacterTextSplitter(
                        chunk_size=500, 
                        chunk_overlap=100
                    )
                    resume_chunks = text_splitter.split_text(resume_text)
                    
                    # For each resume chunk, find matching job description chunks
                    resume_matches = []
                    for chunk in resume_chunks:
                        matches = vectorstore.similarity_search_with_score(chunk, k=3)
                        for match, score in matches:
                            # Convert distance to similarity score (0-1)
                            similarity_score = 1.0 / (1.0 + float(score))
                            resume_matches.append({
                                'resume_chunk': chunk,
                                'job_chunk': match.page_content,
                                'job_id': match.metadata['job_id'],
                                'filename': match.metadata['filename'],
                                'similarity': similarity_score
                            })
                    
                    # Calculate overall match score for this resume
                    if resume_matches:
                        avg_similarity = sum(match['similarity'] for match in resume_matches) / len(resume_matches)
                        match_percentage = float(avg_similarity * 100)
                        
                        # Filter out very weak matches (below threshold)
                        good_matches = [match for match in resume_matches if match['similarity'] > 0.3]
                        
                        if good_matches:
                            # Get top matching chunks for display
                            top_matches = sorted(good_matches, key=lambda x: x['similarity'], reverse=True)[:5]
                            
                            # Add highlighted text to each match
                            for match in top_matches:
                                highlighted_job, highlighted_resume, common_words, common_phrases = highlight_matching_words(
                                    match['job_chunk'], match['resume_chunk']
                                )
                                match['highlighted_job'] = highlighted_job
                                match['highlighted_resume'] = highlighted_resume
                                match['common_words'] = common_words
                                match['common_phrases'] = common_phrases
                            
                            results.append({
                                'resume_name': resume_file.name,
                                'score': match_percentage,
                                'top_matches': top_matches,
                                'total_matches': len(good_matches),
                                'has_good_matches': True
                            })
                        else:
                            results.append({
                                'resume_name': resume_file.name,
                                'score': 0.0,
                                'top_matches': [],
                                'total_matches': 0,
                                'has_good_matches': False
                            })
                    else:
                        results.append({
                            'resume_name': resume_file.name,
                            'score': 0.0,
                            'top_matches': [],
                            'total_matches': 0,
                            'has_good_matches': False
                        })
            
            # Display results
            st.subheader("🎯 Matching Results")
            
            if not any(result['has_good_matches'] for result in results):
                st.warning("❌ No strong matches found. The resumes don't match the job requirements well.")
                return
            
            for rank, result in enumerate(results, 1):
                if result['has_good_matches']:
                    with st.expander(f"#{rank}: {result['resume_name']} - Match: {result['score']:.2f}% ({result['total_matches']} matches)", expanded=True):
                        progress_value = float(min(max(result['score']/100, 0.0), 1.0))
                        st.progress(progress_value)
                        
                        st.subheader("🔍 Top Matching Sections")
                        
                        for i, match in enumerate(result['top_matches'], 1):
                            match_container = st.container()
                            
                            with match_container:
                                st.markdown(f"### 🎯 Match #{i} → **{match['filename']}** (Similarity: `{match['similarity']:.3f}`)")
                                
                                # Show common words and phrases
                                if match['common_words'] or match['common_phrases']:
                                    st.markdown("#### 🎯 Why This Match Happened:")
                                    if match['common_words']:
                                        st.markdown(f"**Common Keywords:** `{', '.join(sorted(match['common_words']))}`")
                                    if match['common_phrases']:
                                        st.markdown(f"**Common Phrases:** `{' | '.join(match['common_phrases'])}`")
                                    st.markdown("---")
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown("#### 📋 Job Description Content")
                                    # Use markdown to render highlighted text
                                    st.markdown(match['highlighted_job'], unsafe_allow_html=True)
                                
                                with col2:
                                    st.markdown("#### 📄 Resume Content")
                                    st.markdown(match['highlighted_resume'], unsafe_allow_html=True)
                                
                                st.markdown("<br>", unsafe_allow_html=True)
                                st.markdown("---")
                                st.markdown("<br>", unsafe_allow_html=True)
                else:
                    with st.expander(f"#{rank}: {result['resume_name']} - ❌ No good matches found"):
                        st.warning("This resume doesn't match any job requirements well.")

if __name__ == "__main__":
    main()