import tkinter as tk
from time import strftime
import calendar 
from datetime import datetime
import threading
import random
import pytz 
from pytz import all_timezones
import sys
import os

try:
    from playsound import playsound
    PLAY_SOUND_AVAILABLE = True
except ImportError:
    PLAY_SOUND_AVAILABLE = False

# === Main Window Setup ===
root = tk.Tk()
root.title("Clock")
root.configure(bg="black")
root.update_idletasks()
app_width = 900
app_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (app_width // 2)
y = (screen_height // 2) - (app_height // 2)
root.geometry(f"{app_width}x{app_height}+{x}+{y}")

# === Layout Frames ===
main_container = tk.Frame(root, bg="black")
main_container.pack(expand=True, fill="both")
content_frame = tk.Frame(main_container, bg="black")
content_frame.pack(side="left", expand=True, fill="both")
button_panel = tk.Frame(main_container, bg="#111111", width=180)
button_panel.pack(side="right", fill="y", padx=5, pady=5)

# === App Content Frames ===
clock_frame = tk.Frame(content_frame, bg="black")
alarm_frame = tk.Frame(content_frame, bg="black")
stopwatch_frame = tk.Frame(content_frame, bg="black")
calendar_frame = tk.Frame(content_frame, bg="black")
worldclock_frame = tk.Frame(content_frame, bg="black")

# === Clock Frame Widgets ===
center_frame = tk.Frame(clock_frame, bg="black")
center_frame.pack(expand=True)
label_time = tk.Label(center_frame, font=('Helvetica', 60, 'bold'), bg='black', fg='orange')
label_time.pack()
label_date = tk.Label(center_frame, font=('Helvetica', 35), bg='black', fg='white')
label_date.pack(pady=(96, 0))  # 1 inch below time

# === Stopwatch Functionality ===
stopwatch_running = False
start_time = 0
elapsed_time = 0

def update_stopwatch():
    if stopwatch_running:
        global elapsed_time
        current_time = datetime.now()
        elapsed = (current_time - start_time).total_seconds() + elapsed_time
        mins, secs = divmod(int(elapsed), 60)
        hours, mins = divmod(mins, 60)
        ms = int((elapsed - int(elapsed)) * 100)
        time_string = f"{hours:02d}:{mins:02d}:{secs:02d}.{ms:02d}"
        stopwatch_display.config(text=time_string)
        stopwatch_display.after(50, update_stopwatch)

def start_stopwatch():
    global stopwatch_running, start_time
    if not stopwatch_running:
        stopwatch_running = True
        start_time = datetime.now()
        update_stopwatch()

def stop_stopwatch():
    global stopwatch_running, elapsed_time
    if stopwatch_running:
        stopwatch_running = False
        elapsed_time += (datetime.now() - start_time).total_seconds()

def reset_stopwatch():
    global stopwatch_running, start_time, elapsed_time
    stopwatch_running = False
    start_time = 0
    elapsed_time = 0
    stopwatch_display.config(text="00:00:00.00")

stopwatch_center = tk.Frame(stopwatch_frame, bg="black")
stopwatch_center.place(relx=0.5, rely=0.5, anchor="center")
stopwatch_display = tk.Label(stopwatch_center, text="00:00:00.00", font=('Helvetica', 60, 'bold'), fg='lime', bg='black')
stopwatch_display.pack(pady=40)
btn_frame = tk.Frame(stopwatch_center, bg="black")
btn_frame.pack()
start_btn = tk.Button(btn_frame, text="Start", command=start_stopwatch, font=('Helvetica', 18, 'bold'), bg="#69f0ae", fg="black", width=10)
start_btn.grid(row=0, column=0, padx=10)
stop_btn = tk.Button(btn_frame, text="Stop", command=stop_stopwatch, font=('Helvetica', 18, 'bold'), bg="#ffcc80", fg="black", width=10)
stop_btn.grid(row=0, column=1, padx=10)
reset_btn = tk.Button(btn_frame, text="Reset", command=reset_stopwatch, font=('Helvetica', 18, 'bold'), bg="#ef5350", fg="white", width=10)
reset_btn.grid(row=0, column=2, padx=10)

# === Render Calendar Function ===
def render_calendar(year, month):
    for widget in calendar_content_frame.winfo_children():
        widget.destroy()
    cal = calendar.monthcalendar(year, month)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for idx, day in enumerate(days):
        tk.Label(calendar_content_frame, text=day,
                 font=('Helvetica', 22, 'bold'),
                 bg='black', fg='cyan',
                 width=8, height=2, borderwidth=1, relief='solid').grid(row=0, column=idx, padx=3, pady=3)
    for row_idx, week in enumerate(cal):
        for col_idx, day in enumerate(week):
            day_text = f"{day}" if day != 0 else ""
            tk.Label(calendar_content_frame, text=day_text,
                     font=('Helvetica', 20),
                     bg='black', fg='white',
                     width=8, height=3,
                     borderwidth=1, relief='solid').grid(row=row_idx+1, column=col_idx, padx=3, pady=3)

# === Update Calendar Function ===
def update_calendar(*args):
    year = int(year_var.get())
    month = month_names.index(month_var.get()) + 1
    render_calendar(year, month)

# === Calendar UI Layout ===
calendar_header_frame = tk.Frame(calendar_frame, bg="black")
calendar_header_frame.pack(pady=32)
month_names = list(calendar.month_name)[1:]
month_var = tk.StringVar(value=month_names[datetime.now().month - 1])
month_menu = tk.OptionMenu(calendar_header_frame, month_var, *month_names, command=update_calendar)
month_menu.config(font=('Helvetica', 18, 'bold'), bg='black', fg='orange', width=9, highlightthickness=0)
month_menu["menu"].config(bg="black", fg="white", font=('Helvetica', 16))
month_menu.pack(side="left", padx=18)
year_var = tk.StringVar(value=str(datetime.now().year))
year_spinbox = tk.Spinbox(calendar_header_frame, from_=1990, to=2999, textvariable=year_var,
                          font=('Helvetica', 18, 'bold'), width=8, command=update_calendar,
                          bg="black", fg="orange", justify='center')
year_spinbox.pack(side="left", padx=18)
calendar_content_frame = tk.Frame(calendar_frame, bg="black")
calendar_content_frame.pack()
render_calendar(datetime.now().year, datetime.now().month)

# === Switch View Function ===
def show_frame(frame_to_show):
    for frame in (clock_frame, alarm_frame, stopwatch_frame, calendar_frame, worldclock_frame):
        frame.pack_forget()
    frame_to_show.pack(expand=True, fill="both")

show_frame(clock_frame)

# === Fancy Button Class ===
class FancyButton(tk.Canvas):
    def __init__(self, master, text, command=None, width=160, height=50,
                 bg1="#ff6e40", bg2="#ff3d00", fg="white",
                 font=('Helvetica', 14, 'bold'), radius=20, **kwargs):
        super().__init__(master, width=width, height=height, bg=master['bg'],
                         highlightthickness=0, **kwargs)
        self.command = command
        self.radius = radius
        self.width = width
        self.height = height
        self.bg1 = bg1
        self.bg2 = bg2
        self.fg = fg
        self.font = font
        self.text = text
        self.current_color = self.bg1
        self.draw_button(self.bg1)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)

    def draw_button(self, color):
        self.current_color = color
        self.delete("all")
        self.create_arc((0, 0, 2*self.radius, self.height), start=90, extent=180,
                        fill=color, outline=color, tags="button_shape")
        self.create_arc((self.width - 2*self.radius, 0, self.width, self.height),
                        start=270, extent=180, fill=color, outline=color, tags="button_shape")
        self.create_rectangle(self.radius, 0, self.width - self.radius, self.height,
                              fill=color, outline=color, tags="button_shape")
        self.create_text(self.width//2, self.height//2, text=self.text,
                         fill=self.fg, font=self.font, tags="button_text")

    def on_enter(self, event):
        self.draw_button(self.bg2)
        self.itemconfig("button_text", fill="#fffbcf")

    def on_leave(self, event):
        self.draw_button(self.bg1)
        self.itemconfig("button_text", fill=self.fg)

    def on_click(self, event):
        if self.command:
            self.command()

# === Create Buttons ===
btn_clock = FancyButton(button_panel, "Clock", command=lambda: show_frame(clock_frame))
btn_clock.pack(pady=10)
btn_alarm = FancyButton(button_panel, "Alarm", command=lambda: show_frame(alarm_frame),
                        bg1="#40c4ff", bg2="#0091ea")
btn_alarm.pack(pady=10)
btn_stopwatch = FancyButton(button_panel, "Stopwatch", command=lambda: show_frame(stopwatch_frame),
                            bg1="#69f0ae", bg2="#00c853", fg="black")
btn_stopwatch.pack(pady=10)
btn_calendar = FancyButton(button_panel, "Calendar", command=lambda: show_frame(calendar_frame),
                           bg1="#ea40ff", bg2="#9c27b0")
btn_calendar.pack(pady=10)
btn_worldclock = FancyButton(button_panel, "World Clock", command=lambda: show_frame(worldclock_frame),
                            bg1="#ffa500", bg2="#ff8c00", fg="black")
btn_worldclock.pack(pady=10)

# === Time and Date Functions ===
def update_time():
    current_time = strftime('%I:%M:%S %p')
    label_time.config(text=current_time)
    label_time.after(1000, update_time)

def update_date():
    current_date = datetime.now().strftime('%d %B %Y')
    label_date.config(text=current_date)

update_time()
update_date()

# === Alarm Section ===
quotes = [
    "Push yourself, because no one else will.",
    "Don't watch the clock; do what it does. Keep going.",
    "Success doesn’t find you — you hunt it down.",
    "Stay positive, work hard, make it happen.",
    "Discipline is choosing between what you want now and what you want most."
]
alarm_time = None
alarm_triggered = False

def play_alarm_sound():
    if PLAY_SOUND_AVAILABLE:
        sound_path = os.path.join(os.path.dirname(__file__), "alarm.wav")
        if os.path.exists(sound_path):
            playsound(sound_path)
        else:
            print("alarm.wav not found, playing bell sound instead.")
            print('\a')
    else:
        print('\a')

def check_alarm():
    global alarm_triggered
    if alarm_time and not alarm_triggered:
        now = datetime.now().strftime("%I:%M:%S %p")
        if now == alarm_time:
            alarm_triggered = True
            threading.Thread(target=play_alarm_sound).start()
            show_quote()
    root.after(1000, check_alarm)

def show_quote():
    quote = random.choice(quotes)
    top = tk.Toplevel(alarm_frame)
    top.configure(bg="black")
    top.geometry("400x200")
    top.title("Motivational Quote")
    tk.Label(top, text=quote, font=('Helvetica', 16, 'bold'), fg='cyan', bg='black', wraplength=380, justify='center').pack(expand=True, padx=20, pady=20)
    tk.Button(top, text="Close", command=top.destroy, bg="#40c4ff", fg="black", font=('Helvetica', 12, 'bold')).pack(pady=10)

def set_alarm():
    global alarm_time, alarm_triggered
    h = hour_var.get()
    m = minute_var.get()
    s = second_var.get()
    ampm = ampm_var.get()
    alarm_time = f"{int(h):02d}:{int(m):02d}:{int(s):02d} {ampm}"
    alarm_label.config(text=f"Alarm set for {alarm_time}")
    alarm_triggered = False

def create_spinbox(parent, from_, to_, textvariable, width=3):
    return tk.Spinbox (parent, from_=from_, to=to_, wrap=True, textvariable=textvariable, width=width,
                      font=('Helvetica', 32, 'bold'), state='readonly', justify='center',
                      bg='black', fg='orange', buttonbackground='#ff6e40', relief='flat')

for widget in alarm_frame.winfo_children():
    widget.destroy()

alarm_center = tk.Frame(alarm_frame, bg="black")
alarm_center.place(relx=0.5, rely=0.5, anchor='center')
tk.Label(alarm_center, text="Set Alarm Time", font=('Helvetica', 36, 'bold'), fg='cyan', bg='black').pack(pady=20)
time_picker_frame = tk.Frame(alarm_center, bg="black")
time_picker_frame.pack(pady=20)

hour_var = tk.StringVar(value="12")
minute_var = tk.StringVar(value="00")
second_var = tk.StringVar(value="00")
ampm_var = tk.StringVar(value="AM")

hour_spinbox = create_spinbox(time_picker_frame, 1, 12, hour_var)
hour_spinbox.grid(row=0, column=0, padx=(0,10))
tk.Label(time_picker_frame, text=":", font=('Helvetica', 36, 'bold'), fg='orange', bg='black').grid(row=0, column=1)
minute_spinbox = create_spinbox(time_picker_frame, 0, 59, minute_var)
minute_spinbox.grid(row=0, column=2, padx=10)
tk.Label(time_picker_frame, text=":", font=('Helvetica', 36, 'bold'), fg='orange', bg='black').grid(row=0, column=3)
second_spinbox = create_spinbox(time_picker_frame, 0, 59, second_var)
second_spinbox.grid(row=0, column=4, padx=(10,20))
ampm_spinbox = tk.Spinbox(time_picker_frame, values=("AM", "PM"), textvariable=ampm_var, width=5,
                          font=('Helvetica', 32, 'bold'), state='readonly', justify='center',
                          bg='black', fg='orange', buttonbackground='#ff6e40', relief='flat')
ampm_spinbox.grid(row=0, column=5)

set_alarm_btn = tk.Button(alarm_center, text="Set Alarm", font=('Helvetica', 28, 'bold'), bg="#ff6e40", fg='black', command=set_alarm)
set_alarm_btn.pack(pady=20)

alarm_label = tk.Label(alarm_center, font=('Helvetica', 22), fg='orange', bg='black')
alarm_label.pack()

check_alarm()

# --- Scrollable Frame with mouse wheel support and red scrollbar ---
class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, bg='black', highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        # Style scrollbar - red color
        self.scrollbar.config(bg='red', troughcolor='black', activebackground='darkred')
        
        self.scrollable_frame = tk.Frame(self.canvas, bg='black')
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bind mouse wheel for Windows and Mac
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        # For Linux
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        # Windows / MacOS
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

# --- World Clock Frame ---
worldclock_frame = tk.Frame(content_frame, bg="black")

timezone_labels = {}
region_frames = {}  # Hold frames for each region to hide/show on search

regions = {
    "Africa": [tz for tz in pytz.all_timezones if tz.startswith("Africa/")],
    "America": [tz for tz in pytz.all_timezones if tz.startswith("America/")],
    "Antarctica": [tz for tz in pytz.all_timezones if tz.startswith("Antarctica/")],
    "Asia": [tz for tz in pytz.all_timezones if tz.startswith("Asia/")],
    "Atlantic": [tz for tz in pytz.all_timezones if tz.startswith("Atlantic/")],
    "Australia": [tz for tz in pytz.all_timezones if tz.startswith("Australia/")],
    "Europe": [tz for tz in pytz.all_timezones if tz.startswith("Europe/")],
    "Indian": [tz for tz in pytz.all_timezones if tz.startswith("Indian/")],
    "Pacific": [tz for tz in pytz.all_timezones if tz.startswith("Pacific/")],
}

for region in regions:
    regions[region].sort()

# --- Search Bar ---
search_var = tk.StringVar()

def on_search(*args):
    query = search_var.get().strip().lower()
    for region, frame in region_frames.items():
        # Show/hide region based on if any child matches search
        region_match = region.lower().find(query) != -1 if query else True
        any_visible = False
        for child in frame.winfo_children():
            if isinstance(child, tk.Frame):  # Timezone frames
                tz_name = child.tz_name.lower()
                # Match if query is in tz_name or in region name
                visible = (query in tz_name) or region_match or query == ""
                if visible:
                    child.pack(fill='x')
                    any_visible = True
                else:
                    child.pack_forget()
            elif isinstance(child, tk.Label) and child == region_frames[region].region_label:
                # Region label - show only if any timezone visible or region match
                child.pack_forget()  # We'll pack again below
        if any_visible or region_match:
            region_frames[region].region_label.pack(fill='x', pady=(10, 5))
            frame.pack(fill='x')
        else:
            frame.pack_forget()

# Search input UI
search_frame = tk.Frame(worldclock_frame, bg='black')
search_frame.pack(fill='x', pady=5, padx=10)

search_label = tk.Label(search_frame, text="Search:", font=('Helvetica', 20), fg='cyan', bg='black')
search_label.pack(side='left')

search_entry = tk.Entry(search_frame, textvariable=search_var, font=('Helvetica', 18), bg='black', fg='orange', insertbackground='orange')
search_entry.pack(side='left', fill='x', expand=True, padx=10)
search_var.trace_add('write', on_search)

# Scrollable container for world clock entries
scroll_container = ScrollableFrame(worldclock_frame)
scroll_container.pack(fill='both', expand=True, padx=10, pady=10)

# Create region frames and populate timezones
for region, tz_list in regions.items():
    # Frame to hold this region's entries
    region_frame = tk.Frame(scroll_container.scrollable_frame, bg='black')
    region_frame.pack(fill='x')
    region_frame.region_label = tk.Label(region_frame, text=region, font=('Helvetica', 26, 'bold', 'underline'),
                                         fg='cyan', bg='black', anchor='w')
    region_frame.region_label.pack(fill='x', pady=(10, 5))

    for tz_name in tz_list:
        frame = tk.Frame(region_frame, bg='black', pady=2)
        frame.pack(fill='x')
        frame.tz_name = tz_name

        label_name = tk.Label(frame, text=tz_name.replace('_', ' '), font=('Helvetica', 18, 'bold'),
                              fg='orange', bg='black', anchor='w')
        label_name.pack(side='left', padx=10, fill='x', expand=True)

        label_time = tk.Label(frame, text="", font=('Helvetica', 16),
                              fg='white', bg='black', anchor='e')
        label_time.pack(side='right', padx=10)

        timezone_labels[tz_name] = {'name': label_name, 'time': label_time}

    region_frames[region] = region_frame

def update_worldclock_times():
    now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
    for tz_name, labels in timezone_labels.items():
        tz = pytz.timezone(tz_name)
        local_time = now_utc.astimezone(tz)
        formatted_time = local_time.strftime('%I:%M:%S %p')  # 12-hour format with AM/PM
        labels['time'].config(text=formatted_time)
    worldclock_frame.after(1000, update_worldclock_times)

update_worldclock_times()


# === Start app ===
root.mainloop()
