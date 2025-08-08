# 🎸 Guitar Chord Fingering Generator

A professional-quality Python library and CLI tool for generating guitar chord fingerings and visual chord diagrams. Built with music theory foundations and designed for both standalone use and AI integration via MCP (Model Context Protocol).

[![Tests](https://img.shields.io/badge/tests-165%2F165%20passing-brightgreen)](tests/)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## ✨ Features

### 🎵 **Professional Chord Generation**
- **Comprehensive Chord Support**: Major, minor, diminished, augmented, 7th, 9th, 11th, 13th chords
- **Advanced Notation**: Handles complex chords like `Cmaj7/E`, `F#m7b5`, `Dm7add9`, `C7alt`
- **Standard Fingerings**: Generates fingerings matching professional guitar chord charts
- **Smart Ranking**: Prioritizes beginner-friendly, ergonomic fingerings

### 🖼️ **Visual Chord Diagrams**
- **Professional Quality**: Generates chord diagrams matching standard guitar chord books
- **Multiple Formats**: PNG, SVG, and PDF output with configurable DPI
- **Barre Chord Support**: Automatic barre detection with fret position markers ("2fr", "5fr")
- **Consistent Layout**: All diagrams show exactly 5 fret positions for uniform appearance
- **Batch Generation**: Create chord progression diagrams and comparison grids

### 🔧 **Flexible Interfaces**
- **Command-Line Tool**: Full-featured CLI with interactive and batch modes
- **Python Library**: Import and use in your own projects
- **MCP Server**: AI integration for Claude and other AI assistants
- **JSON API**: Structured output for programmatic integration

### 🎯 **Music Theory Foundation**
- **Theoretically Sound**: Built on proper music theory principles
- **Enharmonic Awareness**: Handles F# = Gb equivalencies contextually  
- **Slash Chord Support**: Perfect for fingerstyle and advanced arrangements
- **Pattern Recognition**: Recognizes and prioritizes standard chord patterns

## 🚀 Quick Start

### Installation from Source

```bash
# Clone the repository
git clone https://github.com/username/fretboard-diagram-generator.git
cd fretboard-diagram-generator

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install as package (for CLI and MCP tools)
pip install -e .

# Verify installation
guitar-chord-cli --version
guitar-chord-mcp-server --help
```

### Basic Usage

#### Command Line Interface

```bash
# Generate fingerings for a chord
python -m src.cli generate "Cmaj7"
# OR if installed: guitar-chord-cli generate "Cmaj7"

# Create a visual chord diagram
python -m src.cli diagram "F#" --output fsharp.png

# Interactive chord exploration
python -m src.cli interactive

# Process multiple chords
python -m src.cli batch --chords "C Am F G" --output progression.png
```

#### Python Library

```python
from src.fingering_generator import generate_chord_fingerings
from src.diagram_generator import generate_chord_diagram

# Generate fingerings
fingerings = generate_chord_fingerings("Cmaj7/E", max_results=3)
for f in fingerings:
    print(f"Fingering: {f.positions}")
    print(f"Difficulty: {f.difficulty:.2f}")

# Create diagram
fingering = fingerings[0]
generate_chord_diagram(fingering, "cmaj7_e.png")
```

## 📖 Command Line Interface

The CLI provides comprehensive chord generation and visualization capabilities.

### Commands Overview

#### `generate` - Generate Chord Fingerings
```bash
python -m src.cli generate [OPTIONS] CHORD

Options:
  -n, --max-results INTEGER   Maximum number of fingerings (default: 5)
  --format [text|json]       Output format (default: text)
  -o, --output PATH          Save output to file

Examples:
  python -m src.cli generate "Cmaj7"
  python -m src.cli generate "F#m7b5" -n 3
  python -m src.cli generate "Dm7/G" --format json -o dm7g.json
```

**Example Output:**
```
Chord: C

Fingering #1:
  Shape: x-3-2-0-1-0
  Fingers: 3-2-1
  Difficulty: 0.09
  Type: Open position
```

#### `diagram` - Create Visual Chord Diagrams
```bash
python -m src.cli diagram [OPTIONS] CHORD

Options:
  -o, --output PATH          Output file path (required)
  -f, --format [png|svg|pdf] Image format (default: png)
  --dpi INTEGER             Image resolution (default: 150)
  -n INTEGER                Use nth fingering (default: 1)

Examples:
  python -m src.cli diagram "F#" -o fsharp.png
  python -m src.cli diagram "Bb" -f svg -o bb.svg
  python -m src.cli diagram "Am7" --dpi 300 -o am7_print.png
```

#### `batch` - Process Multiple Chords
```bash
python -m src.cli batch [OPTIONS] INPUT_FILE

Options:
  -o, --output PATH          Output directory or file
  --grid                     Create single grid image
  -c, --columns INTEGER      Grid columns (default: 4)
  -f, --format [png|svg|pdf] Image format (default: png)
  --dpi INTEGER             Image resolution (default: 150)

Examples:
  # Generate individual diagrams
  python -m src.cli batch chords.txt -o diagrams/
  
  # Create chord sheet grid
  python -m src.cli batch chords.txt --grid -o sheet.png
  
  # Customize grid layout
  python -m src.cli batch chords.txt --grid -c 3 --dpi 300
```

**Input File Format:**
```
C
G7
Am
F#m7
Bmaj7/D#
# Comments are supported
```

#### `interactive` - Interactive Chord Explorer
```bash
python -m src.cli interactive

Interactive Commands:
  <chord>     - Generate fingerings (e.g., C, Am7, F#m7b5)
  list        - Show all fingerings for current chord
  save <n>    - Save fingering #n as diagram
  compare     - Generate side-by-side comparison
  help        - Show help
  quit        - Exit
```

## 🤖 MCP Integration (AI Assistant Support)

The project includes an MCP server for seamless integration with AI assistants like Claude.

### Installation

1. **Ensure the guitar-chord-generator package is installed in the project's virtual environment**:
   ```bash
   cd /path/to/fretboard-diagram-generator
   python -m venv venv  # Create venv if it doesn't exist
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   ```

### Configuration

#### Option 1: Virtual Environment Path (Recommended)

Use the full path to the MCP server in the project's virtual environment:

```json
{
  "mcpServers": {
    "guitar-chord-generator": {
      "command": "/path/to/fretboard-diagram-generator/venv/bin/guitar-chord-mcp-server",
      "args": [],
      "env": {},
      "disabled": false
    }
  }
}
```

On Windows, use:
```json
"command": "C:\\path\\to\\fretboard-diagram-generator\\venv\\Scripts\\guitar-chord-mcp-server.exe"
```

#### Option 2: Python Module Configuration

Run the server using the virtual environment's Python interpreter:

```json
{
  "mcpServers": {
    "guitar-chord-generator": {
      "command": "/path/to/fretboard-diagram-generator/venv/bin/python",
      "args": ["-m", "mcp_server"],
      "cwd": "/path/to/fretboard-diagram-generator",
      "env": {
        "PYTHONPATH": "/path/to/fretboard-diagram-generator"
      },
      "disabled": false
    }
  }
}
```

#### Option 3: Global Installation

Only if you've installed the package globally (not recommended):

```json
{
  "mcpServers": {
    "guitar-chord-generator": {
      "command": "guitar-chord-mcp-server",
      "args": [],
      "env": {},
      "disabled": false
    }
  }
}
```

### Using with Claude Desktop

1. **Copy the desired configuration to your Claude Desktop config directory**:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. **If you already have a config file, merge the `mcpServers` section into it**.

3. **Restart Claude Desktop for the changes to take effect**.

### Available MCP Tools

#### `generate_chord_fingerings`
Generate multiple fingerings for a chord with difficulty filtering.

**Parameters:**
- `chord_symbol` (string): Chord to generate (e.g., "Cmaj7/E")
- `max_results` (integer): Maximum fingerings to return (default: 5)
- `difficulty_filter` (number): Maximum difficulty 0.0-1.0 (optional)

#### `create_chord_diagram`
Generate visual chord diagram(s) in a single image. Supports 1-20 chords arranged in a grid layout.

**Parameters:**
- `fingering_specs` (array): Array of fingering specifications (1-20 items)
  - Each spec contains:
    - `positions`: Array of {string, fret, finger} objects
    - `chord_name`: Optional name to display on diagram
- `columns` (integer): Number of columns in grid layout (default: 4, range: 1-8)
- `format` (string): Output format "png" (default: "png")
- `dpi` (integer): Image resolution 72-600 (default: 150)
- `include_names` (boolean): Include chord names in diagrams (default: true)
- `file_path` (string): Optional file path to save the diagram

#### `analyze_chord_progression`
Analyze chord progressions with optimal fingering suggestions and voice leading.

**Parameters:**
- `chord_list` (array): List of chord symbols
- `analysis_type` (string): "fingerings", "theory", or "both" (default: "both")
- `max_per_chord` (integer): Max fingerings per chord (default: 2)

#### `get_chord_info`
Get detailed music theory information about a chord.

**Parameters:**
- `chord_symbol` (string): Chord to analyze
- `include_theory` (boolean): Include interval analysis (default: true)
- `include_alternatives` (boolean): Include alternative voicings (default: true)

### Example Usage with Claude

```
User: "Generate a diagram for F# major and explain the fingering"

Claude: I'll generate a chord diagram for F# major and explain the fingering.

[Uses create_chord_diagram tool]
[Uses get_chord_info tool]

Here's the F# major chord diagram. This is an E-shape barre chord at the 2nd fret:
- Fingering: 2-4-4-3-2-2 (low to high)
- Barre the 2nd fret with your index finger
- This pattern can be moved to any fret to create different major chords
```

### MCP Troubleshooting

- **Make sure the package is installed in the project's virtual environment**
- **Verify the path to the venv is correct in your configuration**
- **For debugging, run the server directly in a terminal**:
  ```bash
  /path/to/fretboard-diagram-generator/venv/bin/guitar-chord-mcp-server
  ```
- **The server logs to stderr, so check Claude's logs for any issues**
- **On Windows, remember to use backslashes in paths and add `.exe` to executables**

## 📚 Python API

### Core Classes

```python
from src.music_theory import Note, Chord
from src.fretboard import Fretboard, FretPosition
from src.fingering import Fingering, FingerAssignment
from src.fingering_generator import generate_chord_fingerings
from src.diagram_generator import ChordDiagramGenerator

# Parse chord symbols
chord = Chord.from_symbol("Cmaj7/E")
print(f"Root: {chord.root}, Quality: {chord.quality}")

# Generate fingerings
fingerings = generate_chord_fingerings("F#", max_results=3)
best_fingering = fingerings[0]

# Analyze fingering properties
print(f"Positions: {best_fingering.positions}")
print(f"Difficulty: {best_fingering.difficulty:.2f}")
print(f"Is barre chord: {best_fingering.characteristics.get('is_barre_chord')}")

# Create visual diagrams
generator = ChordDiagramGenerator()
generator.generate_diagram(best_fingering, "fsharp.png")
```

### Advanced Usage

```python
from src.chord_patterns import ChordPatternDatabase
from src.fingering import FingeringValidator

# Access chord pattern database
patterns = ChordPatternDatabase()
c_patterns = patterns.get_patterns_for_chord("C", "major")

# Validate fingerings
validator = FingeringValidator()
is_valid = validator.is_valid(fingering)
quality_score = validator.get_quality_score(fingering)

# Generate chord progression diagram
from src.diagram_generator import generate_chord_progression_diagram

chord_progression = ['G', 'C', 'D', 'Em']
generate_chord_progression_diagram(
    chord_symbols=chord_progression,
    output_path='progression.png',
    cols=4
)
```

## 📊 Supported Chord Types

### Basic Triads
- **Major**: C, D, E, F, G, A, B
- **Minor**: Cm, Dm, Em, Fm, Gm, Am, Bm  
- **Diminished**: Cdim, Ddim, etc.
- **Augmented**: Caug, Daug, etc.

### Extended Chords
- **7th Chords**: C7, Cmaj7, Cm7, Cm7b5, Cdim7
- **9th Chords**: C9, Cmaj9, Cm9, Cadd9
- **11th Chords**: C11, Cmaj11, Cm11
- **13th Chords**: C13, Cmaj13, Cm13

### Advanced Chords
- **Altered Dominants**: C7alt, C7#5, C7b9#11
- **Suspended**: Csus2, Csus4, C7sus4
- **Added Tones**: Cadd9, Cm6add9, Cmaj7add13
- **Slash Chords**: C/E, Dm7/G, Cmaj7/B

### Enharmonic Support
All chords support enharmonic equivalents:
- **Sharps**: F#, C#, G#, D#, A#
- **Flats**: Gb, Db, Ab, Eb, Bb
- **Context-Aware**: Chooses appropriate naming based on key context

## 🏗️ Architecture

### Core Components

- **`music_theory.py`**: Music theory foundation (notes, intervals, chords)
- **`chord_parser.py`**: Comprehensive chord symbol parsing
- **`fretboard.py`**: Guitar neck modeling and note mapping
- **`fingering.py`**: Fingering representation and validation
- **`fingering_generator.py`**: Core fingering generation algorithms
- **`chord_patterns.py`**: Database of standard chord patterns
- **`diagram_generator.py`**: Visual chord diagram creation
- **`cli.py`**: Command-line interface
- **`mcp_server.py`**: MCP integration layer

### Data Flow

```
Chord Symbol → Parser → Music Theory → Fretboard Mapping → 
Fingering Generation → Pattern Matching → Ranking → 
Output (Text/JSON/Diagram)
```

## 🧪 Testing

Comprehensive test suite with 165+ test cases:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_music_theory.py -v
python -m pytest tests/test_fingering_generator.py -v
python -m pytest tests/test_diagram_generator.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run MCP tests
python -m pytest tests/test_mcp_server.py -v
```

## 🛠️ Development

### Requirements
- **Python 3.10+** (tested with 3.10, 3.11, 3.12, 3.13)
- **matplotlib**: Visual diagram generation
- **click**: CLI framework
- **pytest**: Testing framework
- **mcp**: Model Context Protocol integration

### Project Structure
```
fretboard-diagram-generator/
├── src/                    # Source code
│   ├── __init__.py
│   ├── music_theory.py     # Core music theory
│   ├── chord_parser.py     # Chord symbol parsing  
│   ├── fretboard.py        # Guitar neck modeling
│   ├── fingering.py        # Fingering representation
│   ├── fingering_generator.py  # Generation algorithms
│   ├── chord_patterns.py   # Standard chord patterns
│   ├── diagram_generator.py    # Visual diagrams
│   ├── cli.py             # Command-line interface
│   ├── mcp_server.py      # MCP integration
│   └── mcp_server_standalone.py  # Standalone MCP executable
├── tests/                 # Test suite (165+ tests)
├── sample_diagrams/       # Example output
├── PROJECT_PLAN.md        # Detailed project roadmap
└── README.md             # This file
```

### Building from Fresh Checkout

```bash
# Clone repository
git clone https://github.com/username/fretboard-diagram-generator.git
cd fretboard-diagram-generator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .

# Run tests to verify
python -m pytest tests/ -v

# Try the CLI
guitar-chord-cli generate "C"

# Try the MCP server
guitar-chord-mcp-server --help
```

## 🔍 Troubleshooting

### Common Issues

**1. "command not found: guitar-chord-cli"**
```bash
# Ensure package is installed
pip install -e .

# Check installation
pip show guitar-chord-generator
```

**2. "ModuleNotFoundError: No module named 'matplotlib'"**
```bash
# Install all dependencies
pip install -r requirements.txt
```

**3. Claude Desktop not detecting MCP server**
```bash
# Verify configuration syntax
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Check MCP server runs without errors
guitar-chord-mcp-server 2>&1 | head -5
```

**4. Virtual environment issues**
```bash
# Ensure you're in the virtual environment
which python  # Should show venv/bin/python

# Reactivate if needed
source venv/bin/activate
```

## 📈 Performance

### Benchmarks
- **Chord Generation**: 50-100ms per chord (typical)
- **Batch Processing**: 10-20 chords/second
- **Diagram Creation**: 100-200ms per diagram
- **Memory Usage**: <50MB for typical operations

### Optimization Features
- **Pre-calculated position cache** for O(1) note lookups
- **Pattern matching prioritization** for common chords
- **Lazy loading** of chord pattern database
- **Efficient matplotlib usage** with figure recycling

## 🎯 Quality Metrics

### Fingering Quality Scoring
- **Standardness (50%)**: Matches known standard patterns
- **Technical Quality (25%)**: Playability, hand position, finger stretch
- **Musical Quality (25%)**: Voice leading, bass note correctness

### Visual Diagram Standards
- **Professional Layout**: Matches standard guitar chord book formatting
- **Barre Chord Detection**: Automatic detection with position markers
- **Consistent Spacing**: Uniform 5-fret display across all diagrams
- **Clear Notation**: Muted strings (x), finger numbers (1-4), fret markers

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Music Theory References**: Berklee College of Music chord theory materials
- **Standard Chord Charts**: Professional guitar chord book references
- **Guitar Community**: Feedback from guitarists and music educators
- **Open Source Libraries**: matplotlib, click, pytest, and the Python ecosystem

## 🎸 About

This project was created to bridge the gap between music theory and practical guitar playing. By combining algorithmic generation with music theory principles, it provides both beginners and advanced players with accurate, playable chord fingerings that match professional standards.

Whether you're learning your first chords, exploring advanced harmony, or building music applications, this tool provides the foundation for accurate guitar chord work.

---

**Happy Playing! 🎸🎵**