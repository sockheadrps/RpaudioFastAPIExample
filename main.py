from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import rpaudio
from rpaudio import FadeIn, FadeOut, ChangeSpeed, AudioChannel
import json
import uvicorn

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/templates", StaticFiles(directory="templates"), name="templates")


command_queue = asyncio.Queue()
client_queue = asyncio.Queue()

clients = []


async def client_queue_processor():
    while True:
        await asyncio.sleep(0.2)
        if not client_queue.empty():
            audio_status = client_queue.get_nowait()
            data = {"data": audio_status}
            if len(clients) > 0:
                await clients[0].send_json(data)


def on_audio_stop():
    print("Audio stopped.")


async def audio_command_processor(endpoint):
    channel = None
    audio = None
    command = None

    if not endpoint:
        endpoint = None

    if endpoint == "/audio_sink":
        AUDIO_FILE = r"C:\Users\16145\Desktop\a1.mp3"
        audio = rpaudio.AudioSink(
            callback=on_audio_stop).load_audio(AUDIO_FILE)

    elif endpoint == "/audio_channels":
        AUDIO_FILE = r"C:\Users\16145\Desktop\exc.mp3"
        AUDIO_FILE_2 = r"C:\Users\16145\Desktop\a2.mp3"
        AUDIO_FILE_3 = r"C:\Users\16145\Desktop\Acrylic.mp3"

        audio_1 = rpaudio.AudioSink(
            callback=on_audio_stop).load_audio(AUDIO_FILE)
        audio_2 = rpaudio.AudioSink(
            callback=on_audio_stop).load_audio(AUDIO_FILE_2)
        channel_l = AudioChannel()
        channel_l.push(audio_1)
        channel_l.push(audio_2)

        audio_3 = rpaudio.AudioSink(
            callback=on_audio_stop).load_audio(AUDIO_FILE_3)
        audio_4 = rpaudio.AudioSink(
            callback=on_audio_stop).load_audio(AUDIO_FILE_2)
        channel_2 = AudioChannel()
        channel_2.push(audio_3)
        channel_2.push(audio_4)

        channels = {
            "1": channel_l,
            "2": channel_2
        }

    audio_status = {
        "1": {
            "is_playing": False,
            "data": None
        },
        "2": {
            "is_playing": False,
            "data": None
        },
        "is_playing": False,
        "title": None,
        "artist": None,
        "duration": None,
    }
    client_queue.put_nowait(audio_status)

    while True:
        await asyncio.sleep(0.2)

        try:
            command = await asyncio.wait_for(command_queue.get(), timeout=0.2)
            if endpoint == "/audio_channels":
                target_channel = str(command['channel'])
                channel = channels.get(target_channel)

            if command["type"] == "play":
                if endpoint == "/audio_sink":
                    if not audio_status["is_playing"]:
                        audio.play()
                        audio_status["is_playing"] = True
                elif endpoint == "/audio_channels":
                    if not audio_status[target_channel]["is_playing"]:
                        if channel.current_audio:
                            channel.current_audio.play()
                            audio_status[target_channel]["is_playing"] = True
                        else:
                            print("No current audio to play.")

            elif command["type"] == "pause":
                if endpoint == "/audio_sink":
                    if audio_status["is_playing"]:
                        audio.pause()
                        audio_status["is_playing"] = False
                elif endpoint == "/audio_channels":
                    if audio_status[target_channel]["is_playing"]:
                        if channel.current_audio:
                            channel.current_audio.pause()
                            audio_status[target_channel]["is_playing"] = False

            elif command["type"] == "stop":
                if endpoint == "/audio_sink":
                    audio.stop()
                    audio_status["is_playing"] = False
                elif endpoint == "/audio_channels":
                    if channel.current_audio:
                        channel.current_audio.stop()

            elif command["type"] == "autoplay_on":
                if endpoint == "/audio_channels":
                    channel.auto_consume = True
                    audio_status[target_channel]["is_playing"] = True

            elif command["type"] == "set_volume":
                volume = command["volume"]["value"]
                if endpoint == "/audio_sink":
                    audio.set_volume(float(volume))
                if endpoint == "/audio_channels":
                    channel.current_audio.set_volume(float(volume))

            elif command["type"] == "speed":
                speed = command["speed"]["value"]
                if endpoint == "/audio_sink":
                    audio.set_speed(float(speed))
                if endpoint == "/audio_channels":
                    channel.current_audio.set_speed(float(speed))

            elif command["type"] == "set_effects":
                effects_list = []
                if "fadeIn" in command["effects"]:
                    fade_in_duration = float(
                        command["effects"]["fadeIn"]["duration"])
                    fade_in_apply_after = float(
                        command["effects"]["fadeIn"]["applyAfter"])
                    fade_in_effect = FadeIn(
                        duration=fade_in_duration, apply_after=fade_in_apply_after)
                    effects_list.append(fade_in_effect)

                if "fadeOut" in command["effects"]:
                    fade_out_duration = float(
                        command["effects"]["fadeOut"]["duration"])
                    fade_out_apply_after = float(
                        command["effects"]["fadeOut"]["applyAfter"])
                    fade_out_effect = FadeOut(
                        duration=fade_out_duration, apply_after=fade_out_apply_after)
                    effects_list.append(fade_out_effect)

                if "speed" in command["effects"]:
                    speed_value = float(command["effects"]["speed"]["value"])
                    speed_duration = float(
                        command["effects"]["speed"]["duration"])
                    speed_apply_after = float(
                        command["effects"]["speed"]["applyAfter"])
                    speed_up = ChangeSpeed(
                        end_val=speed_value, duration=speed_duration, apply_after=speed_apply_after)
                    effects_list.append(speed_up)

                if effects_list:
                    channel.set_effects_chain(effects_list)

        except asyncio.TimeoutError:
            if endpoint == "/audio_sink":
                if hasattr(audio, 'metadata'):
                    await client_queue.put(audio.metadata)
                else:
                    print("No audio metadata available.")
            elif endpoint == "/audio_channels":
                for chan_id, chan in enumerate(channels):
                    target_channel_id = str(chan_id + 1)
                    if channels[target_channel_id] is not None and channels[target_channel_id].current_audio is not None:
                        audio_status[target_channel_id]['data'] = channels[chan].current_audio_data(
                        )
                        # print(f"Audio status: {audio_status[target_channel_id]['data']}")
                        await client_queue.put(audio_status)


@ app.get("/audio_channels", response_class=HTMLResponse)
async def get_audio_player():
    return HTMLResponse(content=open("templates/channels.html").read())


@ app.get("/audio_sink", response_class=HTMLResponse)
async def get_audio_player():
    return HTMLResponse(content=open("templates/sink.html").read())


@ app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    data = await websocket.receive_text()

    if data.strip():
        try:
            data_json = json.loads(data)
        except json.JSONDecodeError as e:
            await websocket.send_text(f"Invalid JSON: {str(e)}")

        event_type = data_json.get('event')
        endpoint = data_json.get('data')
        audio_processor_task = asyncio.create_task(
            audio_command_processor(endpoint))
        client_processor_task = asyncio.create_task(
            client_queue_processor())

    try:
        while True:
            await asyncio.sleep(0.2)
            data = await websocket.receive_text()

            if data.strip():
                try:
                    data_json = json.loads(data)
                except json.JSONDecodeError as e:
                    await websocket.send_text(f"Invalid JSON: {str(e)}")
                    continue

                event_type = data_json.get('event')
                channel = data_json.get('channel')
                endpoint = data_json.get('data')

                if event_type == "effects":
                    effects_data = data_json.get('data', {})
                    effects = {}

                    if 'fadeInDuration' in effects_data or 'fadeInApplyAfter' in effects_data:
                        effects['fadeIn'] = {
                            "duration": effects_data.get('fadeInDuration'),
                            "applyAfter": effects_data.get('fadeInApplyAfter')
                        }

                    if 'fadeOutDuration' in effects_data or 'fadeOutApplyAfter' in effects_data:
                        effects['fadeOut'] = {
                            "duration": effects_data.get('fadeOutDuration'),
                            "applyAfter": effects_data.get('fadeOutApplyAfter')
                        }

                    if 'speed' in effects_data or 'speedDuration' in effects_data or 'speedApplyAfter' in effects_data:
                        effects['speed'] = {
                            "value": effects_data.get('speed'),
                            "duration": effects_data.get('speedDuration'),
                            "applyAfter": effects_data.get('speedApplyAfter')
                        }

                    if effects:
                        command_queue.put_nowait({
                            "channel": channel,
                            "type": "set_effects",
                            "effects": effects
                        })

                elif event_type == "audio_control":
                    command = data_json.get('data')
                    if command == "play":
                        command_queue.put_nowait(
                            {"channel": channel, "type": "play"})
                        await websocket.send_text("Play command queued.")

                    elif command == "pause":
                        command_queue.put_nowait(
                            {"channel": channel, "type": "pause"})
                        await websocket.send_text("Pause command queued.")

                    elif command == "stop":
                        command_queue.put_nowait(
                            {"channel": channel, "type": "stop"})
                        await websocket.send_text("Stop command queued.")

                    elif command == "autoplay_on":
                        command_queue.put_nowait(
                            {"channel": channel, "type": "autoplay_on"})
                        await websocket.send_text("Auto play command queued.")

                    elif event_type == "audio_control":
                        data = data_json.get('data')
                        data_type = data_json.get('data')['type']

                        if data_type == "volume":
                            volume = data['value']
                            command_queue.put_nowait({
                                "channel": channel,
                                "type": "set_volume",
                                "volume": {"value": volume}
                            })

                        elif data_type == "speed":
                            speed = data['value']
                            command_queue.put_nowait({
                                "channel": channel,
                                "type": "speed",
                                "speed": {"value": speed}
                            })

                for client in clients:
                    if client != websocket:
                        await client.send_text(f"Audio state updated: {event_type}")

    except (WebSocketDisconnect, RuntimeError):
        audio_processor_task.cancel()
        client_processor_task.cancel()
        clients.remove(websocket)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
