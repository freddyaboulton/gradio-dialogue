
import gradio as gr
from gradio_dialogue import Dialogue


with gr.Blocks() as demo:
    gr.Markdown("# Change the value (keep it JSON) and the front-end will update automatically.")
    Dialogue(interactive=True, emotions=["laugh", "sigh"], speakers=["Speaker 1", "Speaker 2"])


if __name__ == "__main__":
    demo.launch()
