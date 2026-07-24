import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import math
import os

try:
    from PIL import Image, ImageTk, ImageDraw
except ImportError:
    os.system('pip install Pillow')
    from PIL import Image, ImageTk, ImageDraw

class FootprintGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("KiCad Visual Footprint Generator (Pro CAD Edition)")
        self.root.geometry("1450x800")
        
        self.image = None
        self.photo = None
        self.pixels_per_mm = None
        self.origin = None
        self.mode = tk.StringVar(value="perspective")
        
        self.perspective_points = []
        self.level_points = []
        self.calibrate_points = []
        self.pins = []
        self.smd_pads = []
        self.mounting_holes = []
        self.outline_points = []
        self.history = [] 
        
        self.snap_x = None
        self.snap_y = None
        self.mag_photo = None
        self.snap_enabled = True
        
        self.setup_ui()
        
        self.canvas = tk.Canvas(root, cursor="cross", bg="gray20")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Escape>", self.toggle_snap)
        self.canvas.bind("<Button-2>", self.close_outline)
        
        # Nudge bindings
        self.root.bind("<Up>", lambda e: self.nudge(0, -1))
        self.root.bind("<Down>", lambda e: self.nudge(0, 1))
        self.root.bind("<Left>", lambda e: self.nudge(-1, 0))
        self.root.bind("<Right>", lambda e: self.nudge(1, 0))
        
    def nudge(self, dx, dy):
        if not self.history: return
        action_type = self.history[-1][0]
        if action_type == "perspective" and self.perspective_points:
            self.perspective_points[-1] = (self.perspective_points[-1][0] + dx, self.perspective_points[-1][1] + dy)
        elif action_type == "level" and self.level_points:
            self.level_points[-1] = (self.level_points[-1][0] + dx, self.level_points[-1][1] + dy)
        elif action_type == "calibrate" and self.calibrate_points:
            self.calibrate_points[-1] = (self.calibrate_points[-1][0] + dx, self.calibrate_points[-1][1] + dy)
        elif action_type == "origin" and self.origin:
            self.origin = (self.origin[0] + dx, self.origin[1] + dy)
        elif action_type == "pins" and self.pins:
            self.pins[-1] = (self.pins[-1][0] + dx, self.pins[-1][1] + dy)
        elif action_type == "smd_pads" and self.smd_pads:
            self.smd_pads[-1] = (self.smd_pads[-1][0] + dx, self.smd_pads[-1][1] + dy)
        elif action_type == "holes" and self.mounting_holes:
            self.mounting_holes[-1] = (self.mounting_holes[-1][0] + dx, self.mounting_holes[-1][1] + dy)
        elif action_type == "outline" and self.outline_points:
            self.outline_points[-1] = (self.outline_points[-1][0] + dx, self.outline_points[-1][1] + dy)
        self.redraw()
        
    def toggle_snap(self, event=None):
        self.snap_enabled = not self.snap_enabled
        status = "ON" if self.snap_enabled else "OFF"
        self.canvas.delete("guide")
        
        # Show temporary text on canvas
        self.canvas.delete("snap_status")
        color = "lime" if self.snap_enabled else "red"
        vx = self.canvas.canvasx(self.canvas.winfo_width() / 2)
        vy = self.canvas.canvasy(50)
        self.canvas.create_text(vx, vy, text=f"Auto-Snap: {status}", fill=color, font=("Arial", 24, "bold"), tags="snap_status")
        self.root.after(1500, lambda: self.canvas.delete("snap_status"))
        
    def setup_ui(self):
        toolbar = tk.Frame(self.root, bg="gray80", pady=5)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        tk.Button(toolbar, text="Load Image", command=self.load_image, font=("Arial", 10, "bold"), bg="lightblue").pack(side=tk.LEFT, padx=5)
        
        tk.Radiobutton(toolbar, text="1. Perspective (4 pts)", variable=self.mode, value="perspective", bg="pink").pack(side=tk.LEFT, padx=2)
        tk.Radiobutton(toolbar, text="2. Auto-Level", variable=self.mode, value="level", bg="gray80").pack(side=tk.LEFT, padx=2)
        tk.Radiobutton(toolbar, text="3. Calibrate", variable=self.mode, value="calibrate", bg="gray80").pack(side=tk.LEFT, padx=2)
        tk.Radiobutton(toolbar, text="4. Pin 1", variable=self.mode, value="origin", bg="gray80").pack(side=tk.LEFT, padx=2)
        tk.Radiobutton(toolbar, text="5. THT Pins", variable=self.mode, value="pins", bg="gray80").pack(side=tk.LEFT, padx=2)
        tk.Radiobutton(toolbar, text="6. SMD Pads", variable=self.mode, value="smd_pads", bg="yellow").pack(side=tk.LEFT, padx=2)
        tk.Radiobutton(toolbar, text="7. Holes", variable=self.mode, value="holes", bg="gray80").pack(side=tk.LEFT, padx=2)
        tk.Radiobutton(toolbar, text="8. Outline", variable=self.mode, value="outline", bg="gray80").pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Close Outline", command=self.close_outline, bg="plum").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="Undo (Ctrl+Z)", command=self.undo, bg="orange").pack(side=tk.LEFT, padx=10)
        tk.Button(toolbar, text="Export to KiCad", command=self.export, bg="lightgreen", font=("Arial", 10, "bold")).pack(side=tk.RIGHT, padx=10)
        
    def load_image(self):
        filepath = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])
        if filepath:
            self.image = Image.open(filepath).convert("RGBA")
            max_w, max_h = 1200, 700
            if self.image.width > max_w or self.image.height > max_h:
                self.image.thumbnail((max_w, max_h), Image.LANCZOS)
                
            self.photo = ImageTk.PhotoImage(self.image)
            self.canvas.config(scrollregion=(0, 0, self.image.width, self.image.height))
            self.reset_state()
            
    def reset_state(self):
        self.perspective_points.clear()
        self.level_points.clear()
        self.calibrate_points.clear()
        self.pins.clear()
        self.smd_pads.clear()
        self.mounting_holes.clear()
        self.outline_points.clear()
        self.history.clear()
        self.origin = None
        self.redraw()
            
    def redraw(self):
        self.canvas.delete("all")
        if self.photo:
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            
        for p in self.perspective_points:
            self.canvas.create_oval(p[0]-3, p[1]-3, p[0]+3, p[1]+3, fill="pink")
        if len(self.perspective_points) > 1:
            for i in range(len(self.perspective_points)-1):
                self.canvas.create_line(self.perspective_points[i], self.perspective_points[i+1], fill="pink", dash=(4,4))
            
        for p in self.level_points:
            self.canvas.create_oval(p[0]-3, p[1]-3, p[0]+3, p[1]+3, fill="magenta")
        if len(self.level_points) == 2:
            self.canvas.create_line(self.level_points[0], self.level_points[1], fill="magenta", dash=(4,4))
            
        for p in self.calibrate_points:
            self.canvas.create_oval(p[0]-3, p[1]-3, p[0]+3, p[1]+3, fill="red")
        if len(self.calibrate_points) == 2:
            self.canvas.create_line(self.calibrate_points[0], self.calibrate_points[1], fill="red", dash=(4,4))
            
        if self.origin:
            x, y = self.origin
            self.canvas.create_oval(x-4, y-4, x+4, y+4, fill="yellow", outline="black")
            
        for i, p in enumerate(self.pins):
            self.canvas.create_oval(p[0]-3, p[1]-3, p[0]+3, p[1]+3, fill="blue")
            self.canvas.create_text(p[0]+12, p[1], text=str(i+1), fill="white", font=("Arial", 12, "bold"))
            
        for i, p in enumerate(self.smd_pads):
            self.canvas.create_rectangle(p[0]-4, p[1]-4, p[0]+4, p[1]+4, fill="purple", outline="white")
            self.canvas.create_text(p[0]+12, p[1], text=str(len(self.pins)+i+1), fill="yellow", font=("Arial", 12, "bold"))
            
        for p in self.mounting_holes:
            self.canvas.create_oval(p[0]-6, p[1]-6, p[0]+6, p[1]+6, fill="orange", outline="black", width=2)
            
        for p in self.outline_points:
            self.canvas.create_oval(p[0]-2, p[1]-2, p[0]+2, p[1]+2, fill="lime")
        if len(self.outline_points) > 1:
            for i in range(len(self.outline_points)-1):
                self.canvas.create_line(self.outline_points[i], self.outline_points[i+1], fill="lime", width=2)
                
    def on_mouse_move(self, event):
        if not self.image: return
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        
        self.snap_x, self.snap_y = x, y
        self.canvas.delete("guide")
        
        # Always draw full-screen tracking crosshairs in perspective mode for rounded corners
        if self.mode.get() == "perspective":
            self.canvas.create_line(x, 0, x, self.image.height, fill="yellow", dash=(2,2), tags="guide")
            self.canvas.create_line(0, y, self.image.width, y, fill="yellow", dash=(2,2), tags="guide")
            
        if self.mode.get() in ["pins", "smd_pads", "holes", "outline"] and self.snap_enabled:
            snap_dist = 12
            all_pts = self.pins + self.smd_pads + self.mounting_holes + self.outline_points
            if self.origin: all_pts.append(self.origin)
            
            for p in all_pts:
                if abs(x - p[0]) < snap_dist:
                    self.snap_x = p[0]
                    self.canvas.create_line(self.snap_x, 0, self.snap_x, self.image.height, fill="cyan", dash=(4,4), tags="guide")
                if abs(y - p[1]) < snap_dist:
                    self.snap_y = p[1]
                    self.canvas.create_line(0, self.snap_y, self.image.width, self.snap_y, fill="cyan", dash=(4,4), tags="guide")
        
        # Visual feedback for Auto-Closing outline
        if self.mode.get() == "outline" and len(self.outline_points) > 1:
            start_x, start_y = self.outline_points[0]
            if math.hypot(x - start_x, y - start_y) < 15:
                self.canvas.create_oval(start_x-10, start_y-10, start_x+10, start_y+10, outline="magenta", width=3, tags="guide")
                    
        crop_size = 40
        zoom = 4
        mag_size = crop_size * zoom
        
        left, upper = int(self.snap_x - crop_size/2), int(self.snap_y - crop_size/2)
        right, lower = int(self.snap_x + crop_size/2), int(self.snap_y + crop_size/2)
        
        # PIL crop automatically pads with black if out of bounds, so we don't need an if-check!
        crop = self.image.crop((left, upper, right, lower))
        mag_img = crop.resize((mag_size, mag_size), Image.NEAREST)
        draw = ImageDraw.Draw(mag_img)
        draw.line((mag_size/2, 0, mag_size/2, mag_size), fill="red", width=1)
        draw.line((0, mag_size/2, mag_size, mag_size/2), fill="red", width=1)
        self.mag_photo = ImageTk.PhotoImage(mag_img)
        self.canvas.delete("mag")
        vx = self.canvas.canvasx(self.canvas.winfo_width() - mag_size - 30)
        vy = self.canvas.canvasy(30)
        self.canvas.create_image(vx, vy, anchor=tk.NW, image=self.mag_photo, tags="mag")
        self.canvas.create_rectangle(vx, vy, vx+mag_size, vy+mag_size, outline="red", width=3, tags="mag")

    def on_click(self, event):
        x = self.snap_x if self.snap_x else self.canvas.canvasx(event.x)
        y = self.snap_y if self.snap_y else self.canvas.canvasy(event.y)
        
        if self.mode.get() == "perspective":
            self.perspective_points.append((x, y))
            self.history.append(("perspective",))
            if len(self.perspective_points) == 4:
                self.redraw()
                try:
                    import cv2
                    import numpy as np
                except ImportError:
                    self.canvas.delete("all")
                    self.canvas.create_text(500, 400, text="Installing OpenCV for Perspective Math... Please Wait...", fill="white", font=("Arial", 20))
                    self.canvas.update()
                    os.system('pip install opencv-python numpy')
                    import cv2
                    import numpy as np
                
                pts1 = np.float32(self.perspective_points)
                # Calculate bounding box
                width_a = np.linalg.norm(pts1[2] - pts1[3])
                width_b = np.linalg.norm(pts1[1] - pts1[0])
                maxWidth = max(int(width_a), int(width_b))
                
                height_a = np.linalg.norm(pts1[1] - pts1[2])
                height_b = np.linalg.norm(pts1[0] - pts1[3])
                maxHeight = max(int(height_a), int(height_b))
                
                pts2 = np.float32([[0, 0], [maxWidth - 1, 0], [maxWidth - 1, maxHeight - 1], [0, maxHeight - 1]])
                
                cv_img = cv2.cvtColor(np.array(self.image), cv2.COLOR_RGBA2BGRA)
                matrix = cv2.getPerspectiveTransform(pts1, pts2)
                warped = cv2.warpPerspective(cv_img, matrix, (maxWidth, maxHeight))
                
                self.image = Image.fromarray(cv2.cvtColor(warped, cv2.COLOR_BGRA2RGBA))
                self.photo = ImageTk.PhotoImage(self.image)
                self.canvas.config(scrollregion=(0, 0, self.image.width, self.image.height))
                
                self.reset_state()
                messagebox.showinfo("Flattened", "Perspective mathematically corrected! The board is now perfectly flat.")
                self.mode.set("level")
                
        elif self.mode.get() == "level":
            self.level_points.append((x, y))
            self.history.append(("level",))
            if len(self.level_points) == 2:
                self.redraw()
                dx = self.level_points[1][0] - self.level_points[0][0]
                dy = self.level_points[1][1] - self.level_points[0][1]
                angle_deg = math.degrees(math.atan2(dy, dx))
                self.image = self.image.rotate(angle_deg, expand=True, resample=Image.BICUBIC)
                self.photo = ImageTk.PhotoImage(self.image)
                self.canvas.config(scrollregion=(0, 0, self.image.width, self.image.height))
                self.reset_state()
                self.mode.set("calibrate")
                
        elif self.mode.get() == "calibrate":
            self.calibrate_points.append((x, y))
            self.history.append(("calibrate",))
            if len(self.calibrate_points) == 2:
                self.redraw()
                dist_px = math.hypot(self.calibrate_points[1][0] - self.calibrate_points[0][0], self.calibrate_points[1][1] - self.calibrate_points[0][1])
                dist_mm = simpledialog.askfloat("Calibration", "Distance in mm? (e.g. 2.54)")
                if dist_mm and dist_mm > 0:
                    self.pixels_per_mm = dist_px / dist_mm
                    self.mode.set("origin")
                else:
                    self.history.pop(); self.history.pop()
                    self.calibrate_points.clear()
                    
        elif self.mode.get() == "origin":
            old = self.origin
            self.origin = (x, y)
            self.history.append(("origin", old))
            self.mode.set("pins")
        elif self.mode.get() == "pins":
            self.pins.append((x, y))
            self.history.append(("pins",))
        elif self.mode.get() == "smd_pads":
            self.smd_pads.append((x, y))
            self.history.append(("smd_pads",))
        elif self.mode.get() == "holes":
            self.mounting_holes.append((x, y))
            self.history.append(("holes",))
        elif self.mode.get() == "outline":
            # Auto-close snap if clicking near the very first point
            if len(self.outline_points) >= 2:
                start_x, start_y = self.outline_points[0]
                if math.hypot(x - start_x, y - start_y) < 15:
                    self.outline_points.append(self.outline_points[0])
                    self.history.append(("outline",))
                    self.redraw()
                    return
            self.outline_points.append((x, y))
            self.history.append(("outline",))
        self.redraw()
        
    def on_right_click(self, event):
        self.close_outline()
        
    def close_outline(self, event=None):
        if self.mode.get() == "outline" and len(self.outline_points) > 2:
            self.outline_points.append(self.outline_points[0]) 
            self.history.append(("outline",))
            self.redraw()

    def undo(self):
        if not self.history: return
        action = self.history.pop()
        if action[0] == "perspective":
            if self.perspective_points: self.perspective_points.pop()
        elif action[0] == "level":
            if self.level_points: self.level_points.pop()
        elif action[0] == "calibrate":
            if self.calibrate_points: self.calibrate_points.pop()
        elif action[0] == "origin":
            self.origin = action[1]
        elif action[0] == "pins":
            if self.pins: self.pins.pop()
        elif action[0] == "smd_pads":
            if self.smd_pads: self.smd_pads.pop()
        elif action[0] == "holes":
            if self.mounting_holes: self.mounting_holes.pop()
        elif action[0] == "outline":
            if self.outline_points: self.outline_points.pop()
        self.redraw()
        
    def export(self):
        if not self.pixels_per_mm:
            messagebox.showerror("Error", "Calibrate scale first!")
            return
        if not self.origin:
            messagebox.showerror("Error", "Set Pin 1 first!")
            return
            
        filename = filedialog.asksaveasfilename(defaultextension=".kicad_mod", filetypes=[("KiCad Footprint", "*.kicad_mod")], initialfile="Custom_Breakout.kicad_mod")
        if not filename: return
        name = filename.split("/")[-1].replace(".kicad_mod", "")
        
        def px_to_mm(px_x, px_y):
            return (px_x - self.origin[0]) / self.pixels_per_mm, (px_y - self.origin[1]) / self.pixels_per_mm

        out = f'(footprint "{name}" (version 20211014) (generator pcbnew)\n  (layer "F.Cu")\n  (attr smd)\n'
        out += f'  (fp_text reference "REF**" (at 0 -2.5) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))\n'
        
        if len(self.outline_points) > 2:
            pts = " ".join([f"(xy {px_to_mm(p[0], p[1])[0]:.3f} {px_to_mm(p[0], p[1])[1]:.3f})" for p in self.outline_points])
            out += f'  (fp_poly (pts {pts}) (layer "F.SilkS") (width 0.12) (fill none))\n'
            out += f'  (fp_poly (pts {pts}) (layer "F.CrtYd") (width 0.05) (fill none))\n'

        for i, p in enumerate(self.pins):
            mx, my = px_to_mm(p[0], p[1])
            out += f'  (pad "{i+1}" thru_hole {"rect" if i==0 else "circle"} (at {mx:.3f} {my:.3f}) (size 1.7 1.7) (drill 1.0) (layers *.Cu *.Mask))\n'
            
        for i, p in enumerate(self.smd_pads):
            mx, my = px_to_mm(p[0], p[1])
            pad_num = len(self.pins) + i + 1
            out += f'  (pad "{pad_num}" smd rect (at {mx:.3f} {my:.3f}) (size 2.5 1.5) (layers "F.Cu" "F.Paste" "F.Mask"))\n'

        for p in self.mounting_holes:
            mx, my = px_to_mm(p[0], p[1])
            out += f'  (pad "" np_thru_hole circle (at {mx:.3f} {my:.3f}) (size 2.5 2.5) (drill 2.5) (layers *.Cu *.Mask))\n'

        with open(filename, "w") as f:
            f.write(out + ')\n')
        messagebox.showinfo("Success", f"Footprint {name}.kicad_mod exported!")

if __name__ == "__main__":
    root = tk.Tk()
    app = FootprintGenerator(root)
    root.mainloop()
