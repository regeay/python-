import gradio as gr
import os
from search import search  # 导入搜索模块
from chat import  chat # 导入流式聊天

messages = []
history = []

def add_text(history, text):
    # 用户输入 -> history
    history = history + [(text, None)]
    # 模型消息记录 -> messages
    messages.append({"role": "user", "content": text})
    return history, gr.update(value="", interactive=False)


def add_file(history, file):
    """
    TODO
    """
    history = history + [((file.name,), None)]
    return history

def bot(history):

    user_input = messages[-1]["content"]

    # 判断是否是搜索指令
    if user_input.strip().lower().startswith("/search "):
        content = user_input.strip()[8:]
        try:
            enriched_query = search(content)
        except Exception as e:
            assistant_generator = iter([f"Search failed: {e}"])
        else:
            messages[-1]["content"] = enriched_query
            assistant_generator = chat(messages)  # 流式生成
    else:
        assistant_generator = chat(messages)      # 流式生成

    partial_reply = "" # 累积的回复
    for chunk in assistant_generator:
        partial_reply += chunk
        history[-1] = (user_input, partial_reply)  # 替换最后一个元组
        yield history                             # 每得到新内容就推送

    #  messages 最终同步 
    messages.append({"role": "assistant", "content": partial_reply})


with gr.Blocks() as demo:
    chatbot = gr.Chatbot(
        [],
        elem_id="chatbot",
        avatar_images=(None, (os.path.join(os.path.dirname(__file__), "avatar.png"))),
    )

    with gr.Row():
        txt = gr.Textbox(
            scale=4,
            show_label=False,
            placeholder="Enter text and press enter, or upload an image",
            container=False,
        )
        clear_btn = gr.Button('Clear')
        btn = gr.UploadButton("📁", file_types=["image", "video", "audio", "text"])

    # 文本输入后，先调用 add_text 更新消息，再调用 bot 生成回复，最后恢复输入框交互状态
    txt_msg = txt.submit(add_text, [chatbot, txt], [chatbot, txt], queue=False).then(
        bot, chatbot, chatbot
    )
    txt_msg.then(lambda: gr.update(interactive=True), None, [txt], queue=False)

    file_msg = btn.upload(add_file, [chatbot, btn], [chatbot], queue=False).then(
        bot, chatbot, chatbot
    )

    # 清除消息
    def clear_all():
        messages.clear()
        history.clear()
        return []  # chatbot expects a list of tuples like [(user, assistant), ...]

    clear_btn.click(clear_all, inputs=None, outputs=chatbot, queue=False)

demo.queue()
demo.launch()