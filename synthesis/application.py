import sys
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QComboBox, QSlider, QVBoxLayout, QDoubleSpinBox
from pydub.audio_segment import AudioSegment
from pydub.generators import Sine, Sawtooth, Square, WhiteNoise
from pydub.playback import play


class SoundGeneratorApp(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize default values
        self.frequency = 440  # Default frequency: 440 Hz
        self.waveform = 'sine'  # Default waveform: sine
        self.adsr_params = {'attack': 0.1, 'decay': 0.2, 'sustain': 0.5, 'release': 0.3}

        # Initialize UI
        self.init_ui()

    def init_ui(self):
        # UI components
        play_button = QPushButton('Play', self)
        play_button.clicked.connect(self.play_sound)

        export_button = QPushButton('Export', self)
        export_button.clicked.connect(self.export_sound)

        waveform_label = QLabel('Waveform:', self)
        self.waveform_combobox = QComboBox(self)
        self.waveform_combobox.addItems(['sine', 'sawtooth', 'square', 'white noise'])
        self.waveform_combobox.currentIndexChanged.connect(self.update_waveform)

        frequency_label = QLabel('Frequency (Hz):', self)
        self.frequency_slider = QSlider(Qt.Horizontal)
        self.frequency_slider.setRange(50, 1000)
        self.frequency_slider.setValue(self.frequency)
        self.frequency_slider.valueChanged.connect(self.update_frequency)

        adsr_label = QLabel('ADSR Parameters:', self)

        attack_label = QLabel('Attack:', self)
        self.attack_spinbox = QDoubleSpinBox(self)
        self.attack_spinbox.setRange(0, 10)
        self.attack_spinbox.setSingleStep(0.1)
        self.attack_spinbox.setValue(self.adsr_params['attack'])
        self.attack_spinbox.valueChanged.connect(self.update_adsr_params)

        decay_label = QLabel('Decay:', self)
        self.decay_spinbox = QDoubleSpinBox(self)
        self.decay_spinbox.setRange(0, 10)
        self.decay_spinbox.setSingleStep(0.1)
        self.decay_spinbox.setValue(self.adsr_params['decay'])
        self.decay_spinbox.valueChanged.connect(self.update_adsr_params)

        sustain_label = QLabel('Sustain:', self)
        self.sustain_spinbox = QDoubleSpinBox(self)
        self.sustain_spinbox.setRange(0, 1)
        self.sustain_spinbox.setSingleStep(0.1)
        self.sustain_spinbox.setValue(self.adsr_params['sustain'])
        self.sustain_spinbox.valueChanged.connect(self.update_adsr_params)

        release_label = QLabel('Release:', self)
        self.release_spinbox = QDoubleSpinBox(self)
        self.release_spinbox.setRange(0, 10)
        self.release_spinbox.setSingleStep(0.1)
        self.release_spinbox.setValue(self.adsr_params['release'])
        self.release_spinbox.valueChanged.connect(self.update_adsr_params)

        # Layout
        layout = QVBoxLayout()

        layout.addWidget(play_button)

        layout.addWidget(waveform_label)
        layout.addWidget(self.waveform_combobox)

        layout.addWidget(frequency_label)
        layout.addWidget(self.frequency_slider)

        layout.addWidget(adsr_label)

        adsr_layout = QVBoxLayout()
        adsr_layout.addWidget(attack_label)
        adsr_layout.addWidget(self.attack_spinbox)

        adsr_layout.addWidget(decay_label)
        adsr_layout.addWidget(self.decay_spinbox)

        adsr_layout.addWidget(sustain_label)
        adsr_layout.addWidget(self.sustain_spinbox)

        adsr_layout.addWidget(release_label)
        adsr_layout.addWidget(self.release_spinbox)

        layout.addLayout(adsr_layout)

        self.setLayout(layout)

        # Set window properties
        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle('Sound Generator')
        self.show()

    def gen_sound(self):
        duration = 1  # Play the sound for 2 seconds

        # Generate a waveform based on the selected options
        if self.waveform == 'sine':
            sound = Sine(self.frequency).to_audio_segment()
        elif self.waveform == 'sawtooth':
            sound = Sawtooth(self.frequency).to_audio_segment()
        elif self.waveform == 'square':
            sound = Square(self.frequency).to_audio_segment()
        elif self.waveform == 'white noise':
            sound = WhiteNoise().to_audio_segment()
        try:
            # Apply ADSR envelope
            sound_with_envelope = self.apply_envelope(sound)
            return sound_with_envelope
        except Exception as e:
            print(e)

    def play_sound(self):
        play(self.gen_sound())

    def _generate_adsr_envelope(self, duration):
        total_samples = int(duration * 44100)

        # Attack phase
        attack_samples = int(self.adsr_params['attack'] * 44100)
        attack = np.linspace(0, 1, min(attack_samples, total_samples))

        # Decay phase
        decay_samples = int(self.adsr_params['decay'] * 44100)
        decay = np.linspace(1, self.adsr_params['sustain'], min(decay_samples, total_samples - len(attack)))

        # Sustain phase
        sustain_samples = total_samples - len(attack) - len(decay)
        sustain = np.full(sustain_samples, self.adsr_params['sustain'])

        # Release phase
        release_samples = int(self.adsr_params['release'] * 44100)
        release = np.linspace(self.adsr_params['sustain'], 0, min(release_samples, sustain_samples))

        # Combine all phases
        envelope = np.concatenate((attack, decay, sustain, release))

        return envelope[:total_samples]

    def apply_envelope(self, audio_segment, amp=0.8):
        audio_data = np.array(audio_segment.get_array_of_samples())
        duration = len(audio_data) / 44100

        envelope = self._generate_adsr_envelope(duration)

        # Apply ADSR envelope to the audio data as changes in gain
        audio_with_envelope = np.multiply(audio_data, envelope)

        # Create a new AudioSegment with the modified audio data
        modified_audio_segment = AudioSegment(
            audio_with_envelope.astype(np.int16).tobytes(),
            frame_rate=44100,
            sample_width=2,  # 16-bit audio
            channels=1  # Mono audio
        )

        return modified_audio_segment

    def export_sound(self):
        self.gen_sound().export("output.wav", format="wav")

    def update_waveform(self, index):
        waveforms = ['sine', 'sawtooth', 'square', 'white noise']
        self.waveform = waveforms[index]

    def update_frequency(self, value):
        self.frequency = value

    def update_adsr_params(self):
        self.adsr_params['attack'] = self.attack_spinbox.value()
        self.adsr_params['decay'] = self.decay_spinbox.value()
        self.adsr_params['sustain'] = self.sustain_spinbox.value()
        self.adsr_params['release'] = self.release_spinbox.value()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sound_generator = SoundGeneratorApp()
    sys.exit(app.exec_())
