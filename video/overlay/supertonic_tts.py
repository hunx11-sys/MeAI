"""한국어 내레이션 도구 (MeAI 가 얹은 파일 · 오픈몽타주 원본에는 없다).

설치 스크립트(video/openmontage_setup.sh)가 이 파일을 오픈몽타주의 tools/audio/supertonic_tts.py 로,
video/korean_voice.py 를 tools/audio/meai_korean_voice.py 로 복사한다. 오픈몽타주는 tools/ 아래의 도구를
스스로 찾아 등록하므로, 복사만 하면 음성 선택기(tts_selector)에 「supertonic」 으로 나타난다.

Supertonic 3(수퍼톤 · 한국어 포함 31개 언어)를 sherpa-onnx 로 이 컴퓨터 안에서 돌린다. 키 · 요금 없음.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    RetryPolicy,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)


class SupertonicTTS(BaseTool):
    name = "supertonic_tts"
    version = "0.1.0"
    tier = ToolTier.VOICE
    capability = "tts"
    provider = "supertonic"
    stability = ToolStability.EXPERIMENTAL
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.STOCHASTIC
    runtime = ToolRuntime.LOCAL

    dependencies = ["python:sherpa_onnx", "python:soundfile"]
    install_instructions = (
        "MeAI 저장소에서 `bash video/openmontage_setup.sh` 를 돌리면 설치된다.\n"
        "(sherpa-onnx · soundfile 설치 + Supertonic 3 목소리 모델을 npm 재포장본에서 받아 검증)"
    )
    agent_skills = ["text-to-speech"]

    capabilities = ["text_to_speech", "offline_generation", "korean_narration", "sentence_timings"]
    supports = {
        "voice_cloning": False,
        "multilingual": True,
        "offline": True,
        "native_audio": True,
        # 재포장본의 목록 그대로(31개)
        "languages": [
            "ar", "bg", "cs", "da", "de", "el", "en", "es", "et", "fi", "fr", "hi", "hr", "hu", "id", "it",
            "ja", "ko", "lt", "lv", "nl", "pl", "pt", "ro", "ru", "sk", "sl", "sv", "tr", "uk", "vi",
        ],
    }
    best_for = [
        "Korean narration with no API key and no cost",
        "offline / privacy-sensitive narration",
        "sentence-level subtitle timings (returned as segments)",
    ]
    not_good_for = [
        "voice cloning",
        "emotional acting or precise delivery direction",
        "word-level caption timing (segments are per sentence)",
    ]

    input_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {"type": "string", "description": "읽을 글. 문장 단위로 나눠 합성한다."},
            "voice": {
                "type": ["integer", "string"],
                "default": 0,
                "description": "목소리 번호 0~9. 0~4 여성(추정), 5~9 남성(추정).",
            },
            "speed": {"type": "number", "default": 1.0, "description": "말 빠르기. 1.0 보통, 1.1 조금 빠르게."},
            "language_code": {"type": "string", "default": "ko", "description": "언어 코드(ko, en, ja ...)."},
            "num_steps": {"type": "integer", "default": 8},
            "sentence_silence": {"type": "number", "default": 0.35, "description": "문장 사이 쉼(초)."},
            "srt_path": {"type": "string", "description": "주면 문장 단위 자막(SRT)도 함께 쓴다."},
            "output_path": {"type": "string"},
        },
    }

    resource_profile = ResourceProfile(cpu_cores=2, ram_mb=1024, vram_mb=0, disk_mb=200, network_required=False)
    retry_policy = RetryPolicy(max_retries=1, retryable_errors=[])
    idempotency_key_fields = ["text", "voice", "speed", "language_code", "num_steps"]
    side_effects = ["writes audio file to output_path", "writes srt file to srt_path when given"]
    user_visible_verification = ["Listen to generated audio: pronunciation of numbers, English words and names"]

    def get_status(self) -> ToolStatus:
        try:
            import sherpa_onnx  # noqa: F401
            import soundfile  # noqa: F401

            from tools.audio.meai_korean_voice import model_ready
        except Exception:
            return ToolStatus.UNAVAILABLE
        return ToolStatus.AVAILABLE if model_ready() else ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        if self.get_status() != ToolStatus.AVAILABLE:
            return ToolResult(success=False, error="Supertonic TTS not available. " + self.install_instructions)
        from tools.audio import meai_korean_voice as kv

        start = time.time()
        try:
            voice = inputs.get("voice", inputs.get("voice_id", inputs.get("speaker_id", kv.DEFAULT_VOICE)))
            voice = int(voice) if str(voice).strip().lstrip("-").isdigit() else kv.DEFAULT_VOICE
            lang = str(inputs.get("language_code") or inputs.get("voice_language") or "ko").split("-")[0].lower()
            res = kv.synthesize(
                inputs["text"],
                Path(inputs.get("output_path", "tts_output.wav")),
                voice=voice,
                speed=float(inputs.get("speed", inputs.get("speaking_rate", 1.0)) or 1.0),
                lang=lang,
                steps=int(inputs.get("num_steps", kv.DEFAULT_STEPS)),
                pause=float(inputs.get("sentence_silence", kv.SENTENCE_PAUSE)),
            )
            if inputs.get("srt_path"):
                kv.write_srt(res["segments"], inputs["srt_path"])
        except Exception as exc:
            return ToolResult(success=False, error=f"Supertonic TTS generation failed: {exc}")

        artifacts = [res["output"]] + ([str(inputs["srt_path"])] if inputs.get("srt_path") else [])
        result = ToolResult(
            success=True,
            data={
                "provider": self.provider,
                "model": "supertonic-3",
                "voice": res["voice"],
                "voice_label": res["voice_label"],
                "language": res["language"],
                "text_length": len(inputs["text"]),
                "output": res["output"],
                "format": Path(res["output"]).suffix.lstrip(".") or "wav",
                "audio_duration_seconds": res["duration_seconds"],
                "segments": res["segments"],
            },
            artifacts=artifacts,
            model="supertonic-3",
        )
        result.duration_seconds = round(time.time() - start, 2)
        return result
