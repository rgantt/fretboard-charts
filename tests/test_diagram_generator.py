"""
Test suite for visual chord diagram generation.

Tests the diagram generation functionality including image creation,
layout calculation, and integration with fingering objects.
"""

import pytest
import tempfile
import os
from pathlib import Path

from src.diagram_generator import (
    ChordDiagramGenerator, DiagramStyle, generate_chord_diagram,
    generate_chord_progression_diagram
)
from src.fingering_generator import generate_chord_fingerings
from src.music_theory import Chord, ChordQuality, Note
from src.chord_parser import quick_parse


class TestDiagramStyle:
    """Test diagram style configuration"""
    
    def test_default_style(self):
        """Test default style configuration"""
        style = DiagramStyle()
        
        assert style.width == 2.0
        assert style.height == 2.5
        assert style.num_frets == 4
        assert style.grid_color == '#000000'
        assert style.background_color == '#ffffff'
    
    def test_custom_style(self):
        """Test custom style configuration"""
        style = DiagramStyle(
            width=3.0,
            height=3.5,
            grid_color='#333333',
            dot_color='#ff0000'
        )
        
        assert style.width == 3.0
        assert style.height == 3.5
        assert style.grid_color == '#333333'
        assert style.dot_color == '#ff0000'


class TestChordDiagramGenerator:
    """Test the main diagram generator class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.generator = ChordDiagramGenerator()
        
        # Create some test fingerings
        self.c_major_fingerings = generate_chord_fingerings('C', max_results=1)
        self.g_major_fingerings = generate_chord_fingerings('G', max_results=1)
        self.am_fingerings = generate_chord_fingerings('Am', max_results=1)
        
        assert len(self.c_major_fingerings) > 0
        assert len(self.g_major_fingerings) > 0
        assert len(self.am_fingerings) > 0
    
    def test_generator_initialization(self):
        """Test generator initialization"""
        generator = ChordDiagramGenerator()
        assert generator.style is not None
        assert isinstance(generator.style, DiagramStyle)
        
        # Test with custom style
        custom_style = DiagramStyle(width=3.0)
        generator = ChordDiagramGenerator(custom_style)
        assert generator.style.width == 3.0
    
    def test_calculate_diagram_layout_open_position(self):
        """Test layout calculation for open position chords"""
        fingering = self.c_major_fingerings[0]
        layout = self.generator._calculate_diagram_layout(fingering)
        
        assert 'start_fret' in layout
        assert 'display_frets' in layout
        assert 'grid_left' in layout
        assert 'grid_right' in layout
        assert 'string_positions' in layout
        assert 'fret_positions' in layout
        
        # Should be open position for C major
        assert layout['start_fret'] == 0
        assert len(layout['string_positions']) == 6
        assert len(layout['fret_positions']) >= 4
    
    def test_calculate_diagram_layout_higher_position(self):
        """Test layout calculation for higher position chords"""
        # Generate a chord that should be in higher position
        fm_fingerings = generate_chord_fingerings('F', max_results=1)
        if fm_fingerings:
            fingering = fm_fingerings[0]
            layout = self.generator._calculate_diagram_layout(fingering)
            
            # Layout should be calculated correctly
            assert layout['start_fret'] >= 0
            assert layout['display_frets'] >= 4
    
    def test_generate_diagram_bytes(self):
        """Test generating diagram as bytes"""
        fingering = self.c_major_fingerings[0]
        
        # Generate as bytes
        image_bytes = self.generator.generate_diagram(fingering, format='png')
        
        assert image_bytes is not None
        assert len(image_bytes) > 1000  # Should be substantial image data
        assert image_bytes.startswith(b'\x89PNG')  # PNG header
    
    def test_generate_diagram_file(self):
        """Test generating diagram to file"""
        fingering = self.c_major_fingerings[0]
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            try:
                # Generate to file
                result = self.generator.generate_diagram(fingering, 
                                                       output_path=tmp_file.name,
                                                       format='png')
                
                assert result is None  # Should return None when saving to file
                assert os.path.exists(tmp_file.name)
                assert os.path.getsize(tmp_file.name) > 1000  # Should have content
                
            finally:
                if os.path.exists(tmp_file.name):
                    os.unlink(tmp_file.name)
    
    def test_generate_multiple_diagrams(self):
        """Test generating multiple diagrams in a grid"""
        fingerings = [
            self.c_major_fingerings[0],
            self.g_major_fingerings[0],
            self.am_fingerings[0]
        ]
        
        # Generate as bytes
        image_bytes = self.generator.generate_multiple_diagrams(fingerings, cols=3)
        
        assert image_bytes is not None
        assert len(image_bytes) > 3000  # Should be larger than single diagram
        assert image_bytes.startswith(b'\x89PNG')  # PNG header
    
    def test_generate_multiple_diagrams_file(self):
        """Test generating multiple diagrams to file"""
        fingerings = [
            self.c_major_fingerings[0],
            self.g_major_fingerings[0]
        ]
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            try:
                result = self.generator.generate_multiple_diagrams(
                    fingerings, 
                    output_path=tmp_file.name,
                    cols=2
                )
                
                assert result is None
                assert os.path.exists(tmp_file.name)
                assert os.path.getsize(tmp_file.name) > 2000  # Should be larger
                
            finally:
                if os.path.exists(tmp_file.name):
                    os.unlink(tmp_file.name)
    
    def test_different_formats(self):
        """Test generating diagrams in different formats"""
        fingering = self.c_major_fingerings[0]
        
        # Test PNG
        png_bytes = self.generator.generate_diagram(fingering, format='png')
        assert png_bytes.startswith(b'\x89PNG')
        
        # Test SVG
        svg_bytes = self.generator.generate_diagram(fingering, format='svg')
        assert b'<svg' in svg_bytes
        assert b'</svg>' in svg_bytes
    
    def test_empty_fingering_list(self):
        """Test handling empty fingering list"""
        result = self.generator.generate_multiple_diagrams([])
        assert result is None


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    def test_generate_chord_diagram_function(self):
        """Test the convenience function for single diagrams"""
        fingerings = generate_chord_fingerings('G', max_results=1)
        assert len(fingerings) > 0
        
        fingering = fingerings[0]
        image_bytes = generate_chord_diagram(fingering)
        
        assert image_bytes is not None
        assert len(image_bytes) > 1000
        assert image_bytes.startswith(b'\x89PNG')
    
    def test_generate_chord_diagram_with_file(self):
        """Test convenience function saving to file"""
        fingerings = generate_chord_fingerings('Am', max_results=1)
        fingering = fingerings[0]
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            try:
                result = generate_chord_diagram(fingering, output_path=tmp_file.name)
                
                assert result is None
                assert os.path.exists(tmp_file.name)
                assert os.path.getsize(tmp_file.name) > 1000
                
            finally:
                if os.path.exists(tmp_file.name):
                    os.unlink(tmp_file.name)
    
    def test_generate_chord_progression_diagram(self):
        """Test generating diagrams for chord progressions"""
        progression = ['C', 'Am', 'F', 'G']
        
        image_bytes = generate_chord_progression_diagram(progression)
        
        assert image_bytes is not None
        assert len(image_bytes) > 4000  # Should be substantial for 4 chords
        assert image_bytes.startswith(b'\x89PNG')
    
    def test_generate_chord_progression_with_file(self):
        """Test chord progression generation to file"""
        progression = ['G', 'Em', 'C', 'D']
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            try:
                result = generate_chord_progression_diagram(
                    progression, 
                    output_path=tmp_file.name,
                    cols=4
                )
                
                assert result is None
                assert os.path.exists(tmp_file.name)
                assert os.path.getsize(tmp_file.name) > 4000
                
            finally:
                if os.path.exists(tmp_file.name):
                    os.unlink(tmp_file.name)
    
    def test_generate_chord_progression_empty(self):
        """Test handling empty chord progression"""
        result = generate_chord_progression_diagram([])
        assert result is None
    
    def test_generate_chord_progression_multiple_fingerings(self):
        """Test chord progression with multiple fingerings per chord"""
        progression = ['C', 'G']
        
        image_bytes = generate_chord_progression_diagram(
            progression, 
            max_fingerings_per_chord=2
        )
        
        assert image_bytes is not None
        assert len(image_bytes) > 2000  # Should be substantial for multiple fingerings


class TestIntegration:
    """Integration tests with other modules"""
    
    def test_integration_with_fingering_generator(self):
        """Test integration with fingering generator"""
        # Generate fingerings and create diagrams
        chord_symbols = ['C', 'Dm', 'G7', 'Am']
        
        for chord_symbol in chord_symbols:
            fingerings = generate_chord_fingerings(chord_symbol, max_results=1)
            assert len(fingerings) > 0
            
            fingering = fingerings[0]
            image_bytes = generate_chord_diagram(fingering)
            
            assert image_bytes is not None
            assert len(image_bytes) > 1000
    
    def test_standard_chord_diagrams(self):
        """Test that standard chords generate reasonable diagrams"""
        standard_chords = [
            ('C', 'x-3-2-0-1-0'),
            ('G', '3-2-0-0-3-3'),
            ('Am', 'x-0-2-2-1-0'),
            ('Em', '0-2-2-0-0-0'),
            ('Dm', 'x-x-0-2-3-1')
        ]
        
        for chord_name, expected_shape in standard_chords:
            fingerings = generate_chord_fingerings(chord_name, max_results=1)
            assert len(fingerings) > 0
            
            fingering = fingerings[0]
            
            # Verify it's the expected standard fingering
            actual_shape = '-'.join([str(f) if f is not None else 'x' 
                                   for f in fingering.get_chord_shape()])
            assert actual_shape == expected_shape, \
                f"Expected {expected_shape} for {chord_name}, got {actual_shape}"
            
            # Generate diagram
            image_bytes = generate_chord_diagram(fingering)
            assert image_bytes is not None
            assert len(image_bytes) > 1000
    
    def test_different_chord_types(self):
        """Test diagrams for different chord types"""
        test_chords = [
            'C',          # Major
            'Am',         # Minor
            'G7',         # Dominant 7th
            'Cmaj7',      # Major 7th
            'Dm7',        # Minor 7th
            'Cadd9'       # Added tone
        ]
        
        for chord_name in test_chords:
            fingerings = generate_chord_fingerings(chord_name, max_results=1)
            
            if fingerings:  # Some complex chords might not have fingerings yet
                fingering = fingerings[0]
                image_bytes = generate_chord_diagram(fingering)
                
                assert image_bytes is not None
                assert len(image_bytes) > 1000


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_format(self):
        """Test handling of invalid format"""
        fingerings = generate_chord_fingerings('C', max_results=1)
        fingering = fingerings[0]
        
        generator = ChordDiagramGenerator()
        
        # This should still work - matplotlib handles most formats gracefully
        try:
            image_bytes = generator.generate_diagram(fingering, format='invalidformat')
            # If it doesn't raise an error, that's fine too
        except Exception:
            # Expected behavior for invalid format
            pass
    
    def test_fingering_without_chord(self):
        """Test handling fingering without chord information"""
        from src.fretboard import FretPosition
        from src.fingering import Fingering
        from src.music_theory import Note
        
        # Create a fingering without chord info
        positions = [
            FretPosition(string=5, fret=3, note=Note.from_name("C")),
            FretPosition(string=4, fret=2, note=Note.from_name("E")),
            FretPosition(string=3, fret=0, note=Note.from_name("G"))
        ]
        
        fingering = Fingering(positions=positions)  # No chord specified
        
        # Should still generate diagram
        image_bytes = generate_chord_diagram(fingering)
        assert image_bytes is not None
        assert len(image_bytes) > 1000


if __name__ == "__main__":
    pytest.main([__file__])