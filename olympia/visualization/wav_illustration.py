"""
This creates a 3D mesh with perlin noise to simulate
a terrain. The mesh is animated by shifting the noise
to give a "fly-over" effect.
If you don't have pyOpenGL or opensimplex, then:
    - conda install -c anaconda pyopengl
    - pip install opensimplex
"""

import numpy as np
from opensimplex import OpenSimplex
import pyqtgraph.opengl as gl
from qtpy import QtCore, QtWidgets, QtGui
from PIL import Image
import scipy.io.wavfile as wavfile
import struct
import pyaudio
import wave
import sys
import wavio


class Terrain(object):
    def __init__(self, filename):
        """
        Initialize the graphics window and mesh surface
        """

        # setup the view window
        self.app = QtGui.QApplication(sys.argv)
        self.window = gl.GLViewWidget()
        self.window.setWindowTitle("Terrain")
        self.window.setGeometry(0, 110, 1920, 1080)
        self.window.setCameraPosition(distance=50, elevation=12)
        self.window.show()
        self.images = []

        # constants and arrays
        self.nsteps = 1.3
        self.offset = 0
        self.ypoints = np.arange(-20, 20 + self.nsteps, self.nsteps)
        self.xpoints = np.arange(-20, 20 + self.nsteps, self.nsteps)
        self.nfaces = len(self.ypoints)

        self.RATE = 44100
        self.CHUNK = len(self.xpoints) * len(self.ypoints)
        # self.CHUNK = int(self.RATE * 0.01)
        # self.CHUNK = 16

        self.p = pyaudio.PyAudio()
        self.load_audio_data(filename)

        # self.stream = self.p.open(
        #    format=pyaudio.paInt16, channels=1, rate=self.RATE, input=True, output=True, frames_per_buffer=self.CHUNK,
        # )

        # perlin noise object
        self.noise = OpenSimplex()

        # create the veritices array
        verts, faces, colors = self.mesh()

        self.mesh1 = gl.GLMeshItem(
            faces=faces, vertexes=verts, faceColors=colors, drawEdges=True, smooth=False, edgeColor=(0, 0, 0, 1)
        )
        self.mesh1.setGLOptions("additive")
        self.window.addItem(self.mesh1)

    def load_audio_data(self, filename):
        self.wav = wave.open(filename, "rb")
        self.stream = self.p.open(
            format=self.p.get_format_from_width(self.wav.getsampwidth()),
            channels=self.wav.getnchannels(),
            rate=self.wav.getframerate(),
            output=True,
        )

        sizes = {1: "B", 2: "h", 3: "h", 4: "i"}

        self.wavio_file = wavio.read(wav_file)
        self.increment = 0

    #  channels = self.wav.getnchannels()

    #     breakpoint()

    #   self.fmt = "<{0}h".format(self.CHUNK * channels)

    def mesh(self, offset=0, height=2.5, wf_data=None):

        # decoded = struct.unpack(tmp_fmt, wav_r.readframes(tmp_size))
        if wf_data is not None:
            # wf_data = struct.unpack(">I", b"\000" + wf_data)
            wf_data = np.array(wf_data, dtype="b")[::2] + 128
            wf_data = np.array(wf_data, dtype="int32") - 128
            wf_data = wf_data * 0.04
            wf_data = wf_data.reshape((len(self.xpoints), len(self.ypoints)))
        else:
            wf_data = np.array([1] * 1024)
            wf_data = wf_data.reshape((len(self.xpoints), len(self.ypoints)))

        faces = []
        colors = []
        verts = np.array(
            [
                [x, y, wf_data[xid][yid] * self.noise.noise2d(x=xid / 5 + offset, y=yid / 5 + offset)]
                for xid, x in enumerate(self.xpoints)
                for yid, y in enumerate(self.ypoints)
            ],
            dtype=np.float32,
        )

        for yid in range(self.nfaces - 1):
            yoff = yid * self.nfaces
            for xid in range(self.nfaces - 1):
                faces.append(
                    [xid + yoff, xid + yoff + self.nfaces, xid + yoff + self.nfaces + 1,]
                )
                faces.append(
                    [xid + yoff, xid + yoff + 1, xid + yoff + self.nfaces + 1,]
                )
                colors.append([xid / self.nfaces, xid / self.nfaces, xid / self.nfaces, 0.8])
                colors.append([xid / self.nfaces, xid / self.nfaces, xid / self.nfaces, 0.8])

        faces = np.array(faces, dtype=np.uint32)
        colors = np.array(colors, dtype=np.float32)

        return verts, faces, colors

    def update(self):
        """
        update the mesh and shift the noise each time
        """

        wf_data = self.wav.readframes(self.CHUNK)

        if wf_data != "":
            self.stream.write(wf_data)

        data = self.wavio_file.data[self.increment : self.increment + self.CHUNK]
        self.increment = self.increment + self.CHUNK

        verts, faces, colors = self.mesh(offset=self.offset, wf_data=data)
        self.mesh1.setMeshData(vertexes=verts, faces=faces, faceColors=colors)
        self.offset -= 0.05

    def start(self):
        """
       get the graphics window open and setup
        """
        if (sys.flags.interactive != 1) or not hasattr(QtCore, "PYQT_VERSION"):
            QtGui.QApplication.instance().exec_()

    def animation(self, frametime=10):
        """
        calls the update method to run in a loop
        """
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(frametime)
        self.start()


if __name__ == "__main__":
    import os
    import wavio

    wav_file = os.getcwd() + "/olympia/files/olimpia.wav"
    t = Terrain(wav_file)
    t.animation()
