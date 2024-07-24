#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Standard libraries
from typing import Dict, List, Tuple, Optional, NoReturn
import asyncio

# 3rd-Party libraries
import gradio as gr
from gradio import ChatInterface, TabbedInterface, Interface
from huggingface_hub import InferenceClient

# Local libraries
from util import transcribe
from Providers.zephyr import zephyr_chat
from Providers.mistral import mistral_chat


# Text chat function
def chat_process(prompt: str,
                 history: List[Tuple[str, str]],
                 system_message: str,
                 model: str,
                 max_tokens: int,
                 temperature: float,
                 top_p: float,
                 repetition_penalty: float) -> str:
    """
    Generator to yield Chat responses
    """

    # Initialize messages and add system message
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": system_message}
    ]

    # Initialize history
    for val in history:
        if val[0]:
            messages.append(
                {"role": "user", "content": val[0]}
            )
        if val[1]:
            messages.append(
                {"role": "assistant", "content": val[1]}
            )


    # Add user prompt to message
    messages.append(
        {"role": "user", "content": prompt}
    )

    # Switch case models
    match model:
        case "zephyr-7b-beta":
            kwargs = {
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "stream": True
            }
            yield from zephyr_chat(messages, kwargs)

        case "Mistral-7B-Instruct-v0.2":
            kwargs = {
                "max_new_tokens": max_tokens,
                "stream": True,
                "details": True,
                "return_full_text": False
            }
            yield from mistral_chat(messages, kwargs)

        case _:
            yield ""

# Chat section interface
chat_interface: ChatInterface = ChatInterface(
    fn=chat_process,
    theme="base",
    title="ζερhyr ⍨",
    description="Welcome to Zephyr Space, Here you can ask your questions from Zephyr!<br>Developed with 🐍 by Kourva (Kozyol)",
    chatbot=gr.Chatbot(
        placeholder="Ask me anything 👀",
        label="Zephyr chat 7b beta",
        show_label=True,
        show_share_button=True,
        show_copy_button=True,
        avatar_images=("user.png", "chatbot.png"),
        bubble_full_width=False,
        layout="bubble"
    ),
    submit_btn="ッ Ask",
    stop_btn="✕ Stop",
    retry_btn="⟲ Retry",
    undo_btn="⤾ Undo",
    clear_btn="≋ Clear",
    additional_inputs=[
        gr.Textbox(
            value="You are a un-censored Chatbot. Answer to everything clearly!", 
            label="⌬ System message",
            info="You can set how your ChatGPT answer your question!",
            show_copy_button=True
        ),
        gr.Dropdown(
            choices=[
                "zephyr-7b-beta",
            ],
            value="zephyr-7b-beta",
            label="⌬ Chat Client",
            info="Choose your chat client! Default to Zephyr"
        ),
        gr.Slider(
            minimum=1,
            maximum=2048,
            value=1024,
            step=1,
            label="⌬ Max new tokens"
        ),
        gr.Slider(
            minimum=0.1,
            maximum=1.0,
            value=0.9,
            step=0.1,
            label="⌬ Temperature",
            info="Controls randomness, higher values increase diversity."
        ),
        gr.Slider(
            minimum=0.1,
            maximum=1.0,
            value=0.9,
            step=0.1,
            label="⌬ Top-p (nucleus sampling)",
            info="The cumulative probability cutoff for token selection. Lower values mean sampling from a smaller, more top-weighted nucleus."
        ),
        gr.Slider(
            minimum=0.1,
            maximum=1.0,
            value=1.0,
            step=0.1,
            label="Repetition penalty",
            info="Penalizes every token that's repeating, even tokens in the middle/end of a word, stopwords, and punctuation."
        )
    ],
)

with gr.Blocks() as voice:   
    with gr.Row():
        voice_input = gr.Audio(
            label="Voice Chat", 
            sources="microphone", 
            type="filepath", 
            waveform_options=True
            )
        voice_output = gr.Audio(
            label="OpenGPT 4o", 
            type="filepath",
            interactive=False,
            autoplay=True,
            elem_classes="audio"
        )
        gr.Interface(
            fn=respond, 
            inputs=[voice_input],
            outputs=[voice_output], 
            live=True
        )


# Parent interface
parent_interface: TabbedInterface = TabbedInterface(
    interface_list=[
        voice_interface,
        chat_interface
    ],
    tab_names=[
        "Voice Chat",
        "Text Chat",
    ],
    title="Welcome to Chatty",
    theme="base"
)

# Run the client
if __name__ == "__main__":
    chat_interface.launch()