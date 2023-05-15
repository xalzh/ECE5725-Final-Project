from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

# Path to the Python file you want to convert to HTML.
files = ['camera.py', 'IMU.py', 'main.py', 'object_tracking.py', 'PID.py', 'reset.py', 'rolling_control.py', 'UI.py',
         'Update_Screen.py', 'web.py']

for file in files:
    python_file_path = file

    # Create a formatter with line numbers.
    formatter = HtmlFormatter(linenos=True)

    # Read the Python code from the file.
    with open(python_file_path, 'r') as f:
        code = f.read()

    # Highlight the code and convert it to HTML.
    html_code = highlight(code, PythonLexer(), formatter)

    # Write the HTML code to a file.
    with open('python_html/'+python_file_path[:-3]+".html", 'w') as f:
        # HtmlFormatter().get_style_defs('.highlight') is used to include the necessary CSS definitions
        f.write('<html><body><style type="text/css">' + formatter.get_style_defs('.highlight') + '</style>\n')
        f.write(html_code)
        f.write('</body></html>')
