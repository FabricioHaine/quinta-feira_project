import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'speech_service.dart';
import 'ai_service.dart';

class BackgroundService {
  static final BackgroundService _instance = BackgroundService._internal();
  factory BackgroundService() => _instance;
  BackgroundService._internal();

  final SpeechService _speechService = SpeechService();
  final AiService _aiService = AiService();
  
  bool _isRunning = false;
  bool _isListening = false;
  Timer? _checkTimer;
  
  static const String _wakeWord = 'quinta';
  static const int _checkIntervalSeconds = 30;

  Future<void> initialize() async {
    await _speechService.initialize();
    await _aiService.initialize();
  }

  Future<void> startBackgroundListening() async {
    if (_isRunning) return;
    
    _isRunning = true;
    await _saveState(true);
    
    // Inicia escuta contínua em background
    _startContinuousListening();
    
    // Timer para verificar status periodicamente
    _checkTimer = Timer.periodic(
      Duration(seconds: _checkIntervalSeconds),
      (_) => _checkBackgroundStatus(),
    );
    
    debugPrint('[Background] Serviço iniciado');
  }

  Future<void> stopBackgroundListening() async {
    _isRunning = false;
    _isListening = false;
    _checkTimer?.cancel();
    _checkTimer = null;
    
    await _speechService.stop();
    await _saveState(false);
    
    debugPrint('[Background] Serviço parado');
  }

  void _startContinuousListening() {
    if (!_isRunning) return;
    
    _speechService.startListening(
      onResult: (text) async {
        String lowerText = text.toLowerCase();
        
        // Comandos de controle do background
        if (lowerText.contains('desativar background') || 
            lowerText.contains('parar background') ||
            lowerText.contains('desligar background') ||
            lowerText.contains('quinta desativar')) {
          await stopBackgroundListening();
          await _speechService.speak('Background desativado.');
          return;
        }
        
        if (lowerText.contains('ativar background') || 
            lowerText.contains('ligar background') ||
            lowerText.contains('quinta ativar')) {
          await _speechService.speak('Background já está ativo.');
          return;
        }
        
        // Verifica palavra de ativação
        if (lowerText.contains(_wakeWord)) {
          _isListening = true;
          
          // Remove a palavra de ativação
          String command = lowerText.replaceAll(_wakeWord, '').trim();
          
          // Remove comandos de controle já processados
          command = command.replaceAll('ativar', '').replaceAll('desativar', '').trim();
          
          if (command.isNotEmpty) {
            final response = await _aiService.processCommand(command);
            await _speechService.speak(response);
          } else {
            await _speechService.speak('À disposição, senhor.');
          }
          
          _isListening = false;
        }
        
        // Reinicia escuta
        if (_isRunning && !_isListening) {
          Future.delayed(Duration(seconds: 1), () {
            _startContinuousListening();
          });
        }
      },
    );
  }

  Future<void> _checkBackgroundStatus() async {
    if (!_isRunning) return;
    
    final prefs = await SharedPreferences.getInstance();
    final shouldStop = prefs.getBool('stop_background') ?? false;
    
    if (shouldStop) {
      await stopBackgroundListening();
      await prefs.setBool('stop_background', false);
    }
  }

  Future<void> _saveState(bool isRunning) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('background_running', isRunning);
  }

  Future<bool> isRunning() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool('background_running') ?? false;
  }

  bool get isActive => _isRunning;

  Future<void> speak(String text) async {
    await _speechService.speak(text);
  }
}
