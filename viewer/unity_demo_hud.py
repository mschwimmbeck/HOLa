# ------------------------------------------------------------------------
# HOLa
# url: https://github.com/mschwimmbeck/HOLa
# Copyright (c) 2023 Michael Schwimmbeck. All Rights Reserved.
# Licensed under the GNU Affero General Public License v3.0 [see LICENSE for details]
# ------------------------------------------------------------------------
# HL2SS 
# url: https://github.com/jdibenes/hl2ss/tree/main
# Copyright (c) 2022 by Stevens Institute of Technology. All Rights Reserved. [see licences for details]
# ------------------------------------------------------------------------

#------------------------------------------------------------------------------
# This script adds a textured quad to the Unity scene in image space. Press esc
# to stop.
#------------------------------------------------------------------------------

from pynput import keyboard

import threading
import hl2ss
import rus


# Settings --------------------------------------------------------------------

# HoloLens address
host = '192.168.1.7'

# Port
port = hl2ss.IPCPort.UNITY_MESSAGE_QUEUE

# Position in image space (x, y, z)
# x, y in pixels
# z is the depth of the object in meters
position = [int(1440/2), int(936/2), 40]

# Rotation in camera space (x, y, w, z) as a quaternion
rotation = [0, 0, 0, 1]

# Scale (x, y, z)
# x, y, in pixels
# z in meters, for flat objects it should be 1
scale = [256, 256, 1]

# Texture file (must be jpg or png)
texture_file = 'texture.jpg'

#------------------------------------------------------------------------------

stop_event = threading.Event()

def on_press(key):
    if (key == keyboard.Key.esc): 
        stop_event.set()
        return False
    return True

listener = keyboard.Listener(on_press=on_press)
listener.start()

with open(texture_file, mode='rb') as file:
    texture = file.read()

ipc = hl2ss.ipc_umq(host, port)
ipc.open()

key = 0

display_list = rus.command_buffer()
display_list.begin_display_list() # Begin command sequence
display_list.remove_all() # Remove all objects that were created remotely
display_list.create_primitive(rus.PrimitiveType.Quad) # Create a quad, server will return its id
display_list.set_target_mode(rus.TargetMode.UseLast) # Set server to use the last created object as target, this avoids waiting for the id of the quad
display_list.set_local_transform(key, position, rotation, scale) # Set the local transform of the cube
display_list.set_texture(key, texture) # Set the texture of the quad
display_list.set_active(key, rus.ActiveState.Active) # Make the quad visible
display_list.set_target_mode(rus.TargetMode.UseID) # Restore target mode
display_list.end_display_list() # End command sequence
ipc.push(display_list) # Send commands to server
results = ipc.pull(display_list) # Get results from server
key = results[2] # Get the quad id, created by the 3rd command in the list

stop_event.wait()

command_buffer = rus.command_buffer()
command_buffer.remove(key) # Destroy quad
ipc.push(command_buffer)
results = ipc.pull(command_buffer)

ipc.close()

listener.join()
