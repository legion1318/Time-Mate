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
