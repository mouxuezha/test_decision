# 方案生成部分 by XXH

## 概述
    基于劳动竞赛公开场景，研究方案生成的工程，完成从自然语言提示词到子任务序列的过程。这个生成的方案以.pkl文件的形式储存，在text_JSQL工程中加载pkl文件和本工程中定义的数据类型，最终驱动推演。本工程可单独运行，不依赖决胜千里推演平台本身。远程git@github.com:mouxuezha/test_decision.git。以下各文件夹的用处。
    - auto_run.py: 主程序入口，服务于跟我们显示等其他模块交互，非核心功能
    - text_transfer: 文本处理工具
    - templates：预定于数据结构和模板
    - support: 辅助工具
    - plan_evaluate: 方案评估(没写完)
    - output_tools: 报表输出工具
    - model_communication: 大模型接口
    - mission_arrange: 核心业务，生成子任务序列
    - DeLLMa、key_state: 两个我们这边正在写论文的决策方式
    - config：配置文件
    - auto_test: 存结果的，不加版本管理，建议各种输出统一放里面。
    - .env: 本工程所用环境变量，主要是大模型的API_key 

## 运行环境
    合理使用AI，不熟悉的操作、忘记了的命令，均可问豆包、Deepseek等。
    - 需要python，可用VScode+Anaconda，上网搜索后下载安装。VSCode需安装python插件。
    - 打开Anaconda prompt，创建虚拟环境。
    - 安装requirements.txt里面的包。
    - (或者直接把我这里的python虚拟环境解压到...\anaconda3\envs目录下)
    - 配置VScode，使其识别到python虚拟环境。
    

## 运行配置
    - 配置大模型调用方式
      - model_communication\model_comm_langchain.py
        - 改CHAT_MODELS，加入要用的
        - 改用MODEL_KWARGS，配置要用的那个
        - 改.env加入API key，没有就创建一个。
          - 找个云服务商注册后可得，如DeepSeek，阿里云百炼，或者ollama本地开模型
          - 建议先充个10块20块的。
        - 运行测试，看能不能调起大模型来。
    - 配置提示词：
      - examples/text_loader.py: case_name, 选择默认要加载哪个提示词JSON
      - examples/对海打击红方.json，里面具体改提示词
    - 配置结果文件夹：
      - 根目录下创建auto_test文件夹（如无

## 运行和调试
    - 纯命令行运行：
      - 在mission_arrange\mission_arrange.py里，看一下flag配置
      - 修改plan_num=1，每次生成一个方案，即一个子任务序列。
      - 建议在mission_arrange.main_loop中jieguo = self.get_one_plan...一行点个断点，可看到都输入了些什么
      - 逐步调试可理清整个儿运行逻辑。
    - 带界面运行：略，从auto_run进，需要IntelligentCommandSupportSystem前端界面

## 修改
    - 核心是改templates/mission_plan
    - 恐怕需要根据场景重新设定子任务类型和子任务参数，以及状态空间离散方式