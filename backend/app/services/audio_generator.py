"""
Advanced Audio Generation System
Multiple synthesis methods for comprehensive audio testing
"""

import numpy as np
import io
from typing import Literal, Dict, Any, List, Optional
import logging
import struct
import wave

logger = logging.getLogger(__name__)


class AudioSynthesizer:
    """Multi-dimensional audio synthesis"""

    # ========================================================================
    # OSCILLATORS (Basic Waveforms)
    # ========================================================================

    @staticmethod
    def sine_wave(frequency: float, duration: float, sample_rate: int = 44100,
                  amplitude: float = 0.5) -> np.ndarray:
        """Pure sine wave"""
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        wave = amplitude * np.sin(2 * np.pi * frequency * t)
        return wave

    @staticmethod
    def square_wave(frequency: float, duration: float, sample_rate: int = 44100,
                    amplitude: float = 0.5, duty_cycle: float = 0.5) -> np.ndarray:
        """Square wave with adjustable duty cycle"""
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        wave = amplitude * np.sign(np.sin(2 * np.pi * frequency * t) - (1 - 2 * duty_cycle))
        return wave

    @staticmethod
    def sawtooth_wave(frequency: float, duration: float, sample_rate: int = 44100,
                     amplitude: float = 0.5) -> np.ndarray:
        """Sawtooth wave"""
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        wave = amplitude * 2 * (t * frequency - np.floor(t * frequency + 0.5))
        return wave

    @staticmethod
    def triangle_wave(frequency: float, duration: float, sample_rate: int = 44100,
                     amplitude: float = 0.5) -> np.ndarray:
        """Triangle wave"""
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        wave = amplitude * 2 * np.abs(2 * (t * frequency - np.floor(t * frequency + 0.5))) - amplitude
        return wave

    @staticmethod
    def pulse_wave(frequency: float, duration: float, sample_rate: int = 44100,
                   amplitude: float = 0.5, width: float = 0.5) -> np.ndarray:
        """Pulse wave (variable width square wave)"""
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        phase = (t * frequency) % 1
        wave = amplitude * ((phase < width).astype(float) * 2 - 1)
        return wave

    # ========================================================================
    # NOISE GENERATORS
    # ========================================================================

    @staticmethod
    def white_noise(duration: float, sample_rate: int = 44100,
                   amplitude: float = 0.3) -> np.ndarray:
        """White noise (all frequencies equal)"""
        samples = int(sample_rate * duration)
        return amplitude * (np.random.random(samples) * 2 - 1)

    @staticmethod
    def pink_noise(duration: float, sample_rate: int = 44100,
                   amplitude: float = 0.3) -> np.ndarray:
        """Pink noise (1/f noise)"""
        samples = int(sample_rate * duration)
        white = np.random.random(samples) * 2 - 1

        # Simple pink noise filter
        b = np.array([0.049922035, -0.095993537, 0.050612699, -0.004408786])
        a = np.array([1, -2.494956002, 2.017265875, -0.522189400])

        pink = np.zeros(samples)
        for i in range(4, samples):
            pink[i] = (white[i] * b[0] + white[i-1] * b[1] +
                      white[i-2] * b[2] + white[i-3] * b[3] -
                      pink[i-1] * a[1] - pink[i-2] * a[2] - pink[i-3] * a[3])

        # Normalize
        pink = pink / np.max(np.abs(pink)) * amplitude
        return pink

    @staticmethod
    def brown_noise(duration: float, sample_rate: int = 44100,
                    amplitude: float = 0.3) -> np.ndarray:
        """Brown noise (random walk)"""
        samples = int(sample_rate * duration)
        white = np.random.random(samples) * 2 - 1
        brown = np.cumsum(white)
        # Normalize
        brown = brown / np.max(np.abs(brown)) * amplitude
        return brown

    # ========================================================================
    # SYNTHESIS METHODS
    # ========================================================================

    @staticmethod
    def fm_synthesis(carrier_freq: float, modulator_freq: float, mod_index: float,
                    duration: float, sample_rate: int = 44100,
                    amplitude: float = 0.5) -> np.ndarray:
        """Frequency Modulation synthesis"""
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        modulator = np.sin(2 * np.pi * modulator_freq * t)
        carrier = amplitude * np.sin(2 * np.pi * carrier_freq * t + mod_index * modulator)
        return carrier

    @staticmethod
    def am_synthesis(carrier_freq: float, modulator_freq: float,
                    duration: float, sample_rate: int = 44100,
                    amplitude: float = 0.5) -> np.ndarray:
        """Amplitude Modulation synthesis"""
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        modulator = 0.5 * (1 + np.sin(2 * np.pi * modulator_freq * t))
        carrier = amplitude * np.sin(2 * np.pi * carrier_freq * t) * modulator
        return carrier

    @staticmethod
    def additive_synthesis(frequencies: List[float], amplitudes: List[float],
                          duration: float, sample_rate: int = 44100) -> np.ndarray:
        """Additive synthesis (sum of sine waves)"""
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        wave = np.zeros_like(t)

        for freq, amp in zip(frequencies, amplitudes):
            wave += amp * np.sin(2 * np.pi * freq * t)

        # Normalize
        wave = wave / np.max(np.abs(wave)) * 0.7
        return wave

    @staticmethod
    def chord(frequencies: List[float], duration: float,
             sample_rate: int = 44100, amplitude: float = 0.5) -> np.ndarray:
        """Generate a chord (multiple frequencies)"""
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        wave = np.zeros_like(t)

        for freq in frequencies:
            wave += np.sin(2 * np.pi * freq * t)

        # Normalize
        wave = wave / len(frequencies) * amplitude
        return wave

    # ========================================================================
    # ENVELOPES
    # ========================================================================

    @staticmethod
    def adsr_envelope(attack: float, decay: float, sustain_level: float,
                     sustain: float, release: float,
                     sample_rate: int = 44100) -> np.ndarray:
        """ADSR (Attack, Decay, Sustain, Release) envelope"""
        attack_samples = int(attack * sample_rate)
        decay_samples = int(decay * sample_rate)
        sustain_samples = int(sustain * sample_rate)
        release_samples = int(release * sample_rate)

        # Attack
        env_attack = np.linspace(0, 1, attack_samples)
        # Decay
        env_decay = np.linspace(1, sustain_level, decay_samples)
        # Sustain
        env_sustain = np.ones(sustain_samples) * sustain_level
        # Release
        env_release = np.linspace(sustain_level, 0, release_samples)

        envelope = np.concatenate([env_attack, env_decay, env_sustain, env_release])
        return envelope

    @staticmethod
    def apply_envelope(wave: np.ndarray, envelope: np.ndarray) -> np.ndarray:
        """Apply envelope to waveform"""
        # Match lengths
        min_len = min(len(wave), len(envelope))
        return wave[:min_len] * envelope[:min_len]

    # ========================================================================
    # EFFECTS
    # ========================================================================

    @staticmethod
    def tremolo(wave: np.ndarray, rate: float, depth: float = 0.5,
               sample_rate: int = 44100) -> np.ndarray:
        """Tremolo effect (amplitude modulation)"""
        t = np.arange(len(wave)) / sample_rate
        modulator = 1 - depth * (1 + np.sin(2 * np.pi * rate * t)) / 2
        return wave * modulator

    @staticmethod
    def vibrato(wave: np.ndarray, rate: float, depth: float = 0.01,
               sample_rate: int = 44100) -> np.ndarray:
        """Vibrato effect (frequency modulation)"""
        t = np.arange(len(wave)) / sample_rate
        modulation = depth * np.sin(2 * np.pi * rate * t)

        # Apply frequency modulation
        indices = np.arange(len(wave)) + modulation * sample_rate
        indices = indices.clip(0, len(wave) - 1).astype(int)
        return wave[indices]

    @staticmethod
    def echo(wave: np.ndarray, delay: float, decay: float = 0.5,
            sample_rate: int = 44100, num_echoes: int = 3) -> np.ndarray:
        """Echo effect"""
        delay_samples = int(delay * sample_rate)
        output = wave.copy()

        for i in range(1, num_echoes + 1):
            delayed = np.zeros_like(wave)
            start_idx = delay_samples * i
            if start_idx < len(wave):
                delayed[start_idx:] = wave[:-start_idx] * (decay ** i)
                output += delayed

        # Normalize
        output = output / np.max(np.abs(output)) * 0.9
        return output

    # ========================================================================
    # COMPLEX SOUNDS
    # ========================================================================

    @staticmethod
    def drum_kick(duration: float = 0.5, sample_rate: int = 44100) -> np.ndarray:
        """Synthesized kick drum"""
        t = np.linspace(0, duration, int(sample_rate * duration), False)

        # Frequency sweep from 150Hz to 40Hz
        freq_start, freq_end = 150, 40
        freq_sweep = freq_start + (freq_end - freq_start) * t / duration

        # Sine wave with frequency sweep
        phase = 2 * np.pi * np.cumsum(freq_sweep) / sample_rate
        wave = np.sin(phase)

        # Sharp attack, quick decay envelope
        envelope = np.exp(-t * 15)
        return wave * envelope * 0.8

    @staticmethod
    def drum_snare(duration: float = 0.3, sample_rate: int = 44100) -> np.ndarray:
        """Synthesized snare drum"""
        t = np.linspace(0, duration, int(sample_rate * duration), False)

        # Tonal component (200Hz)
        tonal = 0.3 * np.sin(2 * np.pi * 200 * t)

        # Noise component
        noise = 0.7 * (np.random.random(len(t)) * 2 - 1)

        # Combined
        wave = tonal + noise

        # Quick decay envelope
        envelope = np.exp(-t * 20)
        return wave * envelope * 0.6

    @staticmethod
    def sweep(start_freq: float, end_freq: float, duration: float,
             sample_rate: int = 44100, sweep_type: str = 'linear') -> np.ndarray:
        """Frequency sweep"""
        t = np.linspace(0, duration, int(sample_rate * duration), False)

        if sweep_type == 'linear':
            freq = start_freq + (end_freq - start_freq) * t / duration
        elif sweep_type == 'exponential':
            freq = start_freq * (end_freq / start_freq) ** (t / duration)
        else:
            freq = start_freq + (end_freq - start_freq) * t / duration

        phase = 2 * np.pi * np.cumsum(freq) / sample_rate
        return 0.5 * np.sin(phase)


class AdvancedAudioGenerator:
    """High-level audio generation with multiple methods"""

    @staticmethod
    def generate_audio(audio_type: str, duration: float, sample_rate: int = 44100,
                      **params) -> np.ndarray:
        """Universal audio generator"""
        synth = AudioSynthesizer()

        # Oscillators
        if audio_type == 'sine':
            return synth.sine_wave(params.get('frequency', 440), duration, sample_rate,
                                  params.get('amplitude', 0.5))
        elif audio_type == 'square':
            return synth.square_wave(params.get('frequency', 440), duration, sample_rate,
                                    params.get('amplitude', 0.5))
        elif audio_type == 'sawtooth':
            return synth.sawtooth_wave(params.get('frequency', 440), duration, sample_rate,
                                      params.get('amplitude', 0.5))
        elif audio_type == 'triangle':
            return synth.triangle_wave(params.get('frequency', 440), duration, sample_rate,
                                      params.get('amplitude', 0.5))

        # Noise
        elif audio_type == 'white_noise':
            return synth.white_noise(duration, sample_rate, params.get('amplitude', 0.3))
        elif audio_type == 'pink_noise':
            return synth.pink_noise(duration, sample_rate, params.get('amplitude', 0.3))
        elif audio_type == 'brown_noise':
            return synth.brown_noise(duration, sample_rate, params.get('amplitude', 0.3))

        # Synthesis
        elif audio_type == 'fm':
            return synth.fm_synthesis(
                params.get('carrier_freq', 440),
                params.get('modulator_freq', 220),
                params.get('mod_index', 2),
                duration, sample_rate
            )
        elif audio_type == 'am':
            return synth.am_synthesis(
                params.get('carrier_freq', 440),
                params.get('modulator_freq', 5),
                duration, sample_rate
            )

        # Complex sounds
        elif audio_type == 'kick':
            return synth.drum_kick(duration, sample_rate)
        elif audio_type == 'snare':
            return synth.drum_snare(duration, sample_rate)
        elif audio_type == 'sweep':
            return synth.sweep(
                params.get('start_freq', 20),
                params.get('end_freq', 20000),
                duration, sample_rate
            )

        # Default
        return synth.sine_wave(440, duration, sample_rate)

    @staticmethod
    def to_wav_bytes(audio_data: np.ndarray, sample_rate: int = 44100,
                    bit_depth: int = 16, channels: int = 1) -> bytes:
        """Convert audio numpy array to WAV bytes"""
        # Normalize to int16 range
        if bit_depth == 16:
            audio_int = (audio_data * 32767).astype(np.int16)
        elif bit_depth == 24:
            audio_int = (audio_data * 8388607).astype(np.int32)
        elif bit_depth == 32:
            audio_int = (audio_data * 2147483647).astype(np.int32)
        else:
            audio_int = (audio_data * 32767).astype(np.int16)

        # Create WAV file in memory
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(bit_depth // 8)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_int.tobytes())

        return wav_buffer.getvalue()
