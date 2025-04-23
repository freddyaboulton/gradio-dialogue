from gradio import Textbox
from typing import Literal

class Dialogue(Textbox):
    def __init__(self, speakers, emotions,         
        value: str | None = None,
        *,
        label: str | None = None,
        info: str | None = None,
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
        text_align: Literal["left", "right"] | None = None,
        rtl: bool = False,
        show_copy_button: bool = False,
        max_length: int | None = None,
        ):
        super().__init__(value=value, label=label, info=info, show_label=show_label, container=container, scale=scale, min_width=min_width, interactive=interactive, visible=visible, elem_id=elem_id, autofocus=autofocus, autoscroll=autoscroll, elem_classes=elem_classes, render=render, key=key, text_align=text_align, rtl=rtl, show_copy_button=show_copy_button, max_length=max_length)
        self.speakers = speakers
        self.emotions = emotions

    def preprocess(self, payload):
        """
        This docstring is used to generate the docs for this custom component.
        Parameters:
            payload: the data to be preprocessed, sent from the frontend
        Returns:
            the data after preprocessing, sent to the user's function in the backend
        """
        return payload

    def postprocess(self, value):
        """
        This docstring is used to generate the docs for this custom component.
        Parameters:
            payload: the data to be postprocessed, sent from the user's function in the backend
        Returns:
            the data after postprocessing, sent to the frontend
        """
        return value

    def example_payload(self):
        return {"foo": "bar"}

    def example_value(self):
        return {"foo": "bar"}

    def api_info(self):
        return {"type": {}, "description": "any valid json"}
