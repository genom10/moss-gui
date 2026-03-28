"""
Analysis Page - Visualize MOSS plagiarism results as a graph.
"""
import customtkinter as ctk
import os
import re
import requests
from pathlib import Path
from tkinter import filedialog

from components.form_inputs import LabeledEntry, LabeledSlider, StatusLabel


class PlagiarismGraph(ctk.CTkCanvas):
    """Canvas for drawing plagiarism network graph with force-directed layout."""

    def __init__(self, master, **kwargs):
        super().__init__(master, bg="#2b2b2b", highlightthickness=0, **kwargs)
        self.nodes = {}  # {name: {'x': x, 'y': y, 'vx': vx, 'vy': vy}}
        self.edges = []  # [(name1, name2, weight)]
        self.node_radius = 25
        self.colors = {}
        self.layout_running = False
        
        # Zoom and pan state
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.center_x = 400
        self.center_y = 250
        
        # Bind mouse wheel for zoom
        self.bind('<MouseWheel>', self._on_zoom)
        self.bind('<Button-4>', self._on_zoom)
        self.bind('<Button-5>', self._on_zoom)
        
        # Bind drag for pan
        self.bind('<Button-1>', self._on_pan_start)
        self.bind('<B1-Motion>', self._on_pan_move)

    def _on_zoom(self, event):
        """Handle mouse wheel zoom."""
        if event.num == 4 or event.delta > 0:
            # Zoom in
            self.zoom_level = min(3.0, self.zoom_level * 1.15)
        elif event.num == 5 or event.delta < 0:
            # Zoom out
            self.zoom_level = max(0.3, self.zoom_level / 1.15)
        
        self._draw()

    def _on_pan_start(self, event):
        """Start panning."""
        self._pan_start_x = event.x
        self._pan_start_y = event.y

    def _reset_view(self):
        """Reset zoom and pan to default."""
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self._draw()

    def _on_pan_move(self, event):
        """Handle panning."""
        dx = event.x - self._pan_start_x
        dy = event.y - self._pan_start_y
        self.pan_x += dx
        self.pan_y += dy
        self._pan_start_x = event.x
        self._pan_start_y = event.y
        self._draw()

    def clear(self):
        """Clear the graph."""
        self.delete("all")
        self.nodes = {}
        self.edges = []
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0

    def set_data(self, edges: list, cutoff: float = 0):
        """
        Set graph data and run force-directed layout.
        edges: [(name1, name2, weight_percent), ...]
        """
        self.clear()
        
        # Filter by cutoff
        self.edges = [(a, b, w) for a, b, w in edges if w >= cutoff]
        
        # Collect all unique nodes
        all_nodes = set()
        for a, b, _ in self.edges:
            all_nodes.add(a)
            all_nodes.add(b)
        
        if not all_nodes:
            return
        
        # Initialize node positions randomly
        self._init_nodes(list(all_nodes))
        
        # Run force-directed layout
        self._run_force_directed_layout()

    def _init_nodes(self, nodes: list):
        """Initialize nodes with random positions."""
        import random
        width = self.winfo_width() if self.winfo_width() > 1 else 800
        height = self.winfo_height() if self.winfo_height() > 1 else 500
        
        self.center_x = width // 2
        self.center_y = height // 2
        
        for name in nodes:
            self.nodes[name] = {
                'x': random.uniform(width * 0.2, width * 0.8),
                'y': random.uniform(height * 0.2, height * 0.8),
                'vx': 0,
                'vy': 0
            }
            # Assign color based on hash of name
            hue = hash(name) % 360 / 360
            self.colors[name] = self._hsv_to_rgb(hue, 0.7, 0.8)

    def _run_force_directed_layout(self):
        """Run Fruchterman-Reingold force-directed layout simulation."""
        if self.layout_running:
            return
        self.layout_running = True
        
        width = self.winfo_width() if self.winfo_width() > 1 else 800
        height = self.winfo_height() if self.winfo_height() > 1 else 500
        
        n = len(self.nodes)
        if n == 0:
            self.layout_running = False
            return
        
        # Optimal distance between nodes (smaller = more compact)
        k = ((width * height) / n) ** 0.5 * 0.4
        
        # Temperature (controls movement magnitude)
        initial_temp = k / 5
        current_temp = initial_temp
        
        # Track which nodes have edges
        has_edge = {name: False for name in self.nodes}
        for name1, name2, _ in self.edges:
            has_edge[name1] = True
            has_edge[name2] = True
        
        iterations = 500
        
        # Stronger gravity to keep nodes from flying to edges
        gravity = 0.5
        
        def step():
            nonlocal current_temp, iterations
            
            forces = {name: {'fx': 0.0, 'fy': 0.0} for name in self.nodes}
            node_list = list(self.nodes.keys())
            
            # Calculate repulsion between ALL pairs of nodes
            for i, name1 in enumerate(node_list):
                for j in range(i + 1, len(node_list)):
                    name2 = node_list[j]
                    
                    dx = self.nodes[name1]['x'] - self.nodes[name2]['x']
                    dy = self.nodes[name1]['y'] - self.nodes[name2]['y']
                    dist_sq = dx * dx + dy * dy
                    dist = max(0.1, dist_sq ** 0.5)
                    
                    # Repulsion force (stronger for isolated nodes)
                    repulsion_mult = 25 if (not has_edge[name1] or not has_edge[name2]) else 1.0
                    force = repulsion_mult * k * k / dist
                    
                    fx = force * dx / dist
                    fy = force * dy / dist
                    
                    forces[name1]['fx'] += fx
                    forces[name1]['fy'] += fy
                    forces[name2]['fx'] -= fx
                    forces[name2]['fy'] -= fy
            
            # Calculate attraction for connected nodes (spring force)
            for name1, name2, weight in self.edges:
                if name1 not in self.nodes or name2 not in self.nodes:
                    continue
                
                dx = self.nodes[name2]['x'] - self.nodes[name1]['x']
                dy = self.nodes[name2]['y'] - self.nodes[name1]['y']
                dist = max(0.1, (dx * dx + dy * dy) ** 0.5)
                
                # Spring force: F = (dist - ideal_length) / k
                ideal_length = k * 0.6  # Keep connected nodes closer
                force = (dist - ideal_length) / k
                
                fx = force * dx
                fy = force * dy
                
                forces[name1]['fx'] += fx
                forces[name1]['fy'] += fy
                forces[name2]['fx'] -= fx
                forces[name2]['fy'] -= fy
            
            # Apply stronger gravity to keep nodes centered
            center_x, center_y = width / 2, height / 2
            for name in self.nodes:
                dx = center_x - self.nodes[name]['x']
                dy = center_y - self.nodes[name]['y']
                forces[name]['fx'] += dx * gravity
                forces[name]['fy'] += dy * gravity
            
            # Update positions with temperature-based cooling
            for name in self.nodes:
                node = self.nodes[name]
                f = forces[name]
                
                # Calculate displacement magnitude
                disp_sq = f['fx'] * f['fx'] + f['fy'] * f['fy']
                disp = disp_sq ** 0.5
                
                if disp > 0:
                    # Limit displacement by temperature
                    move = min(disp, current_temp)
                    
                    # Update position
                    node['x'] += f['fx'] / disp * move
                    node['y'] += f['fy'] / disp * move
                    
                    # Keep within bounds (with margin) - stronger constraint
                    margin = self.node_radius + 10
                    node['x'] = max(margin, min(width - margin, node['x']))
                    node['y'] = max(margin, min(height - margin, node['y']))
            
            # Draw the graph
            self._draw()
            
            # Cool down temperature (simulated annealing) - faster cooling
            current_temp *= 0.92
            
            # Continue or stop
            iterations -= 1
            if iterations > 0 and current_temp > 0.5:
                self.after(10, step)
            else:
                self.layout_running = False
        
        step()

    def _hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB hex color."""
        i = int(h * 6)
        f = h * 6 - i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        
        if i % 6 == 0:
            r, g, b = v, t, p
        elif i % 6 == 1:
            r, g, b = q, v, p
        elif i % 6 == 2:
            r, g, b = p, v, t
        elif i % 6 == 3:
            r, g, b = p, q, v
        elif i % 6 == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q
        
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

    def _draw(self):
        """Draw the complete graph."""
        self.delete("all")
        
        # Draw edges first (so they appear behind nodes)
        self._draw_edges()
        
        # Draw nodes
        self._draw_nodes()

    def _apply_transform(self, x, y):
        """Apply zoom and pan transform to coordinates."""
        # Transform around center
        cx, cy = self.center_x, self.center_y
        new_x = cx + (x - cx) * self.zoom_level + self.pan_x
        new_y = cy + (y - cy) * self.zoom_level + self.pan_y
        return new_x, new_y

    def _draw_edges(self):
        """Draw all edges with thickness based on weight."""
        for name1, name2, weight in self.edges:
            if name1 not in self.nodes or name2 not in self.nodes:
                continue
            
            x1, y1 = self.nodes[name1]['x'], self.nodes[name1]['y']
            x2, y2 = self.nodes[name2]['x'], self.nodes[name2]['y']
            
            # Apply zoom/pan transform
            x1, y1 = self._apply_transform(x1, y1)
            x2, y2 = self._apply_transform(x2, y2)
            
            # Line thickness based on weight (0-100%)
            # Weight 0% = 1px, Weight 100% = 15px
            line_width = max(1, int(weight / 100 * 15)) * self.zoom_level
            
            # Color based on weight (green -> yellow -> red)
            if weight < 30:
                color = "#2ecc71"  # Green
            elif weight < 60:
                color = "#f39c12"  # Orange
            else:
                color = "#e74c3c"  # Red
            
            self.create_line(x1, y1, x2, y2, fill=color, width=line_width, capstyle="round")

    def _draw_nodes(self):
        """Draw all nodes."""
        for name, data in self.nodes.items():
            x, y = data['x'], data['y']
            
            # Apply zoom/pan transform
            x, y = self._apply_transform(x, y)
            
            color = self.colors.get(name, "#3498db")
            radius = self.node_radius * self.zoom_level
            
            # Draw circle
            self.create_oval(
                x - radius, y - radius,
                x + radius, y + radius,
                fill=color, outline="white", width=max(2, int(2 * self.zoom_level))
            )
            
            # Draw truncated name (scale font with zoom)
            display_name = name
            if len(display_name) > 15:
                display_name = display_name[:12] + "..."
            
            font_size = max(8, int(9 * self.zoom_level))
            self.create_text(
                x, y, text=display_name, fill="white",
                font=ctk.CTkFont(size=font_size, weight="bold"),
                justify="center"
            )


class AnalysisPage(ctk.CTkFrame):
    """Page 4: Analyze and visualize MOSS plagiarism results."""

    def __init__(self, master, on_back=None, **kwargs):
        super().__init__(master, **kwargs)

        self.on_back = on_back
        self.moss_url = ""
        self.parsed_edges = []

        self._create_ui()

    def _create_ui(self):
        """Create the page UI."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self._create_header(header_frame)

        # Main content
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self._create_content(content_frame)

    def _create_header(self, parent):
        """Create header with title."""
        parent.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            parent,
            text="Plagiarism Analysis",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.grid(row=0, column=0, sticky="w", pady=10)

    def _create_content(self, parent):
        """Create main content area."""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        # Top panel - controls
        controls_frame = ctk.CTkFrame(parent)
        controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self._create_controls(controls_frame)

        # Graph canvas
        self.graph = PlagiarismGraph(parent, height=500)
        self.graph.grid(row=1, column=0, sticky="nsew")

    def _create_controls(self, parent):
        """Create control panel."""
        parent.grid_columnconfigure(0, weight=1)

        # URL input
        self.url_entry = LabeledEntry(
            parent,
            label="MOSS Report URL",
            placeholder="http://moss.stanford.edu/results/..."
        )
        self.url_entry.grid(row=0, column=0, sticky="ew", pady=5)

        # Cutoff slider
        self.cutoff_slider = LabeledSlider(
            parent,
            label="Cutoff Percent (%)",
            from_=0,
            to=100,
            initial=10
        )
        self.cutoff_slider.grid(row=1, column=0, sticky="ew", pady=5)

        # Buttons
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", pady=10)

        self.visualize_btn = ctk.CTkButton(
            btn_frame,
            text="Visualize Graph",
            command=self._visualize,
            width=150,
            fg_color="#27ae60"
        )
        self.visualize_btn.pack(side="left", padx=5)

        self.import_btn = ctk.CTkButton(
            btn_frame,
            text="Import from Grading",
            command=self._import_url,
            width=150
        )
        self.import_btn.pack(side="left", padx=5)

        self.reset_view_btn = ctk.CTkButton(
            btn_frame,
            text="Reset View",
            command=self._on_reset_view,
            width=100,
            fg_color="gray"
        )
        self.reset_view_btn.pack(side="left", padx=5)

        # Zoom indicator
        self.zoom_label = ctk.CTkLabel(
            parent,
            text="Zoom: 100%  |  Scroll to zoom, Drag to pan",
            text_color="gray",
            font=ctk.CTkFont(size=10),
            anchor="w"
        )
        self.zoom_label.grid(row=3, column=0, sticky="w", pady=5)

        # Status label
        self.status_label = StatusLabel(parent, anchor="w", justify="left")
        self.status_label.grid(row=4, column=0, sticky="ew", pady=5)

    def _import_url(self):
        """Import URL from grading page."""
        # Try to read from moss_config.json or grading result
        result_file = Path("moss_result.txt")
        if result_file.exists():
            url = result_file.read_text().strip()
            self.url_entry.set(url)
            self.status_label.success(f"Imported URL: {url[:50]}...")
        else:
            self.status_label.warning("No saved result found. Run MOSS first.")

    def _on_reset_view(self):
        """Reset graph view."""
        self.graph._reset_view()

    def _visualize(self):
        """Visualize the plagiarism graph."""
        url = self.url_entry.get().strip()
        cutoff = self.cutoff_slider.get()

        if not url:
            self.status_label.error("Please enter a MOSS report URL")
            return

        self.status_label.info("Fetching and parsing MOSS results...")
        self.visualize_btn.configure(state="disabled", text="Loading...")

        # Run in background thread
        import threading
        thread = threading.Thread(target=self._fetch_and_parse, args=(url, cutoff))
        thread.daemon = True
        thread.start()

    def _fetch_and_parse(self, url: str, cutoff: float):
        """Fetch MOSS page and parse results."""
        try:
            # Fetch the page
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse the HTML
            edges = self._parse_moss_results(response.text)
            
            if not edges:
                self.after(0, lambda: self.status_label.error(
                    "No plagiarism matches found in the report"
                ))
                return

            self.parsed_edges = edges
            
            # Update graph on main thread
            self.after(0, lambda: self._update_graph(cutoff))
            self.after(0, lambda: self.status_label.success(
                f"Found {len(edges)} matches (showing {len([e for e in edges if e[2] >= cutoff])} above cutoff)"
            ))

        except requests.RequestException as e:
            self.after(0, lambda: self.status_label.error(f"Failed to fetch URL: {str(e)}"))
        except Exception as e:
            self.after(0, lambda: self.status_label.error(f"Error: {str(e)}"))
        finally:
            self.after(0, lambda: self.visualize_btn.configure(state="normal", text="Visualize Graph"))

    def _parse_moss_results(self, html_content: str) -> list:
        """
        Parse MOSS results HTML to extract match pairs.
        Returns: [(name1, name2, weight_percent), ...]
        """
        edges = []
        
        # Debug: Save HTML to file for inspection
        debug_file = Path("moss_debug.html")
        debug_file.write_text(html_content)
        print(f"Saved MOSS HTML to {debug_file.absolute()}")
        
        # MOSS table format:
        # <TR><TD><A HREF="...">/path/file1.cpp (99%)</A>
        #     <TD><A HREF="...">/path/file2.cpp (99%)</A>
        # <TD ALIGN=right>598
        
        # Pattern for table row with two files and their percentages
        pattern = r'<TR><TD><A\s+HREF="[^"]*">([^<]+)\s+\((\d+)%\)</A>\s*<TD><A\s+HREF="[^"]*">([^<]+)\s+\((\d+)%\)</A>'
        
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        print(f"Found {len(matches)} matches")
        
        for match in matches:
            file1 = match[0].strip()
            percent1 = int(match[1])
            file2 = match[2].strip()
            percent2 = int(match[3])
            
            # Extract filename from path
            name1 = os.path.basename(file1).replace('.cpp', '').replace('.c', '').replace('.py', '').replace('.java', '')
            name2 = os.path.basename(file2).replace('.cpp', '').replace('.c', '').replace('.py', '').replace('.java', '')
            
            # Use average of the two percentages
            avg_percent = (percent1 + percent2) // 2
            
            edges.append((name1, name2, avg_percent))
            print(f"  {name1} ({percent1}%) <-> {name2} ({percent2}%) = {avg_percent}%")
        
        print(f"Total edges parsed: {len(edges)}")
        return edges

    def _update_graph(self, cutoff: float):
        """Update the graph visualization."""
        self.graph.set_data(self.parsed_edges, cutoff)

    def set_moss_url(self, url: str):
        """Set MOSS result URL from grading page."""
        if url:
            self.url_entry.set(url)
            # Save to file for later import
            result_file = Path("moss_result.txt")
            result_file.write_text(url)
