def test_basic_case_with_px(emotion_colors_fixture):
    result = emotion_colors_fixture.define_canvas("100px", "100px", "100px", "100px")
    assert result == {
        'top': {'x_start': 0, 'x_end': 1920, 'y_start': 0, 'y_end': 100},
        'bottom': {'x_start': 0, 'x_end': 1920, 'y_start': 980, 'y_end': 1080},
        'left': {'x_start': 0, 'x_end': 100, 'y_start': 100, 'y_end': 980},
        'right': {'x_start': 1820, 'x_end': 1920, 'y_start': 100, 'y_end': 980}
    }


def test_mixed_units(emotion_colors_fixture):
    result =  emotion_colors_fixture.define_canvas("10%", "15%", "100px", "20%")
    assert result == {
        'top': {'x_start': 0, 'x_end': 1920, 'y_start': 0, 'y_end': 108},
        'bottom': {'x_start': 0, 'x_end': 1920, 'y_start': 918, 'y_end': 1080},
        'left': {'x_start': 0, 'x_end': 100, 'y_start': 108, 'y_end': 918},
        'right': {'x_start': 1536, 'x_end': 1920, 'y_start': 108, 'y_end': 918}
    }


def test_full_percentage(emotion_colors_fixture):
    result =  emotion_colors_fixture.define_canvas("50%", "50%", "25%", "25%")
    assert result == {
        'top': {'x_start': 0, 'x_end': 1920, 'y_start': 0, 'y_end': 540},
        'bottom': {'x_start': 0, 'x_end': 1920, 'y_start': 540, 'y_end': 1080},
        'left': {'x_start': 0, 'x_end': 480, 'y_start': 540, 'y_end': 540},
        'right': {'x_start': 1440, 'x_end': 1920, 'y_start': 540, 'y_end': 540}
    }


def test_exceeding_screen_size(emotion_colors_fixture):
    try:
        emotion_colors_fixture.define_canvas("600px", "600px", "600px", "600px")
    except ValueError as e:
        assert str(e) == "Invalid dimensions: excluded areas exceed the max dimensions."


# Edge Cases
def test_edge_case_no_exclusion(emotion_colors_fixture):
    result = emotion_colors_fixture.define_canvas("0px", "0px", "0px", "0px")
    assert result == {
        'top': {'x_start': 0, 'x_end': 1920, 'y_start': 0, 'y_end': 0},
        'bottom': {'x_start': 0, 'x_end': 1920, 'y_start': 1080, 'y_end': 1080},
        'left': {'x_start': 0, 'x_end': 0, 'y_start': 0, 'y_end': 1080},
        'right': {'x_start': 1920, 'x_end': 1920, 'y_start': 0, 'y_end': 1080}
    }


def test_edge_case_maximum_exclusion(emotion_colors_fixture):
    result = emotion_colors_fixture.define_canvas("1080px", "0px", "1920px", "0px")
    assert result == {
        'top': {'x_start': 0, 'x_end': 1920, 'y_start': 0, 'y_end': 1080},
        'bottom': {'x_start': 0, 'x_end': 1920, 'y_start': 1080, 'y_end': 1080},
        'left': {'x_start': 0, 'x_end': 1920, 'y_start': 1080, 'y_end': 1080},
        'right': {'x_start': 1920, 'x_end': 1920, 'y_start': 1080, 'y_end': 1080}
    }
