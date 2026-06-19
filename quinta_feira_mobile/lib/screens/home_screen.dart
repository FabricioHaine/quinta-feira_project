import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../services/speech_service.dart';
import '../services/ai_service.dart';
import '../services/background_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final SpeechService _speechService = SpeechService();
  final AiService _aiService = AiService();
  final BackgroundService _backgroundService = BackgroundService();
  
  bool _isListening = false;
  bool _isProcessing = false;
  bool _backgroundEnabled = false;
  String _statusText = 'Pronta';
  String _lastResponse = '';
  final List<Map<String, String>> _conversation = [];

  @override
  void initState() {
    super.initState();
    _initServices();
  }

  Future<void> _initServices() async {
    await _speechService.initialize();
    await _aiService.initialize();
    await _backgroundService.initialize();
    _backgroundEnabled = await _backgroundService.isRunning();
    setState(() {
      _statusText = 'Sistemas online';
    });
  }

  Future<void> _toggleListening() async {
    if (_isListening) {
      await _speechService.stop();
      setState(() => _isListening = false);
    } else {
      setState(() {
        _isListening = true;
        _statusText = 'Ouvindo...';
      });
      
      await _speechService.startListening(
        onResult: (text) async {
          if (text.isNotEmpty) {
            setState(() {
              _isListening = false;
              _isProcessing = true;
              _statusText = 'Processando...';
              _conversation.add({'user': text});
            });
            
            final response = await _aiService.processCommand(text);
            
            setState(() {
              _isProcessing = false;
              _statusText = 'Pronta';
              _lastResponse = response;
              _conversation.add({'quinta': response});
            });
            
            await _aiService.speak(response);
          }
        },
      );
    }
  }

  Future<void> _toggleBackground() async {
    if (_backgroundEnabled) {
      await _backgroundService.stopBackgroundListening();
    } else {
      await _backgroundService.startBackgroundListening();
    }
    setState(() {
      _backgroundEnabled = !_backgroundEnabled;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF0A0A0F), Color(0xFF1A1A2E)],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              _buildHeader(),
              Expanded(child: _buildConversation()),
              _buildStatusBar(),
              _buildControlButton(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.all(20),
      child: Row(
        children: [
          Container(
            width: 50,
            height: 50,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(color: const Color(0xFF00D4FF), width: 2),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF00D4FF).withOpacity(0.3),
                  blurRadius: 15,
                  spreadRadius: 2,
                ),
              ],
            ),
            child: const Icon(
              Icons.shield,
              color: Color(0xFF00D4FF),
              size: 30,
            ),
          ).animate().fadeIn(duration: 600.ms),
          const SizedBox(width: 15),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'QUINTA-FEIRA',
                style: TextStyle(
                  color: Color(0xFF00D4FF),
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 3,
                ),
              ).animate().fadeIn(duration: 600.ms),
              Text(
                _statusText,
                style: TextStyle(
                  color: _statusText == 'Pronta' 
                      ? const Color(0xFF00FF88) 
                      : Colors.white70,
                  fontSize: 12,
                ),
              ).animate().fadeIn(duration: 600.ms),
            ],
          ),
          const Spacer(),
          IconButton(
            icon: Icon(
              _backgroundEnabled ? Icons.volume_up : Icons.volume_off,
              color: _backgroundEnabled ? const Color(0xFF00FF88) : Colors.white54,
            ),
            onPressed: _toggleBackground,
            tooltip: _backgroundEnabled ? 'Background ativo' : 'Background desativado',
          ),
        ],
      ),
    );
  }

  Widget _buildConversation() {
    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      itemCount: _conversation.length,
      itemBuilder: (context, index) {
        final message = _conversation[index];
        final isUser = message.containsKey('user');
        
        return Container(
          margin: const EdgeInsets.only(bottom: 10),
          alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
          child: Container(
            padding: const EdgeInsets.all(12),
            constraints: BoxConstraints(
              maxWidth: MediaQuery.of(context).size.width * 0.75,
            ),
            decoration: BoxDecoration(
              color: isUser 
                  ? const Color(0xFF00D4FF).withOpacity(0.2)
                  : const Color(0xFF1A1A2E),
              borderRadius: BorderRadius.circular(15),
              border: Border.all(
                color: isUser 
                    ? const Color(0xFF00D4FF).withOpacity(0.5)
                    : const Color(0xFF00FF88).withOpacity(0.3),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  isUser ? 'Você' : 'Quinta-Feira',
                  style: TextStyle(
                    color: isUser 
                        ? const Color(0xFF00D4FF)
                        : const Color(0xFF00FF88),
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 5),
                Text(
                  isUser ? message['user']! : message['quinta']!,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ),
        ).animate().fadeIn(duration: 300.ms).slideX(begin: isUser ? 0.1 : -0.1);
      },
    );
  }

  Widget _buildStatusBar() {
    return Container(
      margin: const EdgeInsets.all(20),
      padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 20),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1A2E),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(
          color: _isProcessing 
              ? const Color(0xFFFFAA00).withOpacity(0.5)
              : _isListening 
                  ? const Color(0xFF00FF88).withOpacity(0.5)
                  : const Color(0xFF00D4FF).withOpacity(0.3),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: _isProcessing 
                  ? const Color(0xFFFFAA00)
                  : _isListening 
                      ? const Color(0xFF00FF88)
                      : const Color(0xFF00D4FF),
              boxShadow: [
                BoxShadow(
                  color: (_isProcessing 
                      ? const Color(0xFFFFAA00)
                      : _isListening 
                          ? const Color(0xFF00FF88)
                          : const Color(0xFF00D4FF)).withOpacity(0.5),
                  blurRadius: 10,
                ),
              ],
            ),
          ).animate(
            onPlay: (controller) => controller.repeat(reverse: true),
          ).scale(
            begin: const Offset(1, 1),
            end: const Offset(1.2, 1.2),
            duration: 500.ms,
          ),
          const SizedBox(width: 10),
          Text(
            _isProcessing 
                ? 'Processando...' 
                : _isListening 
                    ? 'Ouvindo...' 
                    : 'Pronta para comandos',
            style: const TextStyle(
              color: Colors.white70,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildControlButton() {
    return Container(
      padding: const EdgeInsets.only(bottom: 40),
      child: GestureDetector(
        onTap: _toggleListening,
        child: Container(
          width: 80,
          height: 80,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: _isListening 
                ? const Color(0xFF00FF88).withOpacity(0.2)
                : const Color(0xFF00D4FF).withOpacity(0.2),
            border: Border.all(
              color: _isListening 
                  ? const Color(0xFF00FF88)
                  : const Color(0xFF00D4FF),
              width: 3,
            ),
            boxShadow: [
              BoxShadow(
                color: (_isListening 
                    ? const Color(0xFF00FF88)
                    : const Color(0xFF00D4FF)).withOpacity(0.4),
                blurRadius: 20,
                spreadRadius: 5,
              ),
            ],
          ),
          child: Icon(
            _isListening ? Icons.mic : Icons.mic_none,
            color: _isListening 
                ? const Color(0xFF00FF88)
                : const Color(0xFF00D4FF),
            size: 40,
          ),
        ),
      ).animate(
        onPlay: (controller) => controller.repeat(reverse: true),
      ).scale(
        begin: const Offset(1, 1),
        end: const Offset(1.05, 1.05),
        duration: 1000.ms,
      ),
    );
  }

  @override
  void dispose() {
    _speechService.dispose();
    super.dispose();
  }
}
