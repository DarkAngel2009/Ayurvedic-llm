import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class AyurLLM:
    def __init__(self, model=None, tokenizer=None, device=None):
        if model and tokenizer and device:
            self.model = model
            self.tokenizer = tokenizer
            self.device = device
        else:
            # Fallback initialization
            model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            self.device = torch.device("cpu")
            print("AyurLLM: Using fallback CPU initialization")
    
    def generate_recommendations(self, user_profile, context):
        try:
            # Limit context to prevent token overflow
            limited_context = self._truncate_context(context)
            prompt = self._create_prompt(user_profile, limited_context)
            
            print(f"Generated prompt length: {len(prompt)} characters")  # Debug
            
            # Tokenize with strict limits
            inputs = self.tokenizer(
                prompt, 
                return_tensors="pt", 
                truncation=True, 
                max_length=1600,  # Leave room for generation
                padding=False
            )
            
            # Move inputs to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            print(f"Input token length: {inputs['input_ids'].shape[1]}")  # Debug
            
            # Clear GPU cache before generation
            if self.device.type == 'cuda':
                torch.cuda.empty_cache()
            
            # Generate with memory-efficient settings
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=200,  # Conservative limit
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1,
                    use_cache=False,  # Disable KV caching
                    early_stopping=True
                )
            
            # Clear cache after generation
            if self.device.type == 'cuda':
                torch.cuda.empty_cache()
            
            # Decode response
            full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the new generated text
            prompt_length = len(prompt)
            recommendations = full_response[prompt_length:].strip()
            
            print(f"Generated recommendations length: {len(recommendations)}")  # Debug
            
            return recommendations if recommendations else "I apologize, but I couldn't generate specific recommendations. Please try rephrasing your query."
            
        except Exception as e:
            print(f"Error in generate_recommendations: {str(e)}")
            if self.device.type == 'cuda':
                torch.cuda.empty_cache()
            return f"I apologize, but I encountered an error while generating recommendations. Please try again with a simpler query."
    
    def _truncate_context(self, context):
        """Limit context to prevent token overflow"""
        if not context:
            return []
        
        # Take only top 2 most relevant contexts and limit their length
        limited_context = []
        for ctx in context[:2]:
            text = ctx['text'][:200]  # Strict character limit
            limited_context.append({'text': text})
        
        return limited_context
    
    def _create_prompt(self, user_profile, context):
        """Create a concise prompt to stay within token limits"""
        
        # Build context string
        if context:
            context_text = " | ".join([c['text'] for c in context])
        else:
            context_text = "Use general Ayurvedic principles"
        
        # Extract key information
        age = user_profile.get('age', 'not specified')
        gender = user_profile.get('gender', 'not specified')
        dosha = user_profile.get('dosha', 'not specified')
        conditions = user_profile.get('conditions', [])
        conditions_text = ', '.join(conditions) if conditions else 'general wellness'
        
        # Create concise prompt
        prompt = f"""As an Ayurvedic practitioner, provide recommendations for:

Patient Profile:
- Age: {age}
- Gender: {gender}
- Dosha: {dosha}
- Health concerns: {conditions_text}

Relevant Knowledge: {context_text}

Ayurvedic Recommendations:
1."""
        
        return prompt
