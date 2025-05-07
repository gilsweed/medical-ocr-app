tell application "Script Editor"
    set scriptPath to (path to desktop folder as text) & "Medical App Launcher.app"
    set scriptContent to "do shell script \"cd /Users/gilsweed/Desktop/Brurya/gil && ./start_app.sh\""
    set newScript to make new script with properties {contents:scriptContent}
    save newScript as "application" in scriptPath
end tell 