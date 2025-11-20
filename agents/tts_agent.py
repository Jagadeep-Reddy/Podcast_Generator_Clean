from .base_agent import BaseAgent
import uuid
import os
from gtts import gTTS

class TTSAgent(BaseAgent):
    def __init__(self, llm_client, output_folder):
        super().__init__("TTSAgent", llm_client)
        self.output_folder = output_folder

    def execute(self, context):
        self.log("Converting script to audio...")
        script = context.get('script')
        
        # Real TTS using Google Text-to-Speech
        # Note: This requires an internet connection
        tts = gTTS(text=script, lang='en', slow=False)
        
        audio_id = str(uuid.uuid4())
        audio_filename = f"{audio_id}.mp3"
        output_path = os.path.join(self.output_folder, audio_filename)
        
        tts.save(output_path)
            
        context['audio_path'] = output_path
        context['audio_url'] = f"/outputs/{audio_filename}"
        self.log(f"Audio generated at {output_path}")
        return context
