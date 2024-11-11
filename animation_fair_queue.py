from manim import *
import random

# CONFIG remains the same as previous version
CONFIG = {
    'colors': {
        'background': "#20204C",
        'primary': "#F4FAFF",
        'accent': "#209CE9",
        'gray': "#6B7280",
        'peer_colors': ["#209CE9", "#4A90E2", "#67A9E8"],
    },
    'fonts': {
        'labels': "Open Sans",
    },
    'font_sizes': {
        'labels': 24,
        'processor': 24
    },
    'spacing': {
        'queue_height': 0.8,
        'queue_width': 4,
        'queue_spacing': 1.4,
        'processor_height': 4,
        'processor_width': 1.5,
        'left_offset': -4
    },
    'timing': {
        'process_priority': 0.2,
        'process_normal': 0.2,
        'new_block': 0.1,
        'initial_setup': 0.8,
        'highlight_duration': 0.3
    },
    'queue': {
        'spammer_size': 8,
        'dot_spacing': 0.4,
        # Different probabilities for each peer
        'new_block_probabilities': [0.6, 0.7, 0.8]
    },
    'highlight': {
        'normal_opacity': 0.1,
        'highlight_opacity': 0.3
    }
}


class NanoFairQueueAnimation(Scene):
    def construct(self):
        self.camera.background_color = CONFIG['colors']['background']
        self.current_highlighted = None

        # Setup queues and labels
        peer_queues = VGroup()
        queue_labels = VGroup()

        # Create spammer queue
        spammer_queue = Rectangle(
            height=CONFIG['spacing']['queue_height'],
            width=CONFIG['spacing']['queue_width'],
            color=CONFIG['colors']['gray'],
            fill_opacity=CONFIG['highlight']['normal_opacity']
        )
        spammer_queue.move_to(
            CONFIG['spacing']['left_offset'] * RIGHT + UP * 2.5)

        spammer_label = Text(
            "Spammer",
            font=CONFIG['fonts']['labels'],
            color=CONFIG['colors']['gray'],
            font_size=CONFIG['font_sizes']['labels']
        ).next_to(spammer_queue, UP, buff=0.2)

        # Create peer queues
        for i in range(3):
            queue = Rectangle(
                height=CONFIG['spacing']['queue_height'],
                width=CONFIG['spacing']['queue_width'],
                color=CONFIG['colors']['peer_colors'][i],
                fill_opacity=CONFIG['highlight']['normal_opacity']
            )
            queue.next_to(spammer_queue, DOWN,
                          buff=CONFIG['spacing']['queue_spacing'] * (i + 1))

            label = Text(
                f"Peer {i+1}",
                font=CONFIG['fonts']['labels'],
                color=CONFIG['colors']['peer_colors'][i],
                font_size=CONFIG['font_sizes']['labels']
            ).next_to(queue, UP, buff=0.2)

            peer_queues.add(queue)
            queue_labels.add(label)

        processor = Rectangle(
            height=CONFIG['spacing']['processor_height'],
            width=CONFIG['spacing']['processor_width'],
            color=CONFIG['colors']['primary'],
            fill_opacity=CONFIG['highlight']['normal_opacity']
        )
        processor.move_to(RIGHT * 1.5)

        processor_label = Text(
            "Fair\nQueue",
            font=CONFIG['fonts']['labels'],
            color=CONFIG['colors']['primary'],
            font_size=CONFIG['font_sizes']['processor']
        ).move_to(processor)

        # Initial setup animation
        self.play(
            *[Create(obj) for obj in [spammer_queue, *peer_queues, processor]],
            run_time=CONFIG['timing']['initial_setup']
        )
        self.play(
            *[Write(obj)
              for obj in [spammer_label, *queue_labels, processor_label]],
            run_time=CONFIG['timing']['initial_setup']
        )

        processed_dots = VGroup()
        next_processed_x = processor.get_right()[0] + 1

        # Create initial spammer messages from right to left
        spammer_dots = VGroup()
        for i in range(CONFIG['queue']['spammer_size']):
            x_pos = spammer_queue.get_left(
            )[0] + 0.5 + i * CONFIG['queue']['dot_spacing']
            dot = Dot(color=CONFIG['colors']['gray'], radius=0.08)
            dot.move_to([x_pos, spammer_queue.get_center()[1], 0])
            spammer_dots.add(dot)

        self.play(
            AnimationGroup(
                *[FadeIn(dot) for dot in spammer_dots],
                lag_ratio=0.05
            ),
            run_time=0.5
        )

        # Initialize each peer with exactly one transaction
        # Change to list of lists to support multiple dots per peer
        peer_dots = [[] for _ in range(3)]
        for i in range(3):
            dot = Dot(color=CONFIG['colors']['peer_colors'][i], radius=0.08)
            dot.move_to(peer_queues[i].get_right() + LEFT * 0.5)
            peer_dots[i].append(dot)
            self.play(FadeIn(dot), run_time=CONFIG['timing']['new_block'])

        def process_message(dot, queue, is_priority=False):
            self.play(
                dot.animate.move_to(processor.get_center()),
                run_time=CONFIG['timing']['process_priority'] if is_priority else CONFIG['timing']['process_normal']
            )

            nonlocal next_processed_x
            final_pos = np.array(
                [next_processed_x, processor.get_center()[1], 0])
            self.play(
                dot.animate.move_to(final_pos),
                run_time=CONFIG['timing']['process_priority']
            )

            next_processed_x += 0.25
            processed_dots.add(dot)

        def highlight_queue(queue):
            self.play(
                *[q.animate.set_fill(opacity=CONFIG['highlight']['normal_opacity'])
                  for q in [spammer_queue, *peer_queues]],
                run_time=CONFIG['timing']['highlight_duration'] / 2
            )
            self.play(
                queue.animate.set_fill(
                    opacity=CONFIG['highlight']['highlight_opacity']),
                run_time=CONFIG['timing']['highlight_duration'] / 2
            )
            self.current_highlighted = queue

        def unhighlight_all():
            self.play(
                *[q.animate.set_fill(opacity=CONFIG['highlight']['normal_opacity'])
                  for q in [spammer_queue, *peer_queues]],
                run_time=CONFIG['timing']['highlight_duration'] / 2
            )
            self.current_highlighted = None

        def add_blocks(peer_dots):
            # Add new transactions with different probabilities for each peer
            for i in range(len(peer_dots)):
                if random.random() < CONFIG['queue']['new_block_probabilities'][i]:
                    dot = Dot(color=CONFIG['colors']
                              ['peer_colors'][i], radius=0.08)
                    x_pos = peer_queues[i].get_right(
                    )[0] - 0.5 - len(peer_dots[i]) * CONFIG['queue']['dot_spacing']
                    dot.move_to([x_pos, peer_queues[i].get_center()[1], 0])
                    peer_dots[i].append(dot)
                    self.play(
                        FadeIn(dot), run_time=CONFIG['timing']['new_block'])

        # Processing loop with round-robin highlighting including spammer
        for round in range(3):  # Number of complete rounds
            # Process all peers
            for i in range(3):  # Process peers 1, 2, and 3
                highlight_queue(peer_queues[i])

                if peer_dots[i]:  # If peer has any dots
                    dot_to_process = peer_dots[i].pop(0)  # Take the first dot
                    process_message(
                        dot_to_process, peer_queues[i], is_priority=True)
                else:
                    # Small pause to show we're checking this empty queue
                    self.wait(CONFIG['timing']['highlight_duration'])

            # Process spammer only in first two rounds
            if round < 2:
                highlight_queue(spammer_queue)

                # Add new transactions with different probabilities for each peer
                add_blocks(peer_dots)

                if len(spammer_dots) > 0:
                    leftmost_dot = spammer_dots[0]
                    process_message(leftmost_dot, spammer_queue)
                    spammer_dots.remove(leftmost_dot)

                    # Add new spammer dot at the right end
                    new_dot = Dot(color=CONFIG['colors']['gray'], radius=0.08)
                    x_pos = spammer_queue.get_left(
                    )[0] + 0.5 + (len(spammer_dots)) * CONFIG['queue']['dot_spacing']
                    new_dot.move_to([x_pos, spammer_queue.get_center()[1], 0])
                    spammer_dots.add(new_dot)
                    self.play(FadeIn(new_dot),
                              run_time=CONFIG['timing']['new_block'])

                # Only add new transactions after first two complete rounds
                unhighlight_all()

        # Fade out all elements
        self.wait(0.5)
        self.play(
            *[FadeOut(mob, shift=UP * 0.3) for mob in self.mobjects],
            run_time=0.5
        )


if __name__ == "__main__":
    scene = NanoFairQueueAnimation()
    scene.render()
