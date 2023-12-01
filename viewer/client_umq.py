# ------------------------------------------------------------------------
# HOLa
# url: https://github.com/mschwimmbeck/HOLa
# Copyright (c) 2023 Michael Schwimmbeck. All Rights Reserved.
# Licensed under the GNU Affero General Public License v3.0 [see LICENSE for details]
# ------------------------------------------------------------------------
# Modified from HL2SS (https://github.com/jdibenes/hl2ss/tree/main)
# Copyright (c) 2022 by Stevens Institute of Technology. All Rights Reserved. [see licences for details]
# ------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# This script demonstrates how to send a command with a string parameter to a
# Unity app using the plugin. The command handler for this client is in the
# IPCSkeleton.cs script.
# ------------------------------------------------------------------------------

import hl2ss


def main(host, text):

    class command_buffer(hl2ss.umq_command_buffer):
        # Command structure
        # id:     u32 (4 bytes)
        # size:   u32 (4 bytes)
        # params: size bytes

        # Send string to Visual Studio debugger
        def debug_message(self, text):
            # Command id: 0xFFFFFFFE
            # Command params: string encoded as utf-8
            self.add(0xFFFFFFFE, text.encode('utf-8'))  # Use the add method from hl2ss.umq_command_buffer to pack commands

        # See hl2ss_rus.py and the unity_sample scripts for more examples.

    client = hl2ss.ipc_umq(host, hl2ss.IPCPort.UNITY_MESSAGE_QUEUE)  # Create hl2ss client object
    client.open()  # Connect to HL2

    buffer = command_buffer()  # Create command buffer
    buffer.debug_message(text)  # Append send_debug_message command

    client.push(buffer)  # Send commands in buffer to the Unity app
    response = client.pull(buffer)  # Receive response from the Unity app (4 byte integer per command)
    # print(response)

    client.close()  # Disconnect
