from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
def chunk_text(text: str, chunk_size: int = 300, overlap: int = 100) -> list[str]:
    """
    Split text into chunks based on word count with overlap.
    
    Args:
        text (str): Input text to be chunked
        chunk_size (int): Number of words per chunk
        overlap (int): Number of words to overlap between chunks
        
    Returns:
        List[str]: List of text chunks
    """
    # Split text into words
    words = text.split()
    
    # If text is shorter than chunk_size, return it as a single chunk
    if len(words) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(words):
        # Calculate end index for current chunk
        end = start + chunk_size
        
        # Get the words for current chunk
        chunk_words = words[start:end]
        
        # Join words back into text
        chunk = ' '.join(chunk_words)
        chunks.append(chunk)
        
        # Move start pointer, accounting for overlap
        start = end - overlap
        
    return chunks

def extract_text_from_pdf(pdf_path):
    # Configure layout analysis parameters
    laparams = LAParams(
        line_margin=0.5,      # Margin between lines
        word_margin=0.1,      # Margin between words
        char_margin=2.0,      # Margin between characters
        boxes_flow=0.5,       # Text flow direction
        detect_vertical=True  # Detect vertical text
    )
    
    # Extract text with custom layout parameters
    text = extract_text(
        pdf_path,
        laparams=laparams,
        codec='utf-8'
    )
    
    return text

def get_allowed_models(llm):
    failing_llms = [
        "llama3-70b-8192",
        "llama-3.2-90b-text-preview",
        "mixtral-8x7b-32768",
        "lava-v1.5-7b-4096-preview",
        "llama-guard-3-8b",
    ]
    return [model for model in llm.allowed_models if model not in failing_llms]
