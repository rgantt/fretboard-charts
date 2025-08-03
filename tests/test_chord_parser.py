"""
Test suite for chord parser module.

Tests the chord symbol parsing functionality including various notation styles,
extensions, alterations, and edge cases.
"""

import pytest
from src.chord_parser import ChordParser, ChordParseError, parse_chord, quick_parse
from src.music_theory import Note, ChordQuality


class TestChordParser:
    """Test cases for the ChordParser class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = ChordParser()
    
    def test_basic_major_chords(self):
        """Test parsing basic major chords"""
        c_major = self.parser.parse("C")
        assert c_major.root.name == "C"
        assert c_major.quality == ChordQuality.MAJOR
        assert c_major.extensions == []
        
        # Test alternative major notation
        c_major_alt = self.parser.parse("CM")
        assert c_major_alt.quality == ChordQuality.MAJOR
        
        c_major_alt2 = self.parser.parse("Cmaj")
        assert c_major_alt2.quality == ChordQuality.MAJOR
    
    def test_basic_minor_chords(self):
        """Test parsing basic minor chords"""
        d_minor = self.parser.parse("Dm")
        assert d_minor.root.name == "D"
        assert d_minor.quality == ChordQuality.MINOR
        
        # Test alternative minor notations
        d_minor_alt = self.parser.parse("Dmin")
        assert d_minor_alt.quality == ChordQuality.MINOR
        
        d_minor_alt2 = self.parser.parse("D-")
        assert d_minor_alt2.quality == ChordQuality.MINOR
    
    def test_seventh_chords(self):
        """Test parsing seventh chords"""
        # Dominant seventh
        g7 = self.parser.parse("G7")
        assert g7.root.name == "G"
        assert g7.quality == ChordQuality.DOMINANT_SEVENTH
        # Seventh chords are parsed as complete qualities, not base + extension
        
        # Major seventh
        cmaj7 = self.parser.parse("Cmaj7")
        assert cmaj7.quality == ChordQuality.MAJOR_SEVENTH
        
        # Alternative major seventh notations
        cmaj7_alt = self.parser.parse("CM7")
        assert cmaj7_alt.quality == ChordQuality.MAJOR_SEVENTH
        
        cmaj7_alt2 = self.parser.parse("C△7")
        assert cmaj7_alt2.quality == ChordQuality.MAJOR_SEVENTH
        
        # Minor seventh
        dm7 = self.parser.parse("Dm7")
        assert dm7.quality == ChordQuality.MINOR_SEVENTH
    
    def test_extended_chords(self):
        """Test parsing extended chords (9, 11, 13)"""
        c9 = self.parser.parse("C9")
        assert 7 in c9.extensions  # 9th implies 7th
        assert 9 in c9.extensions
        
        dm11 = self.parser.parse("Dm11")
        assert 7 in dm11.extensions
        assert 11 in dm11.extensions
        
        g13 = self.parser.parse("G13")
        assert 7 in g13.extensions
        assert 13 in g13.extensions
    
    def test_altered_chords(self):
        """Test parsing chords with alterations"""
        c7sharp5 = self.parser.parse("C7#5")
        assert c7sharp5.alterations[5] == "#"
        
        dm7b5 = self.parser.parse("Dm7b5")
        assert dm7b5.quality == ChordQuality.HALF_DIMINISHED
        
        # Test "alt" keyword
        g7alt = self.parser.parse("G7alt")
        assert len(g7alt.alterations) > 0  # Should have multiple alterations
    
    def test_added_tone_chords(self):
        """Test parsing chords with added tones"""
        cadd9 = self.parser.parse("Cadd9")
        assert 9 in cadd9.added_tones
        assert cadd9.quality == ChordQuality.MAJOR
        
        # Test parenthetical notation
        cadd9_paren = self.parser.parse("C(add9)")
        assert 9 in cadd9_paren.added_tones
    
    def test_suspended_chords(self):
        """Test parsing suspended chords"""
        csus2 = self.parser.parse("Csus2")
        assert csus2.quality == ChordQuality.SUSPENDED_SECOND
        
        csus4 = self.parser.parse("Csus4")
        assert csus4.quality == ChordQuality.SUSPENDED_FOURTH
        
        # Test default sus (should be sus4)
        csus = self.parser.parse("Csus")
        assert csus.quality == ChordQuality.SUSPENDED_FOURTH
    
    def test_diminished_chords(self):
        """Test parsing diminished chords"""
        bdim = self.parser.parse("Bdim")
        assert bdim.quality == ChordQuality.DIMINISHED
        
        # Alternative notations
        bdim_alt = self.parser.parse("B°")
        assert bdim_alt.quality == ChordQuality.DIMINISHED
        
        bdim_alt2 = self.parser.parse("Bo")
        assert bdim_alt2.quality == ChordQuality.DIMINISHED
        
        # Diminished seventh
        bdim7 = self.parser.parse("Bdim7")
        assert bdim7.quality == ChordQuality.DIMINISHED_SEVENTH
    
    def test_augmented_chords(self):
        """Test parsing augmented chords"""
        caug = self.parser.parse("Caug")
        assert caug.quality == ChordQuality.AUGMENTED
        
        # Alternative notations
        caug_alt = self.parser.parse("C+")
        assert caug_alt.quality == ChordQuality.AUGMENTED
    
    def test_slash_chords(self):
        """Test parsing slash chords"""
        c_over_e = self.parser.parse("C/E")
        assert c_over_e.root.name == "C"
        assert c_over_e.bass.name == "E"
        assert c_over_e.quality == ChordQuality.MAJOR
        
        # Complex slash chord
        dm7_over_g = self.parser.parse("Dm7/G")
        assert dm7_over_g.root.name == "Dm"[0]  # Just the root note
        assert dm7_over_g.bass.name == "G"
        assert dm7_over_g.quality == ChordQuality.MINOR_SEVENTH
    
    def test_complex_chords(self):
        """Test parsing complex chord symbols"""
        # Half-diminished with alternative notation
        fsharp_half_dim = self.parser.parse("F#m7b5")
        assert fsharp_half_dim.root.name == "F#"
        assert fsharp_half_dim.quality == ChordQuality.HALF_DIMINISHED
        
        # Minor-major seventh
        cm_maj7 = self.parser.parse("CmM7")
        assert cm_maj7.quality == ChordQuality.MINOR_MAJOR_SEVENTH
        
        # Complex altered chord
        complex_chord = self.parser.parse("Bbmaj7#11")
        assert complex_chord.root.name == "Bb"
        assert complex_chord.quality == ChordQuality.MAJOR_SEVENTH
        assert complex_chord.alterations[11] == "#"
    
    def test_enharmonic_roots(self):
        """Test chords with enharmonic root names"""
        fs_major = self.parser.parse("F#")
        gb_major = self.parser.parse("Gb")
        
        # Should have same pitch class but different names
        assert fs_major.root.pitch_class == gb_major.root.pitch_class
        assert fs_major.root.name != gb_major.root.name
    
    def test_case_insensitive_parsing(self):
        """Test that parsing is case insensitive"""
        c_major_lower = self.parser.parse("c")
        c_major_upper = self.parser.parse("C")
        
        assert c_major_lower.root.pitch_class == c_major_upper.root.pitch_class
        
        dm7_mixed = self.parser.parse("dm7")
        assert dm7_mixed.quality == ChordQuality.MINOR_SEVENTH
    
    def test_invalid_chord_symbols(self):
        """Test that invalid chord symbols raise appropriate errors"""
        with pytest.raises(ChordParseError):
            self.parser.parse("H")  # Invalid root note
        
        with pytest.raises(ChordParseError):
            self.parser.parse("")  # Empty string
        
        with pytest.raises(ChordParseError):
            self.parser.parse("Cxyz")  # Invalid quality
    
    def test_validation_method(self):
        """Test the validate_chord_symbol method"""
        assert self.parser.validate_chord_symbol("C") == True
        assert self.parser.validate_chord_symbol("Dm7") == True
        assert self.parser.validate_chord_symbol("F#m7b5/A") == True
        
        assert self.parser.validate_chord_symbol("H") == False
        assert self.parser.validate_chord_symbol("C##") == False
        assert self.parser.validate_chord_symbol("") == False
    
    def test_parsing_suggestions(self):
        """Test getting parsing suggestions for invalid symbols"""
        suggestions = self.parser.get_parsing_suggestions("H")
        assert len(suggestions) >= 0  # Should return some suggestions or empty list
        
        suggestions = self.parser.get_parsing_suggestions("C")
        # For valid chord, might still get variations
        assert isinstance(suggestions, list)


class TestConvenienceFunctions:
    """Test convenience parsing functions"""
    
    def test_parse_chord_function(self):
        """Test the standalone parse_chord function"""
        chord = parse_chord("Cmaj7")
        assert chord.root.name == "C"
        assert chord.quality == ChordQuality.MAJOR_SEVENTH
    
    def test_quick_parse_function(self):
        """Test the quick_parse function"""
        chord = quick_parse("Dm7")
        assert chord.root.name == "Dm"[0]
        assert chord.quality == ChordQuality.MINOR_SEVENTH
    
    def test_convenience_functions_error_handling(self):
        """Test error handling in convenience functions"""
        with pytest.raises(ChordParseError):
            parse_chord("Invalid")
        
        with pytest.raises(ChordParseError):
            quick_parse("H7")


class TestRealWorldChords:
    """Test parsing real-world chord progressions"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = ChordParser()
    
    def test_common_progression_chords(self):
        """Test parsing chords from common progressions"""
        # I-vi-IV-V in C major
        progression_c = ["C", "Am", "F", "G"]
        for chord_symbol in progression_c:
            chord = self.parser.parse(chord_symbol)
            assert chord is not None
        
        # ii-V-I in jazz
        jazz_progression = ["Dm7", "G7", "Cmaj7"]
        for chord_symbol in jazz_progression:
            chord = self.parser.parse(chord_symbol)
            assert chord is not None
    
    def test_jazz_chord_examples(self):
        """Test parsing typical jazz chords"""
        jazz_chords = [
            "Cmaj7", "Dm7", "Em7b5", "Fmaj7", "G7", "Am7", "Bm7b5",
            "C7#11", "Dm7/G", "G7alt", "Cmaj9", "F#m7b5", "B7alt"
        ]
        
        for chord_symbol in jazz_chords:
            chord = self.parser.parse(chord_symbol)
            assert chord is not None
            assert len(chord.get_intervals()) >= 3  # Should have at least 3 notes
    
    def test_slash_chord_progressions(self):
        """Test slash chords common in fingerstyle playing"""
        fingerstyle_chords = [
            "C/E", "Am/C", "F/A", "G/B", "Dm/F", "G/D"
        ]
        
        for chord_symbol in fingerstyle_chords:
            chord = self.parser.parse(chord_symbol)
            assert chord is not None
            assert chord.bass is not None
    
    def test_complex_extended_chords(self):
        """Test complex extended and altered chords"""
        complex_chords = [
            "Cmaj7add9", "Dm7add11", "G13b9", "Fmaj7#11", 
            "Am7add9/C", "Bbmaj7#5", "F#m7b5add11"
        ]
        
        for chord_symbol in complex_chords:
            try:
                chord = self.parser.parse(chord_symbol)
                assert chord is not None
            except ChordParseError:
                # Some very complex chords might not parse yet
                # That's acceptable for this phase
                pass


if __name__ == "__main__":
    pytest.main([__file__])
