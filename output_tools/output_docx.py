# 搞一个输出文档的东西，先把形似的问题解决了，然后再把别的逐渐往上加。
import docx
from text_transfer.text_transfer import *

class output_docx():
    def __init__(self):
        # 这个的说法是把各种需要存的东西都弄进来，然后存着，然后最后一声令下输出出去。这部分应该是无益于发文章的所以差不多得了
        self.text_dict = {} 
        self.file_name = "demo1.docx"
        self.template_name = "templates/docx_template.docx"
        self.document = docx.Document(self.template_name)
        self.text_transfer = text_transfer()
        pass

    def save_file(self):
        self.arrange_docx()
        full_name = r"auto_test/" + self.file_name
        self.document.save(full_name)
        pass

    def set_heading(self,heading_str:str):
        self.text_dict["heading"] = heading_str
    
    def set_jieguo(self,jieguo_dict:dict):
        self.text_dict["jieguo"] = jieguo_dict

    def set_context(self, context_str:str):
        self.text_dict["context"] = context_str
    
    def set_submission(self,submission_list:list):
        self.text_dict["submission_list"] = submission_list
    
    def set_ufunc_json(self, ufunc_json:dict):
        if not("ufunc_json_list" in self.text_dict):
            self.text_dict["ufunc_json_list"] = []
        self.text_dict["ufunc_json_list"].append(ufunc_json)

    def arrange_docx(self):
        #开始之前得先删除一下，不然就不太对了。
        self.document = docx.Document(self.template_name)

        self.document.add_heading(self.text_dict["heading"], level=1)

        self.document.add_heading("一、推演背景", level=2)

        self.document.add_paragraph(self.text_dict["context"])

        self.document.add_heading("二、子任务信息", level=2)

        # self.document.add_paragraph(self.text_dict["jieguo"])
        self.arrange_submission()

        self.document.add_heading("三、未完待续", level=2)

        self.document.add_paragraph("当朝大学士，统共有五位，朕不得不罢免四位，六部尚书，朕不得不罢免三位。")

    def arrange_submission(self):
        print("output_docx.arrange_submission: unfinished yet")
        for i in range(len(self.text_dict["submission_list"])):
            submission_single = self.text_dict["submission_list"][i]

            self.document.add_heading(submission_single.id_str, level=3)

            # 然后参与的单位和时间啥的写一下
            str_single = "在第" + str(submission_single.time_arrange[0]) + "帧到第" +str(submission_single.time_arrange[1]) + "帧期间，辅助决策系统为" + submission_single.force_arrange + "分配了一个任务，命令其" + submission_single.type_str + "。"

            self.document.add_paragraph(str_single)

            # 然后决策依据写一下。
            state_shuofa_str = self.text_dict["jieguo"]["state_str_list"][i]
            state_shuofa_str = self.text_transfer.cut_from_str(state_shuofa_str,"**","**",model="infinite")
            state_shuofa_str = self.text_transfer.clean_the_str(state_shuofa_str)
            self.document.add_paragraph(state_shuofa_str)

            # 然后是utility函数的那个
            utilitys_shuofa_str = self.text_dict["ufunc_json_list"][i]["explanation"]
            self.document.add_paragraph(utilitys_shuofa_str)
