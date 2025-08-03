#!/usr/bin/env python3
"""
Debug script to check chord parser regex matching
"""

import sys
sys.path.append('src')

from src.chord_parser import ChordParser

def debug_chord_parsing():
    parser = ChordParser()
    
    test_chords = ["G7", "Cmaj7", "Dm7", "C", "H", "C##7", ""]
    
    for chord_symbol in test_chords:
        print(f"\n=== Testing: {chord_symbol} ===")
        
        # Test regex match
        match = parser.chord_pattern.match(chord_symbol)
        if match:
            print(f"Regex groups: {match.groups()}")
            
            try:
                components = parser._extract_components(match, chord_symbol)
                print(f"Parsed components:")
                print(f"  Root: '{components.root}'")
                print(f"  Quality: '{components.quality}'")
                print(f"  Extensions: {components.extensions}")
                print(f"  Alterations: {components.alterations}")
                print(f"  Bass: '{components.bass}'")
                
                chord = parser._build_chord(components)
                print(f"Final chord: {chord}")
                print(f"Extensions: {chord.extensions}")
                print(f"Quality: {chord.quality}")
                
            except Exception as e:
                print(f"Error building chord: {e}")
        else:
            print("No regex match!")
            
            # Try to parse anyway to see what error we get
            try:
                chord = parser.parse(chord_symbol)
                print(f"Somehow parsed: {chord}")
            except Exception as e:
                print(f"Parse error: {e}")

if __name__ == "__main__":
    debug_chord_parsing()
