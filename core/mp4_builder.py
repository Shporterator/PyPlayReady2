from modules.utils import Utils

class MP4File:
    def __init__(self):
        # Initialize any required properties here
        pass
        
class MP4Builder:
    class StreamsDesc:
        AUDIO_STREAM_START = "audio="
        VIDEO_STREAM_START = "video="

        def __init__(self, audio_name, audio_quality, video_quality):
            self._audio_name = audio_name
            self._audio_quality = audio_quality
            self._video_quality = video_quality

        def audio_name(self):
            return self._audio_name

        def audio_quality(self):
            return self._audio_quality

        def video_quality(self):
            return self._video_quality

        @staticmethod
        def from_args(audio_desc, video_desc):
            """Constructs StreamsDesc from audio and video description strings."""
            if not audio_desc.startswith(MP4Builder.StreamsDesc.AUDIO_STREAM_START):
                return None
            audio_desc = audio_desc[len(MP4Builder.StreamsDesc.AUDIO_STREAM_START):]

            if not video_desc.startswith(MP4Builder.StreamsDesc.VIDEO_STREAM_START):
                return None
            video_desc = video_desc[len(MP4Builder.StreamsDesc.VIDEO_STREAM_START):]

            audio_params = Utils.tokenize(audio_desc, ".")
            if len(audio_params) != 2:
                return None

            return MP4Builder.StreamsDesc(audio_params[0], audio_params[1], video_desc)

    class TimeDesc:
        SECS_IN_HOURS = 3600
        SECS_IN_MINUTES = 60

        def __init__(self, start_time, duration):
            self._start_time = start_time
            self._duration = duration

        def start_time(self):
            return self._start_time

        def duration(self):
            return self._duration

        @staticmethod
        def parse_time_val(timeval):
            """Converts a string representing seconds to a long value, only if it's a valid range."""
            val = Utils.long_value(timeval)
            return val if 0 <= val < 60 else -1

        @staticmethod
        def parse_time(time_str):
            """Parses a time string formatted as [hh:[mm:]]ss to seconds."""
            if time_str == "":
                return 0

            time_params = Utils.tokenize(time_str, ":")
            hours, minutes, seconds = 0, 0, 0

            try:
                if len(time_params) == 1:
                    seconds = MP4Builder.TimeDesc.parse_time_val(time_params[0])
                elif len(time_params) == 2:
                    minutes = MP4Builder.TimeDesc.parse_time_val(time_params[0])
                    seconds = MP4Builder.TimeDesc.parse_time_val(time_params[1])
                elif len(time_params) == 3:
                    hours = MP4Builder.TimeDesc.parse_time_val(time_params[0])
                    minutes = MP4Builder.TimeDesc.parse_time_val(time_params[1])
                    seconds = MP4Builder.TimeDesc.parse_time_val(time_params[2])
                else:
                    return -1
            except Exception:
                return -1

            if hours < 0 or minutes < 0 or seconds < 0:
                return -1

            return hours * MP4Builder.TimeDesc.SECS_IN_HOURS + minutes * MP4Builder.TimeDesc.SECS_IN_MINUTES + seconds

        @staticmethod
        def from_arg(time_desc):
            """Constructs TimeDesc from a string in the format 'start_time+duration_time'."""
            time_params = Utils.tokenize(time_desc, "+")
            if not (1 <= len(time_params) <= 2):
                return None

            s_time = time_params[0] if len(time_params) >= 1 else "0"
            s_duration = time_params[1] if len(time_params) == 2 else "0"

            start_time = MP4Builder.TimeDesc.parse_time(s_time)
            duration = MP4Builder.TimeDesc.parse_time(s_duration)

            if start_time < 0 or duration < 0:
                return None

            return MP4Builder.TimeDesc(start_time, duration)
