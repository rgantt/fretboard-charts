# Guitar Chord Fingering Generator - Project Plan

## 🚀 Project Status Overview
- ✅ **Phase 1: Core Music Theory Foundation** - COMPLETE
- ✅ **Phase 2: Fretboard Modeling** - COMPLETE  
- 🔄 **Phase 3: Fingering Generation** - IN PROGRESS
- ⏳ **Phase 4: CLI & MCP Integration** - PENDING

**Current Test Status**: 93/93 tests passing (100% success rate)

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

### 🔄 Phase 3: Fingering Generation - NEXT
**Goal**: Generate practical, playable fingerings

#### Tasks:
1. ⏳ **Algorithmic Fingering Search**
   - Implement systematic fingering generation
   - Apply chord tone requirements
   - Generate multiple candidate fingerings

2. ⏳ **Ergonomic Filtering**
   - Define playability constraints
   - Filter impossible or impractical fingerings
   - Add difficulty scoring metrics

3. ⏳ **Ranking and Selection**
   - Implement fingering quality scoring
   - Prioritize common patterns and positions
   - Return top N fingerings ordered by preference

#### Deliverables:
- ⏳ `fingering_generator.py`: Core generation algorithm
- ⏳ `constraints.py`: Playability rules and scoring  
- ⏳ Performance optimization and caching

#### 💡 Ready to Start:
- All foundational components are complete and tested
- Fingering validation and scoring systems already implemented
- Can leverage existing difficulty calculation and playability checks
- Position lookup and chord-to-notes conversion fully functional

### ⏳ Phase 4: CLI & MCP Integration - PENDING
**Goal**: Create usable tools with both standalone and MCP interfaces

#### Tasks:
1. ⏳ **Standalone CLI Tool**
   - Implement command-line interface with `click`
   - Add comprehensive help and examples
   - Include batch processing capabilities

2. ⏳ **MCP Server Integration**
   - Create MCP wrapper maintaining tool decoupling
   - Implement proper error handling for MCP context
   - Add tool descriptions and parameter validation

3. ⏳ **Testing and Validation**
   - Create comprehensive test suite
   - Test against real-world chord progressions
   - Performance testing and optimization

#### Deliverables:
- ⏳ `cli.py`: Standalone command-line tool
- ⏳ `mcp_server.py`: MCP integration layer
- ⏳ Complete test suite and documentation

#### 🎯 Dependencies:
- Requires Phase 3 (Fingering Generation) to be complete
- Will integrate all existing modules into user-facing interfaces

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
