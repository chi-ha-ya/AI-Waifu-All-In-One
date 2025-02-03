# AI-Waifu All In One！

一个脚本调用 ollama 和 gpt-sovits 进行智能对话、语音合成，极简AI角色扮演系统。
![img](/character/nanami/nanami-generated-20250202-195105-2333.jpg)
## 功能特性
- **完全离线**：无需网络连接，离线运行，确保隐私，~~可破限~~。
- **自由定制**：代码仅两百多行，配置均为明文，可自由定制性格，修改音色，扩展开发。
- **多语言**：聊天自带中日英等多语言支持（依赖底模和gpt-sovits）。
## 环境要求
- **Python**: 任意[python](https://www.python.org/downloads/)环境。
- **Ollama**：安装phi4模型并运行。默认服务端口"http://localhost:11434/api"。
- **GPT-SovitsV2**：启用音频推理服务。默认端口"http://127.0.0.1:9880/tts"。

## 安装部署

#### Python依赖
```bash
pip install requests pyaudio keyboard
```
#### Ollama安装
1. 下载安装并运行Ollama（[Ollama 官网](https://ollama.com/)），【添加系统环境变量"OLLAMA_MODELS"指定模型安装路径到其他盘(可选)】。
2. 下载安装对话模型 ([phi4](https://ollama.com/library/phi4))：
    ```bash
    ollama run phi4
    ``` 
3. 命令行进入character/nanami文件夹，运行以下命令创建对话模型nanami：
    ```bash
    ollama create nanami -f modelfile
    ``` 
4. 如果创建成功，可运行以下命令检查已安装的模型列表。其中应该包含"nanami：latest"。
    ```bash
    ollama list
    ```
#### GPT-SOVITS安装
1. 下载解压 [GPT-SoVITS-V2整合包](https://github.com/RVC-Boss/GPT-SoVITS/releases/tag/20240821v2)，任意目录均可。
2. 在它根目录下创建一个名为"go-api.bat"的批处理脚本，脚本内容如下：
    ```bash
    runtime\python.exe api_v2.py
    pause
    ```
3. 双击运行脚本，启动推理服务，跳出的命令行窗口有显示如下内容即可(请务必注意不要关闭该窗口)：
    ```bash
    INFO:     Started server process [9396]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    INFO:     Uvicorn running on http://127.0.0.1:9880 (Press CTRL+C to quit)
    ```
#### 启动项目
```bash
python main.py
```
    
## 文件结构
```
ai-waifu/
├── main.py                # 主程序
├── config.json            # 配置文件
├── README.MD              
├── requirements.txt       
└── character/
    ├── nanami/            # ナナミ角色目录
        ├── modelfile      # 模型参数，用于创建对话模型
        ├── settings.json  # 角色配置
        ├── *.wav          # 参考音频，文件名必须为语音内容
```
## 使用示例
1. **角色定制：** 自行修改`modelfile`文件中的`SYSTEM`提示词等参数(例如切换底模：将`FROM phi4` 改为 `FROM qwen2.5:7b`) ，改完记得重新创建对话模型。
2. **更换音色：** 修改角色配置"settings.json"(参考音频与json放同一目录)：
    ```
    {
        "model_name":      # 对话模型名称
        "ref_audio":       # 参考音频，文件名必须为语音内容
        "ref_audio_lang":  # 参考音频的语言类型（例如：ja）
        "speed_factor":    # 语速
    }
    ```
3. **更换角色：** 可自行创建新角色的`settings.json`文件，添加后将路径填写到"config.json"里的`character`变量中，即可更换角色。


## 注意事项
- 修改modelfile后，需要重新创建对话模型。
- 程序靠"settings.json"里的`model_name`名字找对话模型，改了记得同步。
- 参考语音是5~10s干净的人声，文件名为语音内容，当前为了开箱即用仅支持未训练推理，可自行扩展。
- 推荐底模[phi4](https://ollama.com/library/phi4)，显存不够的话[qwen2.5:7b](https://ollama.com/library/qwen2.5:7b)效果亦可，其他模型请自行测试。

## 已知bug
- 语音播放时爆音，吞字，口胡，等一个大佬o(*￣▽￣*)o。。。

## 未来展望
- GUI
- 训练音色。
- 对话纪录。
- 语音识别。
- 角色记忆，知识库。
- 多模态。
- 模型蒸馏。
- 探索虚拟人格定制的一般规律。

这仅是一个实验性项目，意在搭建最小系统，跑通基本流程，方便大家学习交流，希望能抛砖引玉，吸引更多的人参与进来 ( •̀ ω •́ )✧。
