import os
from manim import *
import numpy as np

# =============================================
# Configuration Settings
# =============================================
CONFIG = {
    # Text Content
    'main_title': "NANO",
    'subtitle': "Fair Queue System",
    'features': [
        "Spam Protection",
        "Fair Resource Distribution",
        "Priority Queuing"
    ],

    # Colors
    'colors': {
        'background': "#20204C",  # NANO_NAVY
        'primary': "#F4FAFF",     # NANO_WHITE
        'accent': "#209CE9",      # NANO_BLUE
        'feature_text': "#F4FAFF"  # Feature text color
    },

    # Typography
    'fonts': {
        'title': "Montserrat",
        'subtitle': "Open Sans",
        'features': "Open Sans"
    },
    'font_sizes': {
        'title': 72,
        'subtitle': 36,
        'features': 24
    },

    # Layout
    'spacing': {
        'title_subtitle': 0.3,    # Space between title and subtitle
        'features_gap': 0.2,      # Space between feature items
        'features_top': 0.3,      # Space above features
        'logo_offset': 3.5,        # Logo distance from center
        'title_group_shift_up': 1  # NEW: Moves entire title group up
    },

    # Animation Timings
    'timings': {
        'logo_entrance': 0.6,
        'logo_rotation': 0.3,
        'title_entrance': 0.8,
        'feature_cascade': 0.5,
        'final_movement': 0.3,
        'final_hold': 1.3,
        'fade_out': 0.3
    },

    # Animation Settings
    'logo': {
        'height': 4,
        'rotation_degrees': 2,
        'flash_radius': 2,
        'flash_lines': 20,
        'flash_length': 0.5,
        'flash_time_width': 0.3
    },

    # Offscreen Starting Position
    'offset_distance': 15
}


def create_nano_svg():
    svg_content = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg viewBox="0 0 506 675" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M505.763 674.778H453.296L254.183 364.339L52.033 674.778H0L226.563 323.078L20.1835 0H73.6716L255.034 284.171L440.234 0H490.421L281.821 322.157L505.763 674.778Z" fill="white"/>
<path d="M49.761 302.515H457.703V340.894H49.761V302.515ZM49.761 417.65H457.72V456.029H49.744L49.761 417.65Z" fill="white"/>
</svg>"""
    with open("nano_logo.svg", "w") as f:
        f.write(svg_content)
    return "nano_logo.svg"


class NanoIntroAnimation(Scene):
    def construct(self):
        # Set background color
        self.camera.background_color = CONFIG['colors']['background']

        # Create and setup logo
        svg_path = create_nano_svg()
        nano_logo = SVGMobject(svg_path)
        nano_logo.set_color(CONFIG['colors']['accent'])
        nano_logo.set_height(CONFIG['logo']['height'])
        nano_logo.move_to(LEFT * CONFIG['spacing']['logo_offset'])

        # Create main title
        title = Text(
            CONFIG['main_title'],
            font=CONFIG['fonts']['title'],
            font_size=CONFIG['font_sizes']['title'],
            weight=BOLD
        ).set_color(CONFIG['colors']['primary'])

        # Create subtitle
        subtitle = Text(
            CONFIG['subtitle'],
            font=CONFIG['fonts']['subtitle'],
            font_size=CONFIG['font_sizes']['subtitle']
        ).set_color(CONFIG['colors']['accent'])

        # Group title elements
        title_group = VGroup(title, subtitle).arrange(
            DOWN,
            buff=CONFIG['spacing']['title_subtitle']
        )
        title_group.move_to(RIGHT * (CONFIG['spacing']['logo_offset'] / 2))
        title_group.shift(UP * CONFIG['spacing']
                          ['title_group_shift_up'])  # Move up

        # Create features
        features = VGroup(*[
            Text(
                f"• {feature}",
                font=CONFIG['fonts']['features'],
                font_size=CONFIG['font_sizes']['features'],
                color=CONFIG['colors']['feature_text']
            )
            for feature in CONFIG['features']
        ]).arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=CONFIG['spacing']['features_gap']
        )
        features.next_to(title_group, DOWN,
                         buff=CONFIG['spacing']['features_top'])

        # Initial positioning
        starting_shifts = VGroup(nano_logo, title_group, features)
        starting_shifts.shift(RIGHT * CONFIG['offset_distance'])

        # Animation sequence
        # 1. Logo entrance
        self.play(
            nano_logo.animate.shift(LEFT * CONFIG['offset_distance']),
            run_time=CONFIG['timings']['logo_entrance'],
            rate_func=smooth
        )

        # 2. Logo rotation
        for angle in [CONFIG['logo']['rotation_degrees'], -CONFIG['logo']['rotation_degrees']]:
            self.play(
                Rotate(
                    nano_logo,
                    angle=angle * DEGREES,
                    about_point=nano_logo.get_center()
                ),
                run_time=CONFIG['timings']['logo_rotation']
            )

        # 3. Title entrance
        self.play(
            title_group.animate.shift(LEFT * CONFIG['offset_distance']),
            run_time=CONFIG['timings']['title_entrance'],
            rate_func=smooth
        )

        # 4. Logo flash effect
        flash = Flash(
            nano_logo.get_center(),
            color=CONFIG['colors']['accent'],
            line_length=CONFIG['logo']['flash_length'],
            num_lines=CONFIG['logo']['flash_lines'],
            flash_radius=CONFIG['logo']['flash_radius'],
            time_width=CONFIG['logo']['flash_time_width']
        )
        self.play(flash)

        # 5. Feature cascade
        for feature in features:
            feature.set_opacity(0)
        features.shift(LEFT * CONFIG['offset_distance'])

        for feature in features:
            self.play(
                feature.animate.set_opacity(1),
                run_time=CONFIG['timings']['feature_cascade']
            )

        # 6. Final subtle movement
        self.play(
            nano_logo.animate.shift(RIGHT * 0.1),
            title_group.animate.shift(LEFT * 0.1),
            run_time=CONFIG['timings']['final_movement']
        )

        # 7. Hold frame
        self.wait(CONFIG['timings']['final_hold'])

        # 8. Fade out
        self.play(
            nano_logo.animate.shift(LEFT * 0.5).set_opacity(0),
            title_group.animate.shift(RIGHT * 0.5).set_opacity(0),
            features.animate.shift(DOWN * 0.3).set_opacity(0),
            run_time=CONFIG['timings']['fade_out']
        )


def cleanup():
    if os.path.exists("nano_logo.svg"):
        os.remove("nano_logo.svg")


if __name__ == "__main__":
    try:
        intro_scene = NanoIntroAnimation()
        intro_scene.render()
    finally:
        cleanup()
