#!/bin/bash

# MCP Server Setup Script
# This script helps you set up MCP servers for your AI infrastructure

set -e

echo "🔌 MCP Server Integration Setup"
echo "================================"

# Check if .mcp.json exists
if [ ! -f ".mcp.json" ]; then
    echo "❌ No .mcp.json file found. Creating template..."
    cat > .mcp.json << 'EOF'
{
  "mcpServers": {
    "example-http": {
      "type": "http",
      "description": "Example HTTP-based MCP server",
      "url": "https://api.example.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    },
    "example-command": {
      "command": "bunx",
      "args": ["@example/mcp-server"],
      "env": {
        "API_TOKEN": "your-token-here"
      },
      "description": "Example command-based MCP server"
    }
  }
}
EOF
    echo "✅ Created .mcp.json template"
else
    echo "✅ .mcp.json already exists"
fi

# Validate JSON syntax
if command -v jq &> /dev/null; then
    if jq empty .mcp.json 2>/dev/null; then
        echo "✅ .mcp.json is valid JSON"
    else
        echo "❌ .mcp.json contains invalid JSON"
        exit 1
    fi
else
    echo "⚠️ jq not installed - skipping JSON validation"
fi

echo ""
echo "📋 Next Steps:"
echo "1. Edit .mcp.json with your actual MCP server configurations"
echo "2. Replace placeholder API keys with real ones"
echo "3. Test your MCP servers are accessible"
echo "4. Restart your AI assistant to pick up the changes"
echo ""
echo "🎯 Popular MCP Servers to Consider:"
echo "- @stripe/mcp (payment processing)"
echo "- @brightdata/mcp (web scraping)"
echo "- @apify/actors-mcp-server (automation)"
echo "- @playwright/mcp (browser automation)"
echo ""
echo "📖 For more MCP servers, visit: https://github.com/modelcontextprotocol"