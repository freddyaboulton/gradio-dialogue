---
tags: [gradio-custom-component, ]
title: gradio_dialogue
short_description: A gradio custom component
colorFrom: blue
colorTo: yellow
sdk: gradio
pinned: false
app_file: space.py
---

# `gradio_dialogue`
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.1%20-%20orange">  

Python library for easily interacting with trained machine learning models

## Installation

```bash
pip install gradio_dialogue
```

## Usage

```python
import gradio as gr
import httpx
from gradio_dialogue import Dialogue

emotions = [
    "(laughs)",
    "(clears throat)",
    "(sighs)",
    "(gasps)",
    "(coughs)",
    "(singing)",
    "(sings)",
    "(mumbles)",
    "(beep)",
    "(groans)",
    "(sniffs)",
    "(claps)",
    "(screams)",
    "(inhales)",
    "(exhales)",
    "(applause)",
    "(burps)",
    "(humming)",
    "(sneezes)",
    "(chuckle)",
    "(whistles)",
]
speakers = ["Speaker 1", "Speaker 2"]

client = httpx.AsyncClient(timeout=180)


async def query(dialogue: str, token: gr.OAuthToken | None):
    if token is None:
        raise gr.Error(
            "No token provided. Use Sign in with Hugging Face to get a token."
        )
    API_URL = "https://router.huggingface.co/fal-ai/fal-ai/dia-tts"
    headers = {
        "Authorization": f"Bearer {token.token}",
    }
    response = await client.post(API_URL, headers=headers, json={"text": dialogue})
    url = response.json()["audio"]["url"]
    return url


def formatter(speaker, text):
    speaker = speaker.split(" ")[1]
    return f"[S{speaker}]: {text}"


with gr.Blocks() as demo:
    with gr.Sidebar():
        login_button = gr.LoginButton()
    gr.HTML(
        """
        <h2 style='text-align: center; display: flex; align-items: center; justify-content: center;'>Model by <a href="https://huggingface.co/nari-labs/Dia-1.6B"> Nari Labs</a>. Powered by HF and <a href="https://fal.ai/">Fal AI</a>  API.</h2>
        <h3>Dia is a dialogue generation model that can generate realistic dialogue between two speakers. Use the dialogue component to create a conversation and then hit the submit button in the bottom right corner to see it come to life .</h3>
        """
    )
    with gr.Row():
        with gr.Column():
            dialogue = Dialogue(
                speakers=speakers, emotions=emotions, formatter=formatter
            )
        with gr.Column():
            with gr.Row():
                audio = gr.Audio(label="Audio")
            with gr.Row():
                gr.DeepLinkButton(value="Share Audio via Link")
    with gr.Row():
        gr.Examples(
            examples=[
                [
                    [
                        {
                            "speaker": "Speaker 1",
                            "text": "I am a little tired today (sighs).",
                        },
                        {"speaker": "Speaker 2", "text": "Hang in there!"},
                    ]
                ],
            ],
            inputs=[dialogue],
            cache_examples=False,
        )

    dialogue.submit(query, [dialogue], audio)

demo.launch(ssr_mode=False)


```

## `Dialogue`

### Initialization

<table>
<thead>
<tr>
<th align="left">name</th>
<th align="left" style="width: 25%;">type</th>
<th align="left">default</th>
<th align="left">description</th>
</tr>
</thead>
<tbody>
<tr>
<td align="left"><code>value</code></td>
<td align="left" style="width: 25%;">

```python
Any
```

</td>
<td align="left"><code>None</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>label</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>info</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>show_label</code></td>
<td align="left" style="width: 25%;">

```python
bool | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>container</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>scale</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>min_width</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>interactive</code></td>
<td align="left" style="width: 25%;">

```python
bool | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>visible</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>elem_id</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>elem_classes</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>render</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>key</code></td>
<td align="left" style="width: 25%;">

```python
int | str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>load_fn</code></td>
<td align="left" style="width: 25%;">

```python
Callable | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>every</code></td>
<td align="left" style="width: 25%;">

```python
Timer | float | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>inputs</code></td>
<td align="left" style="width: 25%;">

```python
Component | Sequence[Component] | set[Component] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">None</td>
</tr>
</tbody></table>




