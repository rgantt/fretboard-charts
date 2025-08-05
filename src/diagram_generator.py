"""
Visual chord diagram generation for guitar fingerings.

This module generates professional-quality chord diagrams that match
standard guitar chord book formatting, including proper grid layout,
finger positions, and notation.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Optional, Tuple, List, Dict, Union
from pathlib import Path
import io
from dataclasses import dataclass

from .fingering import Fingering, FingerAssignment
from .music_theory import Chord


@dataclass
class DiagramStyle:
    """Configuration for chord diagram visual styling"""
    # Diagram dimensions
    width: float = 2.0          # Width in inches
    height: float = 2.5         # Height in inches
    
    # Grid layout
    string_spacing: float = 0.25    # Space between strings
    fret_spacing: float = 0.35     # Space between frets
    num_frets: int = 4             # Number of frets to show
    
    # Colors
    grid_color: str = '#000000'     # Black grid lines
    dot_color: str = '#000000'      # Black finger dots
    text_color: str = '#000000'     # Black text
    background_color: str = '#ffffff' # White background
    
    # Line widths
    string_width: float = 1.5       # String line width
    fret_width: float = 1.0         # Fret line width
    nut_width: float = 3.0          # Nut (top fret) width
    
    # Text sizing
    chord_name_size: int = 14       # Chord name font size
    finger_number_size: int = 10    # Finger number font size
    marker_size: int = 8            # Mute/open marker size
    position_marker_size: int = 10  # Fret position marker size
    
    # Dot sizing
    dot_radius: float = 0.03        # Finger position dot radius (much smaller - half of previous)
    open_circle_radius: float = 0.02 # Open string circle radius (not used anymore)


class ChordDiagramGenerator:
    """
    Generates visual chord diagrams from guitar fingerings.
    
    Creates professional-quality chord diagrams matching standard
    guitar chord book format with proper grid layout, finger positions,
    and notation markers.
    """
    
    def __init__(self, style: DiagramStyle = None):
        """
        Initialize the diagram generator.
        
        Args:
            style: Visual styling configuration (uses default if None)
        """
        self.style = style or DiagramStyle()
    
    def generate_diagram(self, fingering: Fingering, 
                        output_path: Optional[Union[str, Path]] = None,
                        format: str = 'png',
                        dpi: int = 150) -> Optional[bytes]:
        """
        Generate a chord diagram from a fingering.
        
        Args:
            fingering: The fingering to visualize
            output_path: Path to save the image (optional)
            format: Image format ('png', 'svg', 'pdf')
            dpi: Image resolution for raster formats
            
        Returns:
            Image bytes if output_path is None, otherwise None
        """
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(self.style.width, self.style.height))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Set background color
        fig.patch.set_facecolor(self.style.background_color)
        
        # Calculate diagram positioning
        diagram_info = self._calculate_diagram_layout(fingering)
        
        # Draw the chord diagram
        self._draw_grid(ax, diagram_info)
        self._draw_finger_positions(ax, fingering, diagram_info)
        self._draw_string_markers(ax, fingering, diagram_info)
        self._draw_finger_numbers(ax, fingering, diagram_info)
        self._draw_chord_name(ax, fingering, diagram_info)
        self._draw_position_marker(ax, diagram_info, fingering)
        
        # Save or return image
        if output_path:
            plt.savefig(output_path, format=format, dpi=dpi, 
                       bbox_inches='tight', facecolor=self.style.background_color)
            plt.close(fig)
            return None
        else:
            # Return image as bytes
            buffer = io.BytesIO()
            plt.savefig(buffer, format=format, dpi=dpi, 
                       bbox_inches='tight', facecolor=self.style.background_color)
            plt.close(fig)
            buffer.seek(0)
            return buffer.getvalue()
    
    def _calculate_diagram_layout(self, fingering: Fingering) -> Dict:
        """Calculate the layout parameters for the diagram"""
        # Determine fret range to display
        fretted_positions = [pos for pos in fingering.positions if pos.fret > 0]
        
        if not fretted_positions:
            # All open strings
            start_fret = 0
            display_frets = 5
        else:
            frets = [pos.fret for pos in fretted_positions]
            min_fret = min(frets)
            max_fret = max(frets)
            
            if min_fret <= 4:
                # Open position
                start_fret = 0
                display_frets = 5
            else:
                # Higher position - center around the chord
                start_fret = max(1, min_fret - 1)
                display_frets = 5
        
        # Calculate grid positioning
        grid_left = 0.15
        grid_right = 0.85
        grid_top = 0.75
        grid_bottom = 0.25
        
        return {
            'start_fret': start_fret,
            'display_frets': display_frets,
            'grid_left': grid_left,
            'grid_right': grid_right,
            'grid_top': grid_top,
            'grid_bottom': grid_bottom,
            'string_positions': [grid_left + i * (grid_right - grid_left) / 5 
                               for i in range(6)],
            'fret_positions': [grid_top - i * (grid_top - grid_bottom) / display_frets 
                             for i in range(display_frets + 1)]
        }
    
    def _draw_grid(self, ax, diagram_info: Dict):
        """Draw the fretboard grid"""
        string_positions = diagram_info['string_positions']
        fret_positions = diagram_info['fret_positions']
        start_fret = diagram_info['start_fret']
        
        # Draw strings (vertical lines)
        for string_x in string_positions:
            ax.plot([string_x, string_x], 
                   [diagram_info['grid_bottom'], diagram_info['grid_top']], 
                   color=self.style.grid_color, 
                   linewidth=self.style.string_width)
        
        # Draw frets (horizontal lines)
        for i, fret_y in enumerate(fret_positions):
            # Make the nut (top line) thicker for open position
            if start_fret == 0 and i == 0:
                linewidth = self.style.nut_width
            else:
                linewidth = self.style.fret_width
                
            ax.plot([diagram_info['grid_left'], diagram_info['grid_right']], 
                   [fret_y, fret_y], 
                   color=self.style.grid_color, 
                   linewidth=linewidth)
    
    def _draw_finger_positions(self, ax, fingering: Fingering, diagram_info: Dict):
        """Draw finger position dots and barre indicators"""
        string_positions = diagram_info['string_positions']
        fret_positions = diagram_info['fret_positions']
        start_fret = diagram_info['start_fret']
        
        # Check for barre chord - be more strict about what constitutes a barre
        barre_fret = None
        barre_strings = []
        
        if fingering.finger_assignments:
            # Find which fret has the barre (multiple strings, same finger, same fret)
            finger_fret_strings = {}
            for string_num, finger in fingering.finger_assignments.items():
                if finger == FingerAssignment.INDEX:  # Barres are typically with index finger
                    for pos in fingering.positions:
                        if pos.string == string_num and pos.fret > 0:
                            if pos.fret not in finger_fret_strings:
                                finger_fret_strings[pos.fret] = []
                            finger_fret_strings[pos.fret].append(string_num)
                            break
            
            # Find the fret with multiple strings using same finger
            # Check for both E-shape barres (3+ strings) and A-shape barres (2 strings with big span)
            for fret, strings in finger_fret_strings.items():
                strings.sort()
                string_span = strings[-1] - strings[0]  # Total span from lowest to highest string
                
                # E-shape barre: 3+ strings with significant span (like F major: 6,2,1)
                if len(strings) >= 3 and string_span >= 4:
                    barre_fret = fret
                    barre_strings = strings
                    break
                # A-shape barre: 2 strings but spanning the full neck (like Bb: strings 5,1)
                elif len(strings) == 2 and string_span >= 4:
                    barre_fret = fret
                    barre_strings = strings
                    break
        
        # Store barre info for drawing after dots
        barre_line_info = None
        if barre_fret and len(barre_strings) >= 2:
            fret_index = barre_fret - start_fret
            if 0 < fret_index <= len(fret_positions) - 1:
                # Find leftmost and rightmost strings in barre
                min_string = min(barre_strings)
                max_string = max(barre_strings)
                left_x = string_positions[6 - max_string]
                right_x = string_positions[6 - min_string]
                y = (fret_positions[fret_index - 1] + fret_positions[fret_index]) / 2
                
                # Extend the barre slightly past the bounding strings
                extension = self.style.dot_radius * 0.5
                left_x -= extension
                right_x += extension
                
                barre_line_info = {
                    'left_x': left_x,
                    'right_x': right_x,
                    'y': y,
                    'thickness': self.style.dot_radius * 2 * 72
                }
        
        # Draw individual finger dots
        for position in fingering.positions:
            if position.fret == 0:
                continue  # Open strings handled separately
                
            # Skip if this is part of the barre
            if barre_fret and position.fret == barre_fret and position.string in barre_strings:
                continue
                
            # Calculate grid position
            string_index = 6 - position.string  # String 6 is leftmost (index 0)
            fret_index = position.fret - start_fret
            
            if 0 <= string_index < 6 and 0 < fret_index <= len(fret_positions) - 1:
                x = string_positions[string_index]
                # Position dot between frets
                y = (fret_positions[fret_index - 1] + fret_positions[fret_index]) / 2
                
                # Draw finger dot
                circle = patches.Circle((x, y), self.style.dot_radius, 
                                      facecolor=self.style.dot_color, 
                                      edgecolor=self.style.dot_color)
                ax.add_patch(circle)
        
        # Draw barre line AFTER dots so it's visible on top
        if barre_line_info:
            ax.plot([barre_line_info['left_x'], barre_line_info['right_x']], 
                   [barre_line_info['y'], barre_line_info['y']], 
                   color=self.style.dot_color, 
                   linewidth=barre_line_info['thickness'],
                   solid_capstyle='round',
                   zorder=10)  # High z-order to draw on top
            
            # Add barre fret marker for barres on frets higher than 1
            if barre_fret and barre_fret > 1:
                # Position the marker to the right of the barre line
                marker_x = barre_line_info['right_x'] + 0.05
                marker_y = barre_line_info['y']
                marker_text = f"{barre_fret}fr"
                
                ax.text(marker_x, marker_y, marker_text,
                       ha='left', va='center',
                       fontsize=self.style.position_marker_size * 0.8,  # Slightly smaller than main position marker
                       color=self.style.text_color,
                       weight='normal')
    
    def _draw_string_markers(self, ax, fingering: Fingering, diagram_info: Dict):
        """Draw muted (x) string markers only - open strings have no marker"""
        string_positions = diagram_info['string_positions']
        marker_y = diagram_info['grid_top'] + 0.06
        
        # Determine which strings are used
        used_strings = {pos.string for pos in fingering.positions}
        
        for string_num in range(1, 7):
            string_index = 6 - string_num  # String 6 is leftmost
            x = string_positions[string_index]
            
            if string_num not in used_strings:
                # Draw muted string marker (x) - smaller size
                marker_size = 0.02  # Much smaller than before (was 0.04)
                ax.plot([x - marker_size, x + marker_size], 
                       [marker_y - marker_size, marker_y + marker_size], 
                       color=self.style.text_color, linewidth=1.5)
                ax.plot([x - marker_size, x + marker_size], 
                       [marker_y + marker_size, marker_y - marker_size], 
                       color=self.style.text_color, linewidth=1.5)
            # No marker for open or fretted strings - if no X, it's played
    
    def _draw_finger_numbers(self, ax, fingering: Fingering, diagram_info: Dict):
        """Draw finger numbers below the diagram, omitting barre fingerings"""
        if not fingering.finger_assignments:
            return
            
        string_positions = diagram_info['string_positions']
        number_y = diagram_info['grid_bottom'] - 0.08
        
        # Convert finger assignments to numbers
        finger_to_number = {
            FingerAssignment.INDEX: '1',
            FingerAssignment.MIDDLE: '2',
            FingerAssignment.RING: '3',
            FingerAssignment.PINKY: '4'
        }
        
        # Detect barre to omit those finger numbers
        barre_fret = None
        barre_strings = set()
        
        if fingering.finger_assignments:
            # Find barre strings (same logic as in _draw_finger_positions)
            finger_fret_strings = {}
            for string_num, finger in fingering.finger_assignments.items():
                if finger == FingerAssignment.INDEX:
                    for pos in fingering.positions:
                        if pos.string == string_num and pos.fret > 0:
                            if pos.fret not in finger_fret_strings:
                                finger_fret_strings[pos.fret] = []
                            finger_fret_strings[pos.fret].append(string_num)
                            break
            
            # Find the fret with multiple strings using same finger (3+ for barre)
            for fret, strings in finger_fret_strings.items():
                if len(strings) >= 3:
                    strings.sort()
                    string_span = strings[-1] - strings[0]  # Total span from lowest to highest string
                    if string_span >= 4:  # Must span at least 4 string positions
                        barre_fret = fret
                        barre_strings = set(strings)
                        break
        
        # Draw finger numbers, but skip barre strings
        for string_num, finger in fingering.finger_assignments.items():
            if finger in finger_to_number:
                # Skip if this string is part of a barre
                if barre_fret and string_num in barre_strings:
                    continue
                    
                string_index = 6 - string_num  # String 6 is leftmost
                x = string_positions[string_index]
                
                ax.text(x, number_y, finger_to_number[finger], 
                       ha='center', va='center',
                       fontsize=self.style.finger_number_size,
                       color=self.style.text_color,
                       weight='bold')
    
    def _draw_chord_name(self, ax, fingering: Fingering, diagram_info: Dict):
        """Draw chord name above the diagram"""
        if fingering.chord:
            chord_name = str(fingering.chord)
        else:
            chord_name = "Unknown"
            
        # Position chord name at the top center
        center_x = (diagram_info['grid_left'] + diagram_info['grid_right']) / 2
        name_y = 0.92
        
        ax.text(center_x, name_y, chord_name,
               ha='center', va='center',
               fontsize=self.style.chord_name_size,
               color=self.style.text_color,
               weight='bold')
    
    def _draw_position_marker(self, ax, diagram_info: Dict, fingering: Fingering):
        """Draw fret position marker for non-open positions"""
        start_fret = diagram_info['start_fret']
        
        if start_fret > 0:
            # Check if there's a barre that would show the same fret number
            main_position_fret = start_fret + 1
            barre_fret = None
            if fingering.characteristics.get('is_barre_chord', False):
                barre_fret = fingering._get_barre_fret()
            
            # Only show main position marker if it won't duplicate the barre marker
            if barre_fret is None or barre_fret != main_position_fret:
                # Add fret position marker (e.g., "3fr")
                marker_text = f"{main_position_fret}fr"
                marker_x = diagram_info['grid_right'] + 0.08
                
                # Position marker next to the first fret line (which represents start_fret + 1)
                fret_positions = diagram_info['fret_positions']
                if len(fret_positions) > 1:
                    # Position next to the second fret line (index 1), which represents start_fret + 1
                    marker_y = fret_positions[1]
                else:
                    # Fallback to center if something goes wrong
                    marker_y = (diagram_info['grid_top'] + diagram_info['grid_bottom']) / 2
                
                ax.text(marker_x, marker_y, marker_text,
                       ha='left', va='center',
                       fontsize=self.style.position_marker_size,
                       color=self.style.text_color)
    
    def generate_multiple_diagrams(self, fingerings: List[Fingering],
                                 output_path: Optional[Union[str, Path]] = None,
                                 cols: int = 4,
                                 format: str = 'png',
                                 dpi: int = 150) -> Optional[bytes]:
        """
        Generate a grid of multiple chord diagrams.
        
        Args:
            fingerings: List of fingerings to visualize
            output_path: Path to save the image (optional)
            cols: Number of columns in the grid
            format: Image format ('png', 'svg', 'pdf')
            dpi: Image resolution for raster formats
            
        Returns:
            Image bytes if output_path is None, otherwise None
        """
        if not fingerings:
            return None
            
        rows = (len(fingerings) + cols - 1) // cols
        
        # Create figure with subplots
        fig, axes = plt.subplots(rows, cols, 
                               figsize=(self.style.width * cols, 
                                      self.style.height * rows))
        
        # Handle single row/column cases
        if rows == 1 and cols == 1:
            axes = [[axes]]
        elif rows == 1:
            axes = [axes]
        elif cols == 1:
            axes = [[ax] for ax in axes]
        
        fig.patch.set_facecolor(self.style.background_color)
        
        # Generate each diagram
        for i, fingering in enumerate(fingerings):
            row, col = divmod(i, cols)
            ax = axes[row][col]
            
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_aspect('equal')
            ax.axis('off')
            
            # Calculate and draw diagram
            diagram_info = self._calculate_diagram_layout(fingering)
            self._draw_grid(ax, diagram_info)
            self._draw_finger_positions(ax, fingering, diagram_info)
            self._draw_string_markers(ax, fingering, diagram_info)
            self._draw_finger_numbers(ax, fingering, diagram_info)
            self._draw_chord_name(ax, fingering, diagram_info)
            self._draw_position_marker(ax, diagram_info, fingering)
        
        # Hide unused subplots
        for i in range(len(fingerings), rows * cols):
            row, col = divmod(i, cols)
            axes[row][col].axis('off')
        
        # Adjust layout and save
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, format=format, dpi=dpi, 
                       bbox_inches='tight', facecolor=self.style.background_color)
            plt.close(fig)
            return None
        else:
            buffer = io.BytesIO()
            plt.savefig(buffer, format=format, dpi=dpi, 
                       bbox_inches='tight', facecolor=self.style.background_color)
            plt.close(fig)
            buffer.seek(0)
            return buffer.getvalue()


# Convenience functions
def generate_chord_diagram(fingering: Fingering, 
                         output_path: Optional[Union[str, Path]] = None,
                         **kwargs) -> Optional[bytes]:
    """
    Convenience function to generate a single chord diagram.
    
    Args:
        fingering: The fingering to visualize
        output_path: Path to save the image (optional)
        **kwargs: Additional arguments passed to DiagramGenerator
        
    Returns:
        Image bytes if output_path is None, otherwise None
    """
    generator = ChordDiagramGenerator()
    return generator.generate_diagram(fingering, output_path, **kwargs)


def generate_chord_progression_diagram(chord_symbols: List[str],
                                     output_path: Optional[Union[str, Path]] = None,
                                     max_fingerings_per_chord: int = 1,
                                     **kwargs) -> Optional[bytes]:
    """
    Convenience function to generate diagrams for a chord progression.
    
    Args:
        chord_symbols: List of chord symbols (e.g., ['C', 'Am', 'F', 'G'])
        output_path: Path to save the image (optional)
        max_fingerings_per_chord: Maximum fingerings to show per chord
        **kwargs: Additional arguments passed to DiagramGenerator
        
    Returns:
        Image bytes if output_path is None, otherwise None
    """
    from .fingering_generator import generate_chord_fingerings
    
    all_fingerings = []
    for chord_symbol in chord_symbols:
        fingerings = generate_chord_fingerings(chord_symbol, 
                                             max_results=max_fingerings_per_chord)
        all_fingerings.extend(fingerings)
    
    if not all_fingerings:
        return None
    
    generator = ChordDiagramGenerator()
    return generator.generate_multiple_diagrams(all_fingerings, output_path, **kwargs)