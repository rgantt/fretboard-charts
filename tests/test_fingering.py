"""
Test suite for fingering module.

Tests the guitar fingering representation, validation, and scoring system.
"""

import pytest
from src.fingering import (
    Fingering, FingerAssignment, FingeringValidator
)
from src.fretboard import FretPosition, Fretboard
from src.music_theory import Note, Chord, ChordQuality


class TestFingerAssignment:
    """Test cases for FingerAssignment enum"""
    
    def test_finger_assignment_values(self):
        """Test finger assignment enum values"""
        assert FingerAssignment.MUTED.value == -1
        assert FingerAssignment.OPEN.value == 0
        assert FingerAssignment.INDEX.value == 1
        assert FingerAssignment.MIDDLE.value == 2
        assert FingerAssignment.RING.value == 3
        assert FingerAssignment.PINKY.value == 4


class TestFingering:
    """Test cases for Fingering class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Create a simple C major chord fingering
        self.c_major_positions = [
            FretPosition(string=6, fret=0, note=Note.from_name("E")),  # Low E open
            FretPosition(string=5, fret=3, note=Note.from_name("C")),  # A string, 3rd fret (C)
            FretPosition(string=4, fret=2, note=Note.from_name("E")),  # D string, 2nd fret (E)
            FretPosition(string=3, fret=0, note=Note.from_name("G")),  # G string open
            FretPosition(string=2, fret=1, note=Note.from_name("C")),  # B string, 1st fret (C)
            FretPosition(string=1, fret=0, note=Note.from_name("E")),  # High E open
        ]
        
        self.finger_assignments = {
            6: FingerAssignment.OPEN,
            5: FingerAssignment.RING,
            4: FingerAssignment.MIDDLE,
            3: FingerAssignment.OPEN,
            2: FingerAssignment.INDEX,
            1: FingerAssignment.OPEN,
        }
        
        self.c_major_chord = Chord(
            root=Note.from_name("C"),
            quality=ChordQuality.MAJOR
        )
    
    def test_fingering_creation(self):
        """Test creating a basic fingering"""
        fingering = Fingering(
            positions=self.c_major_positions,
            finger_assignments=self.finger_assignments,
            chord=self.c_major_chord
        )
        
        assert len(fingering.positions) == 6
        assert fingering.chord == self.c_major_chord
        assert fingering.difficulty > 0.0  # Should have some calculated difficulty
    
    def test_fingering_characteristics_calculation(self):
        """Test automatic calculation of fingering characteristics"""
        fingering = Fingering(
            positions=self.c_major_positions,
            finger_assignments=self.finger_assignments,
            chord=self.c_major_chord
        )
        
        # Check calculated characteristics
        assert fingering.characteristics['num_notes'] == 6
        assert fingering.characteristics['num_open_strings'] == 3
        assert fingering.characteristics['num_fretted_notes'] == 3
        assert fingering.characteristics['min_fret'] == 1
        assert fingering.characteristics['max_fret'] == 3
        assert fingering.characteristics['fret_span'] == 2  # 3 - 1 = 2
        assert fingering.characteristics['is_open_position'] == True
        assert fingering.characteristics['has_open_strings'] == True
    
    def test_get_chord_shape(self):
        """Test converting fingering to chord shape"""
        fingering = Fingering(
            positions=self.c_major_positions[:3],  # Only first 3 positions
            finger_assignments=self.finger_assignments
        )
        
        shape = fingering.get_chord_shape()
        
        # Should be a list of 6 elements
        assert len(shape) == 6
        
        # Check specific positions (remember shape is from string 6 to string 1)
        assert shape[0] == 0   # String 6 - open
        assert shape[1] == 3   # String 5 - 3rd fret
        assert shape[2] == 2   # String 4 - 2nd fret
        assert shape[3] is None  # String 3 - not in this fingering
        assert shape[4] is None  # String 2 - not in this fingering
        assert shape[5] is None  # String 1 - not in this fingering
    
    def test_get_notes(self):
        """Test getting all notes in fingering"""
        fingering = Fingering(
            positions=self.c_major_positions,
            finger_assignments=self.finger_assignments
        )
        
        notes = fingering.get_notes()
        assert len(notes) == 6
        
        # Should contain C, E, G (C major chord tones)
        note_names = {note.name for note in notes}
        assert 'C' in note_names
        assert 'E' in note_names
        assert 'G' in note_names
    
    def test_get_bass_note(self):
        """Test getting the bass note (lowest string played)"""
        fingering = Fingering(
            positions=self.c_major_positions,
            finger_assignments=self.finger_assignments
        )
        
        bass_note = fingering.get_bass_note()
        # Bass note should be from string 6 (lowest/thickest string)
        assert bass_note.name == "E"
    
    def test_contains_notes(self):
        """Test checking if fingering contains required notes"""
        fingering = Fingering(
            positions=self.c_major_positions,
            finger_assignments=self.finger_assignments
        )
        
        # Should contain C major chord tones
        c_e_g = [Note.from_name("C"), Note.from_name("E"), Note.from_name("G")]
        assert fingering.contains_notes(c_e_g)
        
        # Should not contain F
        c_e_g_f = c_e_g + [Note.from_name("F")]
        assert not fingering.contains_notes(c_e_g_f)
    
    def test_barre_chord_detection(self):
        """Test detection of barre chords"""
        # Create a barre chord (F major)
        f_major_positions = [
            FretPosition(string=6, fret=1, note=Note.from_name("F")),
            FretPosition(string=5, fret=1, note=Note.from_name("A#")),
            FretPosition(string=4, fret=3, note=Note.from_name("F")),
            FretPosition(string=3, fret=3, note=Note.from_name("A#")),
            FretPosition(string=2, fret=2, note=Note.from_name("C")),
            FretPosition(string=1, fret=1, note=Note.from_name("F")),
        ]
        
        barre_assignments = {
            6: FingerAssignment.INDEX,  # Barre across 1st fret
            5: FingerAssignment.INDEX,  # Part of barre
            4: FingerAssignment.RING,
            3: FingerAssignment.PINKY,
            2: FingerAssignment.MIDDLE,
            1: FingerAssignment.INDEX,  # Part of barre
        }
        
        barre_fingering = Fingering(
            positions=f_major_positions,
            finger_assignments=barre_assignments
        )
        
        assert barre_fingering.characteristics['is_barre_chord'] == True
    
    def test_difficulty_calculation(self):
        """Test difficulty calculation for different fingerings"""
        # Simple open chord (should be easier)
        simple_fingering = Fingering(
            positions=self.c_major_positions,
            finger_assignments=self.finger_assignments
        )
        
        # Complex high-fret chord (should be harder)
        complex_positions = [
            FretPosition(string=6, fret=10, note=Note.from_name("D")),
            FretPosition(string=5, fret=12, note=Note.from_name("E")),
            FretPosition(string=4, fret=14, note=Note.from_name("F#")),
        ]
        
        complex_fingering = Fingering(
            positions=complex_positions,
            finger_assignments={6: FingerAssignment.INDEX, 5: FingerAssignment.RING, 4: FingerAssignment.PINKY}
        )
        
        # Complex fingering should have higher difficulty
        assert complex_fingering.difficulty > simple_fingering.difficulty
    
    def test_invalid_fingering_validation(self):
        """Test validation of invalid fingerings"""
        # Test invalid string number
        with pytest.raises(ValueError):
            invalid_positions = [
                FretPosition(string=7, fret=0, note=Note.from_name("E"))  # Invalid string
            ]
            Fingering(positions=invalid_positions)
        
        # Test muted string with position
        with pytest.raises(ValueError):
            Fingering(
                positions=[FretPosition(string=1, fret=0, note=Note.from_name("E"))],
                muted_strings={1}  # String 1 can't be both played and muted
            )
    
    def test_empty_fingering(self):
        """Test handling of empty fingering"""
        empty_fingering = Fingering(positions=[])
        
        assert empty_fingering.characteristics['num_notes'] == 0
        assert empty_fingering.difficulty == 0.0
        assert empty_fingering.get_bass_note() is None
        assert not empty_fingering.is_playable()
    
    def test_string_representation(self):
        """Test string representation of fingering"""
        fingering = Fingering(
            positions=self.c_major_positions,
            finger_assignments=self.finger_assignments,
            chord=self.c_major_chord
        )
        
        fingering_str = str(fingering)
        assert "C" in fingering_str  # Should show chord name
        assert "difficulty" in fingering_str.lower()


class TestFingeringValidator:
    """Test cases for FingeringValidator class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.validator = FingeringValidator()
        self.fretboard = Fretboard()
        
        # Create a good fingering (C major)
        self.good_positions = [
            FretPosition(string=5, fret=3, note=Note.from_name("C")),
            FretPosition(string=4, fret=2, note=Note.from_name("E")),
            FretPosition(string=3, fret=0, note=Note.from_name("G")),
        ]
        
        self.good_fingering = Fingering(
            positions=self.good_positions,
            finger_assignments={5: FingerAssignment.RING, 4: FingerAssignment.MIDDLE, 3: FingerAssignment.OPEN}
        )
    
    def test_validate_good_fingering(self):
        """Test validation of a good fingering"""
        result = self.validator.validate_fingering(self.good_fingering)
        
        assert result['is_valid'] == True
        assert result['is_playable'] == True
        assert result['score'] > 0.5  # Should have decent score
        assert len(result['issues']) == 0
    
    def test_validate_empty_fingering(self):
        """Test validation of empty fingering"""
        empty_fingering = Fingering(positions=[])
        result = self.validator.validate_fingering(empty_fingering)
        
        assert result['is_valid'] == False
        assert "No positions specified" in result['issues']
    
    def test_validate_large_fret_span(self):
        """Test validation of fingering with large fret span"""
        # Create fingering with large fret span
        large_span_positions = [
            FretPosition(string=6, fret=1, note=Note.from_name("F")),
            FretPosition(string=1, fret=8, note=Note.from_name("C")),  # 7 fret span
        ]
        
        large_span_fingering = Fingering(
            positions=large_span_positions,
            finger_assignments={6: FingerAssignment.INDEX, 1: FingerAssignment.PINKY}
        )
        
        result = self.validator.validate_fingering(large_span_fingering)
        
        assert result['is_playable'] == False
        assert any("span" in issue.lower() for issue in result['issues'])
    
    def test_validate_high_fret_position(self):
        """Test validation of high fret positions"""
        high_fret_positions = [
            FretPosition(string=1, fret=20, note=Note.from_name("G")),
        ]
        
        high_fret_fingering = Fingering(
            positions=high_fret_positions,
            finger_assignments={1: FingerAssignment.INDEX}
        )
        
        result = self.validator.validate_fingering(high_fret_fingering)
        
        # Should still be playable but with warnings
        assert result['is_playable'] == True
        assert len(result['warnings']) > 0
    
    def test_rank_fingerings(self):
        """Test ranking multiple fingerings"""
        # Create several fingerings with different characteristics
        easy_fingering = Fingering(
            positions=[FretPosition(string=3, fret=0, note=Note.from_name("G"))],
            finger_assignments={3: FingerAssignment.OPEN}
        )
        
        medium_fingering = self.good_fingering
        
        hard_positions = [
            FretPosition(string=6, fret=1, note=Note.from_name("F")),
            FretPosition(string=5, fret=1, note=Note.from_name("A#")),
            FretPosition(string=4, fret=3, note=Note.from_name("F")),
            FretPosition(string=3, fret=3, note=Note.from_name("A#")),
        ]
        
        hard_fingering = Fingering(
            positions=hard_positions,
            finger_assignments={
                6: FingerAssignment.INDEX,
                5: FingerAssignment.INDEX,  # Barre
                4: FingerAssignment.RING,
                3: FingerAssignment.PINKY,
            }
        )
        
        fingerings = [hard_fingering, easy_fingering, medium_fingering]
        ranked = self.validator.rank_fingerings(fingerings)
        
        # Easy should come first, hard should come last
        assert ranked[0] == easy_fingering
        assert ranked[-1] == hard_fingering
    
    def test_musical_quality_validation(self):
        """Test musical quality aspects of validation"""
        # Create fingering with good bass note
        c_chord = Chord(root=Note.from_name("C"), quality=ChordQuality.MAJOR)
        
        good_bass_fingering = Fingering(
            positions=[
                FretPosition(string=6, fret=0, note=Note.from_name("E")),  # E in bass
                FretPosition(string=4, fret=2, note=Note.from_name("E")),
                FretPosition(string=3, fret=0, note=Note.from_name("G")),
            ],
            chord=c_chord,
            finger_assignments={6: FingerAssignment.OPEN, 4: FingerAssignment.MIDDLE, 3: FingerAssignment.OPEN}
        )
        
        result = self.validator.validate_fingering(good_bass_fingering)
        
        # Should have good score despite non-root bass note
        assert result['is_valid'] == True
        assert result['is_playable'] == True
    
    def test_slash_chord_validation(self):
        """Test validation of slash chord fingerings"""
        # Create C/E chord (C major with E in bass)
        c_over_e = Chord(
            root=Note.from_name("C"),
            quality=ChordQuality.MAJOR,
            bass=Note.from_name("E")
        )
        
        slash_fingering = Fingering(
            positions=[
                FretPosition(string=6, fret=0, note=Note.from_name("E")),  # E in bass (correct)
                FretPosition(string=4, fret=2, note=Note.from_name("E")),
                FretPosition(string=3, fret=0, note=Note.from_name("G")),
            ],
            chord=c_over_e,
            finger_assignments={6: FingerAssignment.OPEN, 4: FingerAssignment.MIDDLE, 3: FingerAssignment.OPEN}
        )
        
        result = self.validator.validate_fingering(slash_fingering)
        
        # Should validate well since bass note matches specified bass
        assert result['is_valid'] == True
        assert result['score'] > 0.7


class TestFingeringIntegration:
    """Integration tests combining fingering with other modules"""
    
    def test_fingering_with_chord_intervals(self):
        """Test creating fingering from chord intervals"""
        # Create D minor chord
        dm_chord = Chord(root=Note.from_name("D"), quality=ChordQuality.MINOR)
        dm_intervals = dm_chord.get_intervals()  # [0, 3, 7] for minor chord
        
        # Create a fingering that contains these intervals
        dm_positions = [
            FretPosition(string=4, fret=0, note=Note.from_name("D")),  # Root
            FretPosition(string=3, fret=2, note=Note.from_name("A")),  # 5th
            FretPosition(string=2, fret=3, note=Note.from_name("D")),  # Root (octave)
            FretPosition(string=1, fret=1, note=Note.from_name("F")),  # Minor 3rd
        ]
        
        dm_fingering = Fingering(
            positions=dm_positions,
            chord=dm_chord,
            finger_assignments={
                4: FingerAssignment.OPEN,
                3: FingerAssignment.MIDDLE,
                2: FingerAssignment.RING,
                1: FingerAssignment.INDEX
            }
        )
        
        # Verify the fingering contains the chord tones
        chord_notes = dm_chord.get_notes()
        assert dm_fingering.contains_notes(chord_notes)
        
        # Should be a reasonable difficulty
        assert 0.0 <= dm_fingering.difficulty <= 1.0
    
    def test_fretboard_fingering_interaction(self):
        """Test interaction between fretboard and fingering modules"""
        fretboard = Fretboard()
        
        # Get positions for A major chord notes
        a_chord = Chord(root=Note.from_name("A"), quality=ChordQuality.MAJOR)
        chord_notes = a_chord.get_notes()
        
        positions_dict = fretboard.get_positions_for_notes(chord_notes, max_fret=5)
        
        # Should find positions for A, C#, E
        assert len(positions_dict) >= 3
        
        # Create a fingering using some of these positions
        selected_positions = []
        for note, positions in positions_dict.items():
            if positions:  # Take first available position for each note
                selected_positions.append(positions[0])
        
        if len(selected_positions) >= 3:
            a_fingering = Fingering(
                positions=selected_positions[:3],  # Take first 3
                chord=a_chord
            )
            
            # Should be valid
            assert len(a_fingering.positions) == 3
            assert a_fingering.contains_notes(chord_notes[:3])


if __name__ == "__main__":
    pytest.main([__file__])
