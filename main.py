from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import rpaudio
from rpaudio import FadeIn, FadeOut, ChangeSpeed
import json
import uvicorn

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

# Global variables
AUDIO_FILE = r"C:\Users\16145\Desktop\exc.mp3"
audio_handler = None
kill_audio = False

command_queue = asyncio.Queue()

clients = []

<<<<<<< Updated upstream
# Callback when the audio stops


def on_audio_stop():
    global kill_audio
    kill_audio = True
    print("Audio has stopped")


async def audio_command_processor():
    """Loop that processes commands from the queue."""
    global audio_handler, kill_audio
    kill_audio = False
    audio_handler = rpaudio.AudioSink(
        callback=on_audio_stop).load_audio(AUDIO_FILE)
    audio_handler.set_volume(0.0)
    audio_handler.try_seek(148.0)
    await asyncio.sleep(0.5)
    current_pos = audio_handler.get_pos()

    while not kill_audio:
        await asyncio.sleep(0.2)

        command = await command_queue.get()

        if command["type"] == "play":
            if not audio_handler.is_playing:
                audio_handler.play()

        elif command["type"] == "pause":
            if audio_handler:
                audio_handler.pause()

        elif command["type"] == "stop":
            if audio_handler:
                audio_handler.stop()
                kill_audio = True
=======

async def client_queue_processor():
    while True:
        await asyncio.sleep(0.2)
        if not client_queue.empty():
            audio_status = client_queue.get_nowait()
            data = {"data": audio_status}
            if len(clients) > 0:
                await clients[0].send_json(data)


def on_audio_stop():
    command_queue.put_nowait({"type": "complete"})


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
        AUDIO_FILE = r"C:\Users\16145\Desktop\a1.mp3"
        AUDIO_FILE_2 = r"C:\Users\16145\Desktop\a2.mp3"
        audio_1 = rpaudio.AudioSink(
            callback=on_audio_stop).load_audio(AUDIO_FILE)
        audio_2 = rpaudio.AudioSink(
            callback=on_audio_stop).load_audio(AUDIO_FILE_2)
        channel = AudioChannel()
        channel.push(audio_1)
        channel.push(audio_2)

    audio_status = {
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
            print(f"Received command: {command}")

            if command["type"] == "play":
                if endpoint == "/audio_sink":
                    if not audio_status["is_playing"]:
                        audio.play()
                        audio_status["is_playing"] = True
                elif endpoint == "/audio_channels":
                    if not audio_status["is_playing"]:
                        if channel.current_audio:
                            channel.current_audio.play()
                            audio_status["is_playing"] = True
                        else:
                            print("No current audio to play.")

            elif command["type"] == "pause":
                if endpoint == "/audio_sink":
                    if audio_status["is_playing"]:
                        audio.pause()
                        audio_status["is_playing"] = False
                elif endpoint == "/audio_channels":
                    if audio_status["is_playing"]:
                        if channel.current_audio:
                            channel.current_audio.pause()
                            audio_status["is_playing"] = False

            elif command["type"] == "stop":
                if endpoint == "/audio_sink":
                    audio.stop()
                    audio_status["is_playing"] = False
                elif endpoint == "/audio_channels":
                    channel.current_audio.stop()
                    audio_status["is_playing"] = False

            elif command["type"] == "autoplay_on":
                if endpoint == "/audio_channels":
                    channel.auto_consume = True
                    audio_status["is_playing"] = True

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
>>>>>>> Stashed changes

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
                if channel is not None and channel.current_audio is not None:
                    await client_queue.put(channel.current_audio_data())
                else:
                    pass

<<<<<<< Updated upstream
            # Handle speed effect if it exists
            if "speed" in command["effects"]:
                speed_value = float(command["effects"]["speed"]["value"])
                speed_duration = float(command["effects"]["speed"]["duration"])
                speed_apply_after = float(
                    command["effects"]["speed"]["applyAfter"])
                speed_up = ChangeSpeed(
                    end_val=speed_value, duration=speed_duration, apply_after=speed_apply_after)
                effects_list.append(speed_up)

            # Apply effects only if any are present
            if effects_list:
                audio_handler.apply_effects(effects_list)
                print(
                    f"Applied effects after: {[effect.apply_after for effect in effects_list]}")

    print("Command processed. Ending the audio command processor loop.")
    command_queue.task_done()
=======
        if command:
            print(f"Command processed: {command}")
            client_queue.put_nowait(audio_status)
            command = None
>>>>>>> Stashed changes


@app.get("/audio_channels", response_class=HTMLResponse)
async def get_audio_player():
    return HTMLResponse(content=open("templates/channels.html").read())


@app.get("/audio_sink", response_class=HTMLResponse)
async def get_audio_player():
    return HTMLResponse(content=open("templates/sink.html").read())


@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    global kill_audio, audio_handler
    await websocket.accept()
    clients.append(websocket)
    data = await websocket.receive_text()

<<<<<<< Updated upstream
    # Create the audio command processor task on connect
    audio_processor_task = asyncio.create_task(audio_command_processor())

    try:
        while True:
            # Receive commands from the client
=======
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
>>>>>>> Stashed changes
            data = await websocket.receive_text()

            if data.strip():
                try:
                    data_json = json.loads(data)
                except json.JSONDecodeError as e:
                    await websocket.send_text(f"Invalid JSON: {str(e)}")
                    continue

                event_type = data_json.get('event')
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
                            "type": "set_effects",
                            "effects": effects
                        })

                elif event_type == "audio_control":
                    command = data_json.get('data')
                    if command == "play":
                        command_queue.put_nowait({"type": "play"})
                        await websocket.send_text("Play command queued.")

                    elif command == "pause":
                        command_queue.put_nowait({"type": "pause"})
                        await websocket.send_text("Pause command queued.")

                    elif command == "stop":
                        command_queue.put_nowait({"type": "stop"})
                        await websocket.send_text("Stop command queued.")

<<<<<<< Updated upstream
                # Broadcast updates or audio state to all connected clients
=======
                    elif command == "autoplay_on":
                        command_queue.put_nowait({"type": "autoplay_on"})
                        await websocket.send_text("Auto play command queued.")

                    elif event_type == "audio_control":
                        data = data_json.get('data')
                        data_type = data_json.get('data')['type']

                        if data_type == "volume":
                            volume = data['value']
                            command_queue.put_nowait({
                                "type": "set_volume",
                                "volume": {"value": volume}
                            })

                        elif data_type == "speed":
                            speed = data['value']
                            command_queue.put_nowait({
                                "type": "speed",
                                "speed": {"value": speed}
                            })

>>>>>>> Stashed changes
                for client in clients:
                    if client != websocket:
                        await client.send_text(f"Audio state updated: {event_type}")

    except WebSocketDisconnect:
        audio_processor_task.cancel()
        clients.remove(websocket)
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
