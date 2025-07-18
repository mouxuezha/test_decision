# 循序渐进吧，把分散在各个地方的东西弄过来

import os.path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest

def test_text_loader1():
    from examples.text_loader import text_loader
    shishi = text_loader()
    shishi.set_case("陆火联合.json")
    shishi.load_JSON()
    function_name = "text_transfer.__init_DeLLMa"
    text_name = "state_enmueration_dict"
    jieguo = shishi.get_certain_text(function_name, text_name)
    assert jieguo == {"敌方经度":["偏西","靠中间","偏东"],
                      "敌方纬度":["偏北","靠中间","偏南"],
                      "敌方聚集程度":["分散","一般","集中"],
                      "我方经度":["偏西","靠中间","偏东"],
                      "我方纬度":["偏北","靠中间","偏南"],
                      "我方聚集程度":["分散","一般","集中"]}

def test_text_transfer1():
    from text_transfer.text_transfer import text_transfer
    shishi = text_transfer()
    text_DeLLMa_state2 = '```json\n{\n    "敌方经度": {\n        "靠中间": "很可能",\n        "偏西": "可能",\n        "偏东": "较不可能"\n    },\n    "敌方纬度": {\n        "靠北": "很可能",  // 考虑到夺控点位置及蓝方初始部署，敌方可能在夺控点附近偏北位置\n        "中间": "不太可能",\n        "靠南": "几乎不可能"\n    },\n    "敌方聚集程度": {\n        "集中": "可能",  // 蓝方可能在中、东、西建筑物附近集中布防\n        "分散": "有点可能",\n        "非常分散": "不太可能"\n    },\n    "我方经度": {\n        "偏东": "很可能",  // 考虑到我方已确定偏东出击方向\n        "靠中间": "不太可能",\n        "偏西": "几乎不可能"\n    },\n    "我方纬度": {\n        "中间": "很可能",  // 我方在推进过程中可能处于地图的中间纬度区域\n        "靠北": "可能",\n        "靠南": "较不可能"\n    },\n    "我方聚集程度": {\n        "集中": "有点可能",  // 我方在攻击前可能会进行一定程度的集中以形成火力优势\n        "分散": "可能",  // 但为了侦察和机动，部分单位可能分散\n        "非常分散": "不太可能"\n    }\n}\n```\n\n**解说员视角下的兵棋推演比赛解说**：\n\n各位观众，欢迎来到这场紧张刺激的陆战攻防兵棋推演比赛。此刻，红方与蓝方正在一片广袤的陆地上展开激烈的较量，双方都在为夺取位于关键坐标(100.1247, 13.6615)的夺控点而竭尽全力。\n\n从当前态势来看，红方已经明确了偏东的出击方向，他们的坦克和自行迫榴炮等重型装备正在稳步向前推进。根据我们的信度分布分析，红方很可能在经度上偏东，纬度上处于中间位置，且他们的装备相对集中，以形成强大的火力优势。\n\n而蓝方方面，他们似乎并不打算轻易放弃这个重要的夺控点。他们的装备在经度上可能更加靠近中间位置，纬度上则更可能偏北，以利用地形和建筑物进行防御。蓝方的装备分散程度适中，既能够保持灵活性，又能够在关键时刻形成局部优势。\n\n现在，比赛进入了关键的阶段。红方需要充分发挥他们的地面火力优势，特别是要优先消灭蓝方的防空导弹发射车，以解除对我方导弹的威胁。同时，红方还需要利用无人机和巡飞弹等侦察手段，不断搜集敌方的情报，为后续的进攻提供有力的支持。\n\n而蓝方则可能会采取灵活的机动战术，利用河流、桥梁和路网等地形条件，不断调动兵力，阻击红方的进攻。他们还可能会利用建筑物作为掩体，进行顽强的抵抗。\n\n在接下来的推演中，我们可以期待双方更加精彩的战术运用和火力对决。红方能否成功突破蓝方的防线，占领夺控点？蓝方又能否凭借他们的坚韧和机智，守住这个重要的战略要地？让我们拭目以待，共同见证这场陆战攻防的巅峰对决！'
    # commands = shishi.text_to_commands(text_demo)
    # shishi.get_num_commands()
    jieguo = shishi.get_json_from_str(text_DeLLMa_state2)
    assert len(jieguo)>0

def test_text_transfer2():
    from text_transfer.text_transfer import text_transfer
    shishi = text_transfer()
    text_demo = '进攻指令：\n[move, obj_id=MainBattleTank_ZTZ100_0, x=100.138, y=13.6196],\n[move, obj_id=MainBattleTank_ZTZ100_1, x=100.138, y=13.6196],\n[move, obj_id=MainBattleTank_ZTZ100_2, x=100.138, y=13.6196],\n[move, obj_id=MainBattleTank_ZTZ100_3, x=100.138, y=13.6196],\n[move, obj_id=ArmoredTruck_ZTL100_0, x=100.138, y=13.6196],\n[move, obj_id=ArmoredTruck_ZTL100_1, x=100.138, y=13.6196],\n[move, obj_id=WheeledCmobatTruck_ZB100_0, x=100.138, y=13.6196],\n[move, obj_id=WheeledCmobatTruck_ZB100_1, x=100.138, y=13.6196],\n[move, obj_id=Howitzer_C100_0, x=100.138, y=13.6196],\n[move, obj_id=ShipboardCombat_plane0, x=100.137, y=13.644],\n[move, obj_id=RedCruiseMissile_0, x=100.116, y=13.643],\n[move, obj_id=RedCruiseMissile_1, x=100.164, y=13.658]'
    commands = shishi.text_to_commands(text_demo)
    assert len(commands)>0



if __name__ == "__main__":

    pytest.main(["-v", "-s", "testing/test_text_transfer.py"])
