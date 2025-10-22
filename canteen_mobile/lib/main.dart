import 'package:flutter/material.dart';
import 'package:flutter_inappwebview/flutter_inappwebview.dart';
import 'package:permission_handler/permission_handler.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'MyMurid Canteen',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: WebViewApp(),
    );
  }
}

class WebViewApp extends StatefulWidget {
  @override
  _WebViewAppState createState() => _WebViewAppState();
}

class _WebViewAppState extends State<WebViewApp> {
  InAppWebViewController? webViewController;
  bool isLoading = true;
  bool hasError = false;
  String errorMessage = '';
  int _currentIndex = 0;

  final List<Map<String, dynamic>> _navItems = [
    {
      'title': 'Home',
      'icon': Icons.home,
      'url': 'https://mymurid.onrender.com',
    },
    {
      'title': 'Order',
      'icon': Icons.restaurant_menu,
      'url': 'https://mymurid.onrender.com/order',
    },
    {
      'title': 'Rewards',
      'icon': Icons.card_giftcard,
      'url': 'https://mymurid.onrender.com/rewards',
    },
    {
      'title': 'Profile',
      'icon': Icons.person,
      'url': 'https://mymurid.onrender.com/student',
    },
  ];

  @override
  void initState() {
    super.initState();
    _requestPermissions();
  }

  Future<void> _requestPermissions() async {
    await Permission.camera.request();
    await Permission.microphone.request();
  }

  void _onTabTapped(int index) {
    setState(() {
      _currentIndex = index;
    });
    webViewController?.loadUrl(
      urlRequest: URLRequest(url: WebUri(_navItems[index]['url'])),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          InAppWebView(
            initialUrlRequest: URLRequest(
              url: WebUri(_navItems[_currentIndex]['url']),
            ),
            initialSettings: InAppWebViewSettings(
              javaScriptEnabled: true,
              mediaPlaybackRequiresUserGesture: false,
              useHybridComposition: true,
              allowsInlineMediaPlayback: true,
              cacheEnabled: true,
              clearCache: false,
            ),
            onWebViewCreated: (controller) {
              webViewController = controller;
            },
            onLoadStart: (controller, url) {
              setState(() {
                isLoading = true;
                hasError = false;
              });
            },
            onLoadStop: (controller, url) {
              setState(() {
                isLoading = false;
              });
            },
            onLoadError: (controller, url, code, message) {
              setState(() {
                isLoading = false;
                hasError = true;
                errorMessage = message ?? 'Failed to load page';
              });
            },
            androidOnPermissionRequest: (controller, origin, resources) async {
              return PermissionRequestResponse(
                resources: resources,
                action: PermissionRequestResponseAction.GRANT,
              );
            },
          ),
          if (isLoading)
            Container(
              color: Colors.white,
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    CircularProgressIndicator(
                      valueColor: AlwaysStoppedAnimation<Color>(
                        Colors.blue[600]!,
                      ),
                    ),
                    SizedBox(height: 16),
                    Text(
                      'Loading MyMurid Canteen...',
                      style: TextStyle(fontSize: 16, color: Colors.grey[600]),
                    ),
                  ],
                ),
              ),
            ),
          if (hasError)
            Container(
              color: Colors.white,
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.error_outline, size: 64, color: Colors.red[300]),
                    SizedBox(height: 16),
                    Text(
                      'Connection Error',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: Colors.red[600],
                      ),
                    ),
                    SizedBox(height: 8),
                    Text(
                      errorMessage,
                      textAlign: TextAlign.center,
                      style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                    ),
                    SizedBox(height: 24),
                    ElevatedButton(
                      onPressed: () {
                        setState(() {
                          hasError = false;
                        });
                        webViewController?.reload();
                      },
                      child: Text('Retry'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blue[600],
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
}
