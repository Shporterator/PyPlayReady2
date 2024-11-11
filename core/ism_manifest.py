import os
from xml.dom import minidom

class ISMManifest:
    class SmoothStreamingMedia:
        def __init__(self):
            self.attMajorVersion = None
            self.attMinorVersion = None
            self.attTimeScale = None
            self.attDuration = None

        def MajorVersion(self):
            return self.attMajorVersion

        def MinorVersion(self):
            return self.attMinorVersion

        def TimeScale(self):
            return self.attTimeScale

        def Duration(self):
            return self.attDuration

        def real_duration(self):
            duration = Utils.long_value(self.attDuration)
            timescale = Utils.long_value(self.attTimeScale)
            if duration < 0 or timescale < 0:
                return -1
            return duration // timescale

        def duration_str(self):
            return MP4File.duration_str(self.real_duration())

        def print(self):
            pp = PaddedPrinter.get_pp()
            pp.println("SmoothStreamingMedia")
            pp.pad(2, "")
            pp.println("MajorVersion: " + self.attMajorVersion)
            pp.println("MinorVersion: " + self.attMinorVersion)
            pp.println("TimeScale: " + self.attTimeScale)
            pp.println("Duration: " + self.attDuration + " [" + self.duration_str() + "]")
            pp.leave()

    class ProtectionHeader:
        def __init__(self):
            self.attSystemID = None
            self.data = None
            self.wrmhdr_data = None
            self.wrmhdr = None

        def SystemID(self):
            return self.attSystemID

        def data(self):
            return self.data

        def set_data(self, data):
            self.data = data
            self.wrmhdr_data = MSPR.wrmhdr_from_prothdr(data)
            self.wrmhdr = WRMHeader(self.wrmhdr_data.encode())

        def wrmhdr_data(self):
            return self.wrmhdr_data

        def wrmhdr(self):
            return self.wrmhdr

        def print(self):
            pp = PaddedPrinter.get_pp()
            pp.println("ProtectionHeader")
            pp.pad(2, "")
            pp.println("SystemID: " + self.attSystemID)
            self.wrmhdr.print()
            pp.leave()

    class QualityLevel:
        def __init__(self):
            self.attIndex = None
            self.attBitrate = None
            self.attFourCC = None
            self.attCodecPrivateData = None
            self.CodecPrivateData = None

        def Index(self):
            return self.attIndex

        def Bitrate(self):
            return self.attBitrate

        def FourCC(self):
            return self.attFourCC

        def CodecPrivateData(self):
            if self.CodecPrivateData is None:
                try:
                    self.CodecPrivateData = Utils.parse_hex_string(self.attCodecPrivateData)
                except Exception:
                    pass
            return self.CodecPrivateData

        def print(self):
            pp = PaddedPrinter.get_pp()
            pp.println("QualityLevel")
            pp.pad(2, "")
            pp.println("Index: " + self.attIndex)
            pp.println("Bitrate: " + self.attBitrate)
            pp.println("FourCC: " + self.attFourCC)
            pp.println("CodecPrivateData: " + self.attCodecPrivateData)
            pp.leave()

    class AudioQualityLevel(QualityLevel):
        def __init__(self):
            super().__init__()
            self.attSamplingRate = None
            self.attChannels = None
            self.attBitsPerSample = None
            self.attPacketSize = None
            self.attAudioTag = None

        def SamplingRate(self):
            return self.attSamplingRate

        def Channels(self):
            return self.attChannels

        def BitsPerSample(self):
            return self.attBitsPerSample

        def PacketSize(self):
            return self.attPacketSize

        def AudioTag(self):
            return self.attAudioTag

        def print(self):
            super().print()
            pp = PaddedPrinter.get_pp()
            pp.pad(2, "")
            pp.println("SamplingRate: " + self.attSamplingRate)
            pp.println("Channels: " + self.attChannels)
            pp.println("BitsPerSample: " + self.attBitsPerSample)
            pp.println("PacketSize: " + self.attPacketSize)
            pp.println("AudioTag: " + self.attAudioTag)
            pp.leave()

    class VideoQualityLevel(QualityLevel):
        def __init__(self):
            super().__init__()
            self.attMaxWidth = None
            self.attMaxHeight = None

        def MaxWidth(self):
            return self.attMaxWidth

        def MaxHeight(self):
            return self.attMaxHeight

        def print(self):
            super().print()
            pp = PaddedPrinter.get_pp()
            pp.pad(2, "")
            pp.println("MaxWidth: " + self.attMaxWidth)
            pp.println("MaxHeight: " + self.attMaxHeight)
            pp.leave()

    class Chunk:
        def __init__(self):
            self.attt = None
            self.attd = None
            self.start_time_val = -1

        def start_time(self):
            return self.attt

        def duration(self):
            return self.attd

        def start_time_val(self):
            return self.start_time_val if self.start_time_val >= 0 else Utils.long_value(self.attt)

        def set_start_time_val(self, val):
            self.start_time_val = val

        def duration_val(self):
            return Utils.long_value(self.attd) if self.attd else 0

        def print(self):
            pp = PaddedPrinter.get_pp()
            pp.pad(2, "")
            pp.println(f"Duration: {self.attd} StartTime: {self.attt if self.attt else ''}")
            pp.leave()

    class StreamIndex:
        def __init__(self):
            self.attType = None
            self.attName = None
            self.attTimeScale = None
            self.attChunks = None
            self.attQualityLevels = None
            self.attUrl = None
            self.qlevels = []
            self.chunks = []

        def Type(self):
            return self.attType

        def Name(self):
            return self.attName

        def TimeScale(self):
            return self.attTimeScale

        def Chunks(self):
            return self.attChunks

        def QualityLevels(self):
            return self.attQualityLevels

        def Url(self):
            return self.attUrl

        def timescale_val(self):
            return Utils.long_value(self.attTimeScale)

        def ql_cnt(self):
            return len(self.qlevels)

        def get_ql(self, i):
            return self.qlevels[i] if i < len(self.qlevels) else None

        def add_ql(self, ql):
            self.qlevels.append(ql)

        def chunk_cnt(self):
            return len(self.chunks)

        def get_chunk(self, i):
            return self.chunks[i] if i < len(self.chunks) else None

        def add_chunk(self, chunk):
            self.chunks.append(chunk)

        def print(self):
            pp = PaddedPrinter.get_pp()
            pp.println("StreamIndex")
            pp.pad(2, "")
            pp.println("Type: " + self.attType)
            pp.println("Name: " + self.attName)
            pp.println("TimeScale: " + self.attTimeScale)
            pp.println("Chunks: " + self.attChunks)
            pp.println("QualityLevels: " + self.attQualityLevels)
            pp.println("Url: " + self.attUrl)
            for ql in self.qlevels:
                pp.pad(2, "")
                ql.print()
                pp.leave()
            pp.leave()

    def __init__(self, path, data):
        self.path = path
        self.data = data
        self.root = XmlUtils.parse_xml(data)
        self.ssm = XmlUtils.instance_from_node(ISMManifest.SmoothStreamingMedia, XmlUtils.first_element(self.root, "SmoothStreamingMedia"))
        self.ph = XmlUtils.instance_from_node(ISMManifest.ProtectionHeader, XmlUtils.select_first(self.root, "SmoothStreamingMedia.Protection.ProtectionHeader"))
        if self.ph:
            xml_data = XmlUtils.get_value(XmlUtils.select_first(self.root, "SmoothStreamingMedia.Protection.ProtectionHeader"))
            if xml_data:
                self.ph.set_data(xml_data)

        self.streams = []
        for si_node in XmlUtils.select(self.root, "SmoothStreamingMedia.StreamIndex"):
            si = XmlUtils.instance_from_node(ISMManifest.StreamIndex, si_node)
            self.streams.append(si)
            for ql_node in XmlUtils.get_elements(si_node, "QualityLevel"):
                ql = XmlUtils.instance_from_node(
                    ISMManifest.AudioQualityLevel if si.Type() == "audio" else ISMManifest.VideoQualityLevel, ql_node
                )
                si.add_ql(ql)
            start_time = 0
            for ch_node in XmlUtils.get_elements(si_node, "c"):
                chunk = XmlUtils.instance_from_node(ISMManifest.Chunk, ch_node)
                chunk.set_start_time_val(start_time)
                si.add_chunk(chunk)
                start_time += chunk.duration_val()

    def get_wrmhdr_data(self):
        return self.ph.wrmhdr_data() if self.ph else None

    @staticmethod
    def from_file(path):
        data = Utils.load_file(path)
        if data:
            return ISMManifest(path, data)
        return None
