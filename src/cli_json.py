#!/usr/bin/env python3
"""
Command-line JSON interface for guitar chord tools
This provides a simple way to call the chord generation functions and get JSON output
"""

import sys
import json
import argparse
import base64
from pathlib import Path

# Import our core functionality
try:
    from .fingering_generator import generate_chord_fingerings
    from .diagram_generator import generate_chord_diagram
    from .music_theory import Chord
    from .chord_parser import parse_chord
    from .fingering import Fingering
    from .fretboard import FretPosition, Fretboard
except ImportError:
    # Try relative imports
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent))
        from fingering_generator import generate_chord_fingerings
        from diagram_generator import generate_chord_diagram
        from music_theory import Chord
        from chord_parser import parse_chord
        from fingering import Fingering
        from fretboard import FretPosition, Fretboard
    except ImportError as e:
        print(f"Error: Could not import required modules: {e}", file=sys.stderr)
        sys.exit(1)


def format_fingering_for_json(fingering):
    """Format a Fingering object for JSON output"""
    try:
        return {
            "positions": [{"string": pos.string, "fret": pos.fret} for pos in fingering.positions],
            "fingering_pattern": str(fingering),
            "difficulty": round(fingering.difficulty, 3),
            "characteristics": {
                "is_barre_chord": fingering.characteristics.get("is_barre_chord", False),
                "span": fingering.characteristics.get("span", 0),
                "hand_position": fingering.characteristics.get("hand_position", "unknown"),
                "requires_muting": len([pos for pos in fingering.positions if pos.fret == -1]) > 0
            },
            "finger_assignments": {
                str(string): finger.name if hasattr(finger, 'name') else str(finger)
                for string, finger in (fingering.finger_assignments or {}).items()
            },
            "chord_name": str(fingering.chord) if fingering.chord else "Unknown"
        }
    except Exception as e:
        return {
            "error": f"Failed to format fingering: {str(e)}",
            "positions": [],
            "fingering_pattern": "Error",
            "difficulty": 1.0
        }


def cmd_generate_fingerings(args):
    """Generate chord fingerings"""
    try:
        fingerings = generate_chord_fingerings(
            args.chord_symbol, 
            max_results=args.max_results
        )
        
        # Filter by difficulty if specified
        if args.difficulty_filter is not None:
            fingerings = [f for f in fingerings if f.difficulty <= args.difficulty_filter]
        
        result = {
            "chord_symbol": args.chord_symbol,
            "total_fingerings": len(fingerings),
            "fingerings": [format_fingering_for_json(f) for f in fingerings]
        }
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


def cmd_create_diagram(args):
    """Create chord diagram"""
    try:
        fingering = None
        
        if args.chord_symbol:
            # Generate fingering from chord symbol
            fingerings = generate_chord_fingerings(args.chord_symbol, max_results=1)
            if not fingerings:
                print(json.dumps({"error": f"No fingerings found for chord '{args.chord_symbol}'"}), file=sys.stderr)
                sys.exit(1)
            fingering = fingerings[0]
            chord_name = args.chord_symbol
            
        else:
            print(json.dumps({"error": "chord_symbol is required"}), file=sys.stderr)
            sys.exit(1)
        
        # Generate diagram
        image_bytes = generate_chord_diagram(fingering, format=args.format)
        
        if not image_bytes:
            print(json.dumps({"error": "Failed to generate diagram"}), file=sys.stderr)
            sys.exit(1)
        
        # Encode as base64
        base64_data = base64.b64encode(image_bytes).decode('utf-8')
        
        result = {
            "chord_name": chord_name,
            "format": args.format,
            "image_data": base64_data,
            "mime_type": f"image/{args.format}"
        }
        
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Guitar Chord Generator CLI (JSON output)")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate fingerings command
    gen_parser = subparsers.add_parser('generate_chord_fingerings', help='Generate chord fingerings')
    gen_parser.add_argument('chord_symbol', help='Chord symbol (e.g., C, Am7, F#m7b5)')
    gen_parser.add_argument('--max_results', type=int, default=5, help='Maximum number of results')
    gen_parser.add_argument('--difficulty_filter', type=float, help='Maximum difficulty (0.0-1.0)')
    
    # Create diagram command
    diag_parser = subparsers.add_parser('create_chord_diagram', help='Create chord diagram')
    diag_parser.add_argument('--chord_symbol', required=True, help='Chord symbol')
    diag_parser.add_argument('--format', choices=['png', 'svg'], default='png', help='Output format')
    diag_parser.add_argument('--include_name', type=bool, default=True, help='Include chord name')
    
    args = parser.parse_args()
    
    if args.command == 'generate_chord_fingerings':
        cmd_generate_fingerings(args)
    elif args.command == 'create_chord_diagram':
        cmd_create_diagram(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()