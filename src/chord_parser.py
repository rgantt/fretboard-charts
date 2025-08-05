"""
Chord symbol parser for converting chord names to structured Chord objects.

This module handles parsing of chord symbols like:
- Basic chords: C, Dm, G7
- Extensions: Cmaj7, Dm9, G13
- Alterations: C7#5, Dm7b5, G7alt
- Added tones: Cadd9, Dm(add11)
- Slash chords: C/E, Dm7/G
- Complex symbols: F#m7b5, Bbmaj7#11, Am7add9/C
"""

import re
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass

from .music_theory import Note, Chord, ChordQuality


@dataclass
class ParsedChordComponents:
    """Intermediate representation of parsed chord components"""
    root: str
    quality: str = ""
    extensions: List[str] = None
    alterations: List[str] = None
    added_tones: List[str] = None
    bass: str = ""
    
    def __post_init__(self):
        if self.extensions is None:
            self.extensions = []
        if self.alterations is None:
            self.alterations = []
        if self.added_tones is None:
            self.added_tones = []


class ChordParseError(Exception):
    """Raised when a chord symbol cannot be parsed"""
    pass


class ChordParser:
    """
    Parses chord symbols into structured Chord objects.
    
    Supports a wide variety of chord notation including:
    - Standard notation: C, Dm, G7, Cmaj7
    - Alternative spellings: CM7, C△7, Cma7
    - Extensions: C9, Dm11, G13
    - Alterations: C7#5, Dm7b5, G7alt
    - Added tones: Cadd9, Dm(add11)
    - Slash chords: C/E, Dm7/G
    """
    
    # Quality mappings for different notation styles
    QUALITY_MAPPINGS = {
        # Major variants
        '': ChordQuality.MAJOR,
        'M': ChordQuality.MAJOR,
        'maj': ChordQuality.MAJOR,
        'major': ChordQuality.MAJOR,
        '△': ChordQuality.MAJOR,
        
        # Minor variants
        'm': ChordQuality.MINOR,
        'min': ChordQuality.MINOR,
        'minor': ChordQuality.MINOR,
        '-': ChordQuality.MINOR,
        
        # Diminished variants
        'dim': ChordQuality.DIMINISHED,
        '°': ChordQuality.DIMINISHED,
        'o': ChordQuality.DIMINISHED,
        
        # Augmented variants
        'aug': ChordQuality.AUGMENTED,
        '+': ChordQuality.AUGMENTED,
        '#5': ChordQuality.AUGMENTED,
        
        # Seventh chords
        '7': ChordQuality.DOMINANT_SEVENTH,
        'dom7': ChordQuality.DOMINANT_SEVENTH,
        
        'M7': ChordQuality.MAJOR_SEVENTH,
        'maj7': ChordQuality.MAJOR_SEVENTH,
        'ma7': ChordQuality.MAJOR_SEVENTH,
        '△7': ChordQuality.MAJOR_SEVENTH,
        
        'm7': ChordQuality.MINOR_SEVENTH,
        'min7': ChordQuality.MINOR_SEVENTH,
        '-7': ChordQuality.MINOR_SEVENTH,
        
        'dim7': ChordQuality.DIMINISHED_SEVENTH,
        '°7': ChordQuality.DIMINISHED_SEVENTH,
        'o7': ChordQuality.DIMINISHED_SEVENTH,
        
        'm7b5': ChordQuality.HALF_DIMINISHED,
        'ø': ChordQuality.HALF_DIMINISHED,
        'ø7': ChordQuality.HALF_DIMINISHED,
        'min7b5': ChordQuality.HALF_DIMINISHED,
        
        'mM7': ChordQuality.MINOR_MAJOR_SEVENTH,
        'mMaj7': ChordQuality.MINOR_MAJOR_SEVENTH,
        'm△7': ChordQuality.MINOR_MAJOR_SEVENTH,
        
        # Suspended chords
        'sus2': ChordQuality.SUSPENDED_SECOND,
        'sus4': ChordQuality.SUSPENDED_FOURTH,
        'sus': ChordQuality.SUSPENDED_FOURTH,  # Default sus is sus4
        
        # Sixth chords
        '6': ChordQuality.SIXTH,
        'add6': ChordQuality.SIXTH,
        'm6': ChordQuality.MINOR_SIXTH,
        'min6': ChordQuality.MINOR_SIXTH,
        
        # Ninth chords  
        '9': ChordQuality.NINTH,
        'add9': ChordQuality.NINTH,
        'm9': ChordQuality.MINOR_NINTH,
        'min9': ChordQuality.MINOR_NINTH,
        'M9': ChordQuality.MAJOR_NINTH,
        'maj9': ChordQuality.MAJOR_NINTH,
        '△9': ChordQuality.MAJOR_NINTH,
    }
    
    def __init__(self):
        """Initialize the chord parser with regex patterns"""
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for parsing chord symbols"""
        
        # Root note pattern (handles sharps, flats, and enharmonics)
        # More restrictive to only allow valid note names
        root_pattern = r'[A-G][#b]?'
        
        # Quality pattern (handles various notations) - filter out empty string and escape special chars
        quality_keys = [k for k in self.QUALITY_MAPPINGS.keys() if k]  # Remove empty string
        quality_options = '|'.join(sorted(quality_keys, key=len, reverse=True))
        # Escape special regex characters
        quality_options = quality_options.replace('°', r'°').replace('△', r'△').replace('+', r'\+') 
        quality_pattern = f'({quality_options})?'
        
        # Extension pattern (7, 9, 11, 13)
        extension_pattern = r'(\d+)?'
        
        # Alteration pattern (#5, b9, #11, etc.)
        alteration_pattern = r'([#b]\d+)*'
        
        # Added tone pattern (add9, add11, etc.)
        add_pattern = r'(add\d+|\(add\d+\))*'
        
        # Alternative patterns
        alt_pattern = r'(alt)?'
        
        # Bass note pattern for slash chords
        bass_pattern = f'(?:/({root_pattern}))?'
        
        # Complete chord pattern
        self.chord_pattern = re.compile(
            f'^({root_pattern}){quality_pattern}{extension_pattern}{alteration_pattern}{add_pattern}{alt_pattern}{bass_pattern}$',
            re.IGNORECASE
        )
        
        # Specific patterns for complex parsing
        self.alteration_sub_pattern = re.compile(r'([#b])(\d+)', re.IGNORECASE)
        self.add_sub_pattern = re.compile(r'add(\d+)|\(add(\d+)\)', re.IGNORECASE)
    
    def parse(self, chord_symbol: str) -> Chord:
        """
        Parse a chord symbol string into a Chord object.
        
        Args:
            chord_symbol: String representation of chord (e.g., "Cmaj7", "Dm7/G")
        
        Returns:
            Chord object representing the parsed chord
        
        Raises:
            ChordParseError: If the chord symbol cannot be parsed
        """
        if not chord_symbol or not isinstance(chord_symbol, str):
            raise ChordParseError("Chord symbol must be a non-empty string")
        
        # Clean the input
        chord_symbol = chord_symbol.strip()
        
        # Try to match the chord pattern
        match = self.chord_pattern.match(chord_symbol)
        if not match:
            raise ChordParseError(f"Cannot parse chord symbol: {chord_symbol}")
        
        try:
            components = self._extract_components(match, chord_symbol)
            return self._build_chord(components)
        except Exception as e:
            raise ChordParseError(f"Error parsing '{chord_symbol}': {str(e)}")
    
    def _extract_components(self, match: re.Match, original: str) -> ParsedChordComponents:
        """Extract chord components from regex match"""
        groups = match.groups()
        
        root = groups[0] if groups[0] else ""
        quality = groups[1] if groups[1] else ""
        extension = groups[2] if groups[2] else ""
        alterations_str = groups[3] if groups[3] else ""
        add_str = groups[4] if groups[4] else ""
        alt_str = groups[5] if groups[5] else ""
        bass = groups[6] if groups[6] else ""
        
        # Parse alterations
        alterations = []
        if alterations_str:
            for alt_match in self.alteration_sub_pattern.finditer(alterations_str):
                alteration = alt_match.group(1) + alt_match.group(2)
                alterations.append(alteration)
        
        # Handle "alt" keyword (shorthand for altered dominant)
        if alt_str.lower() == 'alt':
            alterations.extend(['b9', '#9', '#11', 'b13'])
        
        # Parse added tones
        added_tones = []
        if add_str:
            for add_match in self.add_sub_pattern.finditer(add_str):
                # Handle both add9 and (add9) formats
                tone = add_match.group(1) or add_match.group(2)
                if tone:
                    added_tones.append(tone)
        
        # Handle extensions (9, 11, 13 imply 7th)
        extensions = []
        if extension:
            ext_num = int(extension)
            if ext_num in [9, 11, 13]:
                extensions.append(7)  # Implied 7th
                extensions.append(ext_num)
            elif ext_num == 7:
                extensions.append(7)
        
        return ParsedChordComponents(
            root=root,
            quality=quality,
            extensions=extensions,
            alterations=alterations,
            added_tones=added_tones,
            bass=bass
        )
    
    def _build_chord(self, components: ParsedChordComponents) -> Chord:
        """Build a Chord object from parsed components"""
        
        # Parse root note
        try:
            root_note = Note.from_name(components.root)
        except ValueError as e:
            raise ChordParseError(f"Invalid root note: {components.root}")
        
        # Determine chord quality
        chord_quality = self._determine_quality(components)
        
        # Parse bass note for slash chords
        bass_note = None
        if components.bass:
            try:
                bass_note = Note.from_name(components.bass)
            except ValueError as e:
                raise ChordParseError(f"Invalid bass note: {components.bass}")
        
        # Process alterations
        alterations = {}
        for alt_str in components.alterations:
            interval, alteration = self._parse_alteration(alt_str)
            alterations[interval] = alteration
        
        # Process added tones
        added_tones = []
        for add_str in components.added_tones:
            try:
                added_tones.append(int(add_str))
            except ValueError:
                raise ChordParseError(f"Invalid added tone: {add_str}")
        
        return Chord(
            root=root_note,
            quality=chord_quality,
            extensions=components.extensions,
            alterations=alterations,
            bass=bass_note,
            added_tones=added_tones
        )
    
    def _determine_quality(self, components: ParsedChordComponents) -> ChordQuality:
        """Determine the chord quality from components"""
        
        quality_str = components.quality
        
        # Check for explicit seventh chord qualities first
        if quality_str in self.QUALITY_MAPPINGS:
            mapped_quality = self.QUALITY_MAPPINGS[quality_str]
            # If it's already a seventh chord quality, use it
            if mapped_quality in [ChordQuality.DOMINANT_SEVENTH, ChordQuality.MAJOR_SEVENTH, 
                                 ChordQuality.MINOR_SEVENTH, ChordQuality.DIMINISHED_SEVENTH,
                                 ChordQuality.HALF_DIMINISHED, ChordQuality.MINOR_MAJOR_SEVENTH]:
                return mapped_quality
        
        # Handle cases where extension implies seventh chord quality
        if 7 in components.extensions:
            if quality_str == '' or quality_str == '7':
                return ChordQuality.DOMINANT_SEVENTH
            elif quality_str in ['M', 'maj', 'major', '△']:
                return ChordQuality.MAJOR_SEVENTH
            elif quality_str in ['m', 'min', 'minor', '-']:
                return ChordQuality.MINOR_SEVENTH
            elif quality_str == 'dim':
                return ChordQuality.DIMINISHED_SEVENTH
            elif quality_str in ['m7b5', 'ø']:
                return ChordQuality.HALF_DIMINISHED
            elif quality_str in ['mM7', 'mMaj7', 'm△7']:
                return ChordQuality.MINOR_MAJOR_SEVENTH
        
        # Use quality mapping for basic qualities
        if quality_str in self.QUALITY_MAPPINGS:
            return self.QUALITY_MAPPINGS[quality_str]
        
        # Default to major if no quality specified
        return ChordQuality.MAJOR
    
    def _parse_alteration(self, alt_str: str) -> Tuple[int, str]:
        """Parse an alteration string like '#5' or 'b9'"""
        if len(alt_str) < 2:
            raise ChordParseError(f"Invalid alteration: {alt_str}")
        
        alteration_type = alt_str[0]  # '#' or 'b'
        try:
            interval = int(alt_str[1:])
        except ValueError:
            raise ChordParseError(f"Invalid alteration interval: {alt_str}")
        
        if alteration_type not in ['#', 'b']:
            raise ChordParseError(f"Invalid alteration type: {alteration_type}")
        
        return interval, alteration_type
    
    def validate_chord_symbol(self, chord_symbol: str) -> bool:
        """
        Validate if a chord symbol can be parsed without raising an exception.
        
        Args:
            chord_symbol: String to validate
        
        Returns:
            True if the symbol can be parsed, False otherwise
        """
        try:
            self.parse(chord_symbol)
            return True
        except ChordParseError:
            return False
    
    def get_parsing_suggestions(self, chord_symbol: str) -> List[str]:
        """
        Get suggestions for correcting an invalid chord symbol.
        
        Args:
            chord_symbol: Invalid chord symbol
        
        Returns:
            List of suggested corrections
        """
        suggestions = []
        
        # Common typos and corrections
        common_corrections = {
            'maj': ['M', 'maj7', '△'],
            'min': ['m', 'min7', '-'],
            'dom': ['7', 'dom7'],
            '°': ['dim', 'dim7'],
            'ø': ['m7b5', 'ø7'],
            '+': ['aug', '#5'],
        }
        
        # Try common note name corrections
        if len(chord_symbol) >= 1:
            first_char = chord_symbol[0].upper()
            if first_char in 'ABCDEFG':
                # Try different quality variations
                for quality in ['', 'm', '7', 'maj7', 'm7']:
                    suggestion = first_char + quality
                    if self.validate_chord_symbol(suggestion):
                        suggestions.append(suggestion)
        
        return suggestions[:5]  # Return top 5 suggestions


# Convenience function for direct parsing
def parse_chord(chord_symbol: str) -> Chord:
    """
    Convenience function to parse a chord symbol.
    
    Args:
        chord_symbol: String representation of chord
    
    Returns:
        Chord object
    
    Raises:
        ChordParseError: If parsing fails
    """
    parser = ChordParser()
    return parser.parse(chord_symbol)


# Pre-defined parser instance for efficiency
_default_parser = ChordParser()

def quick_parse(chord_symbol: str) -> Chord:
    """Quick parsing using a pre-initialized parser instance"""
    return _default_parser.parse(chord_symbol)
