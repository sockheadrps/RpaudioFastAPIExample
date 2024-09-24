from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import rpaudio
from rpaudio import FadeIn, FadeOut, ChangeSpeed
import json

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
    audio_handler = rpaudio.AudioSink(callback=on_audio_stop).load_audio(AUDIO_FILE)
    audio_handler.set_volume(0.0)



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
          fade_in_duration = command["effects"]["fadeIn"]["duration"]
          fade_in_apply_after = command["effects"]["fadeIn"]["applyAfter"]
          fade_out_duration = command["effects"]["fadeOut"]["duration"]
          fade_out_apply_after = command["effects"]["fadeOut"]["applyAfter"]
          speed_value = command["effects"]["speed"]["value"]
          speed_duration = command["effects"]["speed"]["duration"]
          speed_apply_after = command["effects"]["speed"]["applyAfter"]

          fade_in_duration = float(fade_in_duration)
          fade_in_apply_after = float(fade_in_apply_after)
          fade_out_duration = float(fade_out_duration)
          fade_out_apply_after = float(fade_out_apply_after)
          speed_value = float(speed_value)
          speed_duration = float(speed_duration)
          speed_apply_after = float(speed_apply_after)

          fade_in_effect = FadeIn(duration=fade_in_duration, apply_after=fade_in_apply_after)
          fade_out_effect = FadeOut(duration=fade_out_duration, apply_after=fade_out_apply_after, start_val=1.0, end_val=0.0)
          speed_up = ChangeSpeed(end_val=speed_value, duration=speed_duration, apply_after=speed_apply_after)

          print(f"fadein value: {fade_in_duration}, fadein apply after: {fade_in_apply_after}")
          print(f"fadeout value: {fade_out_duration}, fadeout apply after: {fade_out_apply_after}")
          print(f"speed value: {speed_value}, speed apply after: {speed_apply_after}, speed duration: {speed_duration}")

          effects_list = [fade_in_effect, speed_up ,fade_out_effect]
          audio_handler.apply_effects(effects_list)

    # Mark the command as done
    print("Command processed. Ending the audio command processor loop.")
    command_queue.task_done()


@app.on_event("startup")
async def startup_event():
    """Start the audio command processor loop on startup."""
    asyncio.create_task(audio_command_processor())

# Serve the HTML for the audio player
@app.get("/", response_class=HTMLResponse)
async def get_audio_player():
    return HTMLResponse(content=open("templates/audio_player.html").read())


@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    global kill_audio, audio_handler
    await websocket.accept()
    clients.append(websocket)
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
                # Updated effects handling in the websocket_endpoint
                if event_type == "effects":
                  # Directly access the 'data' key to get effect values
                  effects_data = data_json.get('data', {})
                  
                  # Get the effect values from the effects_data
                  fade_in_duration = effects_data.get('fadeInDuration')
                  fade_in_apply_after = effects_data.get('fadeInApplyAfter')
                  fade_out_duration = effects_data.get('fadeOutDuration')
                  fade_out_apply_after = effects_data.get('fadeOutApplyAfter')
                  speed = effects_data.get('speed')
                  speed_duration = effects_data.get('speedDuration')
                  speed_apply_after = effects_data.get('speedApplyAfter')

                  # Send effects settings to the command queue
                  command_queue.put_nowait({
                      "type": "set_effects",
                      "effects": {
                          "fadeIn": {
                              "duration": fade_in_duration,
                              "applyAfter": fade_in_apply_after
                          },
                          "fadeOut": {
                              "duration": fade_out_duration,
                              "applyAfter": fade_out_apply_after
                          },
                          "speed": {
                              "value": speed,
                              "duration": speed_duration,
                              "applyAfter": speed_apply_after
                          }
                      }
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
        clients.remove(websocket)
        await websocket.close()
