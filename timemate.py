import tkinter as tk
from time import strftime
from datetime import datetime
import threading
import random
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

try:
    root.attributes('-zoomed', True)
except Exception:
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width-20}x{screen_height-50}+0+0")

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

# === Clock Frame Widgets ===
center_frame = tk.Frame(clock_frame, bg="black")
center_frame.pack(expand=True)

label_time = tk.Label(center_frame, font=('Helvetica', 60, 'bold'), bg='black', fg='orange')
label_time.pack()

label_date = tk.Label(center_frame, font=('Helvetica', 35), bg='black', fg='white')
label_date.pack(pady=(96, 0))  # 1 inch below time

# === Stopwatch Placeholder ===
stopwatch_label = tk.Label(stopwatch_frame, text="Stopwatch Screen (Coming Soon)", font=('Helvetica', 30), bg='black', fg='lime')
stopwatch_label.pack(pady=50)

# === Calendar Placeholder ===
calendar_label = tk.Label(calendar_frame, text="Calendar Screen (Coming Soon)", font=('Helvetica', 30), bg='black', fg='magenta')
calendar_label.pack(pady=50)

# === Switch View Function ===
def show_frame(frame_to_show):
    for frame in (clock_frame, alarm_frame, stopwatch_frame, calendar_frame):
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
    return tk.Spinbox(parent, from_=from_, to=to_, wrap=True, textvariable=textvariable, width=width,
                      font=('Helvetica', 32, 'bold'), state='readonly', justify='center',
                      bg='black', fg='orange', buttonbackground='#ff6e40', relief='flat')

# Clear previous alarm frame widgets
for widget in alarm_frame.winfo_children():
    widget.destroy()

# Center container for alarm UI with some padding & bigger size
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

set_btn = tk.Button(alarm_center, text="Set Alarm", command=set_alarm, font=('Helvetica', 24, 'bold'), bg="#40c4ff", fg="black", width=15)
set_btn.pack(pady=30)

alarm_label = tk.Label(alarm_center, text="No alarm set", font=('Helvetica', 22), fg='white', bg='black')
alarm_label.pack()

root.after(1000, check_alarm)

# === Start App ===
root.mainloop()

