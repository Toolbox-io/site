import mimetypes
import os

from flask import Flask, send_from_directory, redirect, request, render_template

app = Flask(__name__, template_folder='src/templates')

# Путь к папке с контентом
CONTENT_PATH = 'src'


# Функция для поиска файла с учетом разных расширений
def find_file(path: str) -> tuple[str | None, str | None]:
    # Полный путь относительно CONTENT_PATH
    full_path = os.path.join(CONTENT_PATH, path)

    # Если это директория и в ней есть index.html
    if os.path.isdir(full_path):
        index_file = os.path.join(full_path, 'index.html')
        if os.path.isfile(index_file):
            if not path.endswith("/"): return index_file, f"{path}/"
            else: return index_file, None
        # Если index.html нет, ищем <dir>.html в родительской папке
        dir_html = os.path.join(os.path.dirname(full_path), os.path.basename(path) + '.html')
        if os.path.isfile(dir_html):
            return dir_html, None
        return None, None

    # Если это файл без расширения
    if os.path.isfile(full_path):
        return full_path, None

    # Если есть файл с расширением .html
    html_path = os.path.join(CONTENT_PATH, path + '.html')
    if os.path.isfile(html_path):
        return html_path, None

    # Проверяем все подкаталоги
    for dirpath, dirnames, filenames in os.walk(CONTENT_PATH):
        for filename in filenames:
            if filename.startswith(path):
                return os.path.join(dirpath, filename), None

    return None, None


# Обработчик всех запросов
@app.route('/<path:path>')
def serve_files(path):
    file = find_file(path)
    file_path = file[0]
    # If it's a directory and URL doesn't end with '/', redirect
    if file[1]:
        # Preserve query parameters
        query_params = request.query_string.decode()
        redirect_url = file[1]
        if query_params:
            if '?' in redirect_url:
                redirect_url += f"&{query_params}"
            else:
                redirect_url += f"?{query_params}"
        return redirect(redirect_url)
    
    if file_path:
        # Определяем тип контента по расширению
        mime_type = mimetypes.guess_type(file_path)[0]
        return send_from_directory(
            os.path.dirname(file_path),
            os.path.basename(file_path),
            mimetype=mime_type
        )

    return "404 Not Found", 404


# Обработчик для корневой директории
@app.route('/')
def index():
    return send_from_directory(CONTENT_PATH, 'index.html')


@app.route('/guides/<path:subpath>')
def guides_handler(subpath: str):
    # Use find_file to check for file existence
    print(f"subpath: {subpath}")
    print(f"full path: guides/{subpath}")
    file_path, redirect_path = find_file(f"guides/{subpath}")
    print(f"file path of guides/{subpath}: {file_path}")
    print(f"redirect of guides/{subpath}: {redirect_path}")
    print("---")

    # 1. If the request explicitly ends with .md and the file exists, serve it as a static file
    if file_path and ((subpath.lower().endswith('.md') and file_path.endswith('.md')) or "." in subpath):
        mime_type = mimetypes.guess_type(file_path)[0]
        return send_from_directory(
            os.path.dirname(file_path),
            os.path.basename(file_path),
            mimetype=mime_type
        )

    # 2. If the request does not end with .md, but find_file resolved to an .md file, process as a guide
    if not subpath.lower().endswith('.md') and file_path and file_path.endswith('.md'):
        guide_name = os.path.splitext(subpath)[0]
        # Custom guide processing logic (example: render HTML page)
        html = f"""
        <html>
        <head><title>Guide: {guide_name}</title></head>
        <body>
            <h1>Processed Guide: {guide_name}</h1>
            <p>This is a processed guide for: <b>{guide_name}</b></p>
        </body>
        </html>
        """
        return html

    # Handle /raw
    if subpath.lower().endswith('/raw'):
        return render_template("raw_guide.html", guide=f"{os.path.dirname(f"/guides/{subpath}").upper()}.md")

    # If not found, redirect as specified
    guide_name = os.path.splitext(subpath)[0].upper() + '.md'
    return redirect(f"/guides?guide={guide_name}")

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        directory=CONTENT_PATH,
        path="res/favicon.svg",
        mimetype=mimetypes.guess_type(os.path.join(CONTENT_PATH, "res/favicon.svg"))[0]
    )

if __name__ == '__main__':
    app.run(debug=True)
