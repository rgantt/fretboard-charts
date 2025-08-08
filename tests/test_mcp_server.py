"""
Tests for the MCP (Model Context Protocol) Server
"""

import pytest
import asyncio
import json
import base64
from typing import Any, Dict, List

# Import test utilities
from src.fingering import Fingering

# Import MCP server components
from mcp_server import (
    handle_list_tools,
    handle_generate_fingerings,
    handle_create_diagram,
    handle_analyze_progression,
    handle_get_chord_info,
    format_fingering_for_output
)

# Import MCP types for testing
from mcp.types import TextContent, ImageContent


class TestMCPToolList:
    """Test MCP tool listing functionality"""
    
    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test that all expected MCP tools are listed"""
        tools = await handle_list_tools()
        
        # Check all expected tools are present
        expected_tools = {
            "generate_chord_fingerings",
            "create_chord_diagram", 
            "analyze_chord_progression",
            "get_chord_info"
        }
        
        tool_names = {tool.name for tool in tools}
        assert tool_names == expected_tools
        
        # Check each tool has required fields
        for tool in tools:
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            assert hasattr(tool, 'inputSchema')
            
            # Validate input schema structure
            schema = tool.inputSchema
            assert 'type' in schema
            assert schema['type'] == 'object'
            assert 'properties' in schema
            assert 'required' in schema


class TestGenerateFingeringsHandler:
    """Test generate_chord_fingerings MCP tool"""
    
    @pytest.mark.asyncio
    async def test_generate_fingerings_basic(self):
        """Test basic chord fingering generation"""
        args = {"chord_symbol": "C"}
        result = await handle_generate_fingerings(args)
        
        # Should return a list with one TextContent item
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        
        # Parse the JSON response
        response_data = json.loads(result[0].text)
        assert 'chord' in response_data
        assert 'fingerings' in response_data
        assert response_data['chord'] == 'C'
        assert len(response_data['fingerings']) > 0
        
        # Check fingering structure
        fingering = response_data['fingerings'][0]
        assert 'positions' in fingering
        assert 'fingering_pattern' in fingering
        assert 'difficulty' in fingering
    
    @pytest.mark.asyncio
    async def test_generate_fingerings_with_max_results(self):
        """Test limiting number of results"""
        args = {
            "chord_symbol": "Am",
            "max_results": 3
        }
        result = await handle_generate_fingerings(args)
        
        response_data = json.loads(result[0].text)
        assert len(response_data['fingerings']) <= 3
    
    @pytest.mark.asyncio
    async def test_generate_fingerings_with_difficulty_filter(self):
        """Test difficulty filtering"""
        args = {
            "chord_symbol": "F",
            "difficulty_filter": 0.5
        }
        result = await handle_generate_fingerings(args)
        
        response_data = json.loads(result[0].text)
        
        # All returned fingerings should have difficulty <= 0.5
        for fingering in response_data['fingerings']:
            assert fingering['difficulty'] <= 0.5
    
    @pytest.mark.asyncio
    async def test_generate_fingerings_invalid_chord(self):
        """Test handling of invalid chord symbols"""
        args = {"chord_symbol": "InvalidChord123"}
        result = await handle_generate_fingerings(args)
        
        # Should return error message
        assert len(result) == 1
        assert "Error" in result[0].text


class TestCreateDiagramHandler:
    """Test create_chord_diagram MCP tool"""
    
    @pytest.mark.asyncio
    async def test_create_diagram_with_fingering_specs(self):
        """Test diagram creation with fingering specifications"""
        args = {
            "fingering_specs": [
                {
                    "positions": [
                        {"string": 1, "fret": 0},
                        {"string": 2, "fret": 1},
                        {"string": 3, "fret": 0},
                        {"string": 4, "fret": 2},
                        {"string": 5, "fret": 3}
                    ],
                    "chord_name": "C Major"
                }
            ],
            "format": "png",
            "include_names": True
        }
        
        result = await handle_create_diagram(args)
        
        # Should return text and image content
        assert len(result) == 2
        assert isinstance(result[0], TextContent)
        assert isinstance(result[1], ImageContent)
        
        # Check text content
        assert "Generated batch diagram with 1 chord(s)" in result[0].text
        
        # Check image content
        assert result[1].mimeType == "image/png"
        assert len(result[1].data) > 0
        
        # Verify base64 encoding
        try:
            base64.b64decode(result[1].data)
        except:
            pytest.fail("Image data should be valid base64")


class TestAnalyzeProgressionHandler:
    """Test analyze_chord_progression MCP tool"""
    
    @pytest.mark.asyncio
    async def test_analyze_progression_basic(self):
        """Test basic chord progression analysis"""
        args = {
            "chord_list": ["C", "Am", "F", "G"],
            "analysis_type": "both"
        }
        
        result = await handle_analyze_progression(args)
        
        # Should return text content
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        
        # Parse JSON response
        response_data = json.loads(result[0].text)
        
        # Check response structure
        assert 'summary' in response_data
        assert 'progression' in response_data
        assert 'analysis_type' in response_data
        assert 'chords' in response_data
        
        assert response_data['progression'] == ["C", "Am", "F", "G"]
        assert response_data['analysis_type'] == "both"
        assert len(response_data['chords']) == 4
        
        # Check individual chord analysis
        for chord_data in response_data['chords']:
            assert 'chord_symbol' in chord_data
            if 'fingerings' in chord_data:
                assert isinstance(chord_data['fingerings'], list)
            if 'theory' in chord_data:
                assert 'intervals' in chord_data['theory']
                assert 'notes' in chord_data['theory']
    
    @pytest.mark.asyncio
    async def test_analyze_progression_fingerings_only(self):
        """Test progression analysis with fingerings only"""
        args = {
            "chord_list": ["G", "D", "Em"],
            "analysis_type": "fingerings",
            "max_per_chord": 2
        }
        
        result = await handle_analyze_progression(args)
        response_data = json.loads(result[0].text)
        
        # Should have fingerings but not theory
        for chord_data in response_data['chords']:
            assert 'fingerings' in chord_data
            assert 'theory' not in chord_data
            assert len(chord_data['fingerings']) <= 2
    
    @pytest.mark.asyncio
    async def test_analyze_progression_theory_only(self):
        """Test progression analysis with theory only"""
        args = {
            "chord_list": ["Cmaj7", "Dm7", "G7"],
            "analysis_type": "theory"
        }
        
        result = await handle_analyze_progression(args)
        response_data = json.loads(result[0].text)
        
        # Should have theory but not fingerings
        for chord_data in response_data['chords']:
            assert 'theory' in chord_data
            assert 'fingerings' not in chord_data


class TestGetChordInfoHandler:
    """Test get_chord_info MCP tool"""
    
    @pytest.mark.asyncio
    async def test_get_chord_info_basic(self):
        """Test basic chord information retrieval"""
        args = {"chord_symbol": "Cmaj7"}
        result = await handle_get_chord_info(args)
        
        # Should return text content
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        
        # Parse JSON response
        response_data = json.loads(result[0].text)
        
        # Check response structure
        assert 'chord_symbol' in response_data
        assert 'theory' in response_data
        assert 'alternatives' in response_data
        
        assert response_data['chord_symbol'] == 'Cmaj7'
        
        # Check theory information
        theory = response_data['theory']
        assert 'intervals' in theory
        assert 'notes' in theory
        assert 'quality' in theory
        assert 'root' in theory
    
    @pytest.mark.asyncio
    async def test_get_chord_info_without_alternatives(self):
        """Test chord info without alternative fingerings"""
        args = {
            "chord_symbol": "Dm7",
            "include_alternatives": False
        }
        
        result = await handle_get_chord_info(args)
        response_data = json.loads(result[0].text)
        
        # Should not have alternatives
        assert 'alternatives' not in response_data or len(response_data['alternatives']) == 0
    
    @pytest.mark.asyncio
    async def test_get_chord_info_slash_chord(self):
        """Test chord info for slash chords"""
        args = {"chord_symbol": "C/E"}
        result = await handle_get_chord_info(args)
        
        response_data = json.loads(result[0].text)
        
        # Should handle bass note correctly
        theory = response_data['theory']
        assert 'bass' in theory
        assert theory['bass'] == 'E'


class TestBatchDiagramGeneration:
    """Test batch chord diagram generation functionality"""
    
    @pytest.mark.asyncio
    async def test_batch_with_fingering_specs(self):
        """Test batch generation using fingering specifications"""
        args = {
            "fingering_specs": [
                {
                    "positions": [
                        {"string": 1, "fret": 0},
                        {"string": 2, "fret": 1},
                        {"string": 3, "fret": 0},
                        {"string": 4, "fret": 2},
                        {"string": 5, "fret": 3}
                    ],
                    "chord_name": "C Major"
                },
                {
                    "positions": [
                        {"string": 1, "fret": 0},
                        {"string": 2, "fret": 0},
                        {"string": 3, "fret": 0},
                        {"string": 4, "fret": 2},
                        {"string": 5, "fret": 2}
                    ],
                    "chord_name": "A Minor"
                }
            ],
            "columns": 2,
            "include_names": True
        }
        
        result = await handle_create_diagram(args)
        
        # Should return success
        assert len(result) == 2
        assert "Generated batch diagram with 2 chord(s)" in result[0].text
        assert hasattr(result[1], 'data')
    
    @pytest.mark.asyncio
    async def test_batch_empty_fingering_specs(self):
        """Test handling of empty fingering specs"""
        args = {
            "fingering_specs": []
        }
        
        result = await handle_create_diagram(args)
        
        # Should return error about no valid fingerings
        assert len(result) == 1
        assert "No valid fingerings to process" in result[0].text


class TestMCPIntegration:
    """Integration tests for MCP server functionality"""
    
    @pytest.mark.asyncio
    async def test_fingering_output_format(self):
        """Test that fingering output format is consistent"""
        from src.fretboard import FretPosition
        from src.music_theory import Note
        
        # Create a test fingering
        positions = [
            FretPosition(string=5, fret=3, note=Note("C")),
            FretPosition(string=4, fret=2, note=Note("E")),
            FretPosition(string=3, fret=0, note=Note("G")),
            FretPosition(string=2, fret=1, note=Note("C")),
            FretPosition(string=1, fret=0, note=Note("E"))
        ]
        
        fingering = Fingering(positions=positions)
        
        # Format the fingering
        formatted = format_fingering_for_output(fingering)
        
        # Check required fields
        assert 'positions' in formatted
        assert 'fingering_pattern' in formatted
        assert 'difficulty' in formatted
        assert 'characteristics' in formatted
        
        # Check positions format
        assert len(formatted['positions']) == 5
        for pos in formatted['positions']:
            assert 'string' in pos
            assert 'fret' in pos
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete workflow from chord generation to diagram"""
        # Step 1: Generate fingerings
        fingerings_args = {"chord_symbol": "G"}
        fingerings_result = await handle_generate_fingerings(fingerings_args)
        fingerings_data = json.loads(fingerings_result[0].text)
        
        assert len(fingerings_data['fingerings']) > 0
        
        # Step 2: Get chord info
        info_args = {"chord_symbol": "G"}
        info_result = await handle_get_chord_info(info_args)
        info_data = json.loads(info_result[0].text)
        
        assert info_data['chord_symbol'] == 'G'
        assert 'theory' in info_data
        
        # Step 3: Create diagram from the fingering
        first_fingering = fingerings_data['fingerings'][0]
        diagram_args = {
            "fingering_specs": [
                {
                    "positions": first_fingering['positions'],
                    "chord_name": "G Major"
                }
            ]
        }
        
        diagram_result = await handle_create_diagram(diagram_args)
        
        # Should get text and image
        assert len(diagram_result) == 2
        assert "Generated batch diagram" in diagram_result[0].text
        assert isinstance(diagram_result[1], ImageContent)