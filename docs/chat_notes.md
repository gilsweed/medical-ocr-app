# Chat Notes - March 14, 2024

## How to Update This File

### To Save New Chat Content
1. Say: "Please save our current chat to docs/chat_notes.md"
2. I will:
   - Create a new section with today's date
   - Add the new content with proper formatting
   - Preserve all previous content

### To Update Existing Content
1. Say: "Please update docs/chat_notes.md with [specific changes]"
2. I will:
   - Make the requested changes
   - Keep the formatting consistent
   - Preserve other content

## File Preview System Discussion

### Current Implementation
- Files are displayed in two columns side by side
- Left column shows file previews
- Right column shows OCR text
- Files are sorted by confidence level (low, high, other)

### Page Navigation
- Each file can have multiple pages
- Navigation using < and > buttons
- Page counter shows current position
- Preview and OCR text update together

### File Organization
- Files sorted by confidence:
  * Low confidence files first
  * High confidence files second
  * Other files last

### Rotation Feature
- Each preview has a rotate button (⟳)
- 90-degree rotation increments
- Only affects preview, not OCR text

## Three-Column Layout Discussion

### Column Structure
1. **Left Column (File Previews)**
   - Shows file previews stacked vertically
   - Each preview has:
     * File name and page info
     * Preview content area
     * Page navigation controls
   - Minimum width: 100px (changed from 180px)

2. **Middle Column (OCR Text)**
   - Shows OCR text for each file
   - Synchronized with file previews
   - Each OCR block has:
     * File name and page info
     * OCR text content
   - Minimum width: 100px (changed from 300px)

3. **Right Column (Summary Panel)**
   - Shows document summaries
   - Right-aligned Hebrew text
   - Minimum width: 100px (changed from 350px)

### Divider Behavior
- **Left Divider**
  * Controls space between preview and OCR columns
  * Moving right makes preview column bigger
  * Moving left makes preview column smaller
  * Does not affect right divider or summary panel

- **Right Divider**
  * Controls space between OCR and summary columns
  * Right edge of summary panel stays fixed to screen edge
  * Only left edge of summary panel moves with divider
  * Does not affect left divider or preview column

### Important Notes
- Dividers operate independently
- No cross-divider interference
- Each divider only affects its adjacent columns
- Summary panel's right edge stays fixed to screen
- These behaviors will be maintained in all future iterations 