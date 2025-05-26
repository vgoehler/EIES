def test_brightness_zero(panel, mock_canvas):
    panel._fill_canvas(255, 0, 0, brightness=0)

    # Ensure SetPixel was never called when brightness is zero
    mock_canvas.SetPixel.assert_not_called()

def test_brightness_zero_full_screen(panel, mock_canvas):
    panel.canvas_dimensions.update({"top": {"x_start": 0, "x_end": 63, "y_start": 0, "y_end": 63}})

    panel._fill_canvas(255, 255, 255, brightness=0)

    # Ensure Fill was never called when brightness is zero
    mock_canvas.Fill.assert_not_called()
    mock_canvas.SetPixel.assert_not_called()

def test_full_screen_optimization(panel, mock_canvas):
    panel.canvas_dimensions["top"] = {"x_start": 0, "x_end": 63, "y_start": 0, "y_end": 63}

    panel._fill_canvas(255, 255, 255)

    # Ensure Fill was called instead of SetPixel for full screen
    mock_canvas.Fill.assert_called_once_with(255, 255, 255)
    mock_canvas.SetPixel.assert_not_called()

def test_normal_case(panel, mock_canvas):
    panel._fill_canvas(255, 255, 255)

    # Collect all expected pixels
    expected_pixels = set()
    for region in panel.canvas_dimensions.values():
        for x in range(region["x_start"], region["x_end"] + 1):
            for y in range(region["y_start"], region["y_end"] + 1):
                expected_pixels.add((x, y))

    # Collect actual pixels drawn
    actual_pixels = {(call[0][0], call[0][1]) for call in mock_canvas.SetPixel.call_args_list}

    # Ensure Fill ist not called
    mock_canvas.Fill.assert_not_called()
    # Ensure all expected pixels were drawn
    assert actual_pixels == expected_pixels

def test_partial_top_full_bottom_fill(panel, mock_canvas):
    panel.canvas_dimensions.update({
        "top": {"x_start": 0, "x_end": 63, "y_start": 0, "y_end": 20},
        "bottom": {"x_start": 0, "x_end": 63, "y_start": 0, "y_end": 63}
    })

    panel._fill_canvas(255, 255, 255)

    # Ensure Fill was called for the full screen case
    mock_canvas.Fill.assert_called_once_with(255, 255, 255)
    mock_canvas.SetPixel.assert_not_called()

def test_full_top_full_bottom_fill(panel, mock_canvas):
    panel.canvas_dimensions.update({
        "top": {"x_start": 0, "x_end": 63, "y_start": 0, "y_end": 31},
        "bottom": {"x_start": 0, "x_end": 63, "y_start": 32, "y_end": 63}
    })

    panel._fill_canvas(255, 255, 255)

    # Ensure Fill was called for the full screen case
    mock_canvas.Fill.assert_called_once_with(255, 255, 255)
    mock_canvas.SetPixel.assert_not_called()
