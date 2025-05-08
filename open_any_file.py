from AppKit import NSApplication, NSOpenPanel
from Foundation import NSObject

# Initialize the app environment
app = NSApplication.sharedApplication()

# Create and configure the open panel
panel = NSOpenPanel.openPanel()
panel.setCanChooseFiles_(True)
panel.setCanChooseDirectories_(False)
panel.setAllowsMultipleSelection_(False)

# Important: Set these to ensure all files are shown
panel.setAllowedFileTypes_(None)  # This allows all file types
panel.setAllowsOtherFileTypes_(True)  # This is important to allow any file type
panel.setTreatsFilePackagesAsDirectories_(True)  # This helps with showing all files

# Show the panel and get the result
result = panel.runModal()
if result:
    selected_path = panel.URLs()[0].path()
    print("Selected file:", selected_path)
else:
    print("No file selected.") 