from gradio import Textbox
from gradio.components.base import server
from gradio.data_classes import GradioModel, GradioRootModel
from typing import Callable, List

class DialogueLine(GradioModel):
    speaker: str
    text: str

class DialogueModel(GradioRootModel):
    root: List[DialogueLine]

class Dialogue(Textbox):

    data_model = DialogueModel
    def __init__(self, 
        speakers: list[str],
        formatter: Callable | None = None,
        emotions: list[str] | None = None,         
        value: str | None = None,
        separator: str = " ",
        *,
        label: str | None = "Dialogue",
        info: str | None = "Type colon (:) in the dialogue line to see the available emotion and intonation tags",
        placeholder: str | None = "Enter dialogue here...",
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        autofocus: bool = False,
        autoscroll: bool = True,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | None = None,
        max_lines: int | None = None,
        show_submit_button: bool = True,
        show_copy_button: bool = True,
        ):
        super().__init__(value=value, label=label, info=info, placeholder=placeholder, show_label=show_label, container=container, scale=scale, min_width=min_width, interactive=interactive, visible=visible, elem_id=elem_id, autofocus=autofocus, autoscroll=autoscroll, elem_classes=elem_classes, render=render, key=key, max_lines=max_lines)
        self.speakers = speakers
        self.emotions = emotions or []
        self.formatter = formatter
        self.separator = separator
        self.show_submit_button = show_submit_button
        self.show_copy_button = show_copy_button
    
    def preprocess(self, payload: DialogueModel):
        """
        This docstring is used to generate the docs for this custom component.
        Parameters:
            payload: the data to be preprocessed, sent from the frontend
        Returns:
            the data after preprocessing, sent to the user's function in the backend
        """
        formatter = self.formatter
        if not formatter:
            formatter = lambda speaker, text: f"[{speaker}] {text}"
        return self.separator.join([formatter(line.speaker, line.text) for line in payload.root])

    @server
    async def format(self, value: list[dict]):
        data = DialogueModel(root=value) # type: ignore
        return self.preprocess(data)

    def postprocess(self, value):
        """
        This docstring is used to generate the docs for this custom component.
        Parameters:
            payload: the data to be postprocessed, sent from the user's function in the backend
        Returns:
            the data after postprocessing, sent to the frontend
        """
        return value

    def as_example(self, value):
        return self.preprocess(DialogueModel(root=value))

    def example_payload(self):
        return {"foo": "bar"}

    def example_value(self):
        return {"foo": "bar"}

    def api_info(self):
        return {"type": {}, "description": "any valid json"}
