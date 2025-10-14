#!/bin/bash
# Plays an error sound notification
# Can be chained with other hooks or used standalone

# Play an alert error sound (Basso is the classic macOS error sound)
afplay /System/Library/Sounds/Basso.aiff &

exit 0
