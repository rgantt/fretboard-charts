"""
Tests for MCP Server Integration

Tests the MCP server functionality including tool definitions,
parameter validation, and integration with core functionality.
"""

import pytest
import asyncio
import json
import base64
from unittest.mock import patch, MagicMock

# Import MCP server components
from src.mcp_server import (
    handle_list_tools,
    handle_generate_fingerings,
    handle_create_diagram,
    handle_analyze_progression,
    handle_get_chord_info,
    format_fingering_for_output
)

# Import core functionality for testing
from src.fingering_generator import generate_chord_fingerings
from src.diagram_generator import generate_chord_diagram


class TestMCPToolDefinitions:
    """Test MCP tool definitions and schemas"""
    
    @pytest.mark.asyncio
    async def test_list_tools_returns_all_tools(self):
        """Test that all expected tools are returned"""
        tools = await handle_list_tools()
        
        expected_tools = {
            "generate_chord_fingerings",
            "create_chord_diagram", 
            "analyze_chord_progression",
            "get_chord_info"
        }
        
        tool_names = {tool.name for tool in tools}
        assert tool_names == expected_tools
        
        # Verify each tool has required properties
        for tool in tools:
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            assert hasattr(tool, 'inputSchema')
            assert tool.description  # Non-empty description
            assert tool.inputSchema  # Schema is present
    
    def test_tool_schemas_valid_structure(self):
        """Test that tool schemas have valid JSON Schema structure"""
        async def check_schemas():
            tools = await handle_list_tools()
            
            for tool in tools:
                schema = tool.inputSchema
                
                # Basic JSON Schema requirements
                assert schema.get("type") == "object"
                assert "properties" in schema
                
                # Each property should have type and description
                for prop_name, prop_def in schema["properties"].items():
                    assert "type" in prop_def
                    assert "description" in prop_def
        
        asyncio.run(check_schemas())


class TestGenerateFingeringsHandler:
    """Test generate_chord_fingerings MCP tool"""
    
    @pytest.mark.asyncio
    async def test_generate_fingerings_basic(self):
        """Test basic fingering generation"""
        arguments = {"chord_symbol": "C"}
        
        result = await handle_generate_fingerings(arguments)
        
        assert len(result) >= 1
        assert any("fingering" in content.text.lower() for content in result)
        assert any("C" in content.text for content in result)
        
        # Check for JSON data in response
        json_content = [c for c in result if "json" in c.text.lower()]
        assert len(json_content) > 0
    
    @pytest.mark.asyncio
    async def test_generate_fingerings_with_max_results(self):
        """Test fingering generation with max_results parameter"""
        arguments = {"chord_symbol": "Am", "max_results": 3}
        
        result = await handle_generate_fingerings(arguments)
        
        # Should contain summary and JSON data
        assert len(result) >= 1
        
        # Extract JSON data to verify max_results was respected
        json_text = None
        for content in result:
            if "```json" in content.text:
                json_start = content.text.find("```json") + 7
                json_end = content.text.find("```", json_start)
                json_text = content.text[json_start:json_end].strip()
                break
        
        assert json_text is not None
        data = json.loads(json_text)
        assert data["total_fingerings"] <= 3
    
    @pytest.mark.asyncio
    async def test_generate_fingerings_with_difficulty_filter(self):
        """Test fingering generation with difficulty filter"""
        arguments = {"chord_symbol": "F", "difficulty_filter": 0.5}
        
        result = await handle_generate_fingerings(arguments)
        
        # Should return results (F has easy fingerings available)
        assert len(result) >= 1
        assert any("F" in content.text for content in result)
    
    @pytest.mark.asyncio
    async def test_generate_fingerings_invalid_chord(self):
        """Test handling of invalid chord symbols"""
        arguments = {"chord_symbol": "InvalidChord123"}
        
        result = await handle_generate_fingerings(arguments)
        
        # Should handle gracefully with error message
        assert len(result) >= 1
        error_found = any("error" in content.text.lower() or "no fingerings" in content.text.lower() 
                         for content in result)
        assert error_found


class TestCreateDiagramHandler:
    """Test create_chord_diagram MCP tool"""
    
    @pytest.mark.asyncio
    async def test_create_diagram_from_chord_symbol(self):
        """Test diagram creation from chord symbol"""
        arguments = {"chord_symbol": "C", "format": "png"}
        
        result = await handle_create_diagram(arguments)
        
        assert len(result) >= 1
        
        # Should have text content and image content
        text_content = [c for c in result if hasattr(c, 'text')]
        image_content = [c for c in result if hasattr(c, 'data')]
        
        assert len(text_content) >= 1
        assert len(image_content) >= 1
        
        # Verify image data is base64 encoded
        img = image_content[0]
        assert hasattr(img, 'data')
        assert hasattr(img, 'mimeType')
        assert img.mimeType == "image/png"
        
        # Verify base64 data is valid
        try:
            decoded = base64.b64decode(img.data)
            assert len(decoded) > 0
        except Exception as e:
            pytest.fail(f"Invalid base64 data: {e}")
    
    @pytest.mark.asyncio
    async def test_create_diagram_svg_format(self):
        """Test diagram creation in SVG format"""
        arguments = {"chord_symbol": "Am", "format": "svg"}
        
        result = await handle_create_diagram(arguments)
        
        image_content = [c for c in result if hasattr(c, 'data')]
        assert len(image_content) >= 1
        
        img = image_content[0]
        assert img.mimeType == "image/svg"
    
    @pytest.mark.asyncio 
    async def test_create_diagram_from_fingering_spec(self):
        """Test diagram creation from fingering specification"""
        arguments = {
            "fingering_spec": {
                "positions": [
                    {"string": 1, "fret": 0},
                    {"string": 2, "fret": 1},
                    {"string": 3, "fret": 0},
                    {"string": 4, "fret": 2},
                    {"string": 5, "fret": 3}
                ]
            },
            "format": "png"
        }
        
        result = await handle_create_diagram(arguments)
        
        assert len(result) >= 1
        image_content = [c for c in result if hasattr(c, 'data')]
        assert len(image_content) >= 1
    
    @pytest.mark.asyncio
    async def test_create_diagram_missing_parameters(self):
        """Test diagram creation with missing required parameters"""
        arguments = {"format": "png"}  # Missing chord_symbol and fingering_spec
        
        result = await handle_create_diagram(arguments)
        
        # Should return error message
        assert len(result) >= 1
        assert any("must be provided" in content.text.lower() for content in result)


class TestAnalyzeProgressionHandler:
    """Test analyze_chord_progression MCP tool"""
    
    @pytest.mark.asyncio
    async def test_analyze_progression_basic(self):
        """Test basic chord progression analysis"""
        arguments = {
            "chord_list": ["C", "Am", "F", "G"],
            "analysis_type": "both"
        }
        
        result = await handle_analyze_progression(arguments)
        
        assert len(result) >= 1
        
        # Should contain analysis for all chords
        text_content = " ".join(content.text for content in result)
        for chord in ["C", "Am", "F", "G"]:
            assert chord in text_content
        
        # Should contain both fingering and theory information
        assert "fingering" in text_content.lower()
        assert "theory" in text_content.lower()
    
    @pytest.mark.asyncio
    async def test_analyze_progression_fingerings_only(self):
        """Test progression analysis with fingerings only"""
        arguments = {
            "chord_list": ["C", "G"],
            "analysis_type": "fingerings",
            "max_per_chord": 1
        }
        
        result = await handle_analyze_progression(arguments)
        
        text_content = " ".join(content.text for content in result)
        assert "fingering" in text_content.lower()
        # Should not contain theory analysis
        assert "intervals" not in text_content.lower()
    
    @pytest.mark.asyncio
    async def test_analyze_progression_theory_only(self):
        """Test progression analysis with theory only"""
        arguments = {
            "chord_list": ["Dm7", "G7"],
            "analysis_type": "theory"
        }
        
        result = await handle_analyze_progression(arguments)
        
        text_content = " ".join(content.text for content in result)
        assert "theory" in text_content.lower() or "notes" in text_content.lower()


class TestGetChordInfoHandler:
    """Test get_chord_info MCP tool"""
    
    @pytest.mark.asyncio
    async def test_get_chord_info_complete(self):
        """Test complete chord information retrieval"""
        arguments = {
            "chord_symbol": "Cmaj7",
            "include_theory": True,
            "include_alternatives": True
        }
        
        result = await handle_get_chord_info(arguments)
        
        assert len(result) >= 1
        
        text_content = " ".join(content.text for content in result)
        
        # Should contain chord name
        assert "Cmaj7" in text_content
        
        # Should contain theory information
        assert "theory" in text_content.lower()
        assert "notes" in text_content.lower()
        
        # Should contain fingering alternatives
        assert "fingering" in text_content.lower()
    
    @pytest.mark.asyncio
    async def test_get_chord_info_theory_only(self):
        """Test chord info with theory only"""
        arguments = {
            "chord_symbol": "F#m7b5",
            "include_theory": True,
            "include_alternatives": False
        }
        
        result = await handle_get_chord_info(arguments)
        
        text_content = " ".join(content.text for content in result)
        assert "F#m7b5" in text_content
        assert "theory" in text_content.lower()


class TestUtilityFunctions:
    """Test utility and helper functions"""
    
    def test_format_fingering_for_output(self):
        """Test fingering formatting for JSON output"""
        # Generate a real fingering to test with
        fingerings = generate_chord_fingerings("C", max_results=1)
        assert len(fingerings) > 0
        
        fingering = fingerings[0]
        formatted = format_fingering_for_output(fingering)
        
        # Check required fields
        required_fields = [
            "positions", "fingering_pattern", "difficulty", 
            "characteristics", "chord_name"
        ]
        
        for field in required_fields:
            assert field in formatted
        
        # Check data types
        assert isinstance(formatted["positions"], list)
        assert isinstance(formatted["difficulty"], (int, float))
        assert isinstance(formatted["characteristics"], dict)
        
        # Check positions structure
        if formatted["positions"]:
            pos = formatted["positions"][0]
            assert "string" in pos
            assert "fret" in pos
    
    def test_format_fingering_error_handling(self):
        """Test error handling in fingering formatting"""
        # Create a mock fingering that might cause errors
        mock_fingering = MagicMock()
        mock_fingering.positions = []
        mock_fingering.difficulty = 0.5
        mock_fingering.characteristics = {}
        mock_fingering.finger_assignments = None
        mock_fingering.chord = None
        mock_fingering.__str__ = lambda: "Mock fingering"
        
        formatted = format_fingering_for_output(mock_fingering)
        
        # Should handle error gracefully
        assert "error" in formatted or "fingering_pattern" in formatted


class TestMCPIntegration:
    """Integration tests for MCP server functionality"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_chord_workflow(self):
        """Test complete workflow from chord to diagram"""
        # Step 1: Generate fingerings
        fingering_args = {"chord_symbol": "Dm", "max_results": 2}
        fingering_result = await handle_generate_fingerings(fingering_args)
        
        assert len(fingering_result) >= 1
        
        # Step 2: Create diagram  
        diagram_args = {"chord_symbol": "Dm", "format": "png"}
        diagram_result = await handle_create_diagram(diagram_args)
        
        assert len(diagram_result) >= 1
        image_content = [c for c in diagram_result if hasattr(c, 'data')]
        assert len(image_content) >= 1
        
        # Step 3: Get chord info
        info_args = {"chord_symbol": "Dm", "include_theory": True, "include_alternatives": True}
        info_result = await handle_get_chord_info(info_args)
        
        assert len(info_result) >= 1
    
    @pytest.mark.asyncio
    async def test_complex_chord_handling(self):
        """Test handling of complex chord symbols"""
        complex_chords = ["Cmaj7/E", "F#m7b5", "Bb7#11", "Am7add9"]
        
        for chord_symbol in complex_chords:
            # Test fingering generation
            args = {"chord_symbol": chord_symbol, "max_results": 1}
            result = await handle_generate_fingerings(args)
            
            # Should handle without throwing exceptions
            assert len(result) >= 1
            
            # Should either succeed or provide meaningful error
            text_content = " ".join(content.text for content in result)
            assert chord_symbol in text_content or "error" in text_content.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])