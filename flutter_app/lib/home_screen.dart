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
import 'settings_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with TickerProviderStateMixin {
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

  // Sample data for the home screen
  List<Map<String, dynamic>> _featuredItems = [
    {
      'title': 'Welcome to Flutter App',
      'subtitle': 'Your personal assistant is ready',
      'icon': Icons.home,
      'color': Colors.blue,
    },
    {
      'title': 'Voice Assistant',
      'subtitle': 'Tap the mic to interact',
      'icon': Icons.mic,
      'color': Colors.green,
    },
  ];

  @override
  void initState() {
    super.initState();
    _anim = AnimationController(vsync: this, duration: const Duration(milliseconds: 900));
    _pulse = Tween<double>(begin: 1.0, end: 1.2).animate(CurvedAnimation(parent: _anim, curve: Curves.easeInOut));
    _sizeAnim = AnimationController(vsync: this, duration: const Duration(milliseconds: 300));
    _sizeScale = Tween<double>(begin: 1.0, end: 1.5).animate(CurvedAnimation(parent: _sizeAnim, curve: Curves.easeInOut));
    
    _player.onPlayerComplete.listen((event) async {
      if (!mounted) return;
      setState(() => _isSpeaking = false);
      _anim.stop();
      _anim.reset();
      _sizeAnim.reverse();
      
      // After page description plays, start listening for user input
      if (!_hasPlayedPageDescription) {
        _hasPlayedPageDescription = true;
        _assistantActive = true;
        await _startListening();
      }
    });
    
    // Auto prepare page data and TTS audio on load
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      print('Home page loaded, preparing page audio...');
      await _preparePageAudio();
    });
  }

  @override
  void dispose() {
    _anim.dispose();
    _sizeAnim.dispose();
    _silenceTimer?.cancel();
    _maxRecordingTimer?.cancel();
    _player.dispose();
    super.dispose();
  }

  Future<void> _startListening() async {
    if (_isRecording || _isProcessing || _isSpeaking) {
      print('Already recording/processing/speaking, skipping start listening');
      return;
    }
    
    if (kIsWeb) {
      if (!mounted) return;
      print('Web platform detected - voice recording not fully supported');
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Voice recording is not fully supported on web. Please use a mobile device or desktop app.'),
          duration: Duration(seconds: 3),
        ),
      );
      return;
    }
    
    try {
      final hasPerm = await _recorder.hasPermission();
      if (!hasPerm) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Microphone permission denied')));
        return;
      }
      // Use a concrete file path; some platforms require it in recent record versions
      final dir = await getTemporaryDirectory();
      final filePath = '${dir.path}/voice_${DateTime.now().millisecondsSinceEpoch}.wav';
      await _recorder.start(
        RecordConfig(
          encoder: AudioEncoder.wav,  // Use WAV for better compatibility
          bitRate: 160000,  // Higher bitrate for better quality
          sampleRate: 16000,
          numChannels: 1,
          autoGain: true,  // Enable auto gain for better audio levels
          echoCancel: true,  // Enable echo cancellation
          noiseSuppress: true,  // Enable noise suppression
        ),
        path: filePath,
      );
      if (!mounted) return;
      setState(() => _isRecording = true);
      _sizeAnim.reverse(); // Make icon smaller
      _startSilenceTimer();
      _startMaxRecordingTimer();
    } catch (_) {}
  }

  void _startSilenceTimer() {
    _silenceTimer?.cancel();
    print('Starting 5-second silence timer...');
    _silenceTimer = Timer(const Duration(seconds: 5), () async {
      if (_isRecording) {
        print('5 seconds of silence detected, stopping recording...');
        await _stopRecordingAndProcess();
      }
    });
  }

  void _startMaxRecordingTimer() {
    _maxRecordingTimer?.cancel();
    print('Starting 10-second max recording timer...');
    _maxRecordingTimer = Timer(const Duration(seconds: 10), () async {
      if (_isRecording) {
        print('10 seconds maximum recording time reached, stopping recording...');
        await _stopRecordingAndProcess();
      }
    });
  }

  Future<void> _stopRecordingAndProcess() async {
    print('Stopping recording and processing...');
    _silenceTimer?.cancel();
    _maxRecordingTimer?.cancel();
    setState(() => _isRecording = false);
    _sizeAnim.forward(); // Make icon bigger
    
    if (kIsWeb) {
      // Web platform - no actual recording
      print('Web platform - no audio processing');
      return;
    }
    
    try {
      final path = await _recorder.stop();
      if (path == null) {
        return;
      }
      final bytes = await File(path).readAsBytes();
      final transcript = await _transcribe(bytes, filename: 'voice.wav');
      if (transcript.isNotEmpty) {
        await _processUserInput(transcript);
      } else {
        // No speech detected or command not recognized
        print('No valid speech detected, staying idle');
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Command not recognized. Please try speaking more clearly.'),
            duration: Duration(seconds: 2),
          ),
        );
      }
    } catch (e) {
      print('Error processing audio: $e');
      if (!mounted) return;
    }
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
        final uri = Uri.parse('https://voice-assistant-fgzq.onrender.com/api/tts');
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

  Future<void> _speakText(String text, {bool isHindi = false}) async {
    print('Speaking text: ${text.substring(0, 50)}...');
    setState(() => _isSpeaking = true);
    _anim.repeat(reverse: true);
    _sizeAnim.forward(); // Make icon bigger when speaking
    
    try {
      // Use cached audio if available and not Hindi, otherwise fetch new
      if (_cachedAudioBytes != null && !isHindi) {
        print('Using cached audio');
        final bytes = base64Decode(_cachedAudioBytes!);
        final source = BytesSource(bytes);
        await _player.play(source);
      } else {
        print('Fetching new audio');
        final uri = Uri.parse('https://voice-assistant-fgzq.onrender.com/api/tts');
        final resp = await http.post(uri, headers: {'Content-Type': 'application/json'}, body: jsonEncode({
          'text': text,
          'is_hindi': isHindi
        })).timeout(const Duration(seconds: 30));
        if (resp.statusCode == 200) {
          final bytes = resp.bodyBytes;
          if (!isHindi) {
            _cachedAudioBytes = base64Encode(bytes); // Cache the audio only for English
          }
          final source = BytesSource(bytes);
          await _player.play(source);
        } else {
          if (!mounted) return;
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('TTS failed')));
          setState(() => _isSpeaking = false);
          _anim.stop();
          _anim.reset();
          _sizeAnim.reverse();
        }
      }
    } catch (e) {
      print('Error in _speakText: $e');
      if (!mounted) return;
      setState(() => _isSpeaking = false);
      _anim.stop();
      _anim.reset();
      _sizeAnim.reverse();
    }
  }

  Future<void> _preparePageAudio() async {
    print('Preparing home page audio...');
    final pageJson = _generatePageDescription(context);
    final textForSummarizer = jsonEncode(pageJson);
    try {
      final summary = await _summarize(textForSummarizer, translateToHindi: false);
      if (summary != null && summary.isNotEmpty) {
        _cachedSummary = summary;
        print('Summary cached: ${summary.substring(0, 50)}...');
        // Pre-fetch and cache the TTS audio
        final uri = Uri.parse('https://voice-assistant-fgzq.onrender.com/api/tts');
        final resp = await http.post(uri, headers: {'Content-Type': 'application/json'}, body: jsonEncode({
          'text': summary,
          'is_hindi': false
        })).timeout(const Duration(seconds: 30));
        if (resp.statusCode == 200) {
          _cachedAudioBytes = base64Encode(resp.bodyBytes);
          print('Audio cached successfully');
        } else {
          print('TTS failed with status: ${resp.statusCode}');
        }
      } else {
        print('No summary received');
      }
    } catch (e) {
      print('Error preparing audio: $e');
    }
  }

  Future<String> _transcribe(List<int> bytes, {String filename = 'voice.wav'}) async {
        final uri = Uri.parse('https://voice-assistant-fgzq.onrender.com/api/voice');
    final req = http.MultipartRequest('POST', uri)
      ..files.add(http.MultipartFile.fromBytes('audio', bytes, filename: filename, contentType: MediaType('audio', 'wav')));
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

  Future<String?> _summarize(String text, {bool translateToHindi = false}) async {
    final uri = Uri.parse('https://voice-assistant-fgzq.onrender.com/api/summarize');
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
      'page': 'Home',
      'header': {
        'title': 'Welcome to Flutter App',
        'subtitle': 'Your personal assistant is ready to help'
      },
      'content': {
        'featuredItems': _featuredItems.map((item) => {
          'title': item['title'],
          'subtitle': item['subtitle'],
          'icon': item['icon'].toString(),
          'color': item['color'].toString(),
        }).toList(),
        'sections': [
          {
            'name': 'Featured Items',
            'count': _featuredItems.length,
            'description': 'Main features and capabilities of the app'
          },
          {
            'name': 'Voice Assistant',
            'enabled': true,
            'description': 'Interactive voice assistant for navigation and help'
          }
        ]
      },
      'actions': {
        'appBar': [
          {'icon': 'mic', 'label': 'Voice assistant for home page'}
        ]
      }
    };
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Flutter App'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const SettingsScreen()),
              );
            },
          ),
          Padding(
            padding: const EdgeInsets.only(right: 8.0),
          child: Row(
              mainAxisSize: MainAxisSize.min,
            children: [
                // Status indicators
                if (_isSpeaking)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    margin: const EdgeInsets.only(right: 8),
                  decoration: BoxDecoration(
                      color: Colors.redAccent.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      _hasPlayedPageDescription ? 'Responding...' : 'Describing...',
                      style: const TextStyle(
                        color: Colors.redAccent,
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                if (_isRecording)
              Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    margin: const EdgeInsets.only(right: 8),
                decoration: BoxDecoration(
                      color: Colors.green.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Text(
                      'Listening...',
                      style: TextStyle(
                        color: Colors.green,
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                if (_isProcessing)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    margin: const EdgeInsets.only(right: 8),
                    decoration: BoxDecoration(
                      color: Colors.orange.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Text(
                      'Processing...',
                      style: TextStyle(
                        color: Colors.orange,
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                if (_assistantActive && !_isSpeaking && !_isRecording && !_isProcessing)
                Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    margin: const EdgeInsets.only(right: 8),
                    decoration: BoxDecoration(
                      color: Colors.blue.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Text(
                      'Assistant Active',
                        style: TextStyle(
                        color: Colors.blue,
                        fontSize: 12,
                          fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                // Animated button
                AnimatedBuilder(
                  animation: Listenable.merge([_anim, _sizeAnim]),
                  builder: (context, child) {
                    final pulseScale = _isSpeaking ? _pulse.value : 1.0;
                    final sizeScale = _sizeScale.value;
                    final finalScale = pulseScale * sizeScale;
                    return Transform.scale(
                      scale: finalScale,
                      child: IconButton(
                        tooltip: _isSpeaking ? 'Stop audio' : (_isRecording ? 'Stop and process' : 'Play prepared audio'),
                        onPressed: () async {
                          print('Button pressed - isSpeaking: $_isSpeaking, isRecording: $_isRecording, isProcessing: $_isProcessing, assistantActive: $_assistantActive');
                          
                          if (_isSpeaking) {
                            // Stop audio
                            print('Stopping audio...');
                            try {
                              await _player.stop();
                            } catch (_) {}
                            setState(() => _isSpeaking = false);
                            _anim.stop();
                            _anim.reset();
                            _sizeAnim.reverse();
                          } else if (_isRecording) {
                            // Stop recording manually
                            await _stopRecordingAndProcess();
                          } else if (_isProcessing) {
                            // Do nothing while processing
                            print('Still processing, please wait...');
                          } else if (!_hasPlayedPageDescription) {
                            // First time - play page description
                            print('Playing page description...');
                            if (_cachedAudioBytes != null && _cachedSummary != null) {
                              await _speakText(_cachedSummary!);
      } else {
                              print('No cached audio, preparing...');
                              await _preparePageAudio();
                              if (_cachedAudioBytes != null && _cachedSummary != null) {
                                await _speakText(_cachedSummary!);
                              }
                            }
                          } else if (_assistantActive) {
                            // Assistant is active - toggle it off
                            print('Turning assistant off...');
                            setState(() => _assistantActive = false);
                            _silenceTimer?.cancel();
                            _maxRecordingTimer?.cancel();
                          } else {
                            // Assistant is off - turn it on and start listening
                            print('Turning assistant on...');
                            setState(() => _assistantActive = true);
                            await _startListening();
                          }
                        },
                        icon: Icon(
                          _isSpeaking ? Icons.stop : Icons.volume_up,
                          color: _isRecording
                              ? Colors.green
                              : (_isSpeaking ? Colors.redAccent : Colors.blue),
                        ),
                      ),
                    );
                  },
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
            // Welcome Section
            Card(
              elevation: 4,
              child: Padding(
                padding: const EdgeInsets.all(20.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                    Row(
                      children: [
                        Icon(Icons.home, size: 32, color: Colors.blue),
                        const SizedBox(width: 12),
                      Text(
                          'Welcome to Flutter App',
                          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                      Text(
                      'Your personal assistant is ready to help you navigate and interact with the app.',
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                          color: Colors.grey[600],
                  ),
                ),
              ],
            ),
              ),
            ),
            
            const SizedBox(height: 20),
            
            // Featured Items Section
            Text(
              'Featured Items',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            
            ..._featuredItems.map((item) => Card(
              elevation: 2,
              margin: const EdgeInsets.only(bottom: 12),
              child: ListTile(
                leading: CircleAvatar(
                  backgroundColor: (item['color'] as Color).withOpacity(0.1),
                  child: Icon(
                    item['icon'] as IconData,
                    color: item['color'] as Color,
                  ),
                ),
                title: Text(
                  item['title'] as String,
                  style: const TextStyle(fontWeight: FontWeight.w600),
                ),
                subtitle: Text(item['subtitle'] as String),
                trailing: const Icon(Icons.chevron_right),
                onTap: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Tapped on ${item['title']}')),
                  );
                },
              ),
            )).toList(),
            
            const SizedBox(height: 20),
            
            // Voice Assistant Info
            Card(
              color: Colors.blue.withOpacity(0.1),
      child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Row(
          children: [
                    Icon(Icons.mic, color: Colors.blue, size: 24),
                    const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                       Text(
                            'Voice Assistant',
                            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                           fontWeight: FontWeight.bold,
                              color: Colors.blue,
                         ),
                       ),
                          const SizedBox(height: 4),
                       Text(
                            'Tap the mic icon in the app bar to interact with your voice assistant.',
                            style: Theme.of(context).textTheme.bodyMedium,
                       ),
                    ],
                  ),
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
}