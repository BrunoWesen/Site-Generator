from flask import Flask, request, url_for, render_template, redirect, jsonify, session
from flask_cors import CORS, cross_origin

app = Flask(__name__, static_folder='templates/assets', )
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['JSON_AS_ASCII'] = False
app.secret_key = "RJ283928DJ2D89"


@app.template_filter(name='linebreaksbr')
def linebreaksbr_filter(text):
    return text.replace('\n', '<br>')


class Page:
    def __init__(self):
        self.theme: str = 'Avocado'


class ThemePage:
    def __init__(self, theme):
        if theme == 'Avocado':
            self.bgcolor: str = 'green-100'
            self.fontcolor: str = 'gray-800'
        elif theme == 'Light':
            self.bgcolor: str = 'white'
            self.fontcolor: str = 'black'
        else:
            self.bgcolor: str = "slate-950"
            self.fontcolor: str = 'gray-200'


# Interface Builder
class PageBuilder:
    def __init__(self):
        self.page = Page()

    def add_title(self, title):
        self.page.title = title

    def add_content(self, content):
        self.page.content = content

    def build_page(self):
        return self.page


# Adapter
class RendererHTML:
    def __init__(self, page):
        self.page = page

    def render(self):
        themePage = ThemePage(self.page.theme)
        return render_template('generatedPage.html', **self.page.__dict__, **themePage.__dict__)


# Decorator 1
class AddRodape:
    def __init__(self, page):
        self.page = page

    def add_rodape(self, rodape):
        self.page.footer = rodape


# Decorator 2
class AddTheme:
    def __init__(self, page):
        self.page = page

    def add_theme(self, theme):
        self.page.theme = theme


@app.route("/", methods=['GET'])
@cross_origin()
def home_page():
    return render_template('pageGenerator.html')


@app.route("/decorator/<title>", methods=['GET'])
@cross_origin()
def decorator(title):
    try:
        data = session[title]
    except KeyError:
        return "not found", 404

    return render_template('decoratorPage.html', form_action_url=url_for('handle_decorator_data', title=title))


@app.route("/decorator/<title>", methods=['POST'])
@cross_origin()
def handle_decorator_data(title):
    form_data = request.form.to_dict()
    session[title + "-decorator"] = form_data

    return redirect(url_for('generated_page', title=title))


@app.route("/<title>", methods=['GET'])
@cross_origin()
def generated_page(title):
    try:
        data = session[title]
    except KeyError:
        return "not found", 404

    builder = PageBuilder()
    builder.add_title(title)
    data['texts'] = int(list(data.keys())[-2].split("-")[-1])
    builder.add_content(data)
    page = builder.build_page()

    # Calling Decorators
    try:
        data = session[title + "-decorator"]

        theme_page = AddTheme(page)
        theme_page.add_theme(data['theme'])

        footer_page = AddRodape(page)
        footer_page.add_rodape(data['footer'])
    except KeyError:
        pass

    renderizador = RendererHTML(page)
    html = renderizador.render()

    return html


@app.route("/", methods=['POST'])
@cross_origin()
def handle_data():
    form_data = request.form.to_dict()

    session[form_data['title']] = form_data

    return redirect(url_for('generated_page', title=form_data['title']))


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
