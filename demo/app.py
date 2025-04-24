
import gradio as gr
from gradio_dialogue import Dialogue


with gr.Blocks() as demo:
    with gr.Tabs():
        with gr.Tab("Dialogue Demo"):
            Dialogue(interactive=True, emotions=["laugh", "sigh"], speakers=["Speaker 1", "Speaker 2"])
        with gr.Tab("Component  Functions"):
            gr.Markdown("## Component Functions")
            dialogue = Dialogue(emotions=["laugh", "sigh"], speakers=["S1", "S2"])
            textbox = gr.Textbox(label="Textbox")
            with gr.Row():
                with gr.Column():
                    process = gr.Button("Process")
                    process.click(lambda x: x, dialogue, textbox)
                    dialogue.submit(lambda x: x, dialogue, textbox)
                with gr.Column():
                    process = gr.Button("Update")
                    process.click(lambda: [{"speaker": "S1", "text": "Updated!"}], None, dialogue)

if __name__ == "__main__":
    demo.launch()
