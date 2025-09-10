#!/bin/bash

# Check if Claude output exists and post as comment using gh CLI
if [ -f /tmp/claude-output.txt ]; then
  echo "Posting Claude's CDE discovery results to issue #${{ github.event.issue.number }}"
  
  # Create formatted comment
  cat > /tmp/issue-comment.md << 'EOF'
# AI CDE Discovery Results

Claude AI has analyzed your CDE discovery request and found the following results:

---
EOF
  
  # Append Claude's analysis
  cat /tmp/claude-output.txt >> /tmp/issue-comment.md
  
  # Post comment using GitHub CLI
  gh issue comment ${{ github.event.issue.number }} --body-file /tmp/issue-comment.md
else
  echo "Error: No Claude output found to post"
  exit 1
fi