# Guitar Chord Fingering Generator - Claude Reference Guide

## Quick Start for Claude

This is a Python guitar chord fingering generator with CLI and MCP interfaces. When working with this project, remember these key points:

### Project Location
- **Working directory**: `/Users/ryangantt/Documents/workspaces/fretboard-diagram-generator`
- **Virtual environment**: `venv/` (always activate first!)
- **Python version**: 3.10+ (tested with 3.13)

### Essential Commands to Remember

#### 1. Activate Virtual Environment (ALWAYS DO THIS FIRST)
```bash
cd /Users/ryangantt/Documents/workspaces/fretboard-diagram-generator
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 2. Running the CLI Tool
```bash
# The package is installed in editable mode, so these commands work:
guitar-chord-cli generate "C"
guitar-chord-cli generate "F#m7" -n 5
guitar-chord-cli diagram "Am" -o am.png
guitar-chord-cli batch chords.txt --grid -o sheet.png
guitar-chord-cli interactive

# Alternative: Run directly with Python
python -m src.cli generate "C"
python cli.py generate "C"
```

#### 3. Running the MCP Server
```bash
# The MCP server is installed as a console script:
guitar-chord-mcp-server

# Alternative ways to run:
python mcp_server.py
python -m mcp_server

# For testing/debugging:
/Users/ryangantt/Documents/workspaces/fretboard-diagram-generator/venv/bin/guitar-chord-mcp-server
```

#### 4. Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test files
python -m pytest tests/test_fingering_generator.py -v
python -m pytest tests/test_mcp_server.py -v
python -m pytest tests/test_diagram_generator.py -v

# Run with shorter output
python -m pytest tests/ --tb=short

# Check test coverage
python -m pytest tests/ --cov=src --cov-report=html
```

## Project Structure

### Core Modules (in `src/`)
- **`music_theory.py`**: Note, Chord, interval calculations
- **`chord_parser.py`**: Parse chord symbols like "Cmaj7/E", "F#m7b5"
- **`fretboard.py`**: Guitar neck model, note-to-position mapping
- **`fingering.py`**: Fingering representation and validation
- **`fingering_generator.py`**: Core fingering generation algorithm
- **`chord_patterns.py`**: Database of standard chord patterns
- **`diagram_generator.py`**: Visual chord diagram creation
- **`cli.py`**: Command-line interface (top level, not in src/)
- **`mcp_server.py`**: MCP server for AI integration (top level)

### Key Classes to Know
```python
from src.music_theory import Note, Chord
from src.chord_parser import parse_chord, quick_parse
from src.fretboard import Fretboard, FretPosition
from src.fingering import Fingering, FingeringValidator
from src.fingering_generator import FingeringGenerator, generate_chord_fingerings
from src.diagram_generator import ChordDiagramGenerator, generate_chord_diagram
from src.chord_patterns import ChordPatternDatabase
```

## MCP Server Details

### Available MCP Tools
1. **`generate_chord_fingerings`**: Generate fingerings for a chord
   - Parameters: `chord_symbol`, `max_results`, `difficulty_filter`
   
2. **`create_chord_diagram`**: Create visual chord diagram
   - Parameters: `chord_symbol` OR `fingering_spec`, `format`, `include_name`, `file_path`
   
3. **`analyze_chord_progression`**: Analyze chord progressions
   - Parameters: `chord_list`, `analysis_type`, `max_per_chord`
   
4. **`get_chord_info`**: Get chord theory information
   - Parameters: `chord_symbol`, `include_theory`, `include_alternatives`
   
5. **`generate_chord_diagram_batch`**: Create multiple chord diagrams in grid
   - Parameters: `fingering_specs`, `columns`, `dpi`, `format`, `include_names`, `file_path`

### MCP Configuration Example
```json
{
  "mcpServers": {
    "guitar-chord-generator": {
      "command": "/Users/ryangantt/Documents/workspaces/fretboard-diagram-generator/venv/bin/guitar-chord-mcp-server",
      "args": [],
      "env": {},
      "disabled": false
    }
  }
}
```

## Common Code Patterns

### Generate Fingerings
```python
from src.fingering_generator import generate_chord_fingerings

# Generate fingerings for a chord
fingerings = generate_chord_fingerings("Cmaj7", max_results=5)
for f in fingerings:
    print(f"Pattern: {f}, Difficulty: {f.difficulty:.3f}")
```

### Create Chord Diagram
```python
from src.diagram_generator import generate_chord_diagram

# Create a diagram from chord symbol
generate_chord_diagram("F#", "fsharp.png")

# Create from specific fingering
fingering = fingerings[0]
generate_chord_diagram(fingering, "chord.png", format="png", dpi=150)
```

### Parse Chord Symbols
```python
from src.chord_parser import quick_parse

chord = quick_parse("Cmaj7/E")
print(f"Root: {chord.root}, Quality: {chord.quality}, Bass: {chord.bass}")
```

## Important Implementation Notes

### Fingering Format
- **Positions**: List of (string, fret) tuples, where string=1-6 (low to high), fret=-1 (muted), 0 (open), 1-24 (fretted)
- **String notation**: `x-3-2-0-1-0` means: muted, 3rd fret, 2nd fret, open, 1st fret, open
- **Finger assignments**: 0=open, 1=index, 2=middle, 3=ring, 4=pinky

### Chord Pattern Database
The system includes standard patterns for common open chords:
- Major: C, G, D, A, E, F
- Minor: Am, Em, Dm
- 7th: G7, C7, D7, A7, E7
- Minor 7th: Am7, Em7, Dm7

### Barre Chord Support
- E-shape and A-shape barre patterns
- Automatic transposition to any fret
- Fret markers ("2fr", "5fr") for positions above 1st fret

### Testing Approach
- **165+ test cases** covering all modules
- Test files mirror source structure (test_*.py)
- Run with pytest, not unittest
- MCP tests use async testing

## Troubleshooting

### Common Issues & Solutions

1. **"command not found: guitar-chord-cli"**
   - Activate virtual environment first
   - Check installation: `pip show guitar-chord-generator`
   - Reinstall if needed: `pip install -e .`

2. **Import errors**
   - Always work from project root directory
   - Ensure virtual environment is activated
   - Check PYTHONPATH includes project root

3. **MCP server not working**
   - Test directly: `guitar-chord-mcp-server`
   - Check for port conflicts
   - Verify MCP package installed: `pip show mcp`

4. **Test failures**
   - Run from project root
   - Use pytest, not python -m unittest
   - Check matplotlib backend for diagram tests

## Dependencies

### Core Requirements
- **Python**: 3.10+ (project uses 3.13 features)
- **matplotlib**: >=3.5.0 (diagram generation)
- **click**: >=8.0.0 (CLI framework)
- **mcp**: >=1.12.0 (MCP server)
- **pytest**: >=7.0.0 (testing)

### Installation
```bash
# Install all dependencies
pip install -r requirements.txt

# Install package in editable mode (required for CLI/MCP)
pip install -e .
```

## Development Workflow

### Making Changes
1. Always activate virtual environment first
2. Make changes to relevant files
3. Run tests to verify: `python -m pytest tests/ -v`
4. Test CLI manually: `guitar-chord-cli generate "C"`
5. Test MCP if needed: `guitar-chord-mcp-server`

### Adding New Features
1. Update relevant module in `src/`
2. Add/update tests in `tests/`
3. Update CLI in `cli.py` if needed
4. Update MCP tools in `mcp_server.py` if needed
5. Run full test suite

### Code Style
- Type hints throughout
- Comprehensive docstrings
- No unnecessary comments unless requested
- Follow existing patterns in codebase

## Quick Reference Card

```bash
# Environment setup
cd /Users/ryangantt/Documents/workspaces/fretboard-diagram-generator
source venv/bin/activate

# CLI usage
guitar-chord-cli generate "Am7"                    # Generate fingerings
guitar-chord-cli diagram "F#" -o fsharp.png       # Create diagram
guitar-chord-cli interactive                       # Interactive mode

# MCP server
guitar-chord-mcp-server                           # Run MCP server

# Testing
python -m pytest tests/ -v                        # Run all tests
python -m pytest tests/test_mcp_server.py -v      # Test MCP

# Python usage
python -c "from src.fingering_generator import generate_chord_fingerings; print(generate_chord_fingerings('C')[0])"
```

## Remember for Next Session

When you (Claude) open this project next time:
1. Check this CLAUDE.md file first
2. Activate the virtual environment
3. The package is already installed in editable mode
4. Use `guitar-chord-cli` and `guitar-chord-mcp-server` commands
5. Run tests with `python -m pytest tests/ -v`
6. All core functionality is in `src/` directory
7. MCP tools are already configured and working