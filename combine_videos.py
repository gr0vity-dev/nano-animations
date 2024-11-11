from moviepy.editor import VideoFileClip, concatenate_videoclips


def combine_videos(video1_path: str, video2_path: str, output_path: str):
    """
    Combines two videos by concatenating them in sequence.

    Args:
        video1_path (str): Path to the first video file
        video2_path (str): Path to the second video file
        output_path (str): Path where the combined video will be saved
    """
    # Load the video clips
    clip1 = VideoFileClip(video1_path)
    clip2 = VideoFileClip(video2_path)

    # Combine the clips
    final_clip = concatenate_videoclips([clip1, clip2])

    # Write the result to a file
    final_clip.write_videofile(output_path)

    # Close the clips to free up system resources
    clip1.close()
    clip2.close()
    final_clip.close()


# Example usage
if __name__ == "__main__":
    # Replace these paths with your actual video paths
    combine_videos(
        "media/videos/1080p60/NanoIntroAnimation.mp4",
        "media/videos/1080p60/NanoFairQueueAnimation.mp4",
        "media/videos/1080p60/combined.mp4"
    )
