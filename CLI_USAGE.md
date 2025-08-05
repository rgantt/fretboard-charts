# Guitar Chord Generator CLI

A command-line interface for generating guitar chord fingerings and visual diagrams.

## Installation

```bash
# Install dependencies
pip install click matplotlib

# Run directly
python3 cli.py --help

# Or install as a package
pip install -e .
chord-generator --help
```

## Commands

### 1. Generate Chord Fingerings

Generate multiple fingerings for any chord:

```bash
# Basic usage
python3 cli.py generate C
python3 cli.py generate Am7
python3 cli.py generate "F#m7b5"

# Get more fingerings
python3 cli.py generate G -n 5

# JSON output for programmatic use
python3 cli.py generate "Cmaj7/E" --format json

# Save to file
python3 cli.py generate Dm7 -o dm7_fingerings.txt
```

**Example Output:**
```
Chord: C

Fingering #1:
  Shape: x-3-2-0-1-0
  Fingers: 3-2-1
  Difficulty: 0.09
  Type: Open position

Fingering #2:
  Shape: x-3-2-0-x-x
  Fingers: 2-1
  Difficulty: 0.02
  Type: Open position
```

### 2. Generate Chord Diagrams

Create visual chord diagrams:

```bash
# Basic diagram
python3 cli.py diagram C -o c_major.png

# High resolution for printing
python3 cli.py diagram F --dpi 300 -o f_major_hires.png

# Different formats
python3 cli.py diagram Am -o a_minor.svg
python3 cli.py diagram G7 -o g7.pdf

# Use different fingering
python3 cli.py diagram "Bm7" -n 2 -o bm7_alt.png
```

**Output:** Professional-quality chord diagrams with:
- Proper fret grid (6 strings × 4-5 frets)
- Finger position dots
- Finger numbers (1-4)
- Muted string markers (X)
- Barre chord indicators
- Chord name labels

### 3. Batch Processing

Process multiple chords from a file:

```bash
# Create a chord list file
echo -e "C\nG\nAm\nF\nEm\nDm" > my_chords.txt

# Generate separate diagrams
python3 cli.py batch my_chords.txt -o chord_diagrams/

# Generate a single grid image
python3 cli.py batch my_chords.txt --grid -o chord_sheet.png

# Customize grid layout
python3 cli.py batch my_chords.txt --grid -c 3 -o sheet.png

# Different formats
python3 cli.py batch my_chords.txt -f svg --dpi 200
```

**Input File Format:**
```
C
G7
Am
F#m7
Bmaj7/D#
```

### 4. Interactive Mode

Explore chords interactively:

```bash
python3 cli.py interactive
```

**Interactive Commands:**
- `<chord>` - Generate fingerings (e.g., `C`, `Am7`, `F#m7b5`)
- `list` - Show all fingerings for current chord
- `save <n>` - Save fingering #n as diagram
- `compare` - Generate side-by-side comparison
- `help` - Show help
- `quit` - Exit

**Example Session:**
```
chord> C
Generated 3 fingerings for C:
  1. Shape: x-3-2-0-1-0, Fingers: 3-2-1, Difficulty: 0.09
  ...

chord> list
Fingerings for C:
  1. x-3-2-0-1-0 (difficulty: 0.09)
  2. x-3-2-0-x-x (difficulty: 0.02)

chord> save 1
Save as: c_major.png
Saved to c_major.png

chord> compare
Save comparison as: c_compare.png
Saved comparison to c_compare.png
```

## Supported Chord Types

The generator supports comprehensive chord notation:

### Basic Chords
- **Major**: `C`, `G`, `F#`
- **Minor**: `Am`, `Dm`, `Bbm`
- **Diminished**: `Cdim`, `F#dim7`
- **Augmented**: `Caug`, `G+`

### Extensions & Alterations
- **7th chords**: `C7`, `Am7`, `Gmaj7`, `Bm7b5`
- **Extended**: `C9`, `Am11`, `Gmaj13`
- **Altered**: `C7alt`, `G7#5`, `Dm7b5`
- **Add chords**: `Cadd9`, `Fadd2`
- **Suspended**: `Csus2`, `Gsus4`

### Slash Chords
- **Inversions**: `C/E`, `Am/C`, `G7/B`
- **Bass notes**: `C/G`, `Dm/F`, `Am7/G`

### Complex Examples
- `F#m7b5` - F# half-diminished 7th
- `Bmaj7#11` - B major 7th with raised 11th
- `C7alt` - C altered dominant (b9, #9, #11, b13)
- `Am7/G` - A minor 7th with G in bass

## Output Formats

### Text Output
Human-readable fingering descriptions with:
- Chord shape notation (x-3-2-0-1-0)
- Finger assignments (3-2-1)
- Difficulty scores (0.0-1.0)
- Chord characteristics (open position, barre chord)

### JSON Output
Structured data for programmatic use:
```json
{
  "chord": "C",
  "fingerings": [
    {
      "rank": 1,
      "shape": [null, 3, 2, 0, 1, 0],
      "shape_string": "x-3-2-0-1-0",
      "finger_assignments": {"5": 3, "4": 2, "2": 1},
      "difficulty": 0.09,
      "characteristics": {
        "is_open_position": true,
        "is_barre_chord": false,
        "fingers_used": 3
      }
    }
  ]
}
```

### Visual Diagrams
Professional chord diagrams in multiple formats:
- **PNG**: For web and digital use
- **SVG**: Scalable vector graphics
- **PDF**: Print-ready documents

## Advanced Usage

### Custom Fingering Selection

```bash
# Compare fingering difficulty
python3 cli.py generate Bm7 -n 5 --format json | \
  jq '.fingerings[] | {rank, difficulty, shape_string}'

# Find easiest fingering
python3 cli.py generate F -f json | \
  jq '.fingerings | min_by(.difficulty)'
```

### Batch Processing with Filtering

```bash
# Only process valid chords
grep -v '^#' songbook.txt | \
  python3 cli.py batch - --grid -o songbook.png

# Generate individual PDFs for printing
python3 cli.py batch chords.txt -f pdf --dpi 300 -o print/
```

### Integration with Other Tools

```bash
# Generate chord progression
echo -e "C\nAm\nF\nG" | \
  python3 cli.py batch - --grid -c 4 -o progression.png

# Extract chords from lead sheet
grep -o "[A-G][^[:space:]]*" lead_sheet.txt | \
  sort -u > unique_chords.txt
python3 cli.py batch unique_chords.txt --grid -o all_chords.png
```

## Tips and Best Practices

### Chord Notation
- Use standard notation: `C`, `Am7`, `F#m7b5`
- Quote complex chords: `"Bmaj7#11"`, `"C7alt"`
- Slash chords: `"Am7/G"`, `"C/E"`

### Diagram Generation
- Use high DPI (300) for printing: `--dpi 300`
- Grid layout for chord sheets: `--grid`
- SVG for scalable graphics: `-f svg`

### Batch Processing
- One chord per line in input files
- Use comments (lines starting with #) for organization
- Grid layout works best with 3-6 chords per row

### Interactive Mode
- Great for learning and exploration
- Use `compare` to see multiple fingerings side-by-side
- Save frequently-used fingerings for reference

## Error Handling

The CLI provides helpful error messages:

```bash
# Invalid chord notation
$ python3 cli.py generate "Xyz"
Error parsing chord: Unknown chord quality: xyz

# Missing output file
$ python3 cli.py diagram C
Usage: cli.py diagram [OPTIONS] CHORD_NAME
Error: Missing option '-o' / '--output'.

# Invalid fingering number
$ python3 cli.py diagram C -o c.png -n 10
Only 5 fingerings available. Using the 1st one.
```

## Performance

- **Single chord**: ~50-100ms
- **Batch processing**: ~10-20 chords/second
- **Diagram generation**: ~200-500ms per image
- **Memory usage**: <50MB for typical operations