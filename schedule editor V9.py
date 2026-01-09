
     ##         ##############  #########
    ##         ##    ##    ##  ##     ##
   #########  ##    ##    ##  ##     ##
  ##     ##  ##    ##    ##  ##     ##
 #########  ##    ##    ##  ##     ##

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
from datetime import datetime, timedelta

class NMPTVEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("NMP Television Schedule Editor")
        self.root.geometry("1000x700")
        
        self.data = None
        self.tree = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="NMP Television Schedule Editor", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # File operations frame
        file_frame = ttk.LabelFrame(main_frame, text="File Operations", padding="5")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(file_frame, text="Load Schedule", command=self.load_file).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(file_frame, text="Save Schedule", command=self.save_file).grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="New Schedule", command=self.new_schedule).grid(row=0, column=2, padx=5)
        
        # Channel info frame
        info_frame = ttk.LabelFrame(main_frame, text="Channel Information", padding="5")
        info_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        info_frame.columnconfigure(1, weight=1)
        
        ttk.Label(info_frame, text="Channel Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.channel_name_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.channel_name_var, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(info_frame, text="Base URL:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.base_url_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.base_url_var, width=30).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Schedule frame
        schedule_frame = ttk.LabelFrame(main_frame, text="Schedule Template", padding="5")
        schedule_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        schedule_frame.columnconfigure(0, weight=1)
        schedule_frame.rowconfigure(0, weight=1)
        
        # Treeview for schedule
        columns = ('Start Time', 'Show Name', 'Movement')
        self.tree = ttk.Treeview(schedule_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(schedule_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(schedule_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout for treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(buttons_frame, text="Add Entry", command=self.add_entry).grid(row=0, column=0, padx=5)
        ttk.Button(buttons_frame, text="Edit Entry", command=self.edit_entry).grid(row=0, column=1, padx=5)
        ttk.Button(buttons_frame, text="Delete Entry", command=self.delete_entry).grid(row=0, column=2, padx=5)
        ttk.Button(buttons_frame, text="Move Up", command=self.move_up).grid(row=0, column=3, padx=5)
        ttk.Button(buttons_frame, text="Move Down", command=self.move_down).grid(row=0, column=4, padx=5)
        
        # Bind double-click to edit
        self.tree.bind('<Double-1>', lambda e: self.edit_entry())
        
    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Select NMP TV Schedule File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                self.populate_ui()
                messagebox.showinfo("Success", "Schedule loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    
    def save_file(self):
        if not self.data:
            messagebox.showwarning("Warning", "No data to save!")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save NMP TV Schedule",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.update_data_from_ui()
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Success", "Schedule saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def new_schedule(self):
        self.data = {
            "channel_name": "New Channel",
            "base_url": "A:/Video/Film & TV/",
            "template": []
        }
        self.populate_ui()
        messagebox.showinfo("Success", "New schedule created!")
    
    def populate_ui(self):
        if not self.data:
            return
            
        # Update channel info
        self.channel_name_var.set(self.data.get('channel_name', ''))
        self.base_url_var.set(self.data.get('base_url', ''))
        
        # Clear treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Populate treeview
        for entry in self.data.get('template', []):
            show_name = entry['list'][0] if entry['list'] else ''
            
            self.tree.insert('', 'end', values=(
                entry['start'],
                show_name,
                entry['movement']
            ))
    
    def update_data_from_ui(self):
        if not self.data:
            return
            
        # Update channel info
        self.data['channel_name'] = self.channel_name_var.get()
        self.data['base_url'] = self.base_url_var.get()
        
        # Update template from treeview
        self.data['template'] = []
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            entry = {
                'start': values[0],
                'list': [values[1]],
                'index': [0, 4],  # Default index values
                'movement': int(values[2])
            }
            self.data['template'].append(entry)
    
    def add_entry(self):
        self.entry_dialog()
    
    def edit_entry(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an entry to edit!")
            return
        self.entry_dialog(selected[0])
    
    def delete_entry(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an entry to delete!")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this entry?"):
            self.tree.delete(selected[0])
    
    def move_up(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an entry to move!")
            return
        
        item = selected[0]
        prev_item = self.tree.prev(item)
        if prev_item:
            index = self.tree.index(item)
            self.tree.move(item, '', index - 1)
    
    def move_down(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an entry to move!")
            return
        
        item = selected[0]
        next_item = self.tree.next(item)
        if next_item:
            index = self.tree.index(item)
            self.tree.move(item, '', index + 1)
    
    def entry_dialog(self, item=None):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add/Edit Schedule Entry")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Variables
        start_time_var = tk.StringVar()
        show_name_var = tk.StringVar()
        movement_var = tk.StringVar()
        
        # If editing, populate with current values
        if item:
            values = self.tree.item(item)['values']
            start_time_var.set(values[0])
            show_name_var.set(values[1])
            movement_var.set(str(values[2]))
        else:
            # Default values for new entry
            start_time_var.set("00:00")
            movement_var.set("1")
        
        # Form fields
        ttk.Label(dialog, text="Start Time (HH:MM):").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        ttk.Entry(dialog, textvariable=start_time_var, width=20).grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Show Name:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        ttk.Entry(dialog, textvariable=show_name_var, width=20).grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Movement:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        ttk.Entry(dialog, textvariable=movement_var, width=20).grid(row=2, column=1, padx=10, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        def save_entry():
            try:
                # Validate inputs
                start_time = start_time_var.get()
                show_name = show_name_var.get().strip()
                movement = int(movement_var.get())
                
                if not show_name:
                    messagebox.showerror("Error", "Show name cannot be empty!")
                    return
                
                # Validate time format
                try:
                    datetime.strptime(start_time, "%H:%M")
                except ValueError:
                    messagebox.showerror("Error", "Invalid time format! Use HH:MM")
                    return
                
                values = (start_time, show_name, movement)
                
                if item:
                    # Update existing item
                    for i, col in enumerate(self.tree['columns']):
                        self.tree.set(item, col, values[i])
                else:
                    # Add new item
                    self.tree.insert('', 'end', values=values)
                
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Movement must be a number!")
        
        ttk.Button(button_frame, text="Save", command=save_entry).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).grid(row=0, column=1, padx=5)

def main():
    root = tk.Tk()
    app = NMPTVEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
