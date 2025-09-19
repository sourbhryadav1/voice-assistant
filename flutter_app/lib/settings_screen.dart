import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/foundation.dart';
import 'package:record/record.dart';
import 'dart:io';
import 'dart:async';
import 'package:path_provider/path_provider.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> with TickerProviderStateMixin {
  late final AnimationController _anim;
  late final Animation<double> _pulse;
  late final AnimationController _sizeAnim;
  late final Animation<double> _sizeScale;
  bool _isSpeaking = false;
  bool _loopEnabled = true;
  bool _isRecording = false;
  bool _isProcessing = false;
  bool _hasPlayedPageDescription = false;
  bool _assistantActive = false;
  String? _cachedSummary;
  String? _cachedAudioBytes;
  Timer? _silenceTimer;
  Timer? _maxRecordingTimer;
  final AudioPlayer _player = AudioPlayer();
  final AudioRecorder _recorder = AudioRecorder();

  // Settings data
  bool _notificationsEnabled = true;
  bool _darkModeEnabled = false;
  String _selectedLanguage = 'English';
  double _volume = 0.8;

  @override
  void initState() {
    super.initState();
    _anim = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );
    _pulse = Tween<double>(begin: 1.0, end: 1.2).animate(
      CurvedAnimation(parent: _anim, curve: Curves.easeInOut),
    );
    _sizeAnim = AnimationController(
      duration: const Duration(milliseconds: 200),
      vsync: this,
    );
    _sizeScale = Tween<double>(begin: 1.0, end: 1.1).animate(
      CurvedAnimation(parent: _sizeAnim, curve: Curves.easeInOut),
    );
    _player.onPlayerComplete.listen((_) {
      setState(() => _isSpeaking = false);
      _anim.stop();
      _anim.reset();
      _sizeAnim.reverse();
    });
  }

  @override
  void dispose() {
    _anim.dispose();
    _sizeAnim.dispose();
    _player.dispose();
    _recorder.dispose();
    _silenceTimer?.cancel();
    _maxRecordingTimer?.cancel();
    super.dispose();
  }

  Future<void> _processUserInput(String userInput) async {
    print('Processing user input: $userInput');
    setState(() => _isProcessing = true);
    
    try {
      // Check if user wants Hindi translation
      final isHindiRequest = _isHindiCommand(userInput);
      
      // Combine user input with page context for summarization
      final contextData = {
        'userInput': userInput,
        'pageContext': _generatePageDescription(context),
        'timestamp': DateTime.now().toIso8601String(),
      };
      
      final summary = await _summarize(jsonEncode(contextData), translateToHindi: isHindiRequest);
      if (summary != null && summary.isNotEmpty) {
        // Generate TTS for the response
        final uri = Uri.parse('http://localhost:5000/api/tts');
        final resp = await http.post(
          uri, 
          headers: {'Content-Type': 'application/json'}, 
          body: jsonEncode({
            'text': summary,
            'is_hindi': isHindiRequest
          })
        ).timeout(const Duration(seconds: 30));
        
        if (resp.statusCode == 200) {
          final bytes = resp.bodyBytes;
          final source = BytesSource(bytes);
        setState(() {
            _isProcessing = false;
            _isSpeaking = true;
          });
          _anim.repeat(reverse: true);
          _sizeAnim.forward();
          await _player.play(source);
        } else {
          setState(() => _isProcessing = false);
        }
      } else {
        setState(() => _isProcessing = false);
      }
    } catch (e) {
      print('Error processing user input: $e');
      setState(() => _isProcessing = false);
    }
  }

  Future<String?> _summarize(String text, {bool translateToHindi = false}) async {
    final uri = Uri.parse('http://localhost:5000/api/summarize');
    final resp = await http
        .post(uri, headers: {'Content-Type': 'application/json'}, body: jsonEncode({
          'text': text,
          'translate_to_hindi': translateToHindi
        }))
        .timeout(const Duration(seconds: 25));
    if (resp.statusCode == 200) {
      final data = jsonDecode(resp.body) as Map<String, dynamic>;
      return (data['summary'] as String?)?.trim();
    }
    return null;
  }

  bool _isHindiCommand(String userInput) {
    final hindiKeywords = [
      'hindi', 'hindi mein', 'hindi me', 'to hindi', 'translate to hindi',
      'हिंदी', 'हिंदी में', 'हिंदी मे'
    ];
    
    final lowerInput = userInput.toLowerCase();
    return hindiKeywords.any((keyword) => lowerInput.contains(keyword));
  }

  Map<String, dynamic> _generatePageDescription(BuildContext context) {
    return {
      'appName': 'Flutter App',
      'page': 'Settings',
      'header': {
        'title': 'Settings',
        'subtitle': 'Customize your app experience'
      },
      'content': {
        'settings': [
          {
            'name': 'Notifications',
            'enabled': _notificationsEnabled,
            'description': 'Receive push notifications and alerts',
            'type': 'toggle'
          },
          {
            'name': 'Dark Mode',
            'enabled': _darkModeEnabled,
            'description': 'Switch between light and dark themes',
            'type': 'toggle'
          },
          {
            'name': 'Language',
            'value': _selectedLanguage,
            'description': 'Choose your preferred language',
            'type': 'dropdown',
            'options': ['English', 'Hindi', 'Spanish', 'French']
          },
          {
            'name': 'Volume',
            'value': _volume,
            'description': 'Adjust audio volume level',
            'type': 'slider',
            'min': 0.0,
            'max': 1.0
          }
        ],
        'sections': [
          {
            'name': 'Appearance',
            'count': 2,
            'description': 'Visual and theme settings'
          },
          {
            'name': 'Audio',
            'count': 1,
            'description': 'Sound and volume settings'
          },
          {
            'name': 'Notifications',
            'count': 1,
            'description': 'Alert and notification preferences'
          }
        ]
      },
      'actions': {
        'appBar': [
          {'icon': 'arrow_back', 'label': 'Go back to home'},
          {'icon': 'mic', 'label': 'Voice assistant for settings page'}
        ],
        'navigation': [
          {'type': 'back', 'label': 'Return to home page'},
          {'type': 'save', 'label': 'Save current settings'}
        ]
      }
    };
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 8.0),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (_isSpeaking)
                  AnimatedBuilder(
                    animation: _pulse,
                    builder: (context, child) {
                      return Transform.scale(
                        scale: _pulse.value,
                        child: Container(
                          width: 12,
                          height: 12,
                          decoration: BoxDecoration(
                            color: Colors.green,
                            shape: BoxShape.circle,
                          ),
                        ),
                      );
                    },
                  ),
                if (_isProcessing)
                  SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(
                        Theme.of(context).primaryColor,
                      ),
                    ),
                  ),
                const SizedBox(width: 8),
                GestureDetector(
                  onTap: _isRecording ? _stopRecording : _startRecording,
                  child: AnimatedBuilder(
                    animation: _sizeScale,
                    builder: (context, child) {
                      return Transform.scale(
                        scale: _sizeScale.value,
                        child: Container(
                          width: 50,
                          height: 50,
                          decoration: BoxDecoration(
                            color: _isRecording ? Colors.red : Colors.blue,
                            shape: BoxShape.circle,
                            boxShadow: [
                              BoxShadow(
                                color: (_isRecording ? Colors.red : Colors.blue).withOpacity(0.3),
                                blurRadius: 8,
                                spreadRadius: 2,
                              ),
                            ],
                          ),
                          child: Icon(
                            _isRecording ? Icons.stop : Icons.mic,
                            color: Colors.white,
                            size: 24,
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Notifications Setting
            Card(
              child: SwitchListTile(
                title: const Text('Notifications'),
                subtitle: const Text('Receive push notifications and alerts'),
                value: _notificationsEnabled,
                onChanged: (value) {
                  setState(() {
                    _notificationsEnabled = value;
                  });
                },
              ),
            ),
            const SizedBox(height: 8),
            
            // Dark Mode Setting
            Card(
              child: SwitchListTile(
                title: const Text('Dark Mode'),
                subtitle: const Text('Switch between light and dark themes'),
                value: _darkModeEnabled,
                onChanged: (value) {
                  setState(() {
                    _darkModeEnabled = value;
                  });
                },
              ),
            ),
            const SizedBox(height: 8),
            
            // Language Setting
            Card(
              child: ListTile(
                title: const Text('Language'),
                subtitle: Text(_selectedLanguage),
                trailing: const Icon(Icons.arrow_forward_ios),
                onTap: () {
                  showDialog(
                    context: context,
                    builder: (context) => AlertDialog(
                      title: const Text('Select Language'),
                      content: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: ['English', 'Hindi', 'Spanish', 'French']
                            .map((lang) => ListTile(
                                  title: Text(lang),
                                  onTap: () {
                                    setState(() {
                                      _selectedLanguage = lang;
                                    });
                                    Navigator.pop(context);
                                  },
                                ))
                            .toList(),
                      ),
                    ),
                  );
                },
              ),
            ),
            const SizedBox(height: 8),
            
            // Volume Setting
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Volume',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    Slider(
                      value: _volume,
                      onChanged: (value) {
                        setState(() {
                          _volume = value;
                        });
                      },
                    ),
                    Text(
                      '${(_volume * 100).round()}%',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 24),
            
            // Voice Assistant Info
            Card(
              color: Colors.blue.shade50,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.mic, color: Colors.blue.shade700),
                        const SizedBox(width: 8),
                        Text(
                          'Voice Assistant',
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            color: Colors.blue.shade700,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Tap the microphone to get help with settings. Try saying "hindi mein bolo" for Hindi responses.',
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _startRecording() async {
    if (await _recorder.hasPermission()) {
      setState(() {
        _isRecording = true;
        _assistantActive = true;
      });
      
      final path = await _getRecordingPath();
      await _recorder.start(path: path);
      
      _maxRecordingTimer = Timer(const Duration(seconds: 10), () {
        if (_isRecording) {
          _stopRecording();
        }
      });
    }
  }

  Future<void> _stopRecording() async {
    if (_isRecording) {
      setState(() => _isRecording = false);
      _maxRecordingTimer?.cancel();
      
      final path = await _recorder.stop();
      if (path != null) {
        final bytes = await File(path).readAsBytes();
        try {
          final userInput = await _transcribe(bytes);
          if (userInput.isNotEmpty) {
            await _processUserInput(userInput);
          }
        } catch (e) {
          print('Error transcribing: $e');
        }
      }
    }
  }

  Future<String> _getRecordingPath() async {
    final dir = await getTemporaryDirectory();
    return '${dir.path}/voice_${DateTime.now().millisecondsSinceEpoch}.wav';
  }

  Future<String> _transcribe(List<int> bytes) async {
    final uri = Uri.parse('http://localhost:5000/api/voice');
    final req = http.MultipartRequest('POST', uri)
      ..files.add(http.MultipartFile.fromBytes('audio', bytes, filename: 'voice.wav', contentType: MediaType('audio', 'wav')));
    final streamed = await req.send();
    final resp = await http.Response.fromStream(streamed);
    
    if (resp.statusCode == 200) {
      final data = jsonDecode(resp.body) as Map<String, dynamic>;
      final t = (data['text'] as String?)?.trim();
      final isValid = data['is_valid'] as bool? ?? false;
      
      if (t != null && t.isNotEmpty) {
        if (isValid) {
          print('Valid voice command: $t');
          return t;
        } else {
          print('Invalid or unclear command: $t');
          final message = data['message'] as String? ?? 'Command not recognized';
          print('Reason: $message');
          return ''; // Return empty to avoid processing unclear commands
        }
      }
    }
    throw Exception('STT failed');
  }
}
