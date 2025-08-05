# Guitar Chord Fingering Generator - Project Plan

## 🚀 Project Status Overview
- ✅ **Phase 1: Core Music Theory Foundation** - COMPLETE
- ✅ **Phase 2: Fretboard Modeling** - COMPLETE  
- ✅ **Phase 3: Fingering Generation** - COMPLETE
- ✅ **Phase 3.5: Visual Diagram Generation** - COMPLETE
- ⏳ **Phase 4a: CLI Tool** - PENDING
- ⏳ **Phase 4b: MCP Server Integration** - PENDING

**Current Test Status**: 152/152 tests passing (100% success rate)

## Project Overview

This project creates two complementary tools for guitar chord diagram generation:

1. **Chord-to-Fingerings Tool**: Given a chord name (e.g., "Cmaj7/E"), generate all valid guitar fingerings
2. **Fingering-to-Diagram Tool**: Given a fingering specification, generate a visual fretboard diagram

### Target Audience
- Beginner to intermediate guitar players
- Musicians learning chord theory and fretboard navigation
- Anyone needing practical, theoretically-sound chord fingerings

### Guitar Specifications
- Standard 6-string guitar
- 24 frets (updated from original 22-fret spec)
- Standard tuning: E-A-D-G-B-E (low to high)
- Focus on playable, ergonomic fingerings

### Supported Chord Types
- Major, minor, diminished, augmented
- Extensions: 7th, 9th, 11th, 13th
- Alterations: add, sus, altered dominants
- Slash chords (particularly important for fingerstyle playing)
- Complex notation: "Cmaj7", "F#m7b5", "Dm7/G", etc.

## Design Approach: Rule-Based Musical Theory

### Why This Approach?
After evaluating multiple implementation patterns, we chose the rule-based musical theory approach because:

- **Theoretically Sound**: Generates fingerings based on actual music theory
- **Practical for Target Users**: Focuses on commonly-used, learnable patterns
- **Extensible**: Can handle complex chord types algorithmically
- **Reliable**: Produces consistent, predictable results

### Alternative Approaches Considered
1. **Database Approach**: Pre-curated fingerings (limited scope, maintenance overhead)
2. **Algorithmic Search**: Brute-force generation (computationally expensive, impractical results)
3. **Hybrid System**: Templates + algorithms (complex architecture)
4. **Position-Aware**: Multiple subsystems per fretboard region (maintenance complexity)

## Technical Architecture

### Core Components

#### 1. Chord Symbol Parser
**Purpose**: Convert chord names into structured musical data
**Input**: "Cmaj7/E", "F#m7b5", "Dm7add9"
**Output**: `{root: Note, quality: str, extensions: [int], bass: Note?}`
**Features**:
- Handle notation variations ("Cmaj7" = "CM7" = "C△7")
- Parse slash chord notation
- Validate input and provide helpful error messages
- Support enharmonic equivalents (F# = Gb)

#### 2. Music Theory Engine
**Purpose**: Convert chord symbols to sets of required notes
**Features**:
- Apply interval patterns (maj7 = [1, 3, 5, 7])
- Handle chord extensions and alterations
- Manage voice leading preferences
- Account for guitar's polyphonic limitations

#### 3. Fretboard Mapping System
**Purpose**: Model the guitar neck and map notes to positions
**Features**:
- String/fret coordinate system
- Note-to-position mapping across all strings
- Open string handling
- Fret range management (0-24 frets)

#### 4. Fingering Generation Engine
**Purpose**: Create playable fingerings that contain required chord tones
**Features**:
- Generate candidate fingerings algorithmically
- Apply ergonomic constraints (finger stretch, hand position)
- Prioritize common positions (open chords, barre patterns)
- Handle optional notes and doubling preferences

#### 5. Fingering Ranking & Filtering System
**Purpose**: Select and order the best fingerings
**Criteria**:
- Playability (hand span, finger independence)
- Commonality (frequently-used patterns)
- Musical quality (voice leading, bass note prominence)
- Difficulty level (beginner-friendly prioritization)

### Data Structures

```python
# Core data representations
class Note:
    """Pitch class with enharmonic awareness"""
    pitch_class: int  # 0-11 (C=0, C#=1, etc.)
    name: str         # "C", "F#", "Bb"

class Chord:
    """Structured chord representation"""
    root: Note
    quality: str           # "maj", "min", "dim", "aug"
    extensions: List[int]  # [7, 9, 11, 13]
    alterations: Dict[int, str]  # {5: "b", 9: "#"}
    bass: Optional[Note]   # For slash chords

class Fingering:
    """Guitar fingering representation"""
    positions: List[Tuple[int, int]]  # [(string, fret), ...]
    fingers: List[int]                # [0=open, 1-4=fingers, -1=muted]
    muted_strings: List[int]          # [1, 6] for muted strings
    difficulty: float                 # 0.0-1.0 difficulty score
```

### Technical Stack

- **Language**: Python 3.13+ (tested with 3.13.2)
- **Music Theory**: Custom implementation (decided against `music21` for lighter dependencies)
- **CLI Interface**: `click` for command-line tools
- **MCP Integration**: Official MCP Python SDK
- **Testing**: `pytest` with comprehensive test coverage (93/93 tests passing)
- **Documentation**: Type hints and docstrings throughout

## Implementation Plan

### ✅ Phase 1: Core Music Theory Foundation - COMPLETE
**Goal**: Build the musical knowledge base

#### Tasks:
1. ✅ **Note and Interval System**
   - ✅ Implement Note class with enharmonic handling
   - ✅ Create interval calculations and chord theory rules
   - ✅ Add chromatic and diatonic interval support

2. ✅ **Chord Symbol Parser**
   - ✅ Build comprehensive regex-based parser
   - ✅ Handle all common notation variations
   - ✅ Create extensive test suite with edge cases
   - ✅ Add validation and error reporting

3. ✅ **Chord-to-Intervals Conversion**
   - ✅ Map chord qualities to interval patterns
   - ✅ Handle extensions and alterations
   - ✅ Support slash chord bass note specification
   - ✅ Validate against known chord progressions

#### Deliverables:
- ✅ `music_theory.py`: Core musical classes and functions (327 lines)
- ✅ `chord_parser.py`: Symbol parsing and validation (408 lines)
- ✅ Test suite covering common and edge-case chords (40+ test cases)

#### 📝 Implementation Notes:
- **Custom Implementation**: Built custom music theory engine instead of using `music21` for better control and lighter dependencies
- **Enharmonic Support**: Full enharmonic equivalency handling (F# = Gb) with context-aware naming
- **Complex Parsing**: Successfully handles advanced notation like "F#m7b5/A", "C7alt", "Bbmaj7#11"
- **Comprehensive Coverage**: Supports all common chord types plus extended and altered chords
- **Error Handling**: Robust validation with helpful error messages and suggestions

### ✅ Phase 2: Fretboard Modeling - COMPLETE
**Goal**: Model the guitar and map musical concepts to physical positions

#### Tasks:
1. ✅ **Guitar Fretboard Model**
   - ✅ Implement string/fret coordinate system
   - ✅ Model standard tuning with configurable alternatives
   - ✅ Handle fret range and capo support

2. ✅ **Note-to-Position Mapping**
   - ✅ Calculate all positions for any given note
   - ✅ Handle open strings and fretted positions
   - ✅ Optimize for lookup performance

3. ✅ **Fingering Representation**
   - ✅ Design fingering data structure
   - ✅ Implement fingering validation
   - ✅ Add basic playability constraints

#### Deliverables:
- ✅ `fretboard.py`: Guitar neck modeling (326 lines)
- ✅ `fingering.py`: Fingering representation and validation (449 lines)
- ✅ Position lookup optimizations with caching

#### 📝 Implementation Notes:
- **Extended Fret Range**: Supports 0-24 frets (updated from original 22-fret spec) for modern guitars
- **Performance Optimization**: Pre-calculated position cache for O(1) note-to-position lookups
- **Advanced Fingering Features**: 
  - Automatic barre chord detection
  - Difficulty scoring algorithm (0.0-1.0 scale)
  - Fingering characteristics analysis (span, hand position, finger usage)
  - Musical quality validation (bass note correctness, voice leading)
- **Comprehensive Validation**: FingeringValidator with playability and musical quality checks
- **Tuning Support**: Standard and Drop D tunings implemented, extensible for other tunings
- **Integration Testing**: Full integration between fretboard and fingering modules verified

### ✅ Phase 3: Fingering Generation - COMPLETE
**Goal**: Generate practical, playable fingerings

#### Tasks:
1. ✅ **Algorithmic Fingering Search**
   - ✅ Implement systematic fingering generation
   - ✅ Apply chord tone requirements
   - ✅ Generate multiple candidate fingerings

2. ✅ **Ergonomic Filtering**
   - ✅ Define playability constraints
   - ✅ Filter impossible or impractical fingerings
   - ✅ Add difficulty scoring metrics

3. ✅ **Ranking and Selection**
   - ✅ Implement fingering quality scoring
   - ✅ Prioritize common patterns and positions
   - ✅ Return top N fingerings ordered by preference

#### Deliverables:
- ✅ `fingering_generator.py`: Core generation algorithm (376 lines)
- ✅ `chord_patterns.py`: Common chord pattern database (325 lines)
- ✅ Enhanced `fingering.py`: Added standardness validation (130+ additional lines)
- ✅ Comprehensive test coverage (37+ test cases including standardness validation tests)

#### 📝 Implementation Notes:
- **Hybrid Algorithm**: Successfully combined position-based search with pattern matching
- **Chord Pattern Database**: Built database of 15+ common open chord patterns (C, G, D, A, E, Am, Em, Dm, G7, C7, Am7)
- **Priority System**: Implemented chord tone priority (root > 3rd > 7th > 5th > extensions)
- **Regional Search**: Searches open position (0-4), low position (2-7), and mid position (5-12)
- **Post-Processing**: Smart finger assignment using position-based heuristics
- **Quality Integration**: Leverages existing FingeringValidator for comprehensive quality assessment
- **Performance**: Generates 3-5 quality fingerings per chord in milliseconds

#### 🎯 **Standardness Validation Enhancement** (Post-Implementation Addition):
**Problem Identified**: Initial system generated technically correct but non-standard fingerings. Standard patterns like C major (x-3-2-0-1-0) ranked 3rd behind incomplete 3-note versions.

**Solution Implemented**:
- **Standardness Scoring System**: Added `_check_standardness()` method with 50% weight in overall scoring
- **Pattern Matching Bonus**: Perfect score (1.0) for fingerings matching known standard patterns  
- **Completeness Bonus**: +0.2 for 5-6 note chords, +0.1 for 4-note chords, -0.1 for incomplete 3-note versions
- **Musical Intelligence**: Bass note correctness (+0.1), open position priority for common chords (+0.15)
- **Weighted Scoring**: Rebalanced to Standardness 50%, Technical 25%, Musical 25%

**Results Achieved**:
- **Before**: C major `x-3-x-0-x-0` (3 notes) ranked #1  
- **After**: C major `x-3-2-0-1-0` (5 notes, standard) ranked #1 with score 1.000 ✅
- **All standard open chords** (C, G, Am, Em, Dm, G7, Am7) now rank first with perfect scores
- **130/130 tests passing** including 7 dedicated standardness validation tests
- **System generates what guitarists actually expect and use**

### ✅ Phase 3.5: Visual Diagram Generation - COMPLETE
**Goal**: Generate visual chord diagrams matching standard guitar chord book format

#### Tasks:
1. ✅ **Visual Diagram Engine**
   - ✅ Implement chord diagram image generation using matplotlib/PIL
   - ✅ Support standard elements: strings, frets, finger positions, muted/open strings
   - ✅ Add chord name labels and fret position markers (2fr, 3fr, etc.)

2. ✅ **Fingering Integration**
   - ✅ Convert Fingering objects to visual representations
   - ✅ Handle both open position and higher fret diagrams
   - ✅ Automatic positioning and scaling for different chord types

3. ✅ **Output Formats**
   - ✅ PNG/SVG image generation for web and print use
   - ✅ Batch generation for multiple fingerings
   - ✅ Integration with existing text-based chord shapes

#### Deliverables:
- ✅ `diagram_generator.py`: Visual diagram generation engine (543 lines)
- ✅ Image export functionality (PNG, SVG, PDF formats)
- ✅ Comprehensive test coverage (22 test cases)

#### 📝 Implementation Notes:
- **Professional Quality**: Generates diagrams matching standard guitar chord book appearance
- **Multiple Formats**: Supports PNG, SVG, and PDF output with configurable DPI
- **Flexible Layout**: Automatically handles open position and higher fret diagrams
- **Batch Generation**: Can create grids of multiple chord diagrams
- **Convenience Functions**: Easy-to-use functions for single chords and progressions
- **Complete Integration**: Seamlessly works with existing Fingering objects
- **Sample Output**: Generated 11 sample diagrams for visual verification

#### 🎯 Visual Requirements (from example-diagrams.jpg): ✅ ACHIEVED
- ✅ **Grid Structure**: 6 strings × 4-5 frets with clean lines
- ✅ **Standard Notation**: "x" for muted, "o" for open, dots for fretted positions
- ✅ **Finger Numbers**: 1-4 finger indicators below diagram
- ✅ **Position Markers**: Fret position labels for non-open positions (e.g., "3fr")
- ✅ **Professional Styling**: Matches standard guitar chord book appearance

### ⏳ Phase 4a: CLI Tool - PENDING
**Goal**: Create standalone command-line interface

#### Tasks:
1. ⏳ **Command-Line Interface**
   - Implement CLI with `click` framework
   - Add comprehensive help and examples
   - Support both text and visual diagram output

2. ⏳ **Batch Processing**
   - Process multiple chords from files or arguments
   - Generate chord progression diagrams
   - Export options for different formats

3. ⏳ **User Experience**
   - Interactive chord exploration mode
   - Fingering comparison and selection
   - Progress indication for batch operations

#### Deliverables:
- ⏳ `cli.py`: Main command-line application
- ⏳ Command documentation and help system
- ⏳ Example usage and tutorials

### ⏳ Phase 4b: MCP Server Integration - PENDING  
**Goal**: Create MCP server for Claude integration

#### Tasks:
1. ⏳ **MCP Server Implementation**
   - Create MCP wrapper maintaining tool decoupling
   - Implement proper error handling for MCP context
   - Add tool descriptions and parameter validation

2. ⏳ **Tool Integration**
   - Expose chord generation and diagram creation as MCP tools
   - Support both text and image responses
   - Handle complex chord progression requests

3. ⏳ **Testing and Validation**
   - Test MCP integration with Claude
   - Performance testing and optimization
   - Real-world usage validation

#### Deliverables:
- ⏳ `mcp_server.py`: MCP integration layer
- ⏳ MCP tool definitions and documentation
- ⏳ Integration test suite

#### 🎯 Dependencies:
- Requires Phase 3.5 (Visual Diagrams) for complete functionality
- Requires Phase 4a (CLI) for command-line tool integration

## Key Requirements and Constraints

### Functional Requirements
- Support all common chord types and extensions
- Generate multiple fingering options per chord
- Prioritize beginner-friendly fingerings
- Handle slash chords for fingerstyle applications
- Provide clear error messages for invalid input

### Technical Requirements
- Maintain separation between CLI and MCP interfaces
- Ensure fast response times (< 1 second for common chords)
- Comprehensive error handling and validation
- Extensive test coverage for reliability
- Clean, maintainable code architecture

### User Experience Requirements
- Intuitive chord notation parsing
- Clear fingering output format
- Helpful error messages and suggestions
- Consistent behavior across interfaces

## Future Enhancements
- Visual fretboard diagram generation (Phase 5)
- Alternative tuning support
- Chord progression analysis
- MIDI output for audio playback
- Web interface for broader accessibility

## Success Metrics
- Accurate fingering generation for 95%+ of common chords
- Response time under 1 second for typical requests
- Clean, maintainable codebase with >90% test coverage
- Positive user feedback on fingering quality and practicality
