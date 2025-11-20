from .base_agent import BaseAgent
from pydub import AudioSegment, effects
import os

class AudioMixerAgent(BaseAgent):
    def __init__(self, llm_client):
        super().__init__("AudioMixerAgent", llm_client)

    def execute(self, context):
        self.log("Mixing final audio...")
        audio_path = context.get('audio_path')
        
        if not audio_path or not os.path.exists(audio_path):
            self.log("No audio found to mix.")
            return context

        # Load Audio
        try:
            speech = AudioSegment.from_file(audio_path)
            
            # 1. Normalization (Volume Leveling)
            self.log("Applying normalization...")
            speech = effects.normalize(speech)
            
            # 2. Silence Removal
            self.log("Removing silence...")
            
            def detect_leading_silence(sound, silence_threshold=-50.0, chunk_size=10):
                trim_ms = 0
                while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
                    trim_ms += chunk_size
                return trim_ms

            start_trim = detect_leading_silence(speech)
            end_trim = detect_leading_silence(speech.reverse())
            
            duration = len(speech)
            speech = speech[start_trim:duration-end_trim]
            
            # 3. Add Intro/Outro (Mocking by generating tones if files don't exist)
            intro = AudioSegment.silent(duration=2000) 
            outro = AudioSegment.silent(duration=2000)
            
            final_mix = intro + speech + outro
            
            # 4. Export to WAV (fallback for no ffmpeg)
            output_path = audio_path.replace(".wav", "_mixed.wav")
            final_mix.export(output_path, format="wav")
            
            context['final_audio_url'] = context.get('audio_url').replace(".wav", "_mixed.wav")
            self.log(f"Audio mixing complete. Saved to {output_path}")
            
        except Exception as e:
            self.log(f"Audio processing failed (likely missing ffmpeg): {e}. Returning original audio.")
            context['final_audio_url'] = context.get('audio_url')
            
        return context
