from io import StringIO
from rich.console import Console
from rich.table import Table
import imgkit

# Step 1: Render Rich Table and Save as HTML
console = Console(record=True)
table = Table(title="Example Table")

# Add some columns and rows
table.add_column("Name", justify="right", style="cyan", no_wrap=True)
table.add_column("Age", style="magenta")
table.add_column("Country", style="green")
table.add_row("Alice", "24", "Wonderland")
table.add_row("Bob", "30", "Builderland")
table.add_row("Charlie", "29", "Chocolate Factory")

console.print(table)

# Export to HTML
html_output = console.export_html()
html_file_path = "test.html"
with open(html_file_path, "w") as f:
    f.write(html_output)

# Step 2: Convert HTML to PNG
png_file_path = "test.png"
options = {
    "format": "png",
    "width": 800,
    "disable-smart-width": "",
    "encoding": "UTF-8",
}
imgkit.from_file(html_file_path, png_file_path, options=options)

# Step 3: Check the size
import os
file_size = os.path.getsize(png_file_path)
if file_size <= 500 * 1024:
    print(f"Image saved successfully as '{png_file_path}' with size {file_size / 1024:.2f} KB.")
else:
    print(f"Image size is too large ({file_size / 1024:.2f} KB). Try adjusting the options.")
