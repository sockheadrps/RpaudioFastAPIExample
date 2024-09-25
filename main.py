from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import rpaudio
from rpaudio import FadeIn, FadeOut, ChangeSpeed
import json
import uvicorn

app = FastAPI()

# Mount static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

# Global variables
AUDIO_FILE = r"C:\Users\16145\Desktop\exc.mp3"
audio_handler = None
kill_audio = False

# Queue for handling audio commands
command_queue = asyncio.Queue()

# WebSocket clients
clients = []

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

        elif command["type"] == "set_effects":

            effects_list = []

            # Handle fade in effect if it exists
            if "fadeIn" in command["effects"]:
                fade_in_duration = float(
                    command["effects"]["fadeIn"]["duration"])
                fade_in_apply_after = float(
                    command["effects"]["fadeIn"]["applyAfter"])
                fade_in_effect = FadeIn(
                    duration=fade_in_duration, apply_after=fade_in_apply_after)
                effects_list.append(fade_in_effect)

            # Handle fade out effect if it exists
            if "fadeOut" in command["effects"]:
                fade_out_duration = float(
                    command["effects"]["fadeOut"]["duration"])
                fade_out_apply_after = float(
                    command["effects"]["fadeOut"]["applyAfter"])
                fade_out_effect = FadeOut(
                    duration=fade_out_duration, apply_after=fade_out_apply_after)
                effects_list.append(fade_out_effect)

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


@app.get("/", response_class=HTMLResponse)
async def get_audio_player():
    return HTMLResponse(content=open("templates/audio_player.html").read())


@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    global kill_audio, audio_handler
    await websocket.accept()
    clients.append(websocket)

    # Create the audio command processor task on connect
    audio_processor_task = asyncio.create_task(audio_command_processor())

    try:
        while True:
            # Receive commands from the client
            data = await websocket.receive_text()
            print(f"Received data: {data}")

            if data.strip():
                try:
                    data_json = json.loads(data)
                except json.JSONDecodeError as e:
                    await websocket.send_text(f"Invalid JSON: {str(e)}")
                    continue

                event_type = data_json.get('event')

                if event_type == "effects":
                    # Directly access the 'data' key to get effect values
                    effects_data = data_json.get('data', {})

                    # Create effects dictionary
                    effects = {}

                    # Add fadeIn settings if present
                    if 'fadeInDuration' in effects_data or 'fadeInApplyAfter' in effects_data:
                        effects['fadeIn'] = {
                            "duration": effects_data.get('fadeInDuration'),
                            "applyAfter": effects_data.get('fadeInApplyAfter')
                        }

                    # Add fadeOut settings if present
                    if 'fadeOutDuration' in effects_data or 'fadeOutApplyAfter' in effects_data:
                        effects['fadeOut'] = {
                            "duration": effects_data.get('fadeOutDuration'),
                            "applyAfter": effects_data.get('fadeOutApplyAfter')
                        }

                    # Add speed settings if present
                    if 'speed' in effects_data or 'speedDuration' in effects_data or 'speedApplyAfter' in effects_data:
                        effects['speed'] = {
                            "value": effects_data.get('speed'),
                            "duration": effects_data.get('speedDuration'),
                            "applyAfter": effects_data.get('speedApplyAfter')
                        }

                    # Send effects settings to the command queue if there are any effects
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

                # Broadcast updates or audio state to all connected clients
                for client in clients:
                    if client != websocket:
                        await client.send_text(f"Audio state updated: {event_type}")

    except WebSocketDisconnect:
        # On disconnect, cancel the audio command processor task
        audio_processor_task.cancel()
        clients.remove(websocket)
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
