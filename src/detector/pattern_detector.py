#!/usr/bin/env python3
"""
Pattern Detector for Screen Privacy Blocker
Detects sensitive information patterns in text using regex and entropy analysis
"""

import re
import math
from typing import Dict, List

class PatternDetector:
    """Detects sensitive information patterns in text"""
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
        
    def _initialize_patterns(self) -> Dict[str, Dict]:
        """Initialize regex patterns for different types of sensitive information"""
        return {
            'aws_access_key': {
                'pattern': r'AKIA[0-9A-Z]{16}',
                'description': 'AWS Access Key',
                'confidence': 0.95
            },
            'github_token': {
                'pattern': r'ghp_[A-Za-z0-9]{36}',
                'description': 'GitHub Personal Access Token',
                'confidence': 0.95
            },
            'google_api_key': {
                'pattern': r'AIza[0-9A-Za-z-_]{35}',
                'description': 'Google API Key',
                'confidence': 0.95
            },
            'stripe_key': {
                'pattern': r'sk_(test|live)_[A-Za-z0-9]{24}',
                'description': 'Stripe API Key',
                'confidence': 0.95
            },
            'jwt_token': {
                'pattern': r'eyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+',
                'description': 'JWT Token',
                'confidence': 0.90
            },
            'credit_card': {
                'pattern': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
                'description': 'Credit Card Number',
                'confidence': 0.80
            },
            'phone_number': {
                'pattern': r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
                'description': 'Phone Number',
                'confidence': 0.75
            },
            'email': {
                'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'description': 'Email Address',
                'confidence': 0.70
            },
            'ssn': {
                'pattern': r'\b\d{3}-\d{2}-\d{4}\b',
                'description': 'Social Security Number',
                'confidence': 0.90
            },
            'bitcoin_address': {
                'pattern': r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b',
                'description': 'Bitcoin Address',
                'confidence': 0.85
            },
            'ethereum_address': {
                'pattern': r'\b0x[a-fA-F0-9]{40}\b',
                'description': 'Ethereum Address',
                'confidence': 0.90
            },
            'api_key_generic': {
                'pattern': r'(?:api[_-]?key|apikey|access[_-]?key|secret[_-]?key)\s*[:=]\s*["\']?([A-Za-z0-9\-._~+/]+=*)["\']?',
                'description': 'Generic API Key',
                'confidence': 0.70
            }
        }
    
    def detect_patterns(self, text: str) -> List[Dict]:
        """
        Detect sensitive patterns in text
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of detected patterns with metadata
        """
        detections = []
        
        # Check against known patterns
        for pattern_name, pattern_info in self.patterns.items():
            matches = re.finditer(pattern_info['pattern'], text, re.IGNORECASE)
            
            for match in matches:
                detections.append({
                    'text': match.group(0),
                    'type': pattern_info['description'],
                    'confidence': pattern_info['confidence'],
                    'start': match.start(),
                    'end': match.end(),
                    'pattern_name': pattern_name
                })
        
        # Check for high-entropy strings (potential secrets)
        entropy_detections = self._detect_high_entropy_strings(text)
        detections.extend(entropy_detections)
        
        # Remove duplicates and overlapping detections
        detections = self._deduplicate_detections(detections)
        
        return detections
    
    def _detect_high_entropy_strings(self, text: str) -> List[Dict]:
        """Detect high-entropy strings that might be secrets"""
        detections = []
        
        # Look for strings that might be secrets (high entropy, reasonable length)
        words = re.findall(r'\b[A-Za-z0-9+/=]{20,}\b', text)
        
        for word in words:
            entropy = self._calculate_entropy(word)
            if entropy > 3.5 and len(word) >= 20:  # High entropy threshold
                detections.append({
                    'text': word,
                    'type': 'High Entropy String',
                    'confidence': min(0.8, entropy / 5.0),  # Scale confidence
                    'start': text.find(word),
                    'end': text.find(word) + len(word),
                    'pattern_name': 'high_entropy'
                })
        
        return detections
    
    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of a string"""
        if not text:
            return 0
        
        # Count character frequencies
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Calculate entropy
        entropy = 0
        text_len = len(text)
        for count in char_counts.values():
            probability = count / text_len
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _deduplicate_detections(self, detections: List[Dict]) -> List[Dict]:
        """Remove duplicate and overlapping detections"""
        if not detections:
            return []
        
        # Sort by start position
        detections.sort(key=lambda x: x['start'])
        
        # Remove overlaps
        filtered = [detections[0]]
        for detection in detections[1:]:
            last_detection = filtered[-1]
            
            # If no overlap, add the detection
            if detection['start'] >= last_detection['end']:
                filtered.append(detection)
            # If overlap, keep the one with higher confidence
            elif detection['confidence'] > last_detection['confidence']:
                filtered[-1] = detection
        
        return filtered
