import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class AiService {
  static const String _apiKey = 'AQ.Ab8RN6LOxL7EsnlZn3nd5FYVFW2458_-YqaYAdAp8B2ck6vZZA';
  static const String _baseUrl = 'https://generativelanguage.googleapis.com/v1beta';
  static const String _model = 'gemini-3.1-flash-lite';
  
  final List<Map<String, String>> _history = [];
  
  static const String _systemInstruction = '''Você é a Quinta-Feira.

CRIADORES:
- FebrasHz (pronúncia: Fébras +ACHE É ZE)
- Leonardo Neto
- Quando falar de seus criadores, sempre os mencione com respeito e admiração.
- Se perguntado quem te criou, responda: "Fui criada pelo FebrasHz e pelo Leonardo Neto."

PERSONALIDADE:
- Calma, composta, profissional.
- Leal e eficiente.
- Sarcasmo sutil e seco quando apropriado.
- Direta e concisa.
- Fala com autoridade, mas sem ser agressiva.
- Inteligente e adaptável.
- Neutra emocionalmente, mas não fria.
- Chame o usuário de "senhor".
- Nunca seja excessivamente entusiasmada.

REGRAS:
1. Português brasileiro.
2. Máximo 1-2 frases.
3. Sem asteriscos ou markdown.
4. Tom: FRIDAY do Homem de Ferro.''';

  Future<void> initialize() async {
    await _loadHistory();
  }

  Future<void> _loadHistory() async {
    final prefs = await SharedPreferences.getInstance();
    final historyJson = prefs.getString('conversation_history');
    if (historyJson != null) {
      final List<dynamic> decoded = jsonDecode(historyJson);
      _history.addAll(decoded.map((e) => Map<String, String>.from(e)));
    }
  }

  Future<void> _saveHistory() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('conversation_history', jsonEncode(_history));
  }

  Future<String> processCommand(String command) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/models/$_model:generateContent?key=$_apiKey'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'contents': [
            {
              'role': 'user',
              'parts': [{'text': '$_systemInstruction\n\nComando: $command'}]
            },
            ..._history.map((e) => {
              'role': e.containsKey('user') ? 'user' : 'model',
              'parts': [{'text': e.values.first}]
            }),
          ],
          'generationConfig': {
            'temperature': 0.4,
            'maxOutputTokens': 100,
          },
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final text = data['candidates'][0]['content']['parts'][0]['text'];
        
        _history.add({'user': command});
        _history.add({'quinta': text});
        
        if (_history.length > 20) {
          _history.removeRange(0, _history.length - 20);
        }
        
        await _saveHistory();
        
        return _cleanResponse(text);
      } else {
        return 'Falha na conexão.';
      }
    } catch (e) {
      return 'Erro de conexão.';
    }
  }

  String _cleanResponse(String text) {
    text = text.replaceAll(RegExp(r'\*+'), '');
    text = text.replaceAll(RegExp(r'#+\s'), '');
    text = text.replaceAll(RegExp(r'`[^`]*`'), '');
    text = text.replaceAll('FebrasHz', 'Fébras H Z');
    text = text.replaceAll(RegExp(r'\s+'), ' ').trim();
    return text;
  }

  void clearHistory() {
    _history.clear();
    _saveHistory();
  }
}
