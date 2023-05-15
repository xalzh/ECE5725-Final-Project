from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

# Path to the Python file you want to convert to HTML.
python_file_path = 'main.py'

# Create a formatter with line numbers.
formatter = HtmlFormatter(linenos=True)

# Read the Python code from the file.
with open(python_file_path, 'r') as f:
    code = f.read()

# Highlight the code and convert it to HTML.
html_code = highlight(code, PythonLexer(), formatter)

# Write the HTML code to a file.
with open('main.html', 'w') as f:
    # HtmlFormatter().get_style_defs('.highlight') is used to include the necessary CSS definitions
    f.write('<html><body><style type="text/css">' + formatter.get_style_defs('.highlight') + '</style>\n')
    f.write(html_code)
    f.write('</body></html>')
