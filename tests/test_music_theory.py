"""
Test suite for music theory module.

Tests the core musical building blocks including Note, Chord, and interval calculations.
"""

import pytest
from src.music_theory import Note, Chord, ChordQuality, calculate_interval_semitones, notes_in_key


class TestNote:
    """Test cases for the Note class"""
    
    def test_note_creation_from_name(self):
        """Test creating notes from string names"""
        c = Note.from_name("C")
        assert c.pitch_class == 0
        assert c.name == "C"
        
        f_sharp = Note.from_name("F#")
        assert f_sharp.pitch_class == 6
        assert f_sharp.name == "F#"
        
        b_flat = Note.from_name("Bb")
        assert b_flat.pitch_class == 10
        assert b_flat.name == "Bb"
    
    def test_enharmonic_equivalents(self):
        """Test that enharmonic notes have same pitch class"""
        f_sharp = Note.from_name("F#")
        g_flat = Note.from_name("Gb")
        assert f_sharp.pitch_class == g_flat.pitch_class
        
        c_sharp = Note.from_name("C#")
        d_flat = Note.from_name("Db")
        assert c_sharp.pitch_class == d_flat.pitch_class
    
    def test_invalid_note_names(self):
        """Test that invalid note names raise errors"""
        with pytest.raises(ValueError):
            Note.from_name("H")  # Invalid note name
        
        with pytest.raises(ValueError):
            Note.from_name("C##")  # Double sharp not supported
        
        with pytest.raises(ValueError):
            Note.from_name("")  # Empty string
    
    def test_interval_calculation(self):
        """Test interval calculation between notes"""
        c = Note.from_name("C")
        e = Note.from_name("E")
        g = Note.from_name("G")
        
        assert c.interval_to(e) == 4  # Major third
        assert c.interval_to(g) == 7  # Perfect fifth
        assert e.interval_to(c) == 8  # Descending interval wraps around
    
    def test_transposition(self):
        """Test note transposition"""
        c = Note.from_name("C")
        
        # Test upward transposition
        e = c.transpose(4)
        assert e.pitch_class == 4
        
        # Test downward transposition
        a = c.transpose(-3)
        assert a.pitch_class == 9
        
        # Test octave transposition
        c_octave = c.transpose(12)
        assert c_octave.pitch_class == 0
    
    def test_note_string_representation(self):
        """Test string representation of notes"""
        c = Note.from_name("C")
        assert str(c) == "C"
        assert repr(c) == "Note(C)"


class TestChord:
    """Test cases for the Chord class"""
    
    def test_major_chord_intervals(self):
        """Test major chord interval calculation"""
        c_major = Chord(
            root=Note.from_name("C"),
            quality=ChordQuality.MAJOR
        )
        
        intervals = c_major.get_intervals()
        assert intervals == [0, 4, 7]  # Root, major third, perfect fifth
    
    def test_minor_chord_intervals(self):
        """Test minor chord interval calculation"""
        d_minor = Chord(
            root=Note.from_name("D"),
            quality=ChordQuality.MINOR
        )
        
        intervals = d_minor.get_intervals()
        assert intervals == [0, 3, 7]  # Root, minor third, perfect fifth
    
    def test_dominant_seventh_chord(self):
        """Test dominant seventh chord intervals"""
        g7 = Chord(
            root=Note.from_name("G"),
            quality=ChordQuality.DOMINANT_SEVENTH
        )
        
        intervals = g7.get_intervals()
        assert intervals == [0, 4, 7, 10]  # Root, maj3, P5, min7
    
    def test_major_seventh_chord(self):
        """Test major seventh chord intervals"""
        cmaj7 = Chord(
            root=Note.from_name("C"),
            quality=ChordQuality.MAJOR_SEVENTH
        )
        
        intervals = cmaj7.get_intervals()
        assert intervals == [0, 4, 7, 11]  # Root, maj3, P5, maj7
    
    def test_half_diminished_chord(self):
        """Test half-diminished chord intervals"""
        dm7b5 = Chord(
            root=Note.from_name("D"),
            quality=ChordQuality.HALF_DIMINISHED
        )
        
        intervals = dm7b5.get_intervals()
        assert intervals == [0, 3, 6, 10]  # Root, min3, dim5, min7
    
    def test_chord_with_extensions(self):
        """Test chord with extensions"""
        c9 = Chord(
            root=Note.from_name("C"),
            quality=ChordQuality.DOMINANT_SEVENTH,
            extensions=[9]
        )
        
        intervals = c9.get_intervals()
        assert 2 in intervals  # 9th = 2nd + octave
        assert 10 in intervals  # Has 7th
    
    def test_chord_with_added_tones(self):
        """Test chord with added tones"""
        cadd9 = Chord(
            root=Note.from_name("C"),
            quality=ChordQuality.MAJOR,
            added_tones=[9]
        )
        
        intervals = cadd9.get_intervals()
        assert intervals == [0, 2, 4, 7]  # Root, 9th, 3rd, 5th (sorted)
    
    def test_chord_with_alterations(self):
        """Test chord with alterations"""
        c7sharp5 = Chord(
            root=Note.from_name("C"),
            quality=ChordQuality.DOMINANT_SEVENTH,
            alterations={5: "#"}
        )
        
        intervals = c7sharp5.get_intervals()
        # #5 becomes interval 8 (7 + 1 = 8) - G# from C
        assert 8 in intervals  # #5 (augmented 5th)
        assert 7 not in intervals  # Original 5th removed
    
    def test_slash_chord(self):
        """Test slash chord with bass note"""
        c_over_e = Chord(
            root=Note.from_name("C"),
            quality=ChordQuality.MAJOR,
            bass=Note.from_name("E")
        )
        
        assert c_over_e.bass.name == "E"
        # Intervals should be same as regular C major
        intervals = c_over_e.get_intervals()
        assert intervals == [0, 4, 7]
    
    def test_chord_notes_generation(self):
        """Test getting actual notes from chord"""
        c_major = Chord(
            root=Note.from_name("C"),
            quality=ChordQuality.MAJOR
        )
        
        notes = c_major.get_notes()
        note_names = [note.name for note in notes]
        
        # Should contain C, E, G
        assert len(notes) == 3
        assert "C" in note_names
        # Note: Exact names depend on transposition logic
    
    def test_chord_string_representation(self):
        """Test chord string representation"""
        c_major = Chord(
            root=Note.from_name("C"),
            quality=ChordQuality.MAJOR
        )
        assert "C" in str(c_major)
        
        dm7 = Chord(
            root=Note.from_name("D"),
            quality=ChordQuality.MINOR_SEVENTH
        )
        chord_str = str(dm7)
        assert "D" in chord_str
        assert "m7" in chord_str or "min7" in chord_str


class TestSusChords:
    """Test suspended chords"""
    
    def test_sus2_chord(self):
        """Test sus2 chord intervals"""
        csus2 = Chord(
            root=Note.from_name("C"),
            quality=ChordQuality.SUSPENDED_SECOND
        )
        
        intervals = csus2.get_intervals()
        assert intervals == [0, 2, 7]  # Root, 2nd, 5th
    
    def test_sus4_chord(self):
        """Test sus4 chord intervals"""
        csus4 = Chord(
            root=Note.from_name("C"),
            quality=ChordQuality.SUSPENDED_FOURTH
        )
        
        intervals = csus4.get_intervals()
        assert intervals == [0, 5, 7]  # Root, 4th, 5th


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_interval_calculations(self):
        """Test interval name to semitone conversion"""
        assert calculate_interval_semitones("P1") == 0
        assert calculate_interval_semitones("M3") == 4
        assert calculate_interval_semitones("P5") == 7
        assert calculate_interval_semitones("m7") == 10
        assert calculate_interval_semitones("M7") == 11
    
    def test_invalid_intervals(self):
        """Test invalid interval names"""
        with pytest.raises(ValueError):
            calculate_interval_semitones("X5")
    
    def test_major_scale(self):
        """Test major scale generation"""
        c_major_notes = notes_in_key(Note.from_name("C"), "major")
        
        assert len(c_major_notes) == 7
        
        # Check that we get the right intervals
        intervals = [Note.from_name("C").interval_to(note) for note in c_major_notes]
        expected_intervals = [0, 2, 4, 5, 7, 9, 11]  # Major scale pattern
        assert intervals == expected_intervals
    
    def test_minor_scale(self):
        """Test natural minor scale generation"""
        a_minor_notes = notes_in_key(Note.from_name("A"), "minor")
        
        assert len(a_minor_notes) == 7
        
        # Check intervals for natural minor
        intervals = [Note.from_name("A").interval_to(note) for note in a_minor_notes]
        expected_intervals = [0, 2, 3, 5, 7, 8, 10]  # Natural minor pattern
        assert intervals == expected_intervals


if __name__ == "__main__":
    pytest.main([__file__])
