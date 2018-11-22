"""
调用腾讯智能闲聊API实现聊天，使用腾讯优图语音合成API实现朗读结果
"""
import time;
import base64;
import hashlib;
import random;
import json;
import string;
import os;
import urllib;
from urllib.parse import quote;
from urllib import request;

# 基础类
class BaseClass:
    def __init__(self, url):
        """
        :param url:api的访问地址
        """
        self.URL = url;
        self.APP_ID = 0000000000;  # 你自己的app_id
        self.APP_KEY = "xxxxxxxxxxxxxxxx"; # 你自己的app_key
        # params属性需要用户后来修改，添加对应api所需的参数
        # 这里列举出的key都是共有的，特有的需要用户自己传入
        self.params = {
            'app_id' : self.APP_ID,
            'time_stamp' : None,
            'nonce_str' : None,
        };
        # 调用接口返回的结果
        self.result = None;

    def __get_sign(self):
        """
        计算获得sign的方法
        :return:None
        """
        # 获得时间戳(秒级)，防止请求重放
        time_stamp = int(time.time());
        # 获得随机字符串，保证签名不被预测
        nonce_str = ''.join(random.sample(string.ascii_letters + string.digits, 10))
        # 组合参数（缺少sign，其值要根据以下获得）
        self.params['time_stamp'] = time_stamp;
        self.params['nonce_str'] = nonce_str;
        # 获得sign对应的值
        before_sign = '';
        # 对key排序拼接
        for key in sorted(self.params):
            before_sign += f'{key}={quote(str(self.params[key]).encode("utf-8"))}&';
        # 将应用秘钥以app_key为键名，拼接到before_sign的末尾
        before_sign += f"app_key={self.APP_KEY}";
        # 对获得的before_sign进行MD5加密（结果大写），得到借口请求签名
        sign = hashlib.md5(before_sign.encode("utf-8")).hexdigest().upper();
        # 将请求签名添加进参数字典
        self.params["sign"] = sign;

    def get_result(self):
        """
        该方法用于调用api，获得返回的结果
        :return: None
        """
        # 完善params参数
        self.__get_sign();
        params = urllib.parse.urlencode(self.params).encode("utf-8");
        req = request.Request(url=self.URL, data=params);
        # 设置超时10秒，重试3次
        count = 0;
        while True:
            try:
                count += 1;
                self.result = request.urlopen(req, timeout=10);
                break;
            except Exception as e:
                print(e)
                print(f"连接超时，正在进行第{str(count)}次重连")
                if count <= 3:
                    continue;
                else:
                    break;

    def do_result(self):
        """
        处理结果的方法
        :return: None
        """
        pass;

    def play_audio(self, file_dir, sleep_time, is_delete=False):
        """
        播放下载的语音
        :param file_dir: 包含语音文件的文件夹
        :param sleep_time: 每次播放的时间（因为无法获得语音的时长，只能指定固定时长）
        :param is_delete: 播放完成后是否删除所有语音
        :return: None
        """
        for file in os.listdir(file_dir):
            os.system(file_dir+"\\"+file);
            time.sleep(sleep_time);
        if is_delete:
            for file in os.listdir(file_dir):
                os.remove(file_dir+"\\"+file);

    def run(self):
        """
        主运行方法
        :return: None
        """
        pass;

# 使用腾讯优图语音合成api
class TencentVoice(BaseClass):

    def __init__(self, text,audio_path, sound_choice=2, sound_speed=0):
        """
        :param text: 要合成语音的文本
        :param audio_path: 音频文件的保存位置
        :param sound_choice: 音源选择
        :param sound_speed: 语速选择
        """
        super(TencentVoice, self).__init__('https://api.ai.qq.com/fcgi-bin/aai/aai_tta');
        self.TEXT = text;
        self.audio_path = audio_path;
        self.params['model_type'] = sound_choice;  # 语音 0~2。0：女。1：女英文。2：男
        self.params['speed'] = sound_speed;  # 语速 -2:0.6倍，-1:0.8倍, 0：正常， 1:1.2倍，2:1.5倍

    def deal_text(self):
        """
        处理传入的text
        :return:
        """
        if len(self.TEXT.encode("utf-8")) > 300:
            raise ValueError("text参数长度超出限制，限制utf8下300个字节")
        if isinstance(self.TEXT, str):
            self.params["text"] = self.TEXT;
            self.do_result(self.TEXT);
        elif isinstance(self.TEXT, list):
            for text in self.TEXT:
                if len(text.encode("utf-8")) > 300:
                    raise ValueError("text参数长度超出限制，限制utf8下300个字节");
                else:
                    self.params["text"] = text;
                    self.do_result(text);

    def do_result(self, text):
        """
        将返回的结果处理成mp3格式的音频
        :param text: 用作文件名
        :return:
        """
        self.get_result();
        # print(self.params)
        str_json = self.result.read().decode("utf-8");
        # print(str_json)
        voice_data = json.loads(str_json)["data"]["voice"];
        voice_data = base64.decodestring(bytes(voice_data.encode("utf-8")));
        if len(text) > 10:
            file_name = text[:10];
        else:
            file_name = text;
        if voice_data:
            with open(self.audio_path+"/" + file_name + ".mp3", "wb") as f:
                f.write(voice_data);

    def run(self):
        """
        主运行方法
        :return: None
        """
        self.deal_text();

# 使用腾讯智能闲聊api
class TencetChat(BaseClass):
    def __init__(self, question):
        """
        :param question: 聊天的问题
        """
        super(TencetChat, self).__init__("https://api.ai.qq.com/fcgi-bin/nlp/nlp_textchat");
        self.params["session"] = "10000"
        self.question = question;

    def deal_question(self):
        """
        对提出的问题进行处理，限制长度和类型
        :return: None
        """
        if not isinstance(self.question, str):
            raise TypeError(f"question参数必须是 ‘str’ 类型的，不能是 ‘{type(self.question)}’ 类型的！！！");
        else:
            if len(self.question.encode("utf-8")) > 300:
                raise ValueError("question参数的长度必须小于300个字节（utf-8格式下）")
            else:
                self.params["question"] = self.question;
                # print(self.params)
                self.do_result();

    def do_result(self):
        """
        处理结果
        :return:None
        """
        self.get_result();
        if self.result:
            res = json.loads(self.result.read().decode("utf-8"));
        # print(res)
            if not res["msg"] == "ok":
                self.answer = "我好像出错了："+res["msg"];
            else:
                self.answer = res["data"]["answer"];
        else:
            self.answer="我尝试了4次，但还是失败了，只能说我尽力了。";

    def run(self):
        self.deal_question();

# 整合之后的一个聊天程序
def complete_chat(use_voice=False):
    """
    一个完整的聊天的方法
    :param use_voice: 是否使用语音，出错率较高
    :return: None
    """
    print("欢迎使用智能闲聊，下面开始聊天吧（输入quit退出聊天）：")
    print("*"*50)
    while True:
        question = input("我：");
        if question == "quit":
            break;
        t_chat = TencetChat(question);
        t_chat.run();
        answer = t_chat.answer;
        if use_voice:
            t_voice = TencentVoice(answer,audio_path="TencentChatAudio",sound_choice=0,sound_speed=-1);
            t_voice.run();
            t_voice.play_audio("TencentChatAudio",0,is_delete=True);
        else:
            print("智能闲聊：",answer);
        # print("智能闲聊：",answer);


if __name__ == '__main__':

    complete_chat();