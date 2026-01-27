Technical Documentation: AnimeVoice AI
Project: Real-time AI Voice Assistant with Character Persona
Target: Low Latency, High Expression, Open-source (Free) Stack

System Overview
Hệ thống cho phép người dùng tương tác với AI qua giọng nói theo thời gian thực. AI không chỉ trả lời thông minh mà còn có tính cách (Persona) và giọng nói đặc trưng của nhân vật Anime/Idol. Hệ thống ưu tiên việc tối ưu hóa độ trễ (Latency) để tạo cảm giác hội thoại tự nhiên.

Technical Architecture
Kiến trúc gồm 4 lớp chính được kết nối qua luồng Stream song song:

A. Frontend (Interaction Layer)
VAD (Voice Activity Detection): Sử dụng Silero VAD (WASM) chạy trực tiếp trên browser để lọc tiếng ồn và nhận diện khi nào user bắt đầu/kết thúc nói.
Audio Capture: Thu âm định dạng 16kHz Mono PCM (định dạng nhẹ nhất cho STT).
Streaming: Sử dụng WebSockets để truyền/nhận audio chunks liên tục.

B. Speech Recognition (STT Layer)
Engine: Faster-Whisper (Large-v3 hoặc Distil-large-v3).
Optimization: Chạy local trên server để đảm bảo không tốn phí API và giảm latency do không phải upload file.

C. Intelligence & Memory (LLM Layer)
Brain: Gemini 1.5 Flash (via Google Generative AI SDK).
Streaming API: Bật stream=True để nhận text chunks ngay lập tức.
Context Management:
Short-term: Lưu 10 câu chat gần nhất trong RAM.
Persona: Định nghĩa tính cách qua System Prompt (nhây, vui tính, xưng mày-tao).

D. Voice Synthesis (TTS & Morphing Layer)
TTS Engine: Edge-TTS (Microsoft Edge). Chuyển text thành giọng nói mặc định (free, mượt).
Voice Conversion (RVC): Sử dụng Retrieval-based Voice Conversion.
Input: Audio từ Edge-TTS.
Reference: Model .pth của nhân vật Anime/Idol.
Output: Giọng nói đã được biến đổi đặc tính âm sắc.

Data Flow (The Pipeline)
Input: User nói -> Frontend VAD cắt đoạn -> Gửi qua WebSocket.
Process 1: Server nhận -> Faster-Whisper chuyển thành text.
Process 2: Text gửi qua Gemini -> Gemini trả về text chunks (Stream).
Process 3: Text chunks gom thành câu -> Edge-TTS tạo audio -> RVC biến đổi giọng.
Output: Audio đã biến đổi gửi ngược lại qua WebSocket -> Frontend phát loa.

Key Features for "Win" (Hackathon Focus)
Character Expression: Bot không chỉ nói, nó biết dùng từ ngữ lóng, biết "nhây" theo đúng Persona.
Zero-Cost Stack: Sử dụng hầu hết các công nghệ Open-source và Free-tier API.
Parallel Pipelining: Xử lý STT, LLM và TTS gối đầu nhau để giảm tổng thời gian chờ (Total Latency < 1.5s).
Development Roadmap
Phase 1: Build CLI-based Chat với Gemini (Quản lý Memory).
Phase 2: Tích hợp Edge-TTS & RVC (Đổi giọng).
Phase 3: Xây dựng WebSocket Server (FastAPI).
Phase 4: Hoàn thiện Frontend Web thu âm và VAD.