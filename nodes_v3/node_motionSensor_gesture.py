import time
from codelab_adapter_client import AdapterNode

# 指向 sdk path
import sys, os
kano_sdk_path = "/Users/wuwenjie/mylab/codelabclub/community-sdk"
sys.path.append(kano_sdk_path)

from communitysdk import list_connected_devices, MotionSensorKit


class KanoMotionExtension(AdapterNode):
    NODE_ID = "eim/node_motionSensor"
    HELP_URL = "https://adapter.codelab.club/extension_guide/extension_kano_motion/"  # Documentation page for the project
    VERSION = "1.0"  # extension version
    DESCRIPTION = "kano motion sensor"
    ICON_URL = ""
    REQUIRES_ADAPTER = ""  # ">= 3.2.0"

    def __init__(self):
        super().__init__()

    def extension_message_handle(self, topic, payload):
        self.logger.info(f'eim message:{payload}')
        self.publish({"payload": payload})

    def _publish(self, content):
        message = self.message_template()
        message["payload"]["content"] = content
        self.publish(message)

    def proximity_loop(self, msk):
        # asyncio thread
        if msk != None:

            def on_gesture(gestureValue):
                # print('Gesture detected:', gestureValue)
                self._publish({"gesture": gestureValue})

            info = 'Move your hand above the Motion Sensor:'
            self.pub_notification(info)
            # print(info)
            msk.set_mode('gesture')
            msk.on_gesture = on_gesture
        else:
            error = "No Motion Sensor was found :("
            self.pub_notification(error)

    def run(self):
        '''
        run as thread
        '''
        devices = list_connected_devices()  # hack后
        msk_filter = filter(lambda device: isinstance(device, MotionSensorKit),
                            devices)
        msk = next(msk_filter, None)  # Get first Motion Sensor Kit
        self.proximity_loop(msk)
        while self._running:
            time.sleep(1)

    def terminate(self):
        os._exit(0)


if __name__ == "__main__":
    try:
        node = KanoMotionExtension()
        node.receive_loop_as_thread()
        node.run()
    finally:
        if node._running:
            node.terminate()  # Clean up before exiting.