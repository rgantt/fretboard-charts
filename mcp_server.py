#!/usr/bin/env python3
"""
MCP Server for Guitar Chord Fingering Generator

Provides MCP (Model Context Protocol) integration for AI assistants like Claude
to generate guitar chord fingerings and visual chord diagrams.
"""

import asyncio
import json
import base64
import io
from typing import Any, Dict, List, Optional
import logging

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource, 
    Tool, 
    TextContent, 
    ImageContent, 
    EmbeddedResource,
    LoggingLevel
)
import mcp.types as types

# Import our core functionality
from .fingering_generator import generate_chord_fingerings
from .diagram_generator import generate_chord_diagram, ChordDiagramGenerator
from .music_theory import Chord
from .chord_parser import parse_chord
from .fingering import Fingering


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("guitar-chord-generator")


def format_fingering_for_output(fingering: Fingering) -> Dict[str, Any]:
    """Format a Fingering object for JSON output"""
    try:
        return {
            "positions": [{"string": pos.string, "fret": pos.fret} for pos in fingering.positions],
            "fingering_pattern": str(fingering),
            "difficulty": round(fingering.difficulty, 3),
            "characteristics": {
                "is_barre_chord": fingering.characteristics.get("is_barre_chord", False),
                "span": fingering.characteristics.get("span", 0),
                "hand_position": fingering.characteristics.get("hand_position", "unknown"),
                "requires_muting": len([pos for pos in fingering.positions if pos.fret == -1]) > 0
            },
            "finger_assignments": {
                str(string): finger.name if hasattr(finger, 'name') else str(finger)
                for string, finger in (fingering.finger_assignments or {}).items()
            },
            "chord_name": str(fingering.chord) if fingering.chord else "Unknown"
        }
    except Exception as e:
        logger.error(f"Error formatting fingering: {e}")
        return {
            "error": f"Failed to format fingering: {str(e)}",
            "positions": [],
            "fingering_pattern": "Error",
            "difficulty": 1.0
        }


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="generate_chord_fingerings",
            description="Generate multiple guitar fingerings for a chord symbol",
            inputSchema={
                "type": "object",
                "properties": {
                    "chord_symbol": {
                        "type": "string",
                        "description": "Chord symbol (e.g., 'Cmaj7', 'F#m7b5', 'Dm7/G')"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of fingerings to return",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 10
                    },
                    "difficulty_filter": {
                        "type": "number",
                        "description": "Maximum difficulty level (0.0-1.0, optional)",
                        "minimum": 0.0,
                        "maximum": 1.0
                    }
                },
                "required": ["chord_symbol"]
            }
        ),
        Tool(
            name="create_chord_diagram",
            description="Generate a visual chord diagram image. Provide either chord_symbol OR fingering_spec",
            inputSchema={
                "type": "object",
                "properties": {
                    "chord_symbol": {
                        "type": "string",
                        "description": "Chord symbol to generate diagram for (e.g., 'Cmaj7', 'F#m7b5')"
                    },
                    "fingering_spec": {
                        "type": "object",
                        "description": "Alternative to chord_symbol: specify exact fingering positions",
                        "properties": {
                            "positions": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "string": {"type": "integer", "minimum": 1, "maximum": 6},
                                        "fret": {"type": "integer", "minimum": 0, "maximum": 24}
                                    },
                                    "required": ["string", "fret"]
                                }
                            }
                        },
                        "required": ["positions"]
                    },
                    "format": {
                        "type": "string",
                        "enum": ["png", "svg"],
                        "default": "png",
                        "description": "Output image format"
                    },
                    "include_name": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include chord name in diagram"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="analyze_chord_progression",
            description="Analyze a chord progression with fingering suggestions",
            inputSchema={
                "type": "object",
                "properties": {
                    "chord_list": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of chord symbols"
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": ["fingerings", "theory", "both"],
                        "default": "both",
                        "description": "Type of analysis to perform"
                    },
                    "max_per_chord": {
                        "type": "integer",
                        "default": 2,
                        "minimum": 1,
                        "maximum": 5,
                        "description": "Maximum fingerings per chord"
                    }
                },
                "required": ["chord_list"]
            }
        ),
        Tool(
            name="get_chord_info",
            description="Get detailed music theory information about a chord",
            inputSchema={
                "type": "object",
                "properties": {
                    "chord_symbol": {
                        "type": "string",
                        "description": "Chord symbol to analyze"
                    },
                    "include_theory": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include music theory analysis"
                    },
                    "include_alternatives": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include alternative fingerings"
                    }
                },
                "required": ["chord_symbol"]
            }
        ),
        Tool(
            name="generate_chord_diagram_batch",
            description="Generate a single image containing multiple chord diagrams in a grid layout",
            inputSchema={
                "type": "object",
                "properties": {
                    "chord_list": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of chord symbols to generate diagrams for",
                        "minItems": 1,
                        "maxItems": 20
                    },
                    "fingering_specs": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "positions": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "string": {"type": "integer", "minimum": 1, "maximum": 6},
                                            "fret": {"type": "integer", "minimum": 0, "maximum": 24}
                                        },
                                        "required": ["string", "fret"]
                                    }
                                },
                                "chord_name": {
                                    "type": "string",
                                    "description": "Name to display for this chord diagram"
                                }
                            },
                            "required": ["positions"]
                        },
                        "description": "Alternative: List of specific fingering specifications instead of chord symbols",
                        "minItems": 1,
                        "maxItems": 20
                    },
                    "columns": {
                        "type": "integer",
                        "description": "Number of columns in the grid layout",
                        "default": 4,
                        "minimum": 1,
                        "maximum": 8
                    },
                    "format": {
                        "type": "string",
                        "description": "Output image format",
                        "enum": ["png"],
                        "default": "png"
                    },
                    "dpi": {
                        "type": "integer",
                        "description": "Image resolution in DPI",
                        "default": 150,
                        "minimum": 72,
                        "maximum": 600
                    },
                    "include_names": {
                        "type": "boolean",
                        "description": "Include chord names in diagrams",
                        "default": true
                    }
                },
                "oneOf": [
                    {"required": ["chord_list"]},
                    {"required": ["fingering_specs"]}
                ]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle MCP tool calls"""
    try:
        if name == "generate_chord_fingerings":
            return await handle_generate_fingerings(arguments)
        elif name == "create_chord_diagram":
            return await handle_create_diagram(arguments)
        elif name == "analyze_chord_progression":
            return await handle_analyze_progression(arguments)
        elif name == "get_chord_info":
            return await handle_get_chord_info(arguments)
        elif name == "generate_chord_diagram_batch":
            return await handle_generate_batch_diagram(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        logger.error(f"Error handling tool call {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_generate_fingerings(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle generate_chord_fingerings tool"""
    chord_symbol = arguments["chord_symbol"]
    max_results = arguments.get("max_results", 5)
    difficulty_filter = arguments.get("difficulty_filter")
    
    try:
        # Generate fingerings
        fingerings = generate_chord_fingerings(
            chord_symbol, 
            max_results=max_results
        )
        
        # Filter by difficulty if specified
        if difficulty_filter is not None:
            fingerings = [f for f in fingerings if f.difficulty <= difficulty_filter]
        
        if not fingerings:
            return [TextContent(
                type="text",
                text=f"No fingerings found for chord '{chord_symbol}'" + 
                     (f" with difficulty ≤ {difficulty_filter}" if difficulty_filter else "")
            )]
        
        # Format results
        results = {
            "chord_symbol": chord_symbol,
            "total_fingerings": len(fingerings),
            "fingerings": [format_fingering_for_output(f) for f in fingerings]
        }
        
        # Create readable summary
        summary_lines = [
            f"Generated {len(fingerings)} fingering(s) for {chord_symbol}:",
            ""
        ]
        
        for i, fingering in enumerate(fingerings, 1):
            summary_lines.append(f"{i}. {str(fingering)}")
            if fingering.characteristics.get("is_barre_chord"):
                summary_lines.append("   Type: Barre chord")
            summary_lines.append("")
        
        summary_text = "\n".join(summary_lines)
        json_data = json.dumps(results, indent=2)
        
        return [
            TextContent(type="text", text=summary_text),
            TextContent(type="text", text=f"\nDetailed JSON data:\n```json\n{json_data}\n```")
        ]
        
    except Exception as e:
        logger.error(f"Error generating fingerings for {chord_symbol}: {e}")
        return [TextContent(type="text", text=f"Error generating fingerings: {str(e)}")]


async def handle_create_diagram(arguments: Dict[str, Any]) -> List[types.TextContent | types.ImageContent]:
    """Handle create_chord_diagram tool"""
    chord_symbol = arguments.get("chord_symbol")
    fingering_spec = arguments.get("fingering_spec")
    format_type = arguments.get("format", "png")
    include_name = arguments.get("include_name", True)
    
    # Validate that exactly one of chord_symbol or fingering_spec is provided
    if not chord_symbol and not fingering_spec:
        return [TextContent(type="text", text="Error: Either chord_symbol or fingering_spec must be provided")]
    
    if chord_symbol and fingering_spec:
        return [TextContent(type="text", text="Error: Provide either chord_symbol OR fingering_spec, not both")]
    
    try:
        fingering = None
        
        if chord_symbol:
            # Generate fingering from chord symbol
            fingerings = generate_chord_fingerings(chord_symbol, max_results=1)
            if not fingerings:
                return [TextContent(type="text", text=f"No fingerings found for chord '{chord_symbol}'")]
            fingering = fingerings[0]
            
        elif fingering_spec:
            # Create fingering from specification
            from .fretboard import FretPosition, Fretboard
            from .music_theory import Note
            
            fretboard = Fretboard()
            positions = []
            for pos in fingering_spec["positions"]:
                # Get the note at this position
                note = fretboard.get_note_at_position(pos["string"], pos["fret"])
                positions.append(FretPosition(string=pos["string"], fret=pos["fret"], note=note))
            
            fingering = Fingering(positions=positions)
        
        # Generate diagram
        image_bytes = generate_chord_diagram(fingering, format=format_type)
        
        if not image_bytes:
            return [TextContent(type="text", text="Failed to generate diagram")]
        
        # Encode as base64
        base64_data = base64.b64encode(image_bytes).decode('utf-8')
        
        # Determine MIME type
        mime_type = f"image/{format_type}"
        
        chord_name = str(fingering.chord) if fingering.chord else chord_symbol or "Custom"
        
        return [
            TextContent(
                type="text", 
                text=f"Generated {format_type.upper()} chord diagram for {chord_name}"
            ),
            ImageContent(
                type="image",
                data=base64_data,
                mimeType=mime_type
            )
        ]
        
    except Exception as e:
        logger.error(f"Error creating diagram: {e}")
        return [TextContent(type="text", text=f"Error creating diagram: {str(e)}")]


async def handle_analyze_progression(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle analyze_chord_progression tool"""
    chord_list = arguments["chord_list"]
    analysis_type = arguments.get("analysis_type", "both")
    max_per_chord = arguments.get("max_per_chord", 2)
    
    try:
        results = {
            "progression": chord_list,
            "analysis_type": analysis_type,
            "chords": []
        }
        
        summary_lines = [
            f"Chord Progression Analysis: {' - '.join(chord_list)}",
            f"Analysis Type: {analysis_type}",
            ""
        ]
        
        for chord_symbol in chord_list:
            chord_analysis = {"chord_symbol": chord_symbol}
            
            # Add fingering analysis if requested
            if analysis_type in ["fingerings", "both"]:
                try:
                    fingerings = generate_chord_fingerings(chord_symbol, max_results=max_per_chord)
                    chord_analysis["fingerings"] = [format_fingering_for_output(f) for f in fingerings]
                    
                    summary_lines.append(f"🎵 {chord_symbol}:")
                    for i, f in enumerate(fingerings, 1):
                        summary_lines.append(f"  {i}. {str(f)}")
                    
                except Exception as e:
                    chord_analysis["fingering_error"] = str(e)
                    summary_lines.append(f"🎵 {chord_symbol}: Error generating fingerings")
            
            # Add theory analysis if requested
            if analysis_type in ["theory", "both"]:
                try:
                    chord = parse_chord(chord_symbol)
                    intervals = chord.get_intervals()
                    notes = chord.get_notes()
                    
                    chord_analysis["theory"] = {
                        "root": str(chord.root),
                        "quality": str(chord.quality),
                        "intervals": [str(interval) for interval in intervals],
                        "notes": [str(note) for note in notes],
                        "extensions": list(chord.extensions) if chord.extensions else [],
                        "bass_note": str(chord.bass) if chord.bass else None
                    }
                    
                    if analysis_type == "both":
                        summary_lines.append(f"  Theory: {chord.quality} chord with notes {', '.join(str(n) for n in notes)}")
                    
                except Exception as e:
                    chord_analysis["theory_error"] = str(e)
                    if analysis_type == "theory":
                        summary_lines.append(f"🎵 {chord_symbol}: Error analyzing theory")
            
            summary_lines.append("")
            results["chords"].append(chord_analysis)
        
        # Add progression-level insights
        if len(chord_list) > 1:
            summary_lines.append("💡 Progression Insights:")
            summary_lines.append(f"  - {len(chord_list)} chords total")
            
            # Count chord types
            if analysis_type in ["theory", "both"]:
                qualities = []
                for chord_data in results["chords"]:
                    if "theory" in chord_data:
                        qualities.append(chord_data["theory"]["quality"])
                
                if qualities:
                    unique_qualities = set(qualities)
                    summary_lines.append(f"  - Chord qualities: {', '.join(unique_qualities)}")
        
        summary_text = "\n".join(summary_lines)
        json_data = json.dumps(results, indent=2)
        
        return [
            TextContent(type="text", text=summary_text),
            TextContent(type="text", text=f"\nDetailed JSON data:\n```json\n{json_data}\n```")
        ]
        
    except Exception as e:
        logger.error(f"Error analyzing progression: {e}")
        return [TextContent(type="text", text=f"Error analyzing progression: {str(e)}")]


async def handle_get_chord_info(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle get_chord_info tool"""
    chord_symbol = arguments["chord_symbol"]
    include_theory = arguments.get("include_theory", True)
    include_alternatives = arguments.get("include_alternatives", True)
    
    try:
        results = {"chord_symbol": chord_symbol}
        summary_lines = [f"🎸 Chord Information: {chord_symbol}", ""]
        
        # Parse chord and get theory information
        if include_theory:
            try:
                chord = parse_chord(chord_symbol)
                intervals = chord.get_intervals()
                notes = chord.get_notes()
                
                theory_info = {
                    "root": str(chord.root),
                    "quality": str(chord.quality),
                    "intervals": [str(interval) for interval in intervals],
                    "notes": [str(note) for note in notes],
                    "extensions": list(chord.extensions) if chord.extensions else [],
                    "alterations": {str(k): str(v) for k, v in chord.alterations.items()} if chord.alterations else {},
                    "bass_note": str(chord.bass) if chord.bass else None
                }
                
                results["theory"] = theory_info
                
                summary_lines.extend([
                    "📚 Music Theory:",
                    f"  Root: {chord.root}",
                    f"  Quality: {chord.quality}",
                    f"  Notes: {', '.join(str(n) for n in notes)}",
                    f"  Intervals: {', '.join(str(i) for i in intervals)}"
                ])
                
                if chord.extensions:
                    summary_lines.append(f"  Extensions: {', '.join(map(str, chord.extensions))}")
                
                if chord.alterations:
                    alt_str = ', '.join(f"{interval}{alt}" for interval, alt in chord.alterations.items())
                    summary_lines.append(f"  Alterations: {alt_str}")
                
                if chord.bass:
                    summary_lines.append(f"  Bass Note: {chord.bass}")
                
                summary_lines.append("")
                
            except Exception as e:
                results["theory_error"] = str(e)
                summary_lines.append(f"❌ Theory analysis error: {str(e)}")
                summary_lines.append("")
        
        # Get alternative fingerings
        if include_alternatives:
            try:
                fingerings = generate_chord_fingerings(chord_symbol, max_results=5)
                results["fingerings"] = [format_fingering_for_output(f) for f in fingerings]
                
                summary_lines.append("🎯 Guitar Fingerings:")
                for i, fingering in enumerate(fingerings, 1):
                    summary_lines.append(f"  {i}. {str(fingering)}")
                    
                    characteristics = []
                    if fingering.characteristics.get("is_barre_chord"):
                        characteristics.append("barre chord")
                    if fingering.characteristics.get("hand_position"):
                        pos = fingering.characteristics["hand_position"]
                        if pos != "unknown":
                            characteristics.append(f"{pos} position")
                    
                    if characteristics:
                        summary_lines.append(f"     Type: {', '.join(characteristics)}")
                    
                    summary_lines.append("")
                
            except Exception as e:
                results["fingering_error"] = str(e)
                summary_lines.append(f"❌ Fingering generation error: {str(e)}")
        
        summary_text = "\n".join(summary_lines)
        json_data = json.dumps(results, indent=2)
        
        return [
            TextContent(type="text", text=summary_text),
            TextContent(type="text", text=f"\nDetailed JSON data:\n```json\n{json_data}\n```")
        ]
        
    except Exception as e:
        logger.error(f"Error getting chord info for {chord_symbol}: {e}")
        return [TextContent(type="text", text=f"Error getting chord info: {str(e)}")]


async def handle_generate_batch_diagram(arguments: Dict[str, Any]) -> List[types.TextContent | types.ImageContent]:
    """Handle generate_chord_diagram_batch tool"""
    chord_list = arguments.get("chord_list")
    fingering_specs = arguments.get("fingering_specs")
    columns = arguments.get("columns", 4)
    format_type = arguments.get("format", "png")
    dpi = arguments.get("dpi", 150)
    include_names = arguments.get("include_names", True)
    
    # Validate that exactly one of chord_list or fingering_specs is provided
    if chord_list is None and fingering_specs is None:
        return [TextContent(type="text", text="Error: Either chord_list or fingering_specs must be provided")]
    
    if chord_list is not None and fingering_specs is not None:
        return [TextContent(type="text", text="Error: Provide either chord_list OR fingering_specs, not both")]
    
    try:
        fingerings = []
        failed_items = []
        
        if chord_list:
            # Generate fingerings from chord symbols
            for chord_symbol in chord_list:
                try:
                    chord_fingerings = generate_chord_fingerings(chord_symbol, max_results=1)
                    if chord_fingerings:
                        fingering = chord_fingerings[0]
                        # Set chord name for diagram display if include_names is True
                        if include_names:
                            fingering.chord_name = chord_symbol
                        fingerings.append(fingering)
                    else:
                        failed_items.append(f"{chord_symbol}: No fingerings found")
                except Exception as e:
                    failed_items.append(f"{chord_symbol}: {str(e)}")
        
        elif fingering_specs:
            # Create fingerings from specifications
            from .fretboard import FretPosition, Fretboard
            from .music_theory import Note
            
            fretboard = Fretboard()
            
            for i, spec in enumerate(fingering_specs):
                try:
                    positions = []
                    for pos in spec["positions"]:
                        # Get the note at this position
                        note = fretboard.get_note_at_position(pos["string"], pos["fret"])
                        positions.append(FretPosition(string=pos["string"], fret=pos["fret"], note=note))
                    
                    fingering = Fingering(positions=positions)
                    
                    # Set chord name if provided and include_names is True
                    if include_names and "chord_name" in spec:
                        fingering.chord_name = spec["chord_name"]
                    elif include_names:
                        fingering.chord_name = f"Chord {i+1}"
                    
                    fingerings.append(fingering)
                    
                except Exception as e:
                    failed_items.append(f"Fingering {i+1}: {str(e)}")
        
        if not fingerings:
            error_msg = "No valid fingerings to process"
            if failed_items:
                error_msg += f". Failures: {'; '.join(failed_items)}"
            return [TextContent(type="text", text=error_msg)]
        
        # Generate batch diagram
        diagram_generator = ChordDiagramGenerator()
        image_bytes = diagram_generator.generate_multiple_diagrams(
            fingerings=fingerings,
            cols=columns,
            format=format_type,
            dpi=dpi
        )
        
        if not image_bytes:
            return [TextContent(type="text", text="Failed to generate batch diagram")]
        
        # Encode as base64
        base64_data = base64.b64encode(image_bytes).decode('utf-8')
        
        # Prepare response
        success_msg = f"Generated batch diagram with {len(fingerings)} chord(s)"
        if failed_items:
            success_msg += f". Failed items: {'; '.join(failed_items)}"
        
        response = [
            TextContent(type="text", text=success_msg),
            ImageContent(
                type="image",
                data=base64_data,
                mimeType=f"image/{format_type}"
            )
        ]
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating batch diagram: {e}")
        return [TextContent(type="text", text=f"Error generating batch diagram: {str(e)}")]


async def main():
    """Main entry point for MCP server"""
    # Import here to avoid circular imports during testing
    from mcp.server.stdio import stdio_server
    
    logger.info("Starting Guitar Chord Generator MCP Server")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="guitar-chord-generator",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())