import json
import os
from typing import Dict, List, Optional
from enum import Enum
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
from .prompts import SYSTEM_PROMPTS, get_audio_planning_prompt
import random
from pydub import AudioSegment
import openai
from .utils.logger import Logger

class AudioType(Enum):
    BACKGROUND_MUSIC = "background_music"
    SOUND_EFFECT = "sound_effect"
    NARRATION = "narration"

class AudioGenerator:
    def __init__(self):
        self.audio_dir = "data/audio"
        os.makedirs(self.audio_dir, exist_ok=True)
        self._setup_llm()
        self._setup_tts()
        self.logger = Logger()
    
    def _setup_llm(self):
        """LLM 연결을 설정합니다."""
        # Load environment variables from .env file in project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        load_dotenv(os.path.join(project_root, '.env'))
        
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError(
                "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable "
                "in your .env file or system environment variables."
            )
        
        self.client = openai.OpenAI()
    
    def _setup_tts(self):
        """TTS 연결을 설정합니다."""
        # Load environment variables from .env file in project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        load_dotenv(os.path.join(project_root, '.env'))
        
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise ValueError(
                "ElevenLabs API key not found. Please set the ELEVENLABS_API_KEY environment variable "
                "in your .env file or system environment variables."
            )
        
        self.tts_client = ElevenLabs(api_key=api_key)
    
    def generate_audio_assets(self, script: Dict, target_audience: str, mood: str) -> List[Dict]:
        """스크립트에 맞는 오디오 에셋을 생성합니다."""
        self.logger.section("오디오 에셋 생성 시작")
        self.logger.info(f"대상: {target_audience}")
        self.logger.info(f"분위기: {mood}")
        
        try:
            # 새로운 오디오 에셋 생성
            audio_assets = []
            
            # 오디오 생성 프롬프트 생성
            prompt = get_audio_planning_prompt(
                script=json.dumps(script, ensure_ascii=False),
                target_audience=target_audience,
                mood=mood
            )
            
            # 프롬프트 출력
            self.logger.subsection("프롬프트")
            self.logger.info(f"시스템 프롬프트: {SYSTEM_PROMPTS['audio_engineer']}")
            self.logger.info(f"사용자 프롬프트: {prompt}")
            
            # LLM을 사용하여 오디오 계획 생성
            self.logger.process("GPT-4에게 요청 중...")
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPTS["audio_engineer"]},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # 응답 출력
            self.logger.subsection("생성된 오디오 계획")
            self.logger.info(response.choices[0].message.content)
            
            # 각 섹션에 대한 오디오 생성
            sections = [script["hook"]] + script["main_points"] + [script["conclusion"]]
            
            for section in sections:
                self.logger.process(f"오디오 생성 중... (텍스트: {section['script']})")
                audio_path = self._generate_voice(section["script"])
                
                audio_assets.append({
                    "type": "voice",
                    "content": audio_path,
                    "timing": 0.0,
                    "duration": section["duration_seconds"],
                    "source_type": "tts",
                    "metadata": {
                        "generation_type": "tts",
                        "text": section["script"]
                    }
                })
            
            self.logger.success("오디오 에셋 생성 완료")
            return audio_assets
            
        except Exception as e:
            self.logger.error(f"오디오 에셋 생성 중 오류 발생: {str(e)}")
            return self._generate_dummy_audio()
    
    def _generate_audio_plan(self, script: Dict) -> Dict:
        """오디오 계획을 생성합니다."""
        prompt = get_audio_planning_prompt(
            script=json.dumps(script, ensure_ascii=False),
            target_audience="general",  # TODO: 스크립트에서 가져오기
            mood="energetic"  # TODO: 스크립트에서 가져오기
        )
        
        # 프롬프트 출력
        self.logger.subsection("프롬프트")
        self.logger.info(f"시스템 프롬프트: {SYSTEM_PROMPTS['audio_engineer']}")
        self.logger.info(f"사용자 프롬프트: {prompt}")
        
        # LLM 응답 받기
        self.logger.process("GPT-4에게 요청 중...")
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS["audio_engineer"]},
                {"role": "user", "content": prompt}
            ]
        )
        
        # 응답 출력
        self.logger.subsection("생성된 오디오 계획")
        self.logger.info(response.choices[0].message.content)
        
        return self._parse_audio_plan(response.choices[0].message.content)
    
    def _parse_audio_plan(self, response: str) -> Dict:
        """LLM 응답을 구조화된 형식으로 변환합니다."""
        sections = response.split("\n\n")
        audio_plan = {
            "background_music": sections[0] if len(sections) > 0 else "",
            "sound_effects": sections[1].split("\n") if len(sections) > 1 else [],
            "voice_style": sections[2] if len(sections) > 2 else "",
            "mixing_notes": sections[3] if len(sections) > 3 else ""
        }
        return audio_plan
    
    def _generate_voice(self, text: str) -> str:
        """텍스트를 음성으로 변환합니다."""
        self.logger.process("음성 생성 중...")
        try:
            # 음성 생성
            audio = self.tts_client.text_to_speech.convert(
                text=text,
                voice_id="21m00Tcm4TlvDq8ikWAM",
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128"
            )
            
            # 오디오 저장
            output_path = f"{self.audio_dir}/voice_{hash(text)}.mp3"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 오디오 데이터를 파일로 저장
            with open(output_path, "wb") as f:
                f.write(audio)
            
            self.logger.success(f"음성 파일 저장 완료: {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"음성 생성 중 오류 발생: {str(e)}")
            return self._generate_dummy_audio()["voice"]["path"]
    
    def _generate_sound_effect(self, effect: Dict) -> str:
        """효과음을 생성합니다."""
        self.logger.process("효과음 생성 중...")
        try:
            # 효과음 생성 로직 (실제로는 더 복잡할 수 있음)
            effect_type = effect.get("type", "default")
            output_path = f"{self.audio_dir}/effect_{effect_type}_{hash(str(effect))}.mp3"
            
            # 더미 효과음 생성 (1초 길이의 무음)
            silence = AudioSegment.silent(duration=1000)
            silence.export(output_path, format="mp3")
            
            self.logger.success(f"효과음 파일 저장 완료: {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"효과음 생성 중 오류 발생: {str(e)}")
            return None
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """오디오 파일의 길이를 초 단위로 반환합니다."""
        self.logger.process("오디오 길이 계산 중...")
        try:
            audio = AudioSegment.from_file(audio_path)
            return len(audio) / 1000.0  # 밀리초를 초로 변환
        except Exception as e:
            self.logger.error(f"오디오 길이 계산 중 오류 발생: {str(e)}")
            return 0.0
    
    def _generate_dummy_audio(self) -> Dict:
        """오류 발생 시 사용할 더미 오디오 에셋을 생성합니다."""
        self.logger.process("더미 오디오 에셋 생성 중...")
        dummy_path = f"{self.audio_dir}/dummy_narration.mp3"
        os.makedirs(os.path.dirname(dummy_path), exist_ok=True)
        
        # 더미 오디오 파일이 없으면 생성
        if not os.path.exists(dummy_path):
            # 1초 길이의 무음 오디오 생성
            silence = AudioSegment.silent(duration=1000)  # 1000ms = 1초
            silence.export(dummy_path, format="mp3")
        
        self.logger.success("더미 오디오 에셋 생성 완료")
        return {
            "voice": {
                "path": dummy_path,
                "duration": 1.0  # 1초
            },
            "effects": [],
            "plan": {
                "background_music": "No background music",
                "sound_effects": [],
                "voice_style": "Default voice",
                "mixing_notes": "No mixing required"
            }
        } 