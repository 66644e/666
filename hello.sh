#!/usr/bin/env bash

# ┌──────────────────────────────────────────────────────────────┐
# │   Broad scan — files that can plausibly display/execute as   │
# │   web pages (html/php/asp/jsp/cgi/...) across ENTIRE system  │
# │   Sends to Discord: list OR "None found"                     │
# └──────────────────────────────────────────────────────────────┘

WEBHOOK="https://ptb.discord.com/api/webhooks/1477875333083693119/K0fbmsQUs0apZbO2H0FhhWRbEOBFak4Y8JnSRidgJXr0mTPRWq_AtQwpZky-NKk0palm"

# Temp file
OUTPUT_FILE="/tmp/web_possible_pages_$(date +%s).txt"

echo "Scanning ENTIRE filesystem for possible web-page / executable files..."
echo "(This will take a LONG time — be patient. Errors are hidden.)"

# Very broad search — start from / (root)
# -xdev   → stay on the same filesystem (avoids huge external mounts if any)
# You can remove -xdev if you really want EVERY mounted filesystem
find / -xdev \
  -type f \
  \( -name "*.html"    -o -name "*.htm"     -o -name "*.shtml"   \
  -o -name "*.xhtml"   -o -name "*.php"     -o -name "*.php3"    \
  -o -name "*.php4"    -o -name "*.php5"    -o -name "*.phtml"   \
  -o -name "*.asp"     -o -name "*.aspx"    -o -name "*.jsp"     \
  -o -name "*.jspx"    -o -name "*.pl"      -o -name "*.cgi"     \
  -o -name "*.py"      -o -name "*.rb"      -o -name "*.do"      \
  -o -name "*.action" \) \
  2>/dev/null \
  | sort > "$OUTPUT_FILE"

file_count=$(wc -l < "$OUTPUT_FILE" 2>/dev/null || echo 0)

if [ "$file_count" -eq 0 ]; then
    echo "No matching files found anywhere."
    
    curl -s -X POST "$WEBHOOK" \
      -H "Content-Type: application/json" \
      -d '{"content": "None found (broad system scan for .html/.php/.asp/.jsp/.cgi/etc.)"}' \
      >/dev/null 2>&1
    
    rm -f "$OUTPUT_FILE" 2>/dev/null
    echo "Sent: \"None found\" to webhook"
    exit 0
fi

# ── Files found — make it readable ───────────────────────────────

{
  echo "Possible web-page/executable files — broad system scan"
  echo "Generated: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  echo "Hostname: $(hostname 2>/dev/null || echo unknown)"
  echo "Total found: $file_count"
  echo "----------------------------------------"
  echo ""
  head -n 3000 "$OUTPUT_FILE"   # ← safety: don't make the txt gigantic
  if [ "$file_count" -gt 3000 ]; then
    echo "... (truncated — $file_count total, only first 3000 shown)"
  fi
  echo ""
  echo "----------------------------------------"
  echo "Tip: very large count usually means backups, caches, old installs"
} > "$OUTPUT_FILE.tmp" && mv "$OUTPUT_FILE.tmp" "$OUTPUT_FILE"

size_human=$(du -h "$OUTPUT_FILE" | cut -f1)
echo "Found $file_count files → size $size_human"

# Optional size warning
size_bytes=$(stat -c %s "$OUTPUT_FILE" 2>/dev/null || stat -f %z "$OUTPUT_FILE" 2>/dev/null || echo 0)
if (( size_bytes > 7800000 )); then
    echo "WARNING: >~7.8 MB — Discord might reject attachment"
    echo "         (consider gzipping or splitting)"
fi

# ── Upload to Discord ────────────────────────────────────────────

curl -s -S -X POST "$WEBHOOK" \
  -F 'payload_json={"content": "Broad scan result: '"$file_count"' possible web files found\nSize: '"$size_human"'\n(only first 3000 paths attached if very large)"}' \
  -F "file1=@\"$OUTPUT_FILE\";filename=possible_web_files_$(hostname)_$(date +%Y%m%d_%H%M).txt" \
  -H "User-Agent: bash"

echo ""
echo "Request sent."
rm -f "$OUTPUT_FILE" 2>/dev/null

echo "Done."
