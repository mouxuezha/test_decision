import os.path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from model_communication.model_comm_langchain import ModelCommLangchain

def test_model1():
        # communication = ModelCommLangchain(model_name='qianwen')
        # communication = ModelCommLangchain(model_name='deepseek')
        # communication = ModelCommLangchain(model_name='zhipu')
        # communication = ModelCommLangchain(model_name='deepseek2')
        # communication = ModelCommLangchain(model_name='qianwen2')
        # communication = ModelCommLangchain(model_name='qianwen',Comm_type="DeLLMa",role="none")
        communication = ModelCommLangchain(model_name='local',Comm_type="DeLLMa",role="none")
        # communication.communicate_with_model('你好')
        # test_str = """我方obj_id为MainBattleTank_ZTZ100_3的坦克位置在(100.12147,13.6409)处 \n
        #                 我方obj_id为missile_truck0的导弹发射车位置在(100.12843,13.6423)处 \n
        #                 敌方obj_id为MainBattleTank_ZTZ200_1的坦克位置在(100.13174,13.6571)处 \n
        #                 敌方obj_id为WheeledCmobatTruck_ZB200_3的步战车位置在(100.12582,13.65363)处"""
        test_str = "你好，测试大模型 API调用是否成功，我们成功了吗？"
        ret = communication.communicate_with_model(test_str)
        print(ret)
        print(communication.history_output_tokens)
        assert len(test_str) > 10

def test_model2():
        # communication = ModelCommLangchain(model_name='qianwen')
        # communication = ModelCommLangchain(model_name='deepseek')
        # communication = ModelCommLangchain(model_name='zhipu')
        # communication = ModelCommLangchain(model_name='deepseek2')
        # communication = ModelCommLangchain(model_name='qianwen2')
        communication = ModelCommLangchain(model_name='qianwen',Comm_type="DeLLMa",role="none")
        # communication = ModelCommLangchain(model_name='local',Comm_type="DeLLMa",role="none")
        # communication.communicate_with_model('你好')
        # test_str = """我方obj_id为MainBattleTank_ZTZ100_3的坦克位置在(100.12147,13.6409)处 \n
        #                 我方obj_id为missile_truck0的导弹发射车位置在(100.12843,13.6423)处 \n
        #                 敌方obj_id为MainBattleTank_ZTZ200_1的坦克位置在(100.13174,13.6571)处 \n
        #                 敌方obj_id为WheeledCmobatTruck_ZB200_3的步战车位置在(100.12582,13.65363)处"""
        test_str = "你好，测试大模型 API调用是否成功，我们成功了吗？"
        ret = communication.communicate_with_model(test_str)
        print(ret)
        print(communication.history_output_tokens)
        assert len(test_str) > 10

def test_model3():
        # communication = ModelCommLangchain(model_name='qianwen')
        # communication = ModelCommLangchain(model_name='deepseek')
        # communication = ModelCommLangchain(model_name='zhipu')
        communication = ModelCommLangchain(model_name='deepseek2')
        # communication = ModelCommLangchain(model_name='qianwen2')
        # communication = ModelCommLangchain(model_name='qianwen',Comm_type="DeLLMa",role="none")
        # communication = ModelCommLangchain(model_name='local',Comm_type="DeLLMa",role="none")
        # communication.communicate_with_model('你好')
        # test_str = """我方obj_id为MainBattleTank_ZTZ100_3的坦克位置在(100.12147,13.6409)处 \n
        #                 我方obj_id为missile_truck0的导弹发射车位置在(100.12843,13.6423)处 \n
        #                 敌方obj_id为MainBattleTank_ZTZ200_1的坦克位置在(100.13174,13.6571)处 \n
        #                 敌方obj_id为WheeledCmobatTruck_ZB200_3的步战车位置在(100.12582,13.65363)处"""
        test_str = "你好，测试大模型 API调用是否成功，我们成功了吗？"
        ret = communication.communicate_with_model(test_str)
        print(ret)
        print(communication.history_output_tokens)
        assert len(test_str) > 10

def test_model4():
        # communication = ModelCommLangchain(model_name='qianwen')
        # communication = ModelCommLangchain(model_name='deepseek')
        communication = ModelCommLangchain(model_name='zhipu')
        # communication = ModelCommLangchain(model_name='deepseek2')
        # communication = ModelCommLangchain(model_name='qianwen2')
        # communication = ModelCommLangchain(model_name='qianwen',Comm_type="DeLLMa",role="none")
        # communication = ModelCommLangchain(model_name='local',Comm_type="DeLLMa",role="none")
        # communication.communicate_with_model('你好')
        # test_str = """我方obj_id为MainBattleTank_ZTZ100_3的坦克位置在(100.12147,13.6409)处 \n
        #                 我方obj_id为missile_truck0的导弹发射车位置在(100.12843,13.6423)处 \n
        #                 敌方obj_id为MainBattleTank_ZTZ200_1的坦克位置在(100.13174,13.6571)处 \n
        #                 敌方obj_id为WheeledCmobatTruck_ZB200_3的步战车位置在(100.12582,13.65363)处"""
        test_str = "你好，测试大模型 API调用是否成功，我们成功了吗？"
        ret = communication.communicate_with_model(test_str)
        print(ret)
        print(communication.history_output_tokens)
        assert len(test_str) > 10