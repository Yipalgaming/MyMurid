# MyMurid Mobile App

A Flutter mobile application that wraps the MyMurid web application for a native mobile experience.

## Features

- 🌐 **WebView Integration**: Seamlessly loads your Render-hosted web app
- 📱 **Native Mobile UI**: Custom app bar with navigation controls
- 🔄 **Smart Navigation**: Back/forward buttons, refresh, and quick menu access
- 🎨 **Professional Design**: Green theme matching your canteen brand
- ⚡ **Error Handling**: Graceful error handling with retry options
- 📷 **Camera Support**: Ready for barcode scanning functionality

## Setup Instructions

### 1. Prerequisites
- Flutter SDK installed
- Android Studio / VS Code
- Android device or emulator

### 2. Install Dependencies
```bash
cd canteen_mobile
flutter pub get
```

### 3. Create App Icon
1. Create a 1024x1024 PNG icon for your app
2. Place it as `assets/icon.png`
3. Run: `flutter pub run flutter_launcher_icons:main`

### 4. Build the App

#### For Android:
```bash
flutter build apk --release
```
The APK will be created at: `build/app/outputs/flutter-apk/app-release.apk`

#### For Android App Bundle (Google Play Store):
```bash
flutter build appbundle --release
```

### 5. Test the App
```bash
flutter run
```

## App Structure

- `lib/main.dart` - Basic WebView implementation
- `lib/main_enhanced.dart` - Enhanced version with better navigation
- `pubspec.yaml` - Dependencies and app configuration

## Customization Options

### Change the Web URL
Edit the URL in `main.dart`:
```dart
url: WebUri("https://mymurid.onrender.com"),
```

### Customize Colors
Update the theme in `main.dart`:
```dart
primarySwatch: Colors.green,
backgroundColor: Colors.green[600],
```

### Add More Navigation Options
Edit the `PopupMenuButton` in `main_enhanced.dart` to add more menu items.

## Deployment

### Google Play Store
1. Create a Google Play Developer account
2. Build app bundle: `flutter build appbundle --release`
3. Upload to Google Play Console
4. Configure store listing and release

### Direct APK Distribution
1. Build APK: `flutter build apk --release`
2. Share the APK file directly
3. Users need to enable "Install from unknown sources"

## Troubleshooting

### Common Issues:
1. **WebView not loading**: Check internet connection and URL
2. **Camera permissions**: Ensure camera permission is granted
3. **Build errors**: Run `flutter clean` and `flutter pub get`

### Performance Tips:
1. Enable caching in WebView settings
2. Use release builds for production
3. Optimize web app for mobile viewing

## Support

For issues with the mobile app, check:
- Flutter documentation
- flutter_inappwebview package documentation
- Your web app's mobile responsiveness

## Version History

- v1.0.0: Initial release with basic WebView functionality
- v1.1.0: Enhanced navigation and error handling
