; AutoHotkey Script - Mouse Click Helper
; This script receives click coordinates via command line and performs clicks
; More reliable than PyAutoGUI in VM environments
; Compatible with AutoHotkey v2

; Get command line parameters
if (A_Args.Length < 2) {
    MsgBox("Usage: click_helper.ahk x y [delay]")
    ExitApp
}

x := A_Args[1]
y := A_Args[2]
delay := A_Args.Length >= 3 ? A_Args[3] : 200  ; Default 200ms

; Convert string parameters to numbers
x := Integer(x)
y := Integer(y)
delay := Integer(delay)

; Ensure coordinates are screen-based to work across monitors and scaling
CoordMode("Mouse", "Screen")
CoordMode("Pixel", "Screen")

; Move mouse to position slowly for better reliability
MouseMove(x, y, 2)

; Activate the window under the cursor to ensure it receives input
MouseGetPos(&mx, &my, &hwnd)
try {
    WinActivate("ahk_id " . hwnd)
    Sleep(50)
} catch {
    ; Ignore if activation fails
}

; Wait for application to register movement
Sleep(delay)

; Perform multiple clicks to ensure it registers (fast double click)
MouseClick("Left", x, y, 1, 0)  ; First click
Sleep(70)
MouseClick("Left", x, y, 1, 0)  ; Second click

; Write a simple log entry listing the coordinates we clicked
logPath := A_Temp . "\\allow_clicker_ahk.log"
timestamp := A_Now
FileAppend(timestamp . " - Click at: " . x . "," . y . "`n", logPath)

; Brief pause after clicks
Sleep(100)

; Exit successfully
ExitApp
