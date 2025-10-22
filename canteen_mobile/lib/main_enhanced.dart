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
        primarySwatch: Colors.green,
        visualDensity: VisualDensity.adaptivePlatformDensity,
        appBarTheme: AppBarTheme(
          backgroundColor: Colors.green[600],
          foregroundColor: Colors.white,
          elevation: 0,
        ),
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
  bool canGoBack = false;
  bool canGoForward = false;

  @override
  void initState() {
    super.initState();
    _requestPermissions();
  }

  Future<void> _requestPermissions() async {
    await Permission.camera.request();
    await Permission.microphone.request();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('MyMurid Canteen'),
        actions: [
          IconButton(
            icon: Icon(Icons.arrow_back),
            onPressed: canGoBack ? () => webViewController?.goBack() : null,
          ),
          IconButton(
            icon: Icon(Icons.arrow_forward),
            onPressed: canGoForward ? () => webViewController?.goForward() : null,
          ),
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: () => webViewController?.reload(),
          ),
          PopupMenuButton<String>(
            onSelected: (value) {
              switch (value) {
                case 'home':
                  webViewController?.loadUrl(
                    urlRequest: URLRequest(
                      url: WebUri("https://mymurid.onrender.com"),
                    ),
                  );
                  break;
                case 'login':
                  webViewController?.loadUrl(
                    urlRequest: URLRequest(
                      url: WebUri("https://mymurid.onrender.com/login"),
                    ),
                  );
                  break;
                case 'menu':
                  webViewController?.loadUrl(
                    urlRequest: URLRequest(
                      url: WebUri("https://mymurid.onrender.com/order"),
                    ),
                  );
                  break;
              }
            },
            itemBuilder: (context) => [
              PopupMenuItem(
                value: 'home',
                child: Row(
                  children: [
                    Icon(Icons.home, color: Colors.green[600]),
                    SizedBox(width: 8),
                    Text('Home'),
                  ],
                ),
              ),
              PopupMenuItem(
                value: 'login',
                child: Row(
                  children: [
                    Icon(Icons.login, color: Colors.green[600]),
                    SizedBox(width: 8),
                    Text('Login'),
                  ],
                ),
              ),
              PopupMenuItem(
                value: 'menu',
                child: Row(
                  children: [
                    Icon(Icons.restaurant_menu, color: Colors.green[600]),
                    SizedBox(width: 8),
                    Text('Menu'),
                  ],
                ),
              ),
            ],
            icon: Icon(Icons.more_vert),
          ),
        ],
      ),
      body: Stack(
        children: [
          InAppWebView(
            initialUrlRequest: URLRequest(
              url: WebUri("https://mymurid.onrender.com"),
            ),
            initialSettings: InAppWebViewSettings(
              javaScriptEnabled: true,
              mediaPlaybackRequiresUserGesture: false,
              useHybridComposition: true,
              allowsInlineMediaPlayback: true,
              cacheEnabled: true,
              clearCache: false,
              supportZoom: false,
              displayZoomControls: false,
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
                errorMessage = message;
              });
            },
            onUpdateVisitedHistory: (controller, url, isReload) {
              controller.canGoBack().then((canBack) {
                setState(() {
                  canGoBack = canBack;
                });
              });
              controller.canGoForward().then((canForward) {
                setState(() {
                  canGoForward = canForward;
                });
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
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.green[600]!),
                    ),
                    SizedBox(height: 16),
                    Text(
                      'Loading MyMurid Canteen...',
                      style: TextStyle(
                        fontSize: 16,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          if (hasError)
            Container(
              color: Colors.white,
              child: Center(
                child: Padding(
                  padding: EdgeInsets.all(24),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.error_outline,
                        size: 64,
                        color: Colors.red[300],
                      ),
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
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey[600],
                        ),
                      ),
                      SizedBox(height: 24),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: [
                          ElevatedButton.icon(
                            onPressed: () {
                              setState(() {
                                hasError = false;
                              });
                              webViewController?.reload();
                            },
                            icon: Icon(Icons.refresh),
                            label: Text('Retry'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.green[600],
                              foregroundColor: Colors.white,
                            ),
                          ),
                          ElevatedButton.icon(
                            onPressed: () {
                              setState(() {
                                hasError = false;
                              });
                              webViewController?.loadUrl(
                                urlRequest: URLRequest(
                                  url: WebUri("https://mymurid.onrender.com"),
                                ),
                              );
                            },
                            icon: Icon(Icons.home),
                            label: Text('Home'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.blue[600],
                              foregroundColor: Colors.white,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
