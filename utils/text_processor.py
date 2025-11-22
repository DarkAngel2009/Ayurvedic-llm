import re
import PyPDF2
import os

class TextProcessor:
    def __init__(self, chunk_size=1000, overlap=200):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def extract_pdf_text(self, pdf_path):
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            print(f"Error reading {pdf_path}: {e}")
            return ""
    
    def clean_text(self, text):
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\-\.\,\;\:\(\)]', '', text)
        return text.strip()
    
    def chunk_text(self, text, metadata=None):
        words = text.split()
        chunks = []
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk = ' '.join(words[i:i + self.chunk_size])
            chunks.append({
                'text': chunk,
                'chunk_id': f"chunk_{i}",
                'source': metadata['source'] if metadata else 'unknown',
                'topic': metadata['topic'] if metadata else 'general'
            })
        return chunks

    def process_books(self, books_directory):
        categories = {
            'ayurveda': ['charaka', 'sushruta', 'ashtanga', 'bhavaprakasha'],
            'yoga': ['hatha', 'patanjali', 'pranayama', 'asana'],
            'acupuncture': ['acupuncture', 'meridian', 'points', 'tcm']
        }
        all_chunks = []
        for filename in os.listdir(books_directory):
            if filename.lower().endswith('.pdf') or filename.lower().endswith('.txt'):
                filepath = os.path.join(books_directory, filename)
                text = self.extract_pdf_text(filepath) if filename.endswith('.pdf') else open(filepath, 'r', encoding='utf-8').read()
                text = self.clean_text(text)
                topic = 'general'
                for cat, keywords in categories.items():
                    if any(k in filename.lower() for k in keywords):
                        topic = cat
                        break
                metadata = {'source': filename, 'topic': topic}
                all_chunks.extend(self.chunk_text(text, metadata))
        return all_chunks
