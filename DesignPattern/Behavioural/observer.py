from abc import ABC, abstractmethod
from typing import List, Set

class Observer(ABC):
    """Used by all the observers who subscribed to youtube
            like Users, Applications"""
    @abstractmethod
    def observe(self, video_name: str) -> str:
        pass

    @abstractmethod
    def get_id(self) -> int:
        pass

class Youtube(ABC):
    @abstractmethod
    def subscribe(self, observer: Observer) -> str:
        pass

    @abstractmethod
    def unsubscribe(self, observer: Observer) -> str:
        pass

    @abstractmethod
    def notify_subscribers(self, video_name: str) -> None:
        pass

    @abstractmethod
    def upload_video(self, video_name: str) -> str:
        pass

class YoutubeChannel(Youtube):
    def __init__(self):
        self.subscribers: Set[Observer] = set()

    def subscribe(self, observer: Observer) -> str:
        self.subscribers.add(observer)
        return f"Subscriber added: {observer.get_id()}"

    def unsubscribe(self, observer: Observer) -> str:
        self.subscribers.remove(observer)
        return f"Subscriber removed: {observer.get_id()}"

    def notify_subscribers(self, video_name: str) -> None:
        for subscriber in self.subscribers:
            print(subscriber.observe(video_name))

    def upload_video(self, video_name: str) -> str:
        self.notify_subscribers(video_name)
        return f"Video {video_name} uploaded"

class User(Observer):
    def __init__(self, id: int):
        self.id = id

    def observe(self, video_name: str) -> str:
        return f"User with id: {self.id} got observed with video: {video_name}"

    def get_id(self) -> int:
        return self.id

class Application(Observer):
    def __init__(self, id: int):
        self.id = id

    def observe(self, video_name: str) -> str:
        return f"API with id: {self.id} got observed with video: {video_name}"

    def get_id(self) -> int:
        return self.id


def main():
    user = User(1)
    application = Application(2)
    youtube = YoutubeChannel()
    print(youtube.subscribe(user))
    print(youtube.subscribe(application))
    print(youtube.upload_video("video1"))
    print(youtube.unsubscribe(user))

if __name__ == "__main__":
    main()