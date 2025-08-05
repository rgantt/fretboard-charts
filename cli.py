#!/usr/bin/env python3
"""
Command-line interface for the Guitar Chord Fingering Generator.

This CLI provides commands for:
- Generating chord fingerings from chord symbols
- Creating visual chord diagrams
- Batch processing multiple chords
- Interactive chord exploration
"""

import click
import json
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from src.chord_parser import quick_parse, ChordParseError
from src.fingering_generator import FingeringGenerator
from src.diagram_generator import generate_chord_diagram, ChordDiagramGenerator
from src.fingering import Fingering


@click.group()
@click.version_option(version="1.0.0", prog_name="chord-generator")
def cli():
    """Guitar Chord Fingering Generator - Generate chord fingerings and diagrams."""
    pass


@cli.command()
@click.argument('chord_name')
@click.option('-n', '--num-fingerings', default=3, help='Number of fingerings to generate (default: 3)')
@click.option('-f', '--format', type=click.Choice(['text', 'json']), default='text', 
              help='Output format (default: text)')
@click.option('-o', '--output', type=click.Path(), help='Output to file instead of stdout')
def generate(chord_name: str, num_fingerings: int, format: str, output: Optional[str]):
    """Generate fingerings for a chord.
    
    Examples:
        chord-generator generate C
        chord-generator generate "F#m7" -n 5
        chord-generator generate "Cmaj7/E" --format json -o cmaj7.json
    """
    try:
        # Parse the chord
        chord = quick_parse(chord_name)
        
        # Generate fingerings
        generator = FingeringGenerator()
        fingerings = generator.generate_fingerings(chord)[:num_fingerings]
        
        if not fingerings:
            click.echo(f"No fingerings found for {chord_name}", err=True)
            sys.exit(1)
        
        # Format output
        if format == 'json':
            output_data = {
                'chord': str(chord),
                'fingerings': []
            }
            
            for i, fingering in enumerate(fingerings):
                shape = fingering.get_chord_shape()
                finger_assignments = {}
                for string, finger in fingering.finger_assignments.items():
                    if finger.value > 0:  # Only include actual finger assignments
                        finger_assignments[string] = finger.value
                
                output_data['fingerings'].append({
                    'rank': i + 1,
                    'shape': [None if f is None else f for f in shape],
                    'shape_string': '-'.join(['x' if f is None else str(f) for f in shape]),
                    'finger_assignments': finger_assignments,
                    'difficulty': round(fingering.difficulty, 3),
                    'characteristics': fingering.characteristics
                })
            
            result = json.dumps(output_data, indent=2)
        else:
            # Text format
            lines = [f"Chord: {chord}\n"]
            
            for i, fingering in enumerate(fingerings):
                shape = fingering.get_chord_shape()
                shape_str = '-'.join(['x' if f is None else str(f) for f in shape])
                
                # Get finger numbers for display
                finger_nums = []
                for string in range(6, 0, -1):  # Check strings 6 to 1
                    if string in fingering.finger_assignments:
                        finger = fingering.finger_assignments[string]
                        if finger.value > 0:  # Not OPEN or MUTED
                            finger_nums.append(str(finger.value))
                
                lines.append(f"\nFingering #{i+1}:")
                lines.append(f"  Shape: {shape_str}")
                lines.append(f"  Fingers: {'-'.join(finger_nums) if finger_nums else 'open position'}")
                lines.append(f"  Difficulty: {fingering.difficulty:.2f}")
                
                # Add characteristics
                if fingering.characteristics.get('is_barre_chord'):
                    lines.append("  Type: Barre chord")
                elif fingering.characteristics.get('is_open_position'):
                    lines.append("  Type: Open position")
            
            result = '\n'.join(lines)
        
        # Output
        if output:
            Path(output).write_text(result)
            click.echo(f"Output written to {output}")
        else:
            click.echo(result)
            
    except ChordParseError as e:
        click.echo(f"Error parsing chord: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('chord_name')
@click.option('-o', '--output', required=True, help='Output image file (PNG/SVG/PDF)')
@click.option('-n', '--fingering-number', default=1, help='Which fingering to use (default: 1st)')
@click.option('-d', '--dpi', default=150, help='Image resolution in DPI (default: 150)')
@click.option('-s', '--style', type=click.Choice(['standard', 'compact']), default='standard',
              help='Diagram style (default: standard)')
def diagram(chord_name: str, output: str, fingering_number: int, dpi: int, style: str):
    """Generate a chord diagram image.
    
    Examples:
        chord-generator diagram C -o c_major.png
        chord-generator diagram "F#m7" -o f_sharp_minor_7.svg -n 2
        chord-generator diagram "Gmaj7" -o gmaj7.pdf --dpi 300
    """
    try:
        # Parse the chord
        chord = quick_parse(chord_name)
        
        # Generate fingerings
        generator = FingeringGenerator()
        fingerings = generator.generate_fingerings(chord)
        
        if not fingerings:
            click.echo(f"No fingerings found for {chord_name}", err=True)
            sys.exit(1)
            
        if fingering_number > len(fingerings):
            click.echo(f"Only {len(fingerings)} fingerings available. Using the 1st one.", err=True)
            fingering_number = 1
        
        # Get the selected fingering
        fingering = fingerings[fingering_number - 1]
        
        # Generate diagram
        output_path = Path(output)
        generate_chord_diagram(fingering, str(output_path), dpi=dpi)
        
        click.echo(f"Chord diagram saved to {output_path}")
        
        # Show info about the fingering
        shape = fingering.get_chord_shape()
        shape_str = '-'.join(['x' if f is None else str(f) for f in shape])
        click.echo(f"Shape: {shape_str}")
        click.echo(f"Difficulty: {fingering.difficulty:.2f}")
        
    except ChordParseError as e:
        click.echo(f"Error parsing chord: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output-dir', default='.', help='Output directory for images (default: current)')
@click.option('-f', '--format', type=click.Choice(['png', 'svg', 'pdf']), default='png',
              help='Output format (default: png)')
@click.option('-d', '--dpi', default=150, help='Image resolution in DPI (default: 150)')
@click.option('--grid/--separate', default=False, help='Generate grid layout vs separate files')
@click.option('-c', '--columns', default=4, help='Columns in grid layout (default: 4)')
def batch(input_file: str, output_dir: str, format: str, dpi: int, grid: bool, columns: int):
    """Process multiple chords from a file.
    
    The input file should contain one chord name per line.
    
    Examples:
        chord-generator batch chords.txt -o diagrams/
        chord-generator batch progression.txt --grid -o chord_sheet.png
        chord-generator batch song_chords.txt -f svg --dpi 300
    """
    try:
        # Read chord names from file
        chord_names = Path(input_file).read_text().strip().split('\n')
        chord_names = [name.strip() for name in chord_names if name.strip()]
        
        if not chord_names:
            click.echo("No chord names found in input file", err=True)
            sys.exit(1)
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Generate fingerings for all chords
        generator = FingeringGenerator()
        chord_fingerings = []
        failed_chords = []
        
        with click.progressbar(chord_names, label='Generating fingerings') as chords:
            for chord_name in chords:
                try:
                    chord = quick_parse(chord_name)
                    fingerings = generator.generate_fingerings(chord)
                    if fingerings:
                        chord_fingerings.append(fingerings[0])
                    else:
                        failed_chords.append((chord_name, "No fingerings found"))
                except ChordParseError as e:
                    failed_chords.append((chord_name, str(e)))
                except Exception as e:
                    failed_chords.append((chord_name, f"Error: {str(e)}"))
        
        # Report any failures
        if failed_chords:
            click.echo("\nFailed to process some chords:", err=True)
            for chord_name, error in failed_chords:
                click.echo(f"  {chord_name}: {error}", err=True)
        
        if not chord_fingerings:
            click.echo("No valid chords to process", err=True)
            sys.exit(1)
        
        # Generate diagrams
        if grid:
            # Grid layout
            output_file = output_path / f"chord_grid.{format}"
            diagram_gen = ChordDiagramGenerator()
            diagram_gen.generate_multiple_diagrams(
                chord_fingerings,
                str(output_file),
                cols=columns,
                dpi=dpi
            )
            click.echo(f"\nGenerated grid diagram: {output_file}")
        else:
            # Separate files
            click.echo("\nGenerating individual diagrams...")
            for fingering in chord_fingerings:
                chord_name = str(fingering.chord) if fingering.chord else "chord"
                # Make filename safe
                safe_name = chord_name.replace('/', '_').replace('#', 'sharp').replace(' ', '_')
                output_file = output_path / f"{safe_name}.{format}"
                
                generate_chord_diagram(fingering, str(output_file), dpi=dpi)
            
            click.echo(f"Generated {len(chord_fingerings)} diagrams in {output_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def interactive():
    """Interactive chord exploration mode."""
    click.echo("Guitar Chord Generator - Interactive Mode")
    click.echo("Type 'help' for commands, 'quit' to exit\n")
    
    generator = FingeringGenerator()
    current_chord = None
    current_fingerings = []
    
    while True:
        try:
            command = click.prompt('chord>', type=str).strip()
            
            if command.lower() in ['quit', 'exit', 'q']:
                break
            
            elif command.lower() == 'help':
                click.echo("\nCommands:")
                click.echo("  <chord>     - Generate fingerings for a chord (e.g., C, Am7, F#m7b5)")
                click.echo("  list        - Show all generated fingerings for current chord")
                click.echo("  save <n>    - Save fingering #n as a diagram")
                click.echo("  compare     - Compare all fingerings side by side")
                click.echo("  help        - Show this help")
                click.echo("  quit        - Exit interactive mode\n")
            
            elif command.lower() == 'list':
                if not current_fingerings:
                    click.echo("No chord loaded. Enter a chord name first.")
                else:
                    click.echo(f"\nFingerings for {current_chord}:")
                    for i, fingering in enumerate(current_fingerings):
                        shape = fingering.get_chord_shape()
                        shape_str = '-'.join(['x' if f is None else str(f) for f in shape])
                        click.echo(f"  {i+1}. {shape_str} (difficulty: {fingering.difficulty:.2f})")
            
            elif command.lower().startswith('save '):
                try:
                    num = int(command.split()[1])
                    if not current_fingerings:
                        click.echo("No chord loaded. Enter a chord name first.")
                    elif num < 1 or num > len(current_fingerings):
                        click.echo(f"Invalid fingering number. Choose 1-{len(current_fingerings)}")
                    else:
                        filename = click.prompt('Save as', 
                                              default=f"{str(current_chord).replace('/', '_')}.png")
                        generate_chord_diagram(current_fingerings[num-1], filename)
                        click.echo(f"Saved to {filename}")
                except (ValueError, IndexError):
                    click.echo("Usage: save <fingering_number>")
            
            elif command.lower() == 'compare':
                if not current_fingerings:
                    click.echo("No chord loaded. Enter a chord name first.")
                else:
                    filename = click.prompt('Save comparison as', 
                                          default=f"{str(current_chord).replace('/', '_')}_compare.png")
                    diagram_gen = ChordDiagramGenerator()
                    diagram_gen.generate_multiple_diagrams(
                        current_fingerings[:6],  # Limit to 6 for display
                        filename,
                        cols=3
                    )
                    click.echo(f"Saved comparison to {filename}")
            
            else:
                # Assume it's a chord name
                try:
                    chord = quick_parse(command)
                    fingerings = generator.generate_fingerings(chord)
                    
                    if not fingerings:
                        click.echo(f"No fingerings found for {command}")
                    else:
                        current_chord = chord
                        current_fingerings = fingerings[:5]  # Keep top 5
                        
                        click.echo(f"\nGenerated {len(fingerings)} fingerings for {chord}:")
                        for i, fingering in enumerate(current_fingerings):
                            shape = fingering.get_chord_shape()
                            shape_str = '-'.join(['x' if f is None else str(f) for f in shape])
                            
                            # Get finger numbers
                            finger_nums = []
                            for string in range(6, 0, -1):
                                if string in fingering.finger_assignments:
                                    finger = fingering.finger_assignments[string]
                                    if finger.value > 0:
                                        finger_nums.append(str(finger.value))
                            
                            click.echo(f"\n  {i+1}. Shape: {shape_str}")
                            click.echo(f"     Fingers: {'-'.join(finger_nums) if finger_nums else 'open'}")
                            click.echo(f"     Difficulty: {fingering.difficulty:.2f}")
                            
                            if fingering.characteristics.get('is_barre_chord'):
                                click.echo("     Type: Barre chord")
                            elif fingering.characteristics.get('is_open_position'):
                                click.echo("     Type: Open position")
                
                except ChordParseError as e:
                    click.echo(f"Error parsing chord: {e}")
                except Exception as e:
                    click.echo(f"Error: {e}")
        
        except (EOFError, KeyboardInterrupt):
            click.echo("\nGoodbye!")
            break
        except Exception as e:
            click.echo(f"Error: {e}")


if __name__ == '__main__':
    cli()