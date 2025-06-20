import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import queue
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict
import random
from abc import ABC, abstractmethod

@dataclass
class Task:
    id: int
    room_number: str
    room_class: str
    task_type: str
    priority: int  # 1 = VIP, 2 = Mid-Range, 3 = Economy
    estimated_time: int  # in minutes
    description: str
    timestamp: datetime
    status: str = "Pending"
    assigned_staff: str = ""
    actual_time: int = 0
    service_charge: float = 0.0

# Abstract base class for hotel rooms
class HotelRoom(ABC):
    def __init__(self, room_number: str, floor: int, amenities: List[str]):
        self.room_number = room_number
        self.floor = floor
        self.amenities = amenities
        self.is_occupied = False
        self.guest_name = ""
        self.check_in_time = None
        self.tasks_history = []
    
    @abstractmethod
    def get_room_class(self) -> str:
        pass
    
    @abstractmethod
    def get_service_multiplier(self) -> float:
        pass
    
    @abstractmethod
    def get_priority_level(self) -> int:
        pass
    
    @abstractmethod
    def get_base_service_charge(self) -> float:
        pass
    
    def calculate_service_charge(self, base_charge: float) -> float:
        return base_charge * self.get_service_multiplier()
    
    def add_task_to_history(self, task):
        self.tasks_history.append(task)

class EconomyRoom(HotelRoom):
    def __init__(self, room_number: str, floor: int):
        amenities = ["Basic TV", "Wi-Fi", "Air Conditioning", "Private Bathroom"]
        super().__init__(room_number, floor, amenities)
        self.room_class = "Economy"
    
    def get_room_class(self) -> str:
        return "Economy"
    
    def get_service_multiplier(self) -> float:
        return 1.0  # Base rate
    
    def get_priority_level(self) -> int:
        return 3  # Lowest priority
    
    def get_base_service_charge(self) -> float:
        return 10.0

class MidRangeRoom(HotelRoom):
    def __init__(self, room_number: str, floor: int):
        amenities = ["Premium TV", "High-Speed Wi-Fi", "Climate Control", 
                    "Premium Bathroom", "Mini Fridge", "Coffee Maker", "Room Service Menu"]
        super().__init__(room_number, floor, amenities)
        self.room_class = "Mid-Range"
    
    def get_room_class(self) -> str:
        return "Mid-Range"
    
    def get_service_multiplier(self) -> float:
        return 1.5  # 50% premium
    
    def get_priority_level(self) -> int:
        return 2  # Medium priority
    
    def get_base_service_charge(self) -> float:
        return 15.0

class VIPRoom(HotelRoom):
    def __init__(self, room_number: str, floor: int):
        amenities = ["Smart TV", "Ultra-Fast Wi-Fi", "Premium Climate Control",
                    "Luxury Bathroom", "Mini Bar", "Espresso Machine", "24/7 Room Service",
                    "Concierge Service", "Premium Linens", "Balcony", "Butler Service"]
        super().__init__(room_number, floor, amenities)
        self.room_class = "VIP"
    
    def get_room_class(self) -> str:
        return "VIP"
    
    def get_service_multiplier(self) -> float:
        return 2.5  # 150% premium
    
    def get_priority_level(self) -> int:
        return 1  # Highest priority
    
    def get_base_service_charge(self) -> float:
        return 25.0

class HotelScheduler:
    def __init__(self):
        self.tasks: List[Task] = []
        self.completed_tasks: List[Task] = []
        self.rooms: Dict[str, HotelRoom] = {}
        self.task_counter = 1
        self.staff_members = {
            "VIP": ["Alice (VIP Specialist)", "Robert (Butler)", "Elena (Concierge)"],
            "Mid-Range": ["Bob (Senior Staff)", "Diana (Room Service)", "Carlos (Maintenance)"],
            "Economy": ["Charlie (Staff)", "Eve (Housekeeper)", "Frank (Assistant)"]
        }
        self.current_task = None
        self.is_running = False
        self.scheduler_thread = None
        self.current_algorithm = "Priority"  # Default to priority for hotel service
        self.time_quantum = 15  # for Round Robin
        self.task_queue = queue.Queue()
        self.initialize_rooms()
        
    def initialize_rooms(self):
        # Create Economy rooms (Floors 1-3, Rooms 101-330)
        for floor in range(1, 4):
            for room_num in range(1, 31):
                room_number = f"{floor}{room_num:02d}"
                self.rooms[room_number] = EconomyRoom(room_number, floor)
        
        # Create Mid-Range rooms (Floors 4-6, Rooms 401-630)
        for floor in range(4, 7):
            for room_num in range(1, 31):
                room_number = f"{floor}{room_num:02d}"
                self.rooms[room_number] = MidRangeRoom(room_number, floor)
        
        # Create VIP rooms (Floors 7-10, Rooms 701-1030)
        for floor in range(7, 11):
            for room_num in range(1, 31):
                room_number = f"{floor}{room_num:02d}"
                self.rooms[room_number] = VIPRoom(room_number, floor)
    
    def get_room(self, room_number: str) -> HotelRoom:
        return self.rooms.get(room_number.replace("Room ", ""))
    
    def get_staff_for_room_class(self, room_class: str) -> str:
        staff_list = self.staff_members.get(room_class, self.staff_members["Economy"])
        return random.choice(staff_list)
        
    def add_task(self, room_number: str, task_type: str, estimated_time: int, description: str):
        room = self.get_room(room_number)
        if not room:
            raise ValueError(f"Room {room_number} not found")
        
        # Priority and service charge based on room class
        priority = room.get_priority_level()
        service_charge = room.calculate_service_charge(room.get_base_service_charge())
        
        task = Task(
            id=self.task_counter,
            room_number=room_number,
            room_class=room.get_room_class(),
            task_type=task_type,
            priority=priority,
            estimated_time=estimated_time,
            description=description,
            timestamp=datetime.now(),
            service_charge=service_charge
        )
        
        self.tasks.append(task)
        room.add_task_to_history(task)
        self.task_counter += 1
        return task
    
    def get_priority_text(self, priority: int) -> str:
        priority_map = {1: "VIP", 2: "Mid-Range", 3: "Economy"}
        return priority_map.get(priority, "Unknown")
    
    def fcfs_schedule(self) -> List[Task]:
        return sorted([t for t in self.tasks if t.status == "Pending"], 
                     key=lambda x: x.timestamp)
    
    def priority_schedule(self) -> List[Task]:
        # Primary sort by priority (1=VIP, 2=Mid-Range, 3=Economy)
        # Secondary sort by timestamp for same priority
        return sorted([t for t in self.tasks if t.status == "Pending"], 
                     key=lambda x: (x.priority, x.timestamp))
    
    def sjf_schedule(self) -> List[Task]:
        return sorted([t for t in self.tasks if t.status == "Pending"], 
                     key=lambda x: (x.estimated_time, x.priority, x.timestamp))
    
    def round_robin_schedule(self) -> List[Task]:
        pending_tasks = [t for t in self.tasks if t.status == "Pending"]
        return sorted(pending_tasks, key=lambda x: (x.priority, x.timestamp))
    
    def get_scheduled_tasks(self) -> List[Task]:
        if self.current_algorithm == "FCFS":
            return self.fcfs_schedule()
        elif self.current_algorithm == "Priority":
            return self.priority_schedule()
        elif self.current_algorithm == "SJF":
            return self.sjf_schedule()
        elif self.current_algorithm == "Round Robin":
            return self.round_robin_schedule()
        return []

class HotelManagementGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Hotel Management System - Multi-Class Scheduling")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        self.scheduler = HotelScheduler()
        self.is_simulation_running = False
        
        self.create_widgets()
        self.populate_sample_data()
        self.update_displays()
        
    def create_widgets(self):
        # Main container with notebook for better organization
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="🏨 Enhanced Hotel Management System - Multi-Class Service", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Main Operations Tab
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Main Operations")
        
        # Room Management Tab
        self.room_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.room_tab, text="Room Management")
        
        # Analytics Tab
        self.analytics_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.analytics_tab, text="Analytics")
        
        # Create main tab content
        self.create_main_tab_content()
        self.create_room_tab_content()
        self.create_analytics_tab_content()
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
    def create_main_tab_content(self):
        # Left Panel - Task Creation
        self.create_enhanced_task_panel(self.main_tab)
        
        # Middle Panel - Scheduling Control
        self.create_enhanced_scheduling_panel(self.main_tab)
        
        # Right Panel - Current Status
        self.create_enhanced_status_panel(self.main_tab)
        
        # Bottom Panel - Task Lists
        self.create_enhanced_task_lists_panel(self.main_tab)
        
        # Configure grid
        self.main_tab.columnconfigure(0, weight=1)
        self.main_tab.columnconfigure(1, weight=1)
        self.main_tab.columnconfigure(2, weight=1)
        self.main_tab.rowconfigure(2, weight=1)
        
    def create_enhanced_task_panel(self, parent):
        # Enhanced Task Creation Panel
        task_frame = ttk.LabelFrame(parent, text="🛎️ Create New Service Request", padding="10")
        task_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Room Class Selection
        ttk.Label(task_frame, text="Room Class:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.room_class_var = tk.StringVar()
        class_combo = ttk.Combobox(task_frame, textvariable=self.room_class_var, width=15)
        class_combo['values'] = ["Economy", "Mid-Range", "VIP"]
        class_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        class_combo.bind('<<ComboboxSelected>>', self.on_room_class_change)
        
        # Room Number
        ttk.Label(task_frame, text="Room Number:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.room_var = tk.StringVar()
        self.room_combo = ttk.Combobox(task_frame, textvariable=self.room_var, width=15)
        self.room_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Task Type
        ttk.Label(task_frame, text="Service Type:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.task_type_var = tk.StringVar()
        self.task_type_combo = ttk.Combobox(task_frame, textvariable=self.task_type_var, width=15)
        self.task_type_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Estimated Time
        ttk.Label(task_frame, text="Est. Time (min):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.time_var = tk.StringVar()
        time_spin = ttk.Spinbox(task_frame, from_=5, to=120, textvariable=self.time_var, width=15)
        time_spin.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Description
        ttk.Label(task_frame, text="Description:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.desc_var = tk.StringVar()
        desc_entry = ttk.Entry(task_frame, textvariable=self.desc_var, width=15)
        desc_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Service Charge Display
        ttk.Label(task_frame, text="Service Charge:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.charge_label = ttk.Label(task_frame, text="$0.00", foreground="green")
        self.charge_label.grid(row=5, column=1, sticky=tk.W, pady=2)
        
        # Add Task Button
        add_btn = ttk.Button(task_frame, text="➕ Add Service Request", command=self.add_task)
        add_btn.grid(row=6, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        # Quick Add Buttons by Class
        ttk.Label(task_frame, text="Quick Add by Class:").grid(row=7, column=0, columnspan=2, pady=(10, 5))
        
        # Economy Quick Add
        eco_frame = ttk.LabelFrame(task_frame, text="Economy", padding="2")
        eco_frame.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        ttk.Button(eco_frame, text="🛏️ Housekeeping", 
                  command=lambda: self.quick_add_by_class("Economy", "Housekeeping", 45)).pack(side=tk.LEFT, padx=1)
        ttk.Button(eco_frame, text="🍽️ Room Service", 
                  command=lambda: self.quick_add_by_class("Economy", "Room Service", 20)).pack(side=tk.LEFT, padx=1)
        
        # Mid-Range Quick Add
        mid_frame = ttk.LabelFrame(task_frame, text="Mid-Range", padding="2")
        mid_frame.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        ttk.Button(mid_frame, text="🛏️ Premium Clean", 
                  command=lambda: self.quick_add_by_class("Mid-Range", "Premium Housekeeping", 35)).pack(side=tk.LEFT, padx=1)
        ttk.Button(mid_frame, text="🍽️ Premium Service", 
                  command=lambda: self.quick_add_by_class("Mid-Range", "Premium Room Service", 15)).pack(side=tk.LEFT, padx=1)
        
        # VIP Quick Add
        vip_frame = ttk.LabelFrame(task_frame, text="VIP", padding="2")
        vip_frame.grid(row=10, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        ttk.Button(vip_frame, text="👑 Butler Service", 
                  command=lambda: self.quick_add_by_class("VIP", "Butler Service", 10)).pack(side=tk.LEFT, padx=1)
        ttk.Button(vip_frame, text="🥂 Concierge", 
                  command=lambda: self.quick_add_by_class("VIP", "Concierge Service", 12)).pack(side=tk.LEFT, padx=1)
        
        task_frame.columnconfigure(1, weight=1)
        
    def create_enhanced_scheduling_panel(self, parent):
        # Enhanced Scheduling Control Panel
        sched_frame = ttk.LabelFrame(parent, text="⚙️ Multi-Class Scheduling Control", padding="10")
        sched_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # Algorithm Selection
        ttk.Label(sched_frame, text="Scheduling Algorithm:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.algorithm_var = tk.StringVar(value="Priority")
        algorithm_combo = ttk.Combobox(sched_frame, textvariable=self.algorithm_var, width=20)
        algorithm_combo['values'] = ["Priority", "FCFS", "SJF", "Round Robin"]
        algorithm_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        algorithm_combo.bind('<<ComboboxSelected>>', self.on_algorithm_change)
        
        # Time Quantum (for Round Robin)
        ttk.Label(sched_frame, text="Time Quantum (min):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.quantum_var = tk.StringVar(value="15")
        quantum_spin = ttk.Spinbox(sched_frame, from_=5, to=60, textvariable=self.quantum_var, width=20)
        quantum_spin.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Control Buttons
        control_frame = ttk.Frame(sched_frame)
        control_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        self.start_btn = ttk.Button(control_frame, text="▶️ Start Service", 
                                   command=self.start_simulation)
        self.start_btn.pack(side=tk.LEFT, padx=2)
        
        self.stop_btn = ttk.Button(control_frame, text="⏸️ Stop Service", 
                                  command=self.stop_simulation, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=2)
        
        self.clear_btn = ttk.Button(control_frame, text="🗑️ Clear All", 
                                   command=self.clear_all_tasks)
        self.clear_btn.pack(side=tk.LEFT, padx=2)
        
        # Class Priority Settings
        priority_frame = ttk.LabelFrame(sched_frame, text="Class Service Levels", padding="5")
        priority_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(priority_frame, text="🥇 VIP: Immediate Priority", foreground="gold").pack(anchor=tk.W)
        ttk.Label(priority_frame, text="🥈 Mid-Range: Standard Priority", foreground="silver").pack(anchor=tk.W)
        ttk.Label(priority_frame, text="🥉 Economy: Regular Priority", foreground="brown").pack(anchor=tk.W)
        
        # Algorithm Description
        desc_frame = ttk.LabelFrame(sched_frame, text="Algorithm Info", padding="5")
        desc_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.algo_desc = tk.Text(desc_frame, height=6, width=30, wrap=tk.WORD)
        self.algo_desc.pack(fill=tk.BOTH, expand=True)
        
        sched_frame.columnconfigure(1, weight=1)
        
    def create_enhanced_status_panel(self, parent):
        # Enhanced Current Status Panel
        status_frame = ttk.LabelFrame(parent, text="📊 Current Service Status", padding="10")
        status_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # Current Task
        ttk.Label(status_frame, text="Current Service:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W)
        self.current_task_label = ttk.Label(status_frame, text="None", foreground="red")
        self.current_task_label.grid(row=0, column=1, sticky=tk.W)
        
        # Room Class
        ttk.Label(status_frame, text="Room Class:").grid(row=1, column=0, sticky=tk.W)
        self.room_class_label = ttk.Label(status_frame, text="None")
        self.room_class_label.grid(row=1, column=1, sticky=tk.W)
        
        # Staff Member
        ttk.Label(status_frame, text="Staff Member:").grid(row=2, column=0, sticky=tk.W)
        self.staff_label = ttk.Label(status_frame, text="None")
        self.staff_label.grid(row=2, column=1, sticky=tk.W)
        
        # Service Charge
        ttk.Label(status_frame, text="Service Charge:").grid(row=3, column=0, sticky=tk.W)
        self.current_charge_label = ttk.Label(status_frame, text="$0.00", foreground="green")
        self.current_charge_label.grid(row=3, column=1, sticky=tk.W)
        
        # Progress Bar
        ttk.Label(status_frame, text="Progress:").grid(row=4, column=0, sticky=tk.W, pady=(5, 0))
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Statistics
        stats_frame = ttk.LabelFrame(status_frame, text="Service Statistics", padding="5")
        stats_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.stats_text = tk.Text(stats_frame, height=10, width=30)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        status_frame.columnconfigure(1, weight=1)
        
    def create_enhanced_task_lists_panel(self, parent):
        # Enhanced Task Lists Panel
        lists_frame = ttk.Frame(parent)
        lists_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Pending Tasks (now with class information)
        pending_frame = ttk.LabelFrame(lists_frame, text="📋 Service Queue (Scheduled by Class Priority)", padding="5")
        pending_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        self.pending_tree = ttk.Treeview(pending_frame, 
                                        columns=('Class', 'Room', 'Type', 'Priority', 'Time', 'Charge', 'Description'), 
                                        show='headings', height=10)
        self.pending_tree.heading('Class', text='Class')
        self.pending_tree.heading('Room', text='Room')
        self.pending_tree.heading('Type', text='Service Type')
        self.pending_tree.heading('Priority', text='Priority')
        self.pending_tree.heading('Time', text='Est. Time')
        self.pending_tree.heading('Charge', text='Charge')
        self.pending_tree.heading('Description', text='Description')
        
        self.pending_tree.column('Class', width=80)
        self.pending_tree.column('Room', width=70)
        self.pending_tree.column('Type', width=120)
        self.pending_tree.column('Priority', width=70)
        self.pending_tree.column('Time', width=70)
        self.pending_tree.column('Charge', width=70)
        self.pending_tree.column('Description', width=150)
        
        # Add scrollbar
        pending_scroll = ttk.Scrollbar(pending_frame, orient=tk.VERTICAL, command=self.pending_tree.yview)
        self.pending_tree.configure(yscrollcommand=pending_scroll.set)
        self.pending_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        pending_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Completed Tasks
        completed_frame = ttk.LabelFrame(lists_frame, text="✅ Completed Services", padding="5")
        completed_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        self.completed_tree = ttk.Treeview(completed_frame, 
                                          columns=('Class', 'Room', 'Type', 'Staff', 'Time', 'Charge', 'Status'), 
                                          show='headings', height=10)
        self.completed_tree.heading('Class', text='Class')
        self.completed_tree.heading('Room', text='Room')
        self.completed_tree.heading('Type', text='Service')
        self.completed_tree.heading('Staff', text='Staff')
        self.completed_tree.heading('Time', text='Actual Time')
        self.completed_tree.heading('Charge', text='Charge')
        self.completed_tree.heading('Status', text='Status')
        
        self.completed_tree.column('Class', width=70)
        self.completed_tree.column('Room', width=70)
        self.completed_tree.column('Type', width=100)
        self.completed_tree.column('Staff', width=120)
        self.completed_tree.column('Time', width=80)
        self.completed_tree.column('Charge', width=70)
        self.completed_tree.column('Status', width=80)
        
        # Add scrollbar
        completed_scroll = ttk.Scrollbar(completed_frame, orient=tk.VERTICAL, command=self.completed_tree.yview)
        self.completed_tree.configure(yscrollcommand=completed_scroll.set)
        self.completed_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        completed_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        lists_frame.columnconfigure(0, weight=1)
        lists_frame.columnconfigure(1, weight=1)
        
    def create_room_tab_content(self):
        # Room management interface
        room_info_frame = ttk.LabelFrame(self.room_tab, text="🏨 Room Information", padding="10")
        room_info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Room class breakdown
        class_frame = ttk.Frame(room_info_frame)
        class_frame.pack(fill=tk.X, pady=10)
        
        # Economy info
        eco_frame = ttk.LabelFrame(class_frame, text="Economy Rooms (Floors 1-3)", padding="5")
        eco_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        eco_info = "Rooms: 101-330\nAmenities: Basic TV, Wi-Fi, AC, Bathroom\nService Multiplier: 1.0x\nPriority Level: 3 (Regular)"
        ttk.Label(eco_frame, text=eco_info, justify=tk.LEFT).pack()
        
        # Mid-Range info  
        mid_frame = ttk.LabelFrame(class_frame, text="Mid-Range Rooms (Floors 4-6)", padding="5")
        mid_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        mid_info = "Rooms: 401-630\nAmenities: Premium TV, High-Speed Wi-Fi, Climate Control, Premium Bathroom, Mini Fridge, Coffee Maker, Room Service Menu\nService Multiplier: 1.5x\nPriority Level: 2 (Standard)"
        ttk.Label(mid_frame, text=mid_info, justify=tk.LEFT).pack()

        # VIP info
        vip_frame = ttk.LabelFrame(class_frame, text="VIP Rooms (Floors 7-10)", padding="5")
        vip_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        vip_info = "Rooms: 701-1030\nAmenities: Smart TV, Ultra-Fast Wi-Fi, Premium Climate Control, Luxury Bathroom, Mini Bar, Espresso Machine, 24/7 Room Service, Concierge Service, Premium Linens, Balcony, Butler Service\nService Multiplier: 2.5x\nPriority Level: 1 (Immediate)"
        ttk.Label(vip_frame, text=vip_info, justify=tk.LEFT).pack()

    def on_room_class_change(self, event=None):
        """Update room numbers based on selected room class"""
        selected_class = self.room_class_var.get()
        room_numbers = []
        
        if selected_class == "Economy":
            # Floors 1-3, Rooms 101-330
            for floor in range(1, 4):
                for room in range(1, 31):
                    room_numbers.append(f"{floor}{room:02d}")
        elif selected_class == "Mid-Range":
            # Floors 4-6, Rooms 401-630
            for floor in range(4, 7):
                for room in range(1, 31):
                    room_numbers.append(f"{floor}{room:02d}")
        elif selected_class == "VIP":
            # Floors 7-10, Rooms 701-1030
            for floor in range(7, 11):
                for room in range(1, 31):
                    room_numbers.append(f"{floor}{room:02d}")
        
        self.room_combo['values'] = room_numbers
        if room_numbers:
            self.room_combo.set(room_numbers[0])
        else:
            self.room_combo.set('')

    def add_task(self):
        """Add a new service request"""
        try:
            # Get values from input fields
            room_number = self.room_var.get()
            task_type = self.task_type_var.get()
            estimated_time = int(self.time_var.get())
            description = self.desc_var.get()
            
            # Validate inputs
            if not all([room_number, task_type, estimated_time, description]):
                messagebox.showerror("Error", "Please fill in all fields")
                return
            
            # Add task to scheduler
            task = self.scheduler.add_task(room_number, task_type, estimated_time, description)
            
            # Update displays
            self.update_displays()
            
            # Clear input fields
            self.task_type_var.set('')
            self.time_var.set('')
            self.desc_var.set('')
            
            # Show success message
            messagebox.showinfo("Success", f"Service request added for Room {room_number}")
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def update_displays(self):
        """Update all displays with current data"""
        # Clear existing items
        for item in self.pending_tree.get_children():
            self.pending_tree.delete(item)
        for item in self.completed_tree.get_children():
            self.completed_tree.delete(item)
        
        # Update pending tasks
        for task in self.scheduler.tasks:
            if task.status == "Pending":
                self.pending_tree.insert('', 'end', values=(
                    task.room_class,
                    task.room_number,
                    task.task_type,
                    self.scheduler.get_priority_text(task.priority),
                    f"{task.estimated_time} min",
                    f"${task.service_charge:.2f}",
                    task.description
                ))
        
        # Update completed tasks
        for task in self.scheduler.completed_tasks:
            self.completed_tree.insert('', 'end', values=(
                task.room_class,
                task.room_number,
                task.task_type,
                task.assigned_staff,
                f"{task.actual_time} min",
                f"${task.service_charge:.2f}",
                task.status
            ))

    def on_algorithm_change(self, event=None):
        """Update the scheduling algorithm and description when changed in the dropdown."""
        selected_algo = self.algorithm_var.get()
        self.scheduler.current_algorithm = selected_algo
        # Optionally update the time quantum for Round Robin
        if selected_algo == "Round Robin":
            try:
                self.scheduler.time_quantum = int(self.quantum_var.get())
            except Exception:
                self.scheduler.time_quantum = 15
        # Update algorithm description
        desc = {
            "Priority": "Tasks are scheduled based on room class: VIP > Mid-Range > Economy. Within the same class, earlier requests are served first.",
            "FCFS": "First-Come, First-Served: Tasks are handled in the order they arrive, regardless of class.",
            "SJF": "Shortest Job First: Tasks with the shortest estimated time are served first, with class as a tiebreaker.",
            "Round Robin": "Each class gets a time slice (quantum). Tasks are rotated fairly among classes."
        }
        self.algo_desc.delete('1.0', tk.END)
        self.algo_desc.insert(tk.END, desc.get(selected_algo, ""))
        self.update_displays()

    def start_simulation(self):
        """Start the service simulation: process tasks in a background thread."""
        if self.is_simulation_running:
            return
        self.is_simulation_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.simulation_thread = threading.Thread(target=self.run_simulation, daemon=True)
        self.simulation_thread.start()

    def stop_simulation(self):
        """Stop the service simulation."""
        self.is_simulation_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def run_simulation(self):
        while self.is_simulation_running:
            # Get the next scheduled task
            tasks = self.scheduler.get_scheduled_tasks()
            if not tasks:
                self.update_current_status(None)
                time.sleep(0.5)
                continue
            task = tasks[0]
            # Assign staff
            staff = self.scheduler.get_staff_for_room_class(task.room_class)
            task.assigned_staff = staff
            self.update_current_status(task)
            # Simulate progress
            for i in range(task.estimated_time):
                if not self.is_simulation_running:
                    self.update_current_status(None)
                    return
                self.progress_var.set((i + 1) / task.estimated_time * 100)
                self.progress_bar.update()
                time.sleep(0.1)  # 0.1 sec per minute for fast simulation
            # Mark as completed
            task.status = "Completed"
            task.actual_time = task.estimated_time
            self.scheduler.completed_tasks.append(task)
            self.scheduler.tasks.remove(task)
            self.progress_var.set(0)
            self.update_displays()
            self.update_current_status(None)
        self.update_current_status(None)

    def update_current_status(self, task):
        if task is None:
            self.current_task_label.config(text="None", foreground="red")
            self.room_class_label.config(text="None")
            self.staff_label.config(text="None")
            self.current_charge_label.config(text="$0.00")
            self.progress_var.set(0)
        else:
            self.current_task_label.config(text=task.task_type, foreground="green")
            self.room_class_label.config(text=task.room_class)
            self.staff_label.config(text=task.assigned_staff)
            self.current_charge_label.config(text=f"${task.service_charge:.2f}")
            # Progress bar is updated in run_simulation

    def quick_add_by_class(self, room_class, task_type, estimated_time):
        """Quickly add a service request for a random room in the selected class."""
        # Pick a random room number from the class
        if room_class == "Economy":
            room_numbers = [f"{floor}{room:02d}" for floor in range(1, 4) for room in range(1, 31)]
        elif room_class == "Mid-Range":
            room_numbers = [f"{floor}{room:02d}" for floor in range(4, 7) for room in range(1, 31)]
        elif room_class == "VIP":
            room_numbers = [f"{floor}{room:02d}" for floor in range(7, 11) for room in range(1, 31)]
        else:
            room_numbers = []
        if not room_numbers:
            messagebox.showerror("Error", f"No rooms found for class {room_class}")
            return
        room_number = random.choice(room_numbers)
        description = f"Auto-generated {task_type} for {room_class}"
        self.scheduler.add_task(room_number, task_type, estimated_time, description)
        self.update_displays()
        messagebox.showinfo("Quick Add", f"Added {task_type} for Room {room_number} ({room_class})")

    def create_analytics_tab_content(self):
        """Create a placeholder for analytics tab."""
        analytics_label = ttk.Label(self.analytics_tab, text="Analytics and statistics will be shown here.", font=("Arial", 12))
        analytics_label.pack(padx=20, pady=20)

    def clear_all_tasks(self):
        """Clear all tasks from the scheduler."""
        self.scheduler.tasks.clear()
        self.scheduler.completed_tasks.clear()
        self.update_displays()
        messagebox.showinfo("Clear All", "All tasks have been cleared.")

    def populate_sample_data(self):
        """Populate the system with some sample tasks for demonstration."""
        # Add a few sample tasks for each class
        samples = [
            ("101", "Housekeeping", 30, "Sample cleaning for Economy"),
            ("405", "Premium Housekeeping", 25, "Sample cleaning for Mid-Range"),
            ("710", "Butler Service", 10, "Sample butler for VIP")
        ]
        for room, ttype, tmin, desc in samples:
            self.scheduler.add_task(room, ttype, tmin, desc)
        self.update_displays()

# Add main block to run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = HotelManagementGUI(root)
    root.mainloop()