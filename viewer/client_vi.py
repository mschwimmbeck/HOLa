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
# This script registers voice commands on the HoloLens and continuously checks
# if any of the registered commands has been heard.
# Press esc to stop.
# ------------------------------------------------------------------------------

import hl2ss


def start_command(host):
    # Port
    port = hl2ss.IPCPort.VOICE_INPUT

    # Voice commands
    strings = ['start']

    # ------------------------------------------------------------------------------

    enable = True

    def get_word(strings, index):
        if (index < 0) or (index >= len(strings)):
            return '_UNKNOWN_'
        else:
            return strings[index]

    client = hl2ss.ipc_vi(host, port)
    client.open()

    # See
    # https://learn.microsoft.com/en-us/windows/mixed-reality/develop/native/voice-input-in-directx
    # for details

    flag = False

    client.create_recognizer()
    if client.register_commands(True, strings):
        print('Listening for start voice command...')
        client.start()
        while enable:
            events = client.pop()
            for event in events:
                event.unpack()
                # See
                # https://learn.microsoft.com/en-us/uwp/api/windows.media.speechrecognition.speechrecognitionresult?view=winrt-22621
                # for result details
                print(f'Event: Command={get_word(strings, event.index)} Index={event.index} Confidence={event.confidence} Duration={event.phrase_duration} Start={event.phrase_start_time} RawConfidence={event.raw_confidence}')
                flag = True
            if flag:
                break
        client.stop()
        client.clear()

    client.close()
    return


def stop_command(host):
    # Port
    port = hl2ss.IPCPort.VOICE_INPUT

    # Voice commands
    strings = ['stop']

    # ------------------------------------------------------------------------------

    enable = True

    def get_word(strings, index):
        if (index < 0) or (index >= len(strings)):
            return '_UNKNOWN_'
        else:
            return strings[index]

    client = hl2ss.ipc_vi(host, port)
    client.open()

    # See
    # https://learn.microsoft.com/en-us/windows/mixed-reality/develop/native/voice-input-in-directx
    # for details

    flag = False

    client.create_recognizer()
    if client.register_commands(True, strings):
        print('Listening for stop voice command...')
        client.start()
        while enable:
            events = client.pop()
            for event in events:
                event.unpack()
                # See
                # https://learn.microsoft.com/en-us/uwp/api/windows.media.speechrecognition.speechrecognitionresult?view=winrt-22621
                # for result details
                print(f'Event: Command={get_word(strings, event.index)} Index={event.index} Confidence={event.confidence} Duration={event.phrase_duration} Start={event.phrase_start_time} RawConfidence={event.raw_confidence}')
                flag = True
            if flag:
                break
        client.stop()
        client.clear()

    client.close()
    return
