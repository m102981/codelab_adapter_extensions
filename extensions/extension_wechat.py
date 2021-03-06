import time
import threading
import zmq
from codelab_adapter import settings
from codelab_adapter.core_extension import Extension
from codelab_adapter.utils import get_python3_path, WechatComponent, threaded
'''
使用scratch作为微信聊天界面
    扫码登陆

使用双向消息模拟出request-response
'''

python3_path = get_python3_path()
quit_code = "quit!"


class WechatExtension(Extension):
    def __init__(self):
        name = type(self).__name__
        super().__init__(name)
        self.TOPIC = "eim/wechat"
        self.wechat_server = None

    @threaded
    def message_monitor(self):
        # 接收微信消息 wechat_server
        port = 38783
        self.wechat_server = WechatComponent(
            "wechat", python3_path, port, socket_mode=zmq.REP)
        self.wechat_server.run()  # as thread
        while self._running:
            # try:
            result = self.wechat_server.socket.recv_json()  # todo 使其顺利退出
            if result.get("text") == "quit!":
                break
            self.wechat_server.socket.send_json({"result": "get it!"})
            # 接收微信消息, 发往Scratch
            self.publish({"topic": self.TOPIC, "payload": result})
            #except zmq.error.ContextTerminated:
        self.wechat_server.terminate()

    def run(self):

        self.logger.info("thread start")
        bg_task = self.message_monitor()

        # todo 来自Scratch的消息发往微信
        port = 38784  # todo 随机分配
        context = zmq.Context.instance()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:%s" % port)
        while self._running:
            scratch_message = self.read()  # json
            topic = scratch_message.get("topic")
            if topic == self.TOPIC:
                self.logger.info("wechat message:%s", str(scratch_message))
                data = scratch_message.get("payload")
                username = data["username"]
                text = data["text"]
                socket.send_json({"username": username, "text": text})
                _ = socket.recv_json()

        # 发布退出消息
        socket.send_json({"text": quit_code, "username": ""})
        _ = socket.recv_json()
        time.sleep(0.5)
        socket.close()
        # context.term()


export = WechatExtension
