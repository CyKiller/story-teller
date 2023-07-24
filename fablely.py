import os
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from write_novel_vector import write_novel_milvus

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    children=[
        dcc.Input(id="input-prompt", type="text",
                  placeholder="Enter a prompt for the initial plot"),
        dcc.Input(id="input-chapters", type="number",
                  placeholder="Enter the number of chapters"),
        dcc.Input(id="input-style", type="text",
                  placeholder="Enter the writing style"),
        dcc.Input(id="input-genre", type="text",
                  placeholder="Enter the genre"),
        dcc.Input(id="input-collection", type="text",
                  placeholder="Enter the collection name"),
        dcc.Input(id="input-length", type="number",
                  placeholder="Enter the length of the generated content"),
        html.Button('Start Writing', id='start-writing'),
        html.Div(id='novel-display')
    ]
)


@app.callback(
    Output('novel-display', 'children'),
    Input('start-writing', 'n_clicks'),
    State('input-prompt', 'value'),
    State('input-chapters', 'value'),
    State('input-style', 'value'),
    State('input-genre', 'value'),
    State('input-collection', 'value'),
    State('input-length', 'value')
)
def start_writing(n_clicks, prompt, chapters, style, genre, collection, length):
    if n_clicks is None:
        raise PreventUpdate
    if not all(isinstance(x, str) for x in [prompt, style, genre, collection]) or not isinstance(chapters, int) or not isinstance(length, int):
        return "Invalid input. Please make sure all fields are filled correctly."
    novel, title, chapters, chapter_titles = write_novel_milvus(
        prompt,
        chapters,
        collection,
        style,
        genre,
        length
    )
    if novel is None:
        return "Failed to generate novel."
    return novel


if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0')
