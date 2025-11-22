import os
import torch

# Set environment variable for GPU memory management
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
os.environ["HUGGINGFACE_TOKEN"] = "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"  # Replace with your actual token

from transformers import AutoTokenizer, AutoModelForCausalLM

# Check GPU availability with fallback
try:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # Test GPU memory with small tensor
    if device.type == 'cuda':
        test_tensor = torch.randn(1000, 1000).to(device)
        del test_tensor
        torch.cuda.empty_cache()
    print(f"Successfully using device: {device}")
except Exception as e:
    print(f"GPU test failed: {e}")
    device = torch.device("cpu")
    print("Falling back to CPU")

model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

# Load with memory optimization
tokenizer = AutoTokenizer.from_pretrained(model_name)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16 if device.type == 'cuda' else torch.float32,
    device_map="auto" if device.type == 'cuda' else None,
    low_cpu_mem_usage=True,
    trust_remote_code=True
)

if device.type == 'cpu':
    model = model.to(device)

# Enable gradient checkpointing for memory efficiency
if hasattr(model, 'gradient_checkpointing_enable'):
    model.gradient_checkpointing_enable()

from flask import Flask, request, jsonify, render_template
from models.llm_model import AyurLLM
from models.knowledge_base import KnowledgeBase
from utils.text_processor import TextProcessor
from utils.safety_checker import SafetyChecker
from config import Config

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health_check():
    gpu_info = "N/A"
    if torch.cuda.is_available():
        gpu_properties = torch.cuda.get_device_properties(0)
        gpu_info = f"{gpu_properties.total_memory / 1024**3:.1f}GB"
    
    return jsonify({
        "status": "healthy", 
        "device": str(device),
        "gpu_memory": gpu_info,
        "model_loaded": model is not None
    })

@app.route('/process_books', methods=['POST'])
def process_books():
    try:
        processor = TextProcessor()
        chunks = processor.process_books(Config.BOOKS_PATH)
        kb = KnowledgeBase()
        kb.add_documents(chunks)
        return jsonify({"chunks_added": len(chunks), "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"}), 500

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    try:
        req = request.json
        print(f"Received request: {req}")  # Debug log
        
        user_profile = req.get('user_profile', {})
        print(f"User profile: {user_profile}")  # Debug log
        
        # Validate user profile
        if not user_profile:
            return jsonify({"error": "No user profile provided"}), 400
        
        # Create search query for knowledge base
        conditions = user_profile.get('conditions', [])
        search_terms = [
            str(user_profile.get('age', '')),
            user_profile.get('gender', ''),
            user_profile.get('dosha', ''),
        ]
        search_terms.extend(conditions)
        search_query = ' '.join([term for term in search_terms if term])
        
        print(f"Search query: {search_query}")  # Debug log
        
        # Get relevant context from knowledge base
        kb = KnowledgeBase()
        context = kb.search_relevant_context(search_query)
        print(f"Found {len(context)} context items")  # Debug log
        
        # Clear GPU cache before inference
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        # Generate recommendations
        llm = AyurLLM(model=model, tokenizer=tokenizer, device=device)
        recs_text = llm.generate_recommendations(user_profile, context)
        recs_list = [line.strip() for line in recs_text.split('\n') if line.strip()]
        
        # Safety check
        safety_checker = SafetyChecker()
        safety = safety_checker.check_safety(user_profile, recs_list)
        
        # Clear GPU cache after inference
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        response = {
            "recommendations": recs_list,
            "safety_check": safety,
            "context_snippets": [c['text'][:100] + '...' for c in context[:2]],
            "device_used": str(device),
            "user_profile_processed": user_profile
        }
        
        print(f"Response generated successfully")  # Debug log
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in get_recommendations: {str(e)}")  # Debug log
        # Clear GPU cache on error
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        return jsonify({"error": str(e), "user_profile": user_profile}), 500

if __name__ == '__main__':
    print(f"Starting Ayurvedic LLM server on device: {device}")
    app.run(host='127.0.0.1', port=Config.API_PORT, debug=Config.DEBUG)
