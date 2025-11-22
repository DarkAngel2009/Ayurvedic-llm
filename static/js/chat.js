class AyurvedicChat {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        
        this.initEventListeners();
        this.conversationHistory = [];
        
        console.log('AyurvedicChat initialized');
    }
    
    initEventListeners() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        this.messageInput.addEventListener('input', () => {
            this.autoResize();
        });
    }
    
    autoResize() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        // Disable input during processing
        this.messageInput.disabled = true;
        this.sendButton.disabled = true;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.autoResize();
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Extract user profile from current message
            const userProfile = this.extractUserProfile(message);
            console.log('Extracted user profile:', userProfile);
            
            // Call backend API
            const response = await this.callAyurvedicAPI(userProfile);
            console.log('API response:', response);
            
            // Remove typing indicator
            this.hideTypingIndicator();
            
            // Display recommendations
            if (response.recommendations && response.recommendations.length > 0) {
                const recommendationsText = response.recommendations.join('\n\n');
                this.addMessage(recommendationsText, 'bot');
                
                // Show context if available
                if (response.context_snippets && response.context_snippets.length > 0) {
                    const contextInfo = `\n\n📚 *Based on knowledge from: ${response.context_snippets.join(' | ')}*`;
                    this.addMessage(contextInfo, 'bot', true);
                }
                
                // Show device info for debugging
                if (response.device_used) {
                    console.log('Response generated using:', response.device_used);
                }
            } else {
                this.addMessage('I apologize, but I couldn\'t generate recommendations for your query. Please try providing more specific information about your health concerns.', 'bot');
            }
            
        } catch (error) {
            console.error('Error:', error);
            this.hideTypingIndicator();
            this.addMessage('I apologize, but I encountered an error. Please try again or rephrase your question.', 'bot');
        } finally {
            // Re-enable input
            this.messageInput.disabled = false;
            this.sendButton.disabled = false;
            this.messageInput.focus();
        }
    }
    
    extractUserProfile(message) {
        console.log('Extracting profile from message:', message);
        
        const profile = {
            age: this.extractAge(message),
            gender: this.extractGender(message),
            dosha: this.extractDosha(message),
            conditions: this.extractConditions(message)
        };
        
        console.log('Profile extraction result:', profile);
        return profile;
    }
    
    extractAge(text) {
        // Enhanced age extraction patterns
        const patterns = [
            /(\d{1,3})[- ]*year[s]?[- ]*old/i,
            /age[:\s]+(\d{1,3})/i,
            /(\d{1,3})[- ]*years?[^- ]*old/i,
            /i['\s]*m[:\s]*(\d{1,3})/i,
            /(\d{1,3})[- ]*yo\b/i  // "yo" abbreviation
        ];
        
        for (const pattern of patterns) {
            const match = text.match(pattern);
            if (match) {
                const age = parseInt(match[1]);
                if (age >= 1 && age <= 120) {
                    console.log('Found age:', age);
                    return age;
                }
            }
        }
        
        console.log('No age found, using default');
        return 30; // Default age
    }
    
    extractGender(text) {
        const malePatterns = /\b(male|man|boy|gentleman|he|his|him)\b/i;
        const femalePatterns = /\b(female|woman|girl|lady|she|her|hers)\b/i;
        
        if (malePatterns.test(text)) {
            console.log('Found gender: male');
            return 'male';
        }
        if (femalePatterns.test(text)) {
            console.log('Found gender: female');
            return 'female';
        }
        
        console.log('No gender found');
        return 'not specified';
    }
    
    extractDosha(text) {
        if (/vata[- ]?pitta|pitta[- ]?vata/i.test(text)) {
            console.log('Found dosha: Vata-Pitta');
            return 'Vata-Pitta';
        }
        if (/vata[- ]?kapha|kapha[- ]?vata/i.test(text)) {
            console.log('Found dosha: Vata-Kapha');
            return 'Vata-Kapha';
        }
        if (/pitta[- ]?kapha|kapha[- ]?pitta/i.test(text)) {
            console.log('Found dosha: Pitta-Kapha');
            return 'Pitta-Kapha';
        }
        if (/vata/i.test(text)) {
            console.log('Found dosha: Vata');
            return 'Vata';
        }
        if (/pitta/i.test(text)) {
            console.log('Found dosha: Pitta');
            return 'Pitta';
        }
        if (/kapha/i.test(text)) {
            console.log('Found dosha: Kapha');
            return 'Kapha';
        }
        
        console.log('No dosha found');
        return 'not specified';
    }
    
    extractConditions(text) {
        const conditions = [];
        const conditionPatterns = {
            'diabetes': /diabetes|diabetic|blood sugar|high glucose/i,
            'back pain': /back pain|backache|spine pain|lower back|lumbar pain/i,
            'headache': /headache|head pain|migraine|head ache/i,
            'insomnia': /insomnia|sleep problems|can't sleep|sleepless/i,
            'stress': /stress|stressed|tension|anxiety/i,
            'joint pain': /joint pain|arthritis|knee pain|shoulder pain/i,
            'digestive issues': /digestive|digestion|stomach|gastric|acidity|bloating/i,
            'high blood pressure': /high blood pressure|hypertension|bp|blood pressure/i,
            'fatigue': /fatigue|tired|exhausted|weakness|low energy/i,
            'skin allergies': /skin allerg|rash|eczema|dermatitis/i,
            'hair fall': /hair fall|hair loss|baldness|alopecia/i,
            'constipation': /constipation|constipated|irregular bowel/i,
            'dry skin': /dry skin|skin dryness|rough skin/i,
            'acne': /acne|pimples|breakouts/i
        };
        
        const lowerText = text.toLowerCase();
        
        for (const [condition, pattern] of Object.entries(conditionPatterns)) {
            if (pattern.test(lowerText)) {
                conditions.push(condition);
                console.log('Found condition:', condition);
            }
        }
        
        console.log('All conditions found:', conditions);
        return conditions;
    }
    
    async callAyurvedicAPI(userProfile) {
        const requestBody = {
            user_profile: userProfile
        };
        
        console.log('Sending API request:', requestBody);
        
        const response = await fetch('/get_recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        
        return await response.json();
    }
    
    addMessage(content, sender, isContext = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        if (isContext) {
            contentDiv.style.fontSize = '0.9em';
            contentDiv.style.fontStyle = 'italic';
            contentDiv.style.opacity = '0.8';
        }
        
        // Handle line breaks in content
        contentDiv.innerHTML = content.replace(/\n/g, '<br>');
        
        messageDiv.appendChild(contentDiv);
        this.chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing-indicator';
        typingDiv.id = 'typing-indicator';
        
        typingDiv.innerHTML = `
            <div class="message-content">
                <span>Analyzing your health profile</span>
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(typingDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
}

// Initialize chat when page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing chat...');
    new AyurvedicChat();
});
