import os.path

from emotions import Emotion

class EmotionSounds:

    _sounds_according_to_emotions = {
        Emotion.HAPPINESS : "happy.wav",
        Emotion.FEAR : "fear.wav",
        Emotion.ANGER : "anger.wav",
        Emotion.DISGUST : "disgust.wav",
        Emotion.NEUTRAL : "neutral.wav",
        Emotion.CONTEMPT : "contempt.wav",
        Emotion.SADNESS : "sadness.wav",
        Emotion.SURPRISE : "surprise.wav",
    }

    SOUND_PATH = "sounds/"

    @staticmethod
    def sound_provider(emotion:Emotion):
        return os.path.join(EmotionSounds.SOUND_PATH, EmotionSounds._sounds_according_to_emotions[emotion])