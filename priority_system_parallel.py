from manim import *
import numpy as np


class QueueSystem:
    def __init__(self,
                 queue_height=0.7,
                 queue_width=4,
                 active_width=2,
                 dot_radius=0.05,
                 dot_spacing=0.12,
                 item_color="#FF4444",
                 queue_color=BLUE,
                 active_color=YELLOW,
                 queue_opacity=0.2,
                 active_opacity=0.3,
                 position=LEFT * 3,
                 left_label="<0.000001X"):
        self.QUEUE_HEIGHT = queue_height
        self.QUEUE_WIDTH = queue_width
        self.ACTIVE_WIDTH = active_width
        self.DOT_RADIUS = dot_radius
        self.DOT_SPACING = dot_spacing
        self.ITEM_COLOR = item_color
        self.QUEUE_COLOR = queue_color
        self.ACTIVE_COLOR = active_color
        self.QUEUE_OPACITY = queue_opacity
        self.ACTIVE_OPACITY = active_opacity
        self.POSITION = position
        self.LEFT_LABEL = left_label

        self.blue_dots = []
        self.active_dots = []
        self.confirmed_dots = []

        # Calculate important positions
        self.queue_left = self.POSITION[0] - self.QUEUE_WIDTH/2
        self.queue_right = self.POSITION[0] + self.QUEUE_WIDTH/2
        self.active_left = self.queue_right
        self.active_right = self.queue_right + self.ACTIVE_WIDTH
        self.queue_top = self.POSITION[1] + self.QUEUE_HEIGHT/2
        self.queue_bottom = self.POSITION[1] - self.QUEUE_HEIGHT/2

    def create_containers(self, scene):
        # Create containers group
        self.containers = VGroup()

        # Create and position the blue section
        self.blue_section = Rectangle(
            width=self.QUEUE_WIDTH,
            height=self.QUEUE_HEIGHT,
            color=self.QUEUE_COLOR,
            fill_opacity=self.QUEUE_OPACITY
        ).move_to(self.POSITION)

        # Create and position the active section
        self.active_section = Rectangle(
            width=self.ACTIVE_WIDTH,
            height=self.QUEUE_HEIGHT,
            color=self.ACTIVE_COLOR,
            fill_opacity=self.ACTIVE_OPACITY
        ).next_to(self.blue_section, RIGHT, buff=0)

        # Create left label only
        self.queue_label = Text(
            self.LEFT_LABEL,
            font_size=24
        ).next_to(self.blue_section, LEFT)

        # Add elements to the containers group
        self.containers.add(
            self.blue_section,
            self.active_section,
            self.queue_label
        )

        scene.play(
            Create(self.blue_section),
            Create(self.active_section),
            Write(self.queue_label)
        )

    def create_dot(self, position):
        return Dot(
            point=position,
            radius=self.DOT_RADIUS,
            color=self.ITEM_COLOR
        )

    def calculate_grid_dimensions(self, width, height, margin=0.1):
        # Calculate how many dots can fit in each dimension
        usable_width = width - (2 * margin)
        usable_height = height - (2 * margin)
        dots_per_row = int(usable_width / self.DOT_SPACING)
        rows = int(usable_height / self.DOT_SPACING)
        return dots_per_row, rows

    def get_blue_grid_position(self, index):
        dots_per_row, rows = self.calculate_grid_dimensions(
            self.QUEUE_WIDTH,
            self.QUEUE_HEIGHT
        )

        row = index // dots_per_row
        # Fill from right to left
        col = dots_per_row - 1 - (index % dots_per_row)

        # Calculate actual x,y coordinates
        x = self.queue_right - (self.DOT_SPACING * (dots_per_row - col))
        y = self.queue_top - self.DOT_SPACING - (row * self.DOT_SPACING)

        return np.array([x, y, 0])

    def get_active_grid_position(self, index):
        dots_per_row, rows = self.calculate_grid_dimensions(
            self.ACTIVE_WIDTH,
            self.QUEUE_HEIGHT
        )

        row = index // dots_per_row
        col = index % dots_per_row

        # Calculate actual x,y coordinates
        x = self.active_left + self.DOT_SPACING + (col * self.DOT_SPACING)
        y = self.queue_top - self.DOT_SPACING - (row * self.DOT_SPACING)

        return np.array([x, y, 0])

    def get_confirmed_position(self, index):
        x = self.active_right + self.DOT_SPACING + (index * self.DOT_SPACING)
        y = self.POSITION[1]  # Same height as queue center
        return np.array([x, y, 0])

    def initialize_state(self, scene, initial_queue=100, initial_active=60):
        # Calculate maximum capacity
        queue_dots_per_row, queue_rows = self.calculate_grid_dimensions(
            self.QUEUE_WIDTH,
            self.QUEUE_HEIGHT
        )
        active_dots_per_row, active_rows = self.calculate_grid_dimensions(
            self.ACTIVE_WIDTH,
            self.QUEUE_HEIGHT
        )

        queue_capacity = queue_dots_per_row * queue_rows
        active_capacity = active_dots_per_row * active_rows

        # Limit initial states to capacity
        initial_queue = min(initial_queue, queue_capacity)
        initial_active = min(initial_active, active_capacity)

        for i in range(initial_active):
            pos = self.get_active_grid_position(i)
            dot = self.create_dot(pos)
            self.active_dots.append(dot)
            scene.add(dot)

        for i in range(initial_queue):
            pos = self.get_blue_grid_position(i)
            dot = self.create_dot(pos)
            self.blue_dots.append(dot)
            scene.add(dot)

    def get_stream_animations(self, count, run_time=0.15, direct_to_active=False):
        animations = []
        for _ in range(count):
            start_pos = np.array([self.queue_left - 1, self.POSITION[1], 0])
            new_dot = self.create_dot(start_pos)

            if direct_to_active:
                # Go directly to active section
                final_pos = self.get_active_grid_position(
                    len(self.active_dots))
                self.active_dots.append(new_dot)
            else:
                # Go to blue queue
                final_pos = self.get_blue_grid_position(len(self.blue_dots))
                self.blue_dots.append(new_dot)

            animations.append(Create(new_dot, run_time=run_time))
            animations.append(new_dot.animate.move_to(
                final_pos).set_run_time(run_time))

        return animations

    def get_confirm_animations(self, run_time_confirm=0.3, run_time_replace=0.2):
        animations = []
        if len(self.active_dots) > 0:
            # Select random dot from active section
            random_index = np.random.randint(0, len(self.active_dots))
            dot_to_move = self.active_dots.pop(random_index)
            random_pos = dot_to_move.get_center()

            # Move to confirmed section
            confirmed_pos = self.get_confirmed_position(
                len(self.confirmed_dots))
            self.confirmed_dots.append(dot_to_move)
            animations.append(dot_to_move.animate.move_to(
                confirmed_pos).set_run_time(run_time_confirm))

            # If there are dots in blue section, move one to the vacated position
            if len(self.blue_dots) > 0:
                replacement_dot = self.blue_dots.pop(0)
                self.active_dots.insert(random_index, replacement_dot)
                animations.append(replacement_dot.animate.move_to(
                    random_pos).set_run_time(run_time_replace))
        elif len(self.blue_dots) > 0:
            # If no active dots, move from blue to active then confirm
            dot_to_move = self.blue_dots.pop(0)
            active_pos = self.get_active_grid_position(len(self.active_dots))
            self.active_dots.append(dot_to_move)
            animations.append(dot_to_move.animate.move_to(
                active_pos).set_run_time(run_time_replace))

            # Move to confirmed
            self.active_dots.remove(dot_to_move)
            confirmed_pos = self.get_confirmed_position(
                len(self.confirmed_dots))
            self.confirmed_dots.append(dot_to_move)
            animations.append(dot_to_move.animate.move_to(
                confirmed_pos).set_run_time(run_time_confirm))

        return animations


class MultiQueueScene(Scene):
    def construct(self):
        # Standard dimensions for all queues
        STANDARD_HEIGHT = 0.7
        STANDARD_QUEUE_WIDTH = 4
        STANDARD_ACTIVE_WIDTH = 2

        # Create three queues
        bucket1 = QueueSystem(
            queue_height=STANDARD_HEIGHT,
            queue_width=STANDARD_QUEUE_WIDTH,
            active_width=STANDARD_ACTIVE_WIDTH,
            item_color="#FF4444",
            position=UP * 1.5,
            left_label="<0.000001X"
        )

        bucket2 = QueueSystem(
            queue_height=STANDARD_HEIGHT,
            queue_width=STANDARD_QUEUE_WIDTH,
            active_width=STANDARD_ACTIVE_WIDTH,
            item_color="#FFAA44",
            queue_color=BLUE_B,
            position=ORIGIN,
            left_label="1X ... 3X"
        )

        bucket3 = QueueSystem(
            queue_height=STANDARD_HEIGHT,
            queue_width=STANDARD_QUEUE_WIDTH,
            active_width=STANDARD_ACTIVE_WIDTH,
            item_color="#44FF44",
            queue_color=BLUE_C,
            position=DOWN * 1.5,
            left_label="10X ... 30X"
        )

        # Define different initial states for each queue
        queue_configs = [
            (bucket1, 0, 0),    # High priority: lots of blocks
            (bucket2, 0, 0),     # Medium priority: empty
            (bucket3, 0, 0)         # Low priority: empty
        ]

        # Initialize all queues with their specific states
        for queue, initial_queue, initial_active in queue_configs:
            queue.create_containers(self)
            queue.initialize_state(self,
                                   initial_queue=initial_queue,
                                   initial_active=initial_active)

        # Calculate positions for global labels
        highest_queue_top = bucket1.queue_top
        active_section_right = bucket1.active_right

        # Create global labels
        priority_label = Text(
            "Blocks sorted by priority",
            font_size=24,
            color=BLUE
        ).move_to(
            [bucket1.queue_left + STANDARD_QUEUE_WIDTH/2,
             highest_queue_top + 0.5,
             0]
        )

        active_label = Text(
            "Active elections",
            font_size=24,
            color=YELLOW
        ).move_to(
            [active_section_right - STANDARD_ACTIVE_WIDTH/2,
             highest_queue_top + 0.5,
             0]
        )

        # Add global labels
        self.play(
            Write(priority_label),
            Write(active_label)
        )

        # Animation sequence with parallel actions
        self.wait(0.3)
        animations = []
        animations.extend(bucket1.get_stream_animations(
            30, run_time=0.01, direct_to_active=True))
        self.play(AnimationGroup(*animations, lag_ratio=0.1))

        animations = []
        animations.extend(bucket1.get_confirm_animations())
        self.play(AnimationGroup(*animations, lag_ratio=0.1))

        self.wait(0.3)
        animations = []
        animations.extend(bucket1.get_stream_animations(
            31, run_time=0.01, direct_to_active=True))
        animations.extend(bucket1.get_stream_animations(5, run_time=0.01))
        self.play(AnimationGroup(*animations, lag_ratio=0.1))

        animations = []
        animations.extend(bucket1.get_confirm_animations())
        self.play(AnimationGroup(*animations, lag_ratio=0.1))

        # First round of parallel actions
        animations = []
        animations.extend(bucket1.get_stream_animations(30, run_time=0.1))
        animations.extend(bucket2.get_stream_animations(
            1, direct_to_active=True))
        animations.extend(bucket3.get_stream_animations(
            1, direct_to_active=True))
        self.play(AnimationGroup(*animations, lag_ratio=0.1))

        # First round of parallel confirmations
        confirm_animations = []
        confirm_animations.extend(
            bucket1.get_stream_animations(5, run_time=0.1))
        confirm_animations.extend(bucket1.get_confirm_animations())
        confirm_animations.extend(bucket2.get_confirm_animations())
        confirm_animations.extend(bucket3.get_confirm_animations())
        self.play(AnimationGroup(*confirm_animations, lag_ratio=0.1))

        # Second round of parallel actions
        animations = []
        animations.extend(bucket1.get_stream_animations(5, run_time=0.1))
        animations.extend(bucket2.get_stream_animations(
            1, direct_to_active=True))
        animations.extend(bucket3.get_stream_animations(
            1, direct_to_active=True))
        self.play(AnimationGroup(*animations, lag_ratio=0.1))

        # Second round of parallel confirmations
        confirm_animations = []
        confirm_animations.extend(
            bucket1.get_stream_animations(3, run_time=0.1))
        confirm_animations.extend(bucket1.get_confirm_animations())
        confirm_animations.extend(bucket2.get_confirm_animations())
        confirm_animations.extend(bucket3.get_confirm_animations())
        self.play(AnimationGroup(*confirm_animations, lag_ratio=0.1))

        # Final round
        animations = []

        animations.extend(bucket1.get_stream_animations(5, run_time=0.1))
        animations.extend(bucket3.get_stream_animations(
            1, direct_to_active=True))
        self.play(AnimationGroup(*animations, lag_ratio=0.1))

        confirm_animations = []
        confirm_animations.extend(bucket1.get_confirm_animations())
        confirm_animations.extend(bucket3.get_confirm_animations())
        self.play(AnimationGroup(*confirm_animations, lag_ratio=0.1))

        self.wait(0.3)


# Rendering configuration
config.frame_rate = 30  # Set frame rate to 30 fps
config.renderer = "cairo"  # Use cairo renderer for better quality
config.output_file = "election_system.mp4"  # Set output filename
config.quality = "high_quality"  # Use high quality preset

if __name__ == "__main__":
    intro_scene = MultiQueueScene()
    intro_scene.render()
