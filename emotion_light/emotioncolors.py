from emotions import Emotion


class EmotionColors:
    """
    Encapsulates the colors corresponding to emotions.
    We cover Happiness, Fear, Anger, Disgust, Neutral, Sadness, Surprise.
    Contempt is not yet included, only as a placeholder.
    The class returns a rgb tuple plus brightness.
    """

    _colors_according_to_emotions = {     # hue,     value,   intensity
        Emotion.HAPPINESS : (252,255,  0, 100),# yellow, bright, high
        Emotion.FEAR :      ( 65, 31, 68, 25),# violet, intermediate, low
        Emotion.ANGER :     ( 89, 26, 26, 65),# red, dark, medium
        Emotion.DISGUST :   ( 82, 96, 42, 65),# yellow-green, dark, medium
        Emotion.NEUTRAL :   (124,124,124, 100),# not in paper, just grey
        Emotion.CONTEMPT :  (  0,  0,  0, 0),# not in paper
        Emotion.SADNESS :   (104,109,145, 25),# blue, intermediate, low
        Emotion.SURPRISE :  (191, 77,  0, 100),# red-yellow, bright, high
    }
    @staticmethod
    def color_provider(emotion:Emotion):
        """
        Main static method that returns the corresponding rgb tuple.
        :param emotion: an Emotion
        :return: tuple(red, green, blue, brightness)
        """
        return EmotionColors._colors_according_to_emotions[emotion]
