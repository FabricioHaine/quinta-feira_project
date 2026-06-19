import 'package:speech_to_text/speech_to_text.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:permission_handler/permission_handler.dart';

class SpeechService {
  final SpeechToText _speech = SpeechToText();
  final FlutterTts _tts = FlutterTts();
  
  bool _isInitialized = false;
  bool _isSpeaking = false;

  Future<void> initialize() async {
    await _requestPermissions();
    _isInitialized = await _speech.initialize(
      onError: (error) => print('Speech error: $error'),
      onStatus: (status) => print('Speech status: $status'),
    );
    
    await _tts.setLanguage('pt-BR');
    await _tts.setSpeechRate(0.9);
    await _tts.setVolume(1.0);
    await _tts.setPitch(1.0);
  }

  Future<void> _requestPermissions() async {
    await [Permission.microphone, Permission.speech].request();
  }

  Future<void> startListening({required Function(String) onResult}) async {
    if (!_isInitialized) {
      await initialize();
    }

    await _speech.listen(
      onResult: (result) {
        if (result.finalResult) {
          onResult(result.recognizedWords);
        }
      },
      localeId: 'pt_BR',
      cancelOnError: true,
      listenFor: const Duration(seconds: 10),
      pauseFor: const Duration(seconds: 3),
    );
  }

  Future<void> stop() async {
    await _speech.stop();
  }

  Future<void> speak(String text) async {
    if (_isSpeaking) {
      await _tts.stop();
    }
    
    _isSpeaking = true;
    await _tts.speak(text);
    _isSpeaking = false;
  }

  void dispose() {
    _speech.cancel();
    _tts.stop();
  }
}
