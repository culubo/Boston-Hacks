import SwiftUI

@main
struct ScreenBlockerApp: App {
    @StateObject private var detectionManager = DetectionManager()
    @StateObject private var overlayManager = OverlayManager()
    private let captureBridge = CaptureBridge()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(detectionManager)
                .environmentObject(overlayManager)
                .onAppear { captureBridge.start() }   // start high-quality capture
        }
    }
}
