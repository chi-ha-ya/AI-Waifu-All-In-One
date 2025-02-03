import requests
import pyaudio
import re
import multiprocessing
import threading
import time
import sys
import keyboard
import json
import os

# Ollama 和 GPT-Sovits TTS 的 api
ollama_base_url = "http://localhost:11434/api"
gpt_sovits_tts_url = "http://127.0.0.1:9880/tts"

# True:仅将“”内台词生成语音，False:全部生成，（有bug =.=
extract_dialogue_for_tts = False


def generate_completion(prompt, model, stream=True):
    url = f"{ollama_base_url}/generate"
    data = {
        "model": model,
        "prompt": prompt,
        "stream": stream
    }
    global ollama_headers
    ollama_headers = {"Content-Type": "application/json"}
    response = requests.post(
        url, headers=ollama_headers, json=data, stream=stream)
    return response


def get_audio_from_api(text, character,  audio_queue):
    params = {
        "text": text,
        "text_lang": "auto",
        "ref_audio_path": character["ref_audio_path"],
        "prompt_lang": character["prompt_lang"],
        "prompt_text": character["prompt_text"],
        "speed_factor": character["speed_factor"],
        "text_split_method": "cut5",
        "media_type": "wav",
        "parallel_infer": True,
        "streaming_mode": False
    }

    try:
        response = requests.get(
            gpt_sovits_tts_url, params=params, stream=False)
        if response.status_code == 200:
            audio_queue.put(response)
        else:
            audio_queue.put(None)
    except requests.exceptions.RequestException as e:
        print(f"生成音频失败，TTS 引擎未启动？错误信息: {e}")


def extract_dialogue(text):
    pattern = r'''(?:“[^”]*”|‘[^’]*’|"[^"]*"|'[^']*'|「[^」]*」|『[^』]*』|［[^］]*］|\([^)]*\)|（[^）]*）)'''
    matches = re.findall(pattern, text)
    dialogues = [match[1:-1] if match else match for match in matches]
    return dialogues


def stream_audio(response, stop_event):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1,
                    rate=32000, output=True)
    try:
        for chunk in response.iter_content(chunk_size=1024):
            if stop_event.is_set():
                break
            if chunk:  # Check if chunk is not empty
                stream.write(chunk)
    except Exception as e:  # Catch potential exceptions during streaming
        print(f"Error during audio streaming: {e}", file=sys.stderr)
    finally:
        if stream:
            stream.stop_stream()
            stream.close()
        p.terminate()


def play_audio_process(audio_queue, stop_event):
    while True:
        if not audio_queue.empty():
            response = audio_queue.get()
            if response:
                stream_audio(response, stop_event)
            elif response is None:  # Check for None explicitly
                break  # 处理出错的情况
        if stop_event.is_set():
            break
        time.sleep(0.1)  # Reduce sleep time for responsiveness


def tts_process(character, tts_queue, audio_queue, stop_event):
    while True:
        if not tts_queue.empty():
            text = tts_queue.get()
            if text:
                get_audio_from_api(text, character, audio_queue)
            elif text is None:  # Check for None explicitly
                break
        if stop_event.is_set():
            break
        time.sleep(0.1)  # Reduce sleep time for responsiveness


def get_absolute_path(base_dir: str, path: str):
    if not os.path.isabs(path):
        path = os.path.join(base_dir, path)
    return path


def load_character_settings():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        config = json.load(
            open(os.path.join(current_dir, "config.json"), 'r', encoding='utf-8'))
        character_settings_path = get_absolute_path(
            current_dir, config["character"])
        character_settings = json.load(
            open(character_settings_path, 'r', encoding='utf-8'))
    except Exception as e:
        print(f"Error loading character settings: {e}")
        sys.exit(1)

    character = {
        "model_name": character_settings["model_name"],
        "ref_audio_path": get_absolute_path(os.path.dirname(character_settings_path), character_settings["ref_audio"]),
        "prompt_text": os.path.basename(character_settings["ref_audio"]).split('.')[0],
        "prompt_lang": character_settings["ref_audio_lang"],
        "speed_factor": character_settings["speed_factor"],
    }
    return character


def main():
    character = load_character_settings()
    audio_queue = multiprocessing.Queue()
    tts_queue = multiprocessing.Queue()
    stop_event = multiprocessing.Event()
    audio_thread = threading.Thread(
        target=play_audio_process, args=(audio_queue, stop_event), daemon=True)
    audio_thread.start()

    tts_process_ = multiprocessing.Process(
        target=tts_process, args=(character, tts_queue, audio_queue, stop_event), daemon=True)
    tts_process_.start()

    def stop_audio():
        stop_event.set()
        print("音频播放已停止。")

    keyboard.add_hotkey('ctrl+p', stop_audio)
    print(f"connecting to {character['model_name']}...")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            print("プログラムを終了します。")
            stop_event.set()
            tts_queue.put(None)
            break
        response = generate_completion(user_input, character['model_name'])

        if response.status_code == 200:
            print(character["model_name"] + ":  \n")
            sentence_buffer = ""
            for chunk in response.iter_lines():
                if chunk:
                    try:
                        json_data = json.loads(chunk.decode('utf-8'))
                        if "response" in json_data:
                            text_part = json_data["response"]
                            print(text_part, end="", flush=True)
                            sentence_buffer += text_part

                            if re.search(r"[”）)。？！」.~]$", sentence_buffer):  # 修正点: 仅播放引号内的台词
                                if (extract_dialogue_for_tts):
                                    dialogues = extract_dialogue(
                                        sentence_buffer)
                                    if len(dialogues) > 0:
                                        for dialogue in dialogues:
                                            tts_queue.put(dialogue)
                                        sentence_buffer = ""
                                else:
                                    tts_queue.put(sentence_buffer)
                                    sentence_buffer = ""
                        elif json_data.get("done", False):
                            dialogues = extract_dialogue(sentence_buffer)
                            for dialogue in dialogues:
                                tts_queue.put(dialogue)
                            sentence_buffer = ""
                            break

                    except json.JSONDecodeError:
                        print(f"JSON 解码错误：{chunk}", file=sys.stderr)
                        continue

        else:
            print(response.json())

    keyboard.unhook_all_hotkeys()
    tts_process_.join()
    audio_thread.join()


if __name__ == "__main__":
    main()
