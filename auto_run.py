# 还是逃不了，还是得来个主函数才比较阳间一点儿
from support.Env import *
from mission_arrange.mission_arrange import mission_arrange
import argparse, queue

class auto_run_comunicator():
    # 还是那个路数，开个进程一直转着，看GUI那头有什么东西发过来。发过来的先缓存着，然后每隔一段时间处理一次。
    # 意图识别、调用不同函数的，在这里面先做一个比较拉但是能用的。后面如果要好的，再说。
    def __init__(self) -> None:
        self.__init_net()
        self.__init_env()
        self.flag_init = True # 这个用来标记当前是不是第一步。
        self.flag_debug = False
        self.mission_arrange = mission_arrange() 
        self.commands_queue = queue.Queue()

        pass

    def __init_env(self):
        self.max_episode_len = self.net_args.max_episode_len
        # self.env = Env(self.net_args.ip, self.net_args.port)
        self.env = Env_server(self.net_args.ip, self.net_args.port)


    def __init_net(self):
        parser = argparse.ArgumentParser(description='Provide arguments for agent.')
        parser.add_argument("--ip", type=str, default="127.0.0.1", help="Ip to connect")
        # parser.add_argument("--ip", type=str, default="192.168.43.93", help="Ip to connect")
        parser.add_argument("--port", type=str, default=30001, help="port to connect")
        parser.add_argument("--epochs", type=int, default=200, help="Number of training epochs to run")  # 设置训练轮次数
        parser.add_argument("--max-episode-len", type=int, default=3000, help="maximum episode length")
        net_args = parser.parse_args()
        self.net_args = net_args
        return net_args        
    
    def __init_seat(self):
        # 分席位的处理也是在这里处理一下算了。原则上只需要跑这一个后端python，是有机会把分席位的事情都干了的。有几分劳动竞赛那个对战的意思了，但是要防止像当时那样来回修改和屎山化。各方比较好接受的是前端大哥们写，然后我能改多少改点儿。
        pass
    
    def run_mul(self):
        # 和之前类似，这个就是开起来跑着就好的多线程不阻塞的
        pass 

    def run_single(self):
        # 这个是单线程的，无限循环写在这里面。
        pass

    def get_command(self):
        # 这个就是从GUI那边拿指令的。每一步执行一次的，收命令过来弄到队列里面去。
        pass

    def send_response(self,response_str:str):
        # 这次在后端就分开，显示的命令是显示的命令，增加点儿掌控力.
        pass 

    def send_plan(self,new_plans:list):
        # 把多方案解析解析，给GUI发过去。
        pass

    def send_evaluate(self, pinggu):
        # 给GUI发个评估结果。
        pass

    def handle_command(self,command):
        # 这个就是执行一条完整的指令，比如一次方案编辑，之类的。其实是在为后面做准备了有点儿.
        # 这个和收信息那个应该放在不同的线程。
        pass

  