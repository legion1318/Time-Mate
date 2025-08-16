"""
Multi-Feature Clock App (Tkinter)
---------------------------------
This little project started as a simple clock,
but I kept adding features: a stopwatch, alarm, and a calendar.

Features:
 - Digital clock with date
 - Stopwatch with start/stop/reset
 - Alarm that plays sound and shows motivational quotes
 - Calendar view (pick month/year)

Written with Tkinter. 
"""

import tkinter as tk
from time import strftime
import calendar 
from datetime import datetime
import threading
import random
import os

# Try importing playsound so we can have audio alarms.
# If not available, we’ll just beep.
try:
    from playsound import playsound
    SOUND_ENABLED = True
except ImportError:
    SOUND_ENABLED = False


# ======================================================
# 1. MAIN APP WINDOW
# ======================================================

root = tk.Tk()
root.title("Clock")

# Dark background theme — looks cleaner
root.configure(bg="black")

# Center the window nicely
APP_WIDTH, APP_HEIGHT = 900, 600
screen_w, screen_h = root.winfo_screenwidth(), root.winfo_screenheight()
pos_x = (screen_w // 2) - (APP_WIDTH // 2)
pos_y = (screen_h // 2) - (APP_HEIGHT // 2)
root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}+{pos_x}+{pos_y}")


# ======================================================
# 2. LAYOUT STRUCTURE
# ======================================================

# Split into two areas: content (main) and side panel (buttons)
main_container = tk.Frame(root, bg="black")
main_container.pack(expand=True, fill="both")

content_area = tk.Frame(main_container, bg="black")
content_area.pack(side="left", expand=True, fill="both")

sidebar = tk.Frame(main_container, bg="#111111", width=180)
sidebar.pack(side="right", fill="y", padx=5, pady=5)

# Each "view" is a frame — only one visible at a time
clock_view     = tk.Frame(content_area, bg="black")
alarm_view     = tk.Frame(content_area, bg="black")
stopwatch_view = tk.Frame(content_area, bg="black")
calendar_view  = tk.Frame(content_area, bg="black")


# ======================================================
# 3. CLOCK VIEW
# ======================================================

# Center time + date
clock_center = tk.Frame(clock_view, bg="black")
clock_center.pack(expand=True)

time_label = tk.Label(clock_center, font=('Helvetica', 60, 'bold'), 
                      bg='black', fg='orange')
time_label.pack()

date_label = tk.Label(clock_center, font=('Helvetica', 35), 
                      bg='black', fg='white')
date_label.pack(pady=(96, 0))  # push it down a bit


# ======================================================
# 4. STOPWATCH
# ======================================================

# Stopwatch state
stopwatch_running = False
stopwatch_start = 0
stopwatch_elapsed = 0

def update_stopwatch():
    """Keep stopwatch display ticking while running."""
    if stopwatch_running:
        global stopwatch_elapsed
        now = datetime.now()
        elapsed = (now - stopwatch_start).total_seconds() + stopwatch_elapsed

        mins, secs = divmod(int(elapsed), 60)
        hours, mins = divmod(mins, 60)
        ms = int((elapsed - int(elapsed)) * 100)

        stopwatch_display.config(text=f"{hours:02d}:{mins:02d}:{secs:02d}.{ms:02d}")
        stopwatch_display.after(50, update_stopwatch)  # refresh every 50ms

def start_stopwatch():
    """Start or resume stopwatch."""
    global stopwatch_running, stopwatch_start
    if not stopwatch_running:
        stopwatch_running = True
        stopwatch_start = datetime.now()
        update_stopwatch()

def stop_stopwatch():
    """Pause stopwatch but keep time in memory."""
    global stopwatch_running, stopwatch_elapsed
    if stopwatch_running:
        stopwatch_running = False
        stopwatch_elapsed += (datetime.now() - stopwatch_start).total_seconds()

def reset_stopwatch():
    """Reset stopwatch completely."""
    global stopwatch_running, stopwatch_start, stopwatch_elapsed
    stopwatch_running = False
    stopwatch_start, stopwatch_elapsed = 0, 0
    stopwatch_display.config(text="00:00:00.00")

# Stopwatch UI
sw_center = tk.Frame(stopwatch_view, bg="black")
sw_center.place(relx=0.5, rely=0.5, anchor="center")

stopwatch_display = tk.Label(sw_center, text="00:00:00.00", 
                             font=('Helvetica', 60, 'bold'), fg='lime', bg='black')
stopwatch_display.pack(pady=40)

# Buttons under stopwatch
sw_buttons = tk.Frame(sw_center, bg="black")
sw_buttons.pack()

tk.Button(sw_buttons, text="Start", command=start_stopwatch,
          font=('Helvetica', 18, 'bold'), bg="#69f0ae", fg="black", width=10).grid(row=0, column=0, padx=10)
tk.Button(sw_buttons, text="Stop", command=stop_stopwatch,
          font=('Helvetica', 18, 'bold'), bg="#ffcc80", fg="black", width=10).grid(row=0, column=1, padx=10)
tk.Button(sw_buttons, text="Reset", command=reset_stopwatch,
          font=('Helvetica', 18, 'bold'), bg="#ef5350", fg="white", width=10).grid(row=0, column=2, padx=10)


# ======================================================
# 5. CALENDAR
# ======================================================

def render_calendar(year, month):
    """Draw month view calendar (very minimal)."""
    for widget in calendar_content.winfo_children():
        widget.destroy()

    cal = calendar.monthcalendar(year, month)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    # Day headers
    for i, day in enumerate(days):
        tk.Label(calendar_content, text=day, font=('Helvetica', 22, 'bold'),
                 bg='black', fg='cyan', width=8, height=2,
                 borderwidth=1, relief='solid').grid(row=0, column=i, padx=3, pady=3)

    # Days
    for r, week in enumerate(cal):
        for c, day in enumerate(week):
            tk.Label(calendar_content, text=(day if day else ""), font=('Helvetica', 20),
                     bg='black', fg='white', width=8, height=3,
                     borderwidth=1, relief='solid').grid(row=r+1, column=c, padx=3, pady=3)

def update_calendar(*args):
    """When user changes month/year -> refresh view."""
    year = int(year_var.get())
    month = month_names.index(month_var.get()) + 1
    render_calendar(year, month)

# Calendar header (month + year controls)
calendar_header = tk.Frame(calendar_view, bg="black")
calendar_header.pack(pady=32)

month_names = list(calendar.month_name)[1:]
month_var = tk.StringVar(value=month_names[datetime.now().month - 1])
year_var = tk.StringVar(value=str(datetime.now().year))

month_menu = tk.OptionMenu(calendar_header, month_var, *month_names, command=update_calendar)
month_menu.config(font=('Helvetica', 18, 'bold'), bg='black', fg='orange', width=9, highlightthickness=0)
month_menu["menu"].config(bg="black", fg="white", font=('Helvetica', 16))
month_menu.pack(side="left", padx=18)

year_spin = tk.Spinbox(calendar_header, from_=1990, to=2999, textvariable=year_var,
                       font=('Helvetica', 18, 'bold'), width=8, command=update_calendar,
                       bg="black", fg="orange", justify='center')
year_spin.pack(side="left", padx=18)

calendar_content = tk.Frame(calendar_view, bg="black")
calendar_content.pack()

# Show current month at start
render_calendar(datetime.now().year, datetime.now().month)


# ======================================================
# 6. VIEW SWITCHING
# ======================================================

def show(view):
    """Hide all views and show the chosen one."""
    for f in (clock_view, alarm_view, stopwatch_view, calendar_view):
        f.pack_forget()
    view.pack(expand=True, fill="both")

# Start on clock
show(clock_view)


# ======================================================
# 7. CUSTOM BUTTONS (sidebar)
# ======================================================

class FancyButton(tk.Canvas):
    """Rounded button with hover effect — for sidebar navigation."""
    def __init__(self, master, text, command=None,
                 bg1="#ff6e40", bg2="#ff3d00", fg="white",
                 font=('Helvetica', 14, 'bold')):
        super().__init__(master, width=160, height=50, bg=master['bg'], highlightthickness=0)
        self.command = command
        self.bg1, self.bg2, self.fg, self.font, self.text = bg1, bg2, fg, font, text
        self._draw(self.bg1)

        # Hover + click
        self.bind("<Enter>", lambda e: self._draw(self.bg2))
        self.bind("<Leave>", lambda e: self._draw(self.bg1))
        self.bind("<Button-1>", lambda e: command and command())

    def _draw(self, color):
        self.delete("all")
        self.create_rectangle(20, 0, 140, 50, fill=color, outline=color)  # simple rectangle
        self.create_text(80, 25, text=self.text, fill=self.fg, font=self.font)

# Sidebar buttons
FancyButton(sidebar, "Clock",     lambda: show(clock_view)).pack(pady=10)
FancyButton(sidebar, "Alarm",     lambda: show(alarm_view),     bg1="#40c4ff", bg2="#0091ea").pack(pady=10)
FancyButton(sidebar, "Stopwatch", lambda: show(stopwatch_view), bg1="#69f0ae", bg2="#00c853", fg="black").pack(pady=10)
FancyButton(sidebar, "Calendar",  lambda: show(calendar_view),  bg1="#ea40ff", bg2="#9c27b0").pack(pady=10)


# ======================================================
# 8. CLOCK + DATE UPDATES
# ======================================================

def update_time():
    time_label.config(text=strftime('%I:%M:%S %p'))
    time_label.after(1000, update_time)  # every second

def update_date():
    date_label.config(text=datetime.now().strftime('%d %B %Y'))

update_time()
update_date()


# ======================================================
# 9. ALARM
# ======================================================

# A few motivational quotes for when alarm goes off
QUOTES = [
    "Push yourself, because no one else will.",
    "Don't watch the clock; do what it does. Keep going.",
    "Success doesn’t find you — you hunt it down.",
    "Stay positive, work hard, make it happen.",
    "Discipline is choosing between what you want now and what you want most."
]

alarm_time = None
alarm_triggered = False

def play_alarm_sound():
    """Play sound if possible, otherwise system beep."""
    if SOUND_ENABLED:
        path = os.path.join(os.path.dirname(__file__), "alarm.wav")
        if os.path.exists(path):
            playsound(path)
        else:
            print("No alarm.wav -> fallback beep")
            print("\a")
    else:
        print("\a")

def check_alarm():
    """Check every second if alarm time is reached."""
    global alarm_triggered
    if alarm_time and not alarm_triggered:
        now = datetime.now().strftime("%I:%M:%S %p")
        if now == alarm_time:
            alarm_triggered = True
            threading.Thread(target=play_alarm_sound).start()
            show_quote()
    root.after(1000, check_alarm)

def show_quote():
    """Pop up with a random motivational quote."""
    top = tk.Toplevel(alarm_view)
    top.configure(bg="black")
    top.geometry("400x200")
    top.title("Motivational Quote")

    tk.Label(top, text=random.choice(QUOTES), 
             font=('Helvetica', 16, 'bold'), fg='cyan', bg='black',
             wraplength=380, justify='center').pack(expand=True, padx=20, pady=20)

    tk.Button(top, text="Close", command=top.destroy,
              bg="#40c4ff", fg="black", font=('Helvetica', 12, 'bold')).pack(pady=10)

def set_alarm():
    """Save chosen alarm time."""
    global alarm_time, alarm_triggered
    h, m, s, ampm = hour_var.get(), minute_var.get(), second_var.get(), ampm_var.get()
    alarm_time = f"{int(h):02d}:{int(m):02d}:{int(s):02d} {ampm}"
    alarm_label.config(text=f"Alarm set for {alarm_time}")
    alarm_triggered = False

# Helper for spinbox styling
def create_spinbox(parent, values, var, width=3):
    return tk.Spinbox(parent, values=values, textvariable=var, wrap=True, width=width,
                      font=('Helvetica', 32, 'bold'), state='readonly', justify='center',
                      bg='black', fg='orange', relief='flat')

# Alarm UI
alarm_center = tk.Frame(alarm_view, bg="black")
alarm_center.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(alarm_center, text="Set Alarm Time", font=('Helvetica', 36, 'bold'),
         fg='cyan', bg='black').pack(pady=20)

picker = tk.Frame(alarm_center, bg="black")
picker.pack(pady=20)

hour_var = tk.StringVar(value="12")
minute_var = tk.StringVar(value="00")
second_var = tk.StringVar(value="00")
ampm_var = tk.StringVar(value="AM")

create_spinbox(picker, list(range(1, 13)), hour_var).grid(row=0, column=0, padx=(0,10))
tk.Label(picker, text=":", font=('Helvetica', 36, 'bold'), fg='orange', bg='black').grid(row=0, column=1)

create_spinbox(picker, list(range(0, 60)), minute_var).grid(row=0, column=2, padx=10)
tk.Label(picker, text=":", font=('Helvetica', 36, 'bold'), fg='orange', bg='black').grid(row=0, column=3)

create_spinbox(picker, list(range(0, 60)), second_var).grid(row=0, column=4, padx=(10,20))
tk.Spinbox(picker, values=("AM", "PM"), textvariable=ampm_var, width=5,
           font=('Helvetica', 32, 'bold'), state='readonly', justify='center',
           bg='black', fg='orange', relief='flat').grid(row=0, column=5)

tk.Button(alarm_center, text="Set Alarm", font=('Helvetica', 28, 'bold'),
          bg="#ff6e40", fg='black', command=set_alarm).pack(pady=20)

alarm_label = tk.Label(alarm_center, font=('Helvetica', 22), fg='orange', bg='black')
alarm_label.pack()

check_alarm()  # start loop


# ======================================================
# 10. RUN APP
# ======================================================

root.mainloop()
