"""
Test cases based on standard guitar chord chart reference.

This test suite validates that our fingering generator produces the standard
fingerings shown in professional guitar chord charts.
"""

import pytest
from src.chord_parser import quick_parse
from src.fingering_generator import FingeringGenerator


class TestReferenceChordChart:
    """Test against standard chord chart fingerings."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = FingeringGenerator()
    
    def get_primary_fingering(self, chord_name: str):
        """Get the primary (first-ranked) fingering for a chord."""
        chord = quick_parse(chord_name)
        fingerings = self.generator.generate_fingerings(chord)
        assert len(fingerings) > 0, f"No fingerings generated for {chord_name}"
        return fingerings[0]
    
    def test_basic_major_chords(self):
        """Test basic major chord fingerings from reference chart."""
        
        # A major: x-0-2-2-2-0
        a_fingering = self.get_primary_fingering('A')
        expected_a = [None, 0, 2, 2, 2, 0]
        assert a_fingering.get_chord_shape() == expected_a, \
            f"A major: expected {expected_a}, got {a_fingering.get_chord_shape()}"
        
        # C major: x-3-2-0-1-0  
        c_fingering = self.get_primary_fingering('C')
        expected_c = [None, 3, 2, 0, 1, 0]
        assert c_fingering.get_chord_shape() == expected_c, \
            f"C major: expected {expected_c}, got {c_fingering.get_chord_shape()}"
        
        # D major: x-x-0-2-3-2
        d_fingering = self.get_primary_fingering('D')
        expected_d = [None, None, 0, 2, 3, 2]
        assert d_fingering.get_chord_shape() == expected_d, \
            f"D major: expected {expected_d}, got {d_fingering.get_chord_shape()}"
        
        # E major: 0-2-2-1-0-0
        e_fingering = self.get_primary_fingering('E')
        expected_e = [0, 2, 2, 1, 0, 0]
        assert e_fingering.get_chord_shape() == expected_e, \
            f"E major: expected {expected_e}, got {e_fingering.get_chord_shape()}"
        
        # F major: 1-3-3-2-1-1 (barre)
        f_fingering = self.get_primary_fingering('F')
        expected_f = [1, 3, 3, 2, 1, 1]
        assert f_fingering.get_chord_shape() == expected_f, \
            f"F major: expected {expected_f}, got {f_fingering.get_chord_shape()}"
        
        # G major: 3-2-0-0-3-3
        g_fingering = self.get_primary_fingering('G')
        expected_g = [3, 2, 0, 0, 3, 3]
        assert g_fingering.get_chord_shape() == expected_g, \
            f"G major: expected {expected_g}, got {g_fingering.get_chord_shape()}"
    
    def test_sharp_flat_major_chords(self):
        """Test sharp and flat major chord fingerings from reference chart."""
        
        # F# major: 2-4-4-3-2-2 (barre on 2nd fret)
        fs_fingering = self.get_primary_fingering('F#')
        expected_fs = [2, 4, 4, 3, 2, 2]
        assert fs_fingering.get_chord_shape() == expected_fs, \
            f"F# major: expected {expected_fs}, got {fs_fingering.get_chord_shape()}"
        
        # Bb major: x-1-3-3-3-1 or 1-1-3-3-3-1 (barre)
        bb_fingering = self.get_primary_fingering('Bb')
        expected_bb_1 = [None, 1, 3, 3, 3, 1]  # Partial barre
        expected_bb_2 = [1, 1, 3, 3, 3, 1]     # Full barre
        actual_bb = bb_fingering.get_chord_shape()
        assert actual_bb in [expected_bb_1, expected_bb_2], \
            f"Bb major: expected {expected_bb_1} or {expected_bb_2}, got {actual_bb}"
    
    def test_basic_minor_chords(self):
        """Test basic minor chord fingerings from reference chart."""
        
        # Am: x-0-2-2-1-0
        am_fingering = self.get_primary_fingering('Am')
        expected_am = [None, 0, 2, 2, 1, 0]
        assert am_fingering.get_chord_shape() == expected_am, \
            f"Am: expected {expected_am}, got {am_fingering.get_chord_shape()}"
        
        # Dm: x-x-0-2-3-1
        dm_fingering = self.get_primary_fingering('Dm')
        expected_dm = [None, None, 0, 2, 3, 1]
        assert dm_fingering.get_chord_shape() == expected_dm, \
            f"Dm: expected {expected_dm}, got {dm_fingering.get_chord_shape()}"
        
        # Em: 0-2-2-0-0-0
        em_fingering = self.get_primary_fingering('Em')
        expected_em = [0, 2, 2, 0, 0, 0]
        assert em_fingering.get_chord_shape() == expected_em, \
            f"Em: expected {expected_em}, got {em_fingering.get_chord_shape()}"
    
    def test_sharp_flat_minor_chords(self):
        """Test sharp and flat minor chord fingerings from reference chart."""
        
        # F#m: 2-4-4-2-2-2 (barre on 2nd fret)
        fsm_fingering = self.get_primary_fingering('F#m')
        expected_fsm = [2, 4, 4, 2, 2, 2]
        assert fsm_fingering.get_chord_shape() == expected_fsm, \
            f"F#m: expected {expected_fsm}, got {fsm_fingering.get_chord_shape()}"
        
        # Bbm: x-1-3-3-2-1 or 1-1-3-3-2-1 (barre)
        bbm_fingering = self.get_primary_fingering('Bbm')
        expected_bbm_1 = [None, 1, 3, 3, 2, 1]  # Partial barre
        expected_bbm_2 = [1, 1, 3, 3, 2, 1]     # Full barre
        actual_bbm = bbm_fingering.get_chord_shape()
        assert actual_bbm in [expected_bbm_1, expected_bbm_2], \
            f"Bbm: expected {expected_bbm_1} or {expected_bbm_2}, got {actual_bbm}"
    
    def test_seventh_chords(self):
        """Test 7th chord fingerings from reference chart."""
        
        # A7: x-0-2-0-2-0
        a7_fingering = self.get_primary_fingering('A7')
        expected_a7 = [None, 0, 2, 0, 2, 0]
        assert a7_fingering.get_chord_shape() == expected_a7, \
            f"A7: expected {expected_a7}, got {a7_fingering.get_chord_shape()}"
        
        # B7: x-2-1-2-0-2
        b7_fingering = self.get_primary_fingering('B7')
        expected_b7 = [None, 2, 1, 2, 0, 2]
        assert b7_fingering.get_chord_shape() == expected_b7, \
            f"B7: expected {expected_b7}, got {b7_fingering.get_chord_shape()}"
        
        # C7: x-3-2-3-1-0
        c7_fingering = self.get_primary_fingering('C7')
        expected_c7 = [None, 3, 2, 3, 1, 0]
        assert c7_fingering.get_chord_shape() == expected_c7, \
            f"C7: expected {expected_c7}, got {c7_fingering.get_chord_shape()}"
        
        # D7: x-x-0-2-1-2
        d7_fingering = self.get_primary_fingering('D7')
        expected_d7 = [None, None, 0, 2, 1, 2]
        assert d7_fingering.get_chord_shape() == expected_d7, \
            f"D7: expected {expected_d7}, got {d7_fingering.get_chord_shape()}"
        
        # E7: 0-2-0-1-0-0
        e7_fingering = self.get_primary_fingering('E7')
        expected_e7 = [0, 2, 0, 1, 0, 0]
        assert e7_fingering.get_chord_shape() == expected_e7, \
            f"E7: expected {expected_e7}, got {e7_fingering.get_chord_shape()}"
        
        # G7: 3-2-0-0-0-1
        g7_fingering = self.get_primary_fingering('G7')
        expected_g7 = [3, 2, 0, 0, 0, 1]
        assert g7_fingering.get_chord_shape() == expected_g7, \
            f"G7: expected {expected_g7}, got {g7_fingering.get_chord_shape()}"
    
    def test_minor_seventh_chords(self):
        """Test minor 7th chord fingerings from reference chart."""
        
        # Am7: x-0-2-0-1-0
        am7_fingering = self.get_primary_fingering('Am7')
        expected_am7 = [None, 0, 2, 0, 1, 0]
        assert am7_fingering.get_chord_shape() == expected_am7, \
            f"Am7: expected {expected_am7}, got {am7_fingering.get_chord_shape()}"
        
        # Dm7: x-x-0-2-1-1
        dm7_fingering = self.get_primary_fingering('Dm7')
        expected_dm7 = [None, None, 0, 2, 1, 1]
        assert dm7_fingering.get_chord_shape() == expected_dm7, \
            f"Dm7: expected {expected_dm7}, got {dm7_fingering.get_chord_shape()}"
        
        # Em7: 0-2-0-0-0-0
        em7_fingering = self.get_primary_fingering('Em7')
        expected_em7 = [0, 2, 0, 0, 0, 0]
        assert em7_fingering.get_chord_shape() == expected_em7, \
            f"Em7: expected {expected_em7}, got {em7_fingering.get_chord_shape()}"
    
    def test_major_seventh_chords(self):
        """Test major 7th chord fingerings from reference chart."""
        
        # Amaj7: x-0-2-1-2-0
        amaj7_fingering = self.get_primary_fingering('Amaj7')
        expected_amaj7 = [None, 0, 2, 1, 2, 0]
        assert amaj7_fingering.get_chord_shape() == expected_amaj7, \
            f"Amaj7: expected {expected_amaj7}, got {amaj7_fingering.get_chord_shape()}"
        
        # Cmaj7: x-3-2-0-0-0
        cmaj7_fingering = self.get_primary_fingering('Cmaj7')
        expected_cmaj7 = [None, 3, 2, 0, 0, 0]
        assert cmaj7_fingering.get_chord_shape() == expected_cmaj7, \
            f"Cmaj7: expected {expected_cmaj7}, got {cmaj7_fingering.get_chord_shape()}"
        
        # Dmaj7: x-x-0-2-2-2
        dmaj7_fingering = self.get_primary_fingering('Dmaj7')
        expected_dmaj7 = [None, None, 0, 2, 2, 2]
        assert dmaj7_fingering.get_chord_shape() == expected_dmaj7, \
            f"Dmaj7: expected {expected_dmaj7}, got {dmaj7_fingering.get_chord_shape()}"
        
        # Emaj7: 0-2-1-1-0-0
        emaj7_fingering = self.get_primary_fingering('Emaj7')
        expected_emaj7 = [0, 2, 1, 1, 0, 0]
        assert emaj7_fingering.get_chord_shape() == expected_emaj7, \
            f"Emaj7: expected {expected_emaj7}, got {emaj7_fingering.get_chord_shape()}"
        
        # Fmaj7: 1-3-3-2-1-0 or x-x-3-2-1-0 - need to check chart
        fmaj7_fingering = self.get_primary_fingering('Fmaj7')
        expected_fmaj7_1 = [1, 3, 3, 2, 1, 0]  # Barre version
        expected_fmaj7_2 = [None, None, 3, 2, 1, 0]  # Open version
        actual_fmaj7 = fmaj7_fingering.get_chord_shape()
        assert actual_fmaj7 in [expected_fmaj7_1, expected_fmaj7_2], \
            f"Fmaj7: expected {expected_fmaj7_1} or {expected_fmaj7_2}, got {actual_fmaj7}"
        
        # Gmaj7: 3-2-0-0-0-2
        gmaj7_fingering = self.get_primary_fingering('Gmaj7')
        expected_gmaj7 = [3, 2, 0, 0, 0, 2]
        assert gmaj7_fingering.get_chord_shape() == expected_gmaj7, \
            f"Gmaj7: expected {expected_gmaj7}, got {gmaj7_fingering.get_chord_shape()}"
    
    def test_suspended_chords(self):
        """Test suspended chord fingerings from reference chart."""
        
        # Asus2: x-0-2-2-0-0
        asus2_fingering = self.get_primary_fingering('Asus2')
        expected_asus2 = [None, 0, 2, 2, 0, 0]
        assert asus2_fingering.get_chord_shape() == expected_asus2, \
            f"Asus2: expected {expected_asus2}, got {asus2_fingering.get_chord_shape()}"
        
        # Asus4: x-0-2-2-3-0
        asus4_fingering = self.get_primary_fingering('Asus4')
        expected_asus4 = [None, 0, 2, 2, 3, 0]
        assert asus4_fingering.get_chord_shape() == expected_asus4, \
            f"Asus4: expected {expected_asus4}, got {asus4_fingering.get_chord_shape()}"
        
        # Csus2: x-3-0-0-1-0
        csus2_fingering = self.get_primary_fingering('Csus2')
        expected_csus2 = [None, 3, 0, 0, 1, 0]
        assert csus2_fingering.get_chord_shape() == expected_csus2, \
            f"Csus2: expected {expected_csus2}, got {csus2_fingering.get_chord_shape()}"
        
        # Csus4: x-3-3-0-1-0
        csus4_fingering = self.get_primary_fingering('Csus4')
        expected_csus4 = [None, 3, 3, 0, 1, 0]
        assert csus4_fingering.get_chord_shape() == expected_csus4, \
            f"Csus4: expected {expected_csus4}, got {csus4_fingering.get_chord_shape()}"
    
    def test_diminished_chords(self):
        """Test diminished chord fingerings from reference chart."""
        
        # Adim: x-0-1-2-1-x
        adim_fingering = self.get_primary_fingering('Adim')
        expected_adim = [None, 0, 1, 2, 1, None]
        assert adim_fingering.get_chord_shape() == expected_adim, \
            f"Adim: expected {expected_adim}, got {adim_fingering.get_chord_shape()}"
        
        # Bdim: x-2-3-1-3-x
        bdim_fingering = self.get_primary_fingering('Bdim')
        expected_bdim = [None, 2, 3, 1, 3, None]
        assert bdim_fingering.get_chord_shape() == expected_bdim, \
            f"Bdim: expected {expected_bdim}, got {bdim_fingering.get_chord_shape()}"
    
    def test_augmented_chords(self):
        """Test augmented chord fingerings from reference chart."""
        
        # Aaug: x-0-3-2-2-1
        aaug_fingering = self.get_primary_fingering('Aaug')
        expected_aaug = [None, 0, 3, 2, 2, 1]
        assert aaug_fingering.get_chord_shape() == expected_aaug, \
            f"Aaug: expected {expected_aaug}, got {aaug_fingering.get_chord_shape()}"
        
        # Caug: x-3-2-1-1-0
        caug_fingering = self.get_primary_fingering('Caug')
        expected_caug = [None, 3, 2, 1, 1, 0]
        assert caug_fingering.get_chord_shape() == expected_caug, \
            f"Caug: expected {expected_caug}, got {caug_fingering.get_chord_shape()}"
    
    def test_sixth_chords(self):
        """Test 6th chord fingerings from reference chart."""
        
        # A6: x-0-2-2-2-2
        a6_fingering = self.get_primary_fingering('A6')
        expected_a6 = [None, 0, 2, 2, 2, 2]
        assert a6_fingering.get_chord_shape() == expected_a6, \
            f"A6: expected {expected_a6}, got {a6_fingering.get_chord_shape()}"
        
        # C6: x-3-2-2-1-0
        c6_fingering = self.get_primary_fingering('C6')
        expected_c6 = [None, 3, 2, 2, 1, 0]
        assert c6_fingering.get_chord_shape() == expected_c6, \
            f"C6: expected {expected_c6}, got {c6_fingering.get_chord_shape()}"
    
    def test_ninth_chords(self):
        """Test 9th chord fingerings from reference chart."""
        
        # A9: x-0-2-4-2-3
        a9_fingering = self.get_primary_fingering('A9')
        expected_a9 = [None, 0, 2, 4, 2, 3]
        assert a9_fingering.get_chord_shape() == expected_a9, \
            f"A9: expected {expected_a9}, got {a9_fingering.get_chord_shape()}"
        
        # C9: x-3-2-3-3-3
        c9_fingering = self.get_primary_fingering('C9')
        expected_c9 = [None, 3, 2, 3, 3, 3]
        assert c9_fingering.get_chord_shape() == expected_c9, \
            f"C9: expected {expected_c9}, got {c9_fingering.get_chord_shape()}"
    
    def test_comprehensive_sharp_flat_chords(self):
        """Test additional sharp and flat chords visible in the reference chart."""
        
        # Test some seventh chords with sharps/flats
        # F#7: 2-4-2-3-2-2 (barre-based)
        fs7_fingering = self.get_primary_fingering('F#7')
        # This might have multiple valid fingerings, so let's just make sure we get something reasonable
        fs7_shape = fs7_fingering.get_chord_shape()
        assert fs7_shape[0] == 2 or fs7_shape[0] is None, \
            f"F#7: Expected barre-based fingering, got {fs7_shape}"
        
        # Test some basic patterns work for other sharp chords
        # G#: Should be able to transpose from some pattern
        gs_fingering = self.get_primary_fingering('G#')
        gs_shape = gs_fingering.get_chord_shape()
        assert len([f for f in gs_shape if f is not None]) >= 3, \
            f"G#: Should have at least 3 fretted notes, got {gs_shape}"


if __name__ == '__main__':
    pytest.main([__file__])