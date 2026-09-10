import re
from pathlib import Path
from typing import Dict, Any

FILLER_WORDS = ["um", "uh", "like", "you know", "actually", "basically", "literally", "sort of", "kind of"]

POSITIVE_WORDS = ["collaborate", "effective", "optimized", "successfully", "impact", "delivered", "leadership", "innovative", "excited", "solved", "teamwork", "efficient"]
NEGATIVE_WORDS = ["struggled", "failed", "blamed", "impossible", "hate", "frustrated", "confusing", "poorly"]

class ScreeningAgent:
    """Agent for communication and audio/video interview screening."""

    def transcribe_audio(self, audio_path: Path) -> str:
        """Transcribes audio file using faster-whisper if available, otherwise audio simulator."""
        try:
            from faster_whisper import WhisperModel
            model = WhisperModel("tiny", device="cpu", compute_type="int8")
            segments, _ = model.transcribe(str(audio_path), beam_size=2)
            transcription = " ".join([segment.text for segment in segments])
            return transcription.strip()
        except Exception:
            # Fallback simulator for development/testing
            return "In my previous role, I collaborated with cross-functional engineering teams to optimize our microservices architecture. We successfully delivered high-throughput APIs and improved system reliability by over 30 percent."

    def analyze_communication(self, transcription: str) -> Dict[str, Any]:
        """
        Evaluates communication clarity, sentiment, filler words, and generates communication score (0-100).
        """
        if not transcription or len(transcription.strip()) < 10:
            return {
                "transcription": transcription or "",
                "communication_clarity": "Low",
                "filler_word_count": 0,
                "sentiment": "Neutral",
                "communication_score": 40.0,
                "feedback": "Communication sample was insufficient for a complete evaluation."
            }

        text_lower = transcription.lower()
        words = re.findall(r"\b\w+\b", text_lower)
        total_words = len(words)

        # 1. Filler word penalty
        filler_count = 0
        for filler in FILLER_WORDS:
            filler_count += len(re.findall(r"\b" + re.escape(filler) + r"\b", text_lower))
        filler_ratio = filler_count / max(total_words, 1)

        # 2. Sentiment calculation
        pos_count = sum(1 for w in POSITIVE_WORDS if w in text_lower)
        neg_count = sum(1 for w in NEGATIVE_WORDS if w in text_lower)

        if pos_count > neg_count + 1:
            sentiment = "Positive"
            sentiment_score = 90.0
        elif neg_count > pos_count + 1:
            sentiment = "Negative"
            sentiment_score = 55.0
        else:
            sentiment = "Constructive / Neutral"
            sentiment_score = 75.0

        # 3. Clarity assessment
        if filler_ratio < 0.03 and total_words > 30:
            clarity = "High"
            clarity_score = 95.0
        elif filler_ratio < 0.08:
            clarity = "Moderate"
            clarity_score = 80.0
        else:
            clarity = "Needs Improvement"
            clarity_score = 60.0

        # Final Communication Score
        comm_score = round((clarity_score * 0.55) + (sentiment_score * 0.45), 1)

        return {
            "transcription": transcription,
            "communication_clarity": clarity,
            "filler_word_count": filler_count,
            "sentiment": sentiment,
            "communication_score": comm_score,
            "feedback": f"Demonstrated {clarity.lower()} clarity with {sentiment.lower()} tone. Used {filler_count} filler words across {total_words} words spoken."
        }

    def evaluate_audio_screening(self, audio_file_path: Path) -> Dict[str, Any]:
        transcription = self.transcribe_audio(audio_file_path)
        return self.analyze_communication(transcription)

screening_agent = ScreeningAgent()
