# 🚀 Installation Guide

This guide provides step-by-step instructions for installing the Guitar Chord Fingering Generator as a standalone package with MCP server support.

## 📋 Prerequisites

- **Python 3.10+** (recommended: Python 3.10, 3.11, or 3.12)
- **pip** package manager
- **Claude Desktop** (for MCP integration)

## 🔧 Installation Methods

### Method 1: Install from Source (Recommended)

This method installs the package directly from the source code:

```bash
# Clone or download the repository
git clone https://github.com/username/fretboard-diagram-generator.git
cd fretboard-diagram-generator

# Install the package
pip install -e .

# Verify installation
guitar-chord-cli --version
guitar-chord-mcp-server --help
```

### Method 2: Install from ZIP/Archive

If you have the source code as a ZIP file:

```bash
# Extract the archive
unzip fretboard-diagram-generator.zip
cd fretboard-diagram-generator

# Install the package
pip install .

# Verify installation
guitar-chord-cli --version
which guitar-chord-mcp-server
```

## ✅ Verify Installation

After installation, you should have two new command-line tools:

```bash
# Test the CLI tool
guitar-chord-cli generate "Cmaj7"

# Check MCP server is available
which guitar-chord-mcp-server
```

Expected output:
```
✅ CLI tool working: Should show chord fingerings for Cmaj7
✅ MCP server available: /usr/local/bin/guitar-chord-mcp-server (or similar path)
```

## 🤖 Claude Desktop Integration

### 1. Locate Claude Desktop Configuration

Find your Claude Desktop configuration file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### 2. Add MCP Server Configuration

Add the guitar chord generator to your configuration:

```json
{
  "mcpServers": {
    "guitar-chord-generator": {
      "command": "guitar-chord-mcp-server"
    }
  }
}
```

**That's it!** No PYTHONPATH or complex configuration needed.

### 3. Restart Claude Desktop

Close and restart Claude Desktop to load the MCP server.

### 4. Test Integration

In Claude Desktop, try these requests:
- "Generate fingerings for F# major"
- "Create a chord diagram for Bb major"  
- "Analyze the progression C - Am - F - G"

## 🛠️ Development Installation

For developers who want to modify the code:

```bash
# Clone the repository
git clone https://github.com/username/fretboard-diagram-generator.git
cd fretboard-diagram-generator

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/ -v

# Run MCP tests
pytest tests/test_mcp_server.py -v
```

## 🔍 Troubleshooting

### Common Issues

**1. "command not found: guitar-chord-mcp-server"**
```bash
# Check if pip installed to the correct location
pip show guitar-chord-generator

# Verify the entry point exists
python -c "import pkg_resources; print([ep for ep in pkg_resources.iter_entry_points('console_scripts') if 'guitar-chord' in ep.name])"

# Try reinstalling
pip uninstall guitar-chord-generator
pip install -e .
```

**2. "ModuleNotFoundError" when running MCP server**
```bash
# Check Python version
python --version  # Should be 3.10+

# Verify package installation
pip list | grep guitar-chord

# Try running directly
python guitar_chord_mcp_server.py
```

**3. Claude Desktop not detecting MCP server**
```bash
# Verify configuration file syntax
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Check MCP server starts without errors
guitar-chord-mcp-server 2>&1 | head -5
```

**4. Import errors or missing dependencies**
```bash
# Install all dependencies
pip install matplotlib click mcp

# Check for conflicting packages
pip check

# Try fresh install
pip uninstall guitar-chord-generator
pip install --no-cache-dir -e .
```

### Debug Mode

Enable detailed logging for troubleshooting:

```bash
# Run MCP server with debug output
PYTHONPATH=. python guitar_chord_mcp_server.py --verbose

# Test specific functionality
python -c "
from guitar_chord_mcp_server import handle_list_tools
import asyncio
print(asyncio.run(handle_list_tools()))
"
```

## 🎯 Uninstallation

To remove the package:

```bash
# Uninstall the package
pip uninstall guitar-chord-generator

# Remove Claude Desktop configuration
# Edit ~/Library/Application Support/Claude/claude_desktop_config.json
# Remove the "guitar-chord-generator" entry from mcpServers
```

## 📊 Package Information

After installation, the package provides:

### Command-Line Tools
- **`guitar-chord-cli`**: Interactive CLI for chord generation and analysis
- **`guitar-chord-mcp-server`**: Standalone MCP server for AI integration

### Python Modules
- **`src.fingering_generator`**: Core fingering generation algorithms
- **`src.diagram_generator`**: Visual chord diagram creation
- **`src.music_theory`**: Music theory and chord parsing
- **`src.chord_patterns`**: Database of standard chord patterns

### Dependencies
- **matplotlib** ≥3.5.0: For chord diagram generation
- **click** ≥8.0.0: For CLI interface
- **mcp** ≥1.12.0: For AI assistant integration

## 🎉 Success!

If you can run these commands without errors, installation is complete:

```bash
✅ guitar-chord-cli generate "C"
✅ guitar-chord-mcp-server --help
✅ Claude Desktop shows guitar chord tools
```

**You're ready to generate professional guitar chord fingerings with AI integration!** 🎸✨

## 📞 Support

If you encounter issues:

1. **Check Prerequisites**: Ensure Python 3.10+ and pip are installed
2. **Review Error Messages**: Most errors indicate missing dependencies or path issues
3. **Try Fresh Install**: `pip uninstall guitar-chord-generator && pip install -e .`
4. **Check Documentation**: Review README.md and MCP_INTEGRATION.md for additional details

For additional help, please check the project repository or submit an issue with your installation details and error messages.