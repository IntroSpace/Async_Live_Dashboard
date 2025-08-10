from flask import Flask, render_template

# Создаем экземпляр Flask-приложения
app = Flask(__name__)


@app.route('/')
def index():
    """
    Эта функция отвечает за отображение главной страницы.
    `render_template` находит HTML-файл в папке `templates` и отдает его браузеру.
    """
    return render_template('index.html')
