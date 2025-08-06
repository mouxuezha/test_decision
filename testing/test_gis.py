import os.path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest

def test_gis1():
    from templates.gis import gis
    shishi_gis = gis()
    shishi_gis.set_gis_ldjs2024()

    # 构建一个独立的单元测试。
    from text_transfer.text_transfer import text_transfer
    from model_communication.model_comm_langchain import ModelCommLangchain
    
    shishi_tt = text_transfer()
    model_communication = ModelCommLangchain(model_name="local",Comm_type="DeLLMa",role="none")

    # 组装测试字符串，并进行测试。
    test_str_list = shishi_gis.get_gis_test_list()
    gis_str = shishi_gis.get_gis_str()
    for test_str in test_str_list:
        all_str = shishi_tt.prepare_context(gis_str = gis_str)
        all_str += "接下来我会问一些问题，以测试你是否正确理解了场景。\n"+test_str
        print(all_str)
        response_str = model_communication.communicate_with_model(all_str)
    assert len(response_str) > 114