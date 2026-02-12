from abc import ABC, abstractmethod

class VideoProcessor(ABC):
    @abstractmethod
    def process_video(self, video_name: str) -> str:
        pass

class HDVideoProcessor(VideoProcessor):
    def process_video(self, video_name: str) -> str:
        return f"Processed HD Video for video: {video_name}"

class  FourKVideoProcessor(VideoProcessor):
    def process_video(self, video_name: str) -> str:
        return f"Processed 4k Video for video: {video_name}"

# Create classes for HD and 4K videos

class VideoPlayer(ABC):
    def __init__(self, processor: VideoProcessor):
        self.processor = processor

    @abstractmethod
    def play_video(self, video_name: str) -> str:
        pass

class YoutubeVideoPlayer(VideoPlayer):
    def __init__(self, processor: VideoProcessor):
        super().__init__(processor)

    def play_video(self, video_name: str) -> str:
        print(self.processor.process_video(video_name))
        return f"Youtube Played video: {video_name} Successfully"

class NetflixVideoPlayer(VideoPlayer):
    def __init__(self, processor: VideoProcessor):
        super().__init__(processor)

    def play_video(self, video_name: str) -> str:
        print(self.processor.process_video(video_name))
        return f"Netflix Played video: {video_name} Successfully"

if __name__ == '__main__':
    hd_processor = HDVideoProcessor()
    youtube_player = YoutubeVideoPlayer(hd_processor)
    print(youtube_player.play_video("Samajavaragamana Song"))