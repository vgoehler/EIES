# EIES
Emotion Intent Evoking System

## Prerequisites

### rpi-rgb-led-64x64-matrix-py

- this is my fork of [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix)
- fixed to a 64x64 matrix
- some bug fixes, mainly installer

#### install

- in *rpi-rgb-led-64x64-matrix-py* -> ``` make build-python ```
- also in *rpi-rgb-led-64x64-matrix-py* -> ``` make install-python ```
- pip will install rgbmatrix into your current environment
- if you are using poetry, you don't have to do any of this
- but we need cython for compiling the sources;
     - I did a work around
     - after poetry failed I activated the venv ```$HOME/.cache/pypoetry/virtualenvs```
     - then installed cython with pip  ```pip install cython```
     - TODO: need to automate this in the makefile

### install libraries

- we need bluetooth! ```sudo apt-get install libbluetooth-dev```
- we need ffmpeg! ```sudo apt-get install ffmpeg```
- run ``` poetry install ```

### Build-System Notes

- on my raspberry I only got an ancient poetry version, but poetry 2+ is needed
- did direct install from [Official Poetry Install Website](https://python-poetry.org/docs/#installing-with-the-official-installer)

## Server

The Server runs the Bluetooth Server and is contactable over REST.
It accepts a POST Json:

## LED Panel Emotion Controller

```json
{
"action": "draw",
"emotion": ["fear"|"happiness"|"disgust"|"anger"|"surprise"|"neutral"|"sadness"|"contempt"]
}
```
- see the `Emotion` enum in `emotions.py`.

## Sound Listener Controller

```json
{
"action": "play",
"emotion": ["fear"|"happiness"|"disgust"|"anger"|"surprise"|"neutral"|"sadness"|"contempt"],
"duration": (int),
"fade_time": (int)
}
```
- see the `Emotion` enum in `emotions.py`
- duration in seconds is an `int`
- fade_time in milliseconds is an `int`

## Client

On the Client (Raspi) that is LED-Panel enabled runs the 
- *led_panel_client_bt.py* -- manages the bt connection and forwards the emotion string
- *ledpanelemotioncontroller.py* -- gets the emotion string and sets the color of the LED-Panel accordingly

```mermaid
   sequenceDiagram
    participant S as Server
    participant BT as led_panel_client_bt.py
    participant EC as ledpanelemotioncontroller.py
    participant Raspi as Raspberry Pi (Client)

    S->>BT: Sends emotion string via BT
    BT->>EC: Forwards emotion string
    EC-->>Raspi: Updates LED-Panel color
 
```
