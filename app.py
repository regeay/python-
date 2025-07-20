import gradio as gr
import os
from search import search  # 导入搜索模块
from chat import  chat # 导入流式聊天
from fetch import fetch # 导入网页总结
from pdf import * # 导入文件聊天

messages = []
history = []
current_file_text = "" # 存储当前上传的文件内容
file_processed = False # 记录当前文件是否需要处理

def add_text(history, text):
    # 用户输入 -> history
    history = history + [(text, None)]
    # 模型消息记录 -> messages
    messages.append({"role": "user", "content": text})
    return history, gr.update(value="", interactive=False)

def add_file(history, file):
    global current_file_text, file_processed
    if file.name.lower().endswith('.txt'):
        try:
            # 读取文件内容
            with open(file, 'r', encoding='utf-8') as f:
                current_file_text = f.read().strip()
            messages.append({"role": "user", "content": (file.name,)})
            
            # 表明当前文件需要处理并返回
            file_processed = True
            history = history + [((file.name,), None)]
            return history
    
        except Exception as e:
            return history + [((file.name,), f"Error: {str(e)}")]
    else:
        return history + [((file.name,), "Only .txt files supported")]

   

def bot(history):
    global current_file_text, file_processed
    user_input = messages[-1]["content"]

    # 如果是第一次处理上传的文件，生成总结
    if file_processed:
        file_processed = False
        summary_prompt = generate_summary(current_file_text)
        messages[-1]["content"] = summary_prompt
        assistant_generator = generate_text(summary_prompt)
    # 处理基于文件内容的提问
    elif user_input.strip().lower().startswith("/file "):
        if not current_file_text:
            assistant_generator = iter(["请先上传文件"])
        else:
            content = user_input.strip()[6:]
            question = generate_question(current_file_text, content)
            assistant_generator = generate_text(question)
    # 判断是否是搜索指令
    elif user_input.strip().lower().startswith("/search "):
        content = user_input.strip()[8:]
        try:
            enriched_query = search(content)
        except Exception as e:
            assistant_generator = iter([f"Search failed: {e}"])
        else:
            messages[-1]["content"] = enriched_query
            assistant_generator = chat(messages)  # 流式生成
    # 判断是否是网页总结
    elif user_input.strip().lower().startswith("/fetch "):
        url = user_input.strip()[7:]
        try:
            question = fetch(url)
        except Exception as e:
            assistant_generator = iter([f"Fetch failed: {e}"])
        else:
            messages[-1]["content"] = question
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
        global current_file_name, current_file_text
        current_file_text = ""
        current_file_name = ""
        return []  # chatbot expects a list of tuples like [(user, assistant), ...]

    clear_btn.click(clear_all, inputs=None, outputs=chatbot, queue=False)

demo.queue()
demo.launch()