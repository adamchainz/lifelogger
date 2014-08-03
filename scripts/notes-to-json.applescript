#!/usr/bin/osascript

-- Dump notes from Notes.app to a json file as a list of objects.
-- Pass 1 argument - the filename to write the json notes into.

on run argv
    set argc to 0
    try
        set argc to (count of argv)
    end try

    if argc is not 1
        error 128
    end if

    set filename to item 1 of argv

    -- delete file if it exists
    tell application "Finder"
        try
            delete POSIX file filename
        on error
            log "fail"
            set a to 1
        end try
    end tell

    set jsonNotes to my getJsonNotes()

    my saveJsonNotes(filename, jsonNotes)
end run


on getJsonNotes()
    set jsonNotes to {}
    tell application "Notes"
        set counter to 0

        repeat with each in every note
            set noteId to id of each
            set noteBody to body of each
            set creationDate to creation date of each
            set modificationDate to modification date of each
            set noteJson to my buildNoteJson(noteId, noteBody as text, creationDate, modificationDate)
            if length of noteBody is less than 3000 then
                copy noteJson to the end of jsonNotes
            end if
            set counter to counter + 1
        end repeat

    end tell
    return jsonNotes
end getJsonNotes


on buildNoteJson(noteId, body, creationDate, modificationDate)
    set normalizedBody to replace(body, "\n", "\\n")
    set normalizedBody to replace(normalizedBody, "\"", "\\\"")
    set json to ("{\"id\": \"" & noteId & "\", \"body\": \"" & normalizedBody & "\", \"creationDate\": \"" & creationDate & "\", \"modificationDate\": \"" & modificationDate & "\"}")
    return json
end buildNoteJson


on replace(originalText, fromText, toText)
    set AppleScript's text item delimiters to the fromText
    set the item_list to every text item of originalText
    set AppleScript's text item delimiters to the toText
    set originalText to the item_list as string
    set AppleScript's text item delimiters to ""
    return originalText
end replace


on saveJsonNotes(filename, jsonNotes)
    set the output to open for access filename with write permission
    write "[" to the output

    set counter to 1
    set num to length of jsonNotes
    repeat with each in jsonNotes
        write each to the output

        if counter is less than num
            write "," to the output
        end if

        set counter to counter + 1
    end repeat

    write "]" to the output

    close access the output
end saveJsonNotes
