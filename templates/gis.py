# 这个是用来研究地理信息怎么建模的。确切地说，高精地图和地形地物怎么转化成大模型容易理解的形式。
# 调研一下，不要再自己创了，有标准的就用标准的，哪怕是美军的也行。
import os.path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class gis():
    # 当前设想是，专门整一个东西来处理地理信息，试试以一定程度上结构化数据的方式把地理信息传给大模型，看看它的理解效果如何。
    def __init__(self):
        self.gis_type_dict= {} # 这个是存各种地形地物的描述的，
        self.gis_type_dict["河流"] = "河流能阻碍地面单位，不影响空中单位和火力打击。由多个坐标点的连线表示，第一个点为影响通过的河段起点，最后一个为影响交通的河段终点，认为坐标点之间河道较直。"
        self.gis_type_dict["桥梁"] = "桥梁在影响交通的河段上，能通过地面单位。由一个坐标点表示。"
        self.gis_type_dict["建筑物"] = "建筑物在陆地上，可供步兵占领和防御。由一个坐标点表示。"
        self.gis_type_dict["道路"] = "道路能加速地面部队移动，不影响空中单位和火力打击，地面单位可以从道路任意位置上下道路。由多个坐标点的连线表示，认为坐标点之间道路较直。"

        self.gis_data_dict = {} 
        
        self.set_gis_ldjs2024()
        print("gis.__init__: set_gis_ldjs2024 done")

    def set_gis_ldjs2024(self):
        self.gis_data_dict["建筑物1"] = {"坐标":[100.116,13.643]}
        self.gis_data_dict["建筑物2"] = {"坐标":[100.137,13.644]}
        self.gis_data_dict["建筑物3"] = {"坐标":[100.164,13.658]}
        
        # 从左到右从下到上了，
        self.gis_data_dict["桥梁1"] = {"坐标":[100.141,13.607]}
        self.gis_data_dict["桥梁2"] = {"坐标":[100.162,13.610]}
        self.gis_data_dict["桥梁3"] = {"坐标":[100.170,13.6227]}
        self.gis_data_dict["桥梁4"] = {"坐标":[100.116,13.6421]}
        self.gis_data_dict["桥梁5"] = {"坐标":[100.140,13.6433]}

        # 河流也是从左到右从下到上。
        self.gis_data_dict["河流1"] = {"坐标":[[100.131,13.6021],[100.161,13.6177],[100.194,13.6351]]}
        self.gis_data_dict["河流2"] = {"坐标":[[100.161,13.6177],[100.163,13.6015]]}
        self.gis_data_dict["河流3"] = {"坐标":[[100.103,13.6719],[100.116,13.643],[100.122,13.6287]]}
        self.gis_data_dict["河流4"] = {"坐标":[[100.130,13.6663],[100.140,13.6433],[100.141,13.635]]}

        # 道路标几条来看看成色，至少桥梁附近要有道路的吧
        self.gis_data_dict["道路1"] = {"坐标":[[100.141,13.607],[100.133,13.6423],[100.125,13.6617]]}
        self.gis_data_dict["道路2"] = {"坐标":[[100.154,13.6064],[100.162,13.610],[100.185,13.6258]]}
        self.gis_data_dict["道路3"] = {"坐标":[[100.116,13.6421],[100.133,13.6423],[100.140,13.6433],[100.164,13.657]]}



    def get_gis_str(self):
        # 转化成字符串形式到时候弄到提示词里面去。
        gis_str = "地图范围为经度100.0923到100.18707，纬度范围为13.6024到13.6724，大部分平坦，主要以下几种地形地物：\n"

        for gis_type in self.gis_type_dict.keys():
            gis_str += gis_type + "：" + self.gis_type_dict[gis_type] + "。\n"
        
        gis_str += "具体的地形地物如下：\n"

        for gis_name in self.gis_data_dict.keys():
            gis_str += gis_name + "：" + str(self.gis_data_dict[gis_name]) + "。\n"
        
        return gis_str
    
    def get_gis_test_list(self):
        # 这个用于定义一些测试用的问题，问一下看它到底知不知道这些东西之间的相互关系。
        test_list = []
        test_list.append("测试提问1：从坐标点[100.154,13.6063]出发，坦克和装甲车辆机动至坐标点[100.139,13.6122]，是否需要经过桥梁，需要经过哪些桥梁？")
        test_list.append("测试提问2：从坐标点[100.154,13.6063]出发，无人机机动至坐标点[100.139,13.6122]，是否需要经过桥梁，需要经过哪些桥梁？")
        test_list.append("测试提问3：从坐标点[100.125,13.6616]出发，坦克和装甲车辆机动至坐标点[100.142,13.6438]，是否能够利用道路？先后经过哪些道路？")
        test_list.append("测试提问4：部署在坐标点[100.133,13.6422]的步兵，离其最近的建筑物是哪一个？")

        return test_list

if __name__ == '__main__':
    # 这里应该是组装一个提示词喂到大模型里面去，看看它能不能正确理解通过性，因为这个通过性其实带点逻辑特征在里面的。
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


