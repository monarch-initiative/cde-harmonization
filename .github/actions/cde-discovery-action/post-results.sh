#!/bin/bash

# Check if Claude output exists and post as comment using gh CLI
if [ -f /tmp/claude-output.txt ]; then
  echo "Claude output file found. Checking contents..."
  
  # Check if the file has content
  if [ -s /tmp/claude-output.txt ]; then
    echo "Claude output file has content ($(wc -l < /tmp/claude-output.txt) lines)"
    echo "First few lines of output:"
    head -5 /tmp/claude-output.txt
    
    echo "Posting Claude's CDE discovery results to issue #${ISSUE_NUMBER}"
    
    # Create formatted comment
    cat > /tmp/issue-comment.md << 'EOF'
# AI CDE Discovery Results

Claude AI has analyzed your CDE discovery request and found the following results:

---
EOF
    
    # Append Claude's analysis
    cat /tmp/claude-output.txt >> /tmp/issue-comment.md
    
    # Post comment using GitHub CLI
    gh issue comment ${ISSUE_NUMBER} --body-file /tmp/issue-comment.md
  else
    echo "Error: Claude output file is empty"
    echo "Creating comment about empty output..."
    cat > /tmp/issue-comment.md << 'EOF'
# AI CDE Discovery Results

⚠️ The AI analysis completed but produced no output. This might indicate:
- No relevant CDEs found matching the search criteria
- An error occurred during processing
- The request needs to be more specific

Please try rephrasing your request or adding more specific keywords.
EOF
    gh issue comment ${ISSUE_NUMBER} --body-file /tmp/issue-comment.md
  fi
else
  echo "Error: No Claude output found to post"
  echo "Checking if any related files exist..."
  ls -la /tmp/claude* || echo "No claude-related files found"
  exit 1
fi