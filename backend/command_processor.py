#!/usr/bin/env python3
"""
Command processor for voice recognition
Helps filter and process voice commands more effectively
"""
import re
from typing import List, Dict, Optional

class VoiceCommandProcessor:
    def __init__(self):
        # Common voice command patterns
        self.command_patterns = {
            'help': [r'\b(help|assist|support)\b', r'\b(what can you do|how do you work)\b'],
            'navigation': [r'\b(go to|navigate to|open|show)\b', r'\b(home|settings|profile|menu)\b'],
            'action': [r'\b(do|perform|execute|run)\b', r'\b(click|tap|select|choose)\b'],
            'search': [r'\b(search|find|look for|lookup)\b'],
            'stop': [r'\b(stop|quit|exit|cancel)\b', r'\b(that\'s all|done|finished)\b'],
            'repeat': [r'\b(repeat|say again|what did you say)\b'],
            'volume': [r'\b(volume|louder|quieter|sound)\b'],
            'time': [r'\b(time|what time|current time)\b'],
            'weather': [r'\b(weather|temperature|forecast)\b'],
            'hindi': [
                r'\b(to hindi|hindi|hindi mein|hindi me|translate to hindi|hindi translate|hindi me translate|hindi mein translate)\b', 
                r'\b(हिंदी|हिंदी में|हिंदी मे|हिंदी में बोलो|हिंदी मे बोलो|हिंदी में बताओ|हिंदी मे बताओ)\b',
                r'\b(hindi mein bolo|hindi me bolo|hindi mein batao|hindi me batao|hindi me kaho|hindi mein kaho)\b',
                r'\b(bolo hindi mein|batao hindi mein|kaho hindi mein|speak in hindi|talk in hindi)\b'
            ],
        }
        
        # Noise words to filter out
        self.noise_words = {
            'um', 'uh', 'ah', 'er', 'hmm', 'like', 'you know', 'actually',
            'basically', 'literally', 'so', 'well', 'right', 'okay', 'ok'
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize the transcribed text"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common noise words
        words = text.split()
        cleaned_words = [word for word in words if word not in self.noise_words]
        
        return ' '.join(cleaned_words)
    
    def extract_command(self, text: str) -> Dict[str, any]:
        """Extract command type and parameters from text"""
        cleaned_text = self.clean_text(text)
        
        if not cleaned_text:
            return {'type': 'none', 'confidence': 0.0, 'text': text, 'cleaned': ''}
        
        # Check against command patterns
        best_match = {'type': 'unknown', 'confidence': 0.0, 'text': text, 'cleaned': cleaned_text}
        
        for command_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                if re.search(pattern, cleaned_text, re.IGNORECASE):
                    confidence = 0.8  # Base confidence
                    
                    # Increase confidence for exact matches
                    if re.match(pattern, cleaned_text, re.IGNORECASE):
                        confidence = 0.9
                    
                    if confidence > best_match['confidence']:
                        best_match = {
                            'type': command_type,
                            'confidence': confidence,
                            'text': text,
                            'cleaned': cleaned_text,
                            'pattern': pattern
                        }
        
        # If no pattern matches but we have substantial text, it might be a general query
        if best_match['type'] == 'unknown' and len(cleaned_text.split()) >= 2:
            best_match['type'] = 'general_query'
            best_match['confidence'] = 0.5
        
        return best_match
    
    def is_valid_command(self, text: str, min_confidence: float = 0.3) -> bool:
        """Check if the text contains a valid command"""
        command = self.extract_command(text)
        return command['confidence'] >= min_confidence
    
    def process_voice_input(self, text: str) -> Dict[str, any]:
        """Main processing function for voice input"""
        command = self.extract_command(text)
        
        # Add processing suggestions
        suggestions = []
        
        if command['type'] == 'help':
            suggestions.append("I can help you navigate the app, search for information, or perform various actions.")
        elif command['type'] == 'navigation':
            suggestions.append("I'll help you navigate to the requested section.")
        elif command['type'] == 'action':
            suggestions.append("I'll help you perform the requested action.")
        elif command['type'] == 'search':
            suggestions.append("I'll help you search for that information.")
        elif command['type'] == 'stop':
            suggestions.append("Stopping current operation.")
        elif command['type'] == 'repeat':
            suggestions.append("I'll repeat the last response.")
        elif command['type'] == 'hindi':
            suggestions.append("I'll translate the response to Hindi and speak it aloud.")
            suggestions.append("मैं जवाब को हिंदी में अनुवाद करके बोलूंगा।")
        elif command['type'] == 'general_query':
            suggestions.append("I'll help you with that question.")
        
        command['suggestions'] = suggestions
        return command

# Global instance
command_processor = VoiceCommandProcessor()

def process_voice_command(text: str) -> Dict[str, any]:
    """Process a voice command and return structured result"""
    return command_processor.process_voice_input(text)

def is_valid_voice_command(text: str) -> bool:
    """Check if text is a valid voice command"""
    return command_processor.is_valid_command(text)

if __name__ == "__main__":
    # Test the command processor
    test_inputs = [
        "help me navigate to the home page",
        "um, can you, like, search for something?",
        "what time is it?",
        "stop the current operation",
        "repeat that please",
        "random gibberish that doesn't make sense",
        "open the settings menu",
        "uh, well, actually, I need help with...",
    ]
    
    print("Voice Command Processor Test")
    print("=" * 40)
    
    for text in test_inputs:
        result = process_voice_command(text)
        print(f"\nInput: '{text}'")
        print(f"Cleaned: '{result['cleaned']}'")
        print(f"Command: {result['type']} (confidence: {result['confidence']:.2f})")
        if result['suggestions']:
            print(f"Response: {result['suggestions'][0]}")
        print(f"Valid: {is_valid_voice_command(text)}")
