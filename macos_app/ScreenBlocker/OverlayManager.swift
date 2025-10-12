import SwiftUI
import AppKit
import Combine

class OverlayManager: ObservableObject {
    @Published var isVisible = false
    @Published var detections: [Detection] = []
    
    private var overlayWindow: NSWindow?
    private var cancellables = Set<AnyCancellable>()
    private var webSocketTask: URLSessionWebSocketTask?
    private let detectionQueue = DispatchQueue(label: "detection.queue")
    
    // Scaling factors for coordinate conversion
    private var scaleX: CGFloat = 1.0
    private var scaleY: CGFloat = 1.0
    private let thumbnailWidth: CGFloat = 960.0  // Matches Python receiver
    
    init() {
        // Listen for screen frames
        NotificationCenter.default.publisher(for: .screenFrame)
            .compactMap { $0.object as? CVPixelBuffer }
            .sink { [weak self] pixelBuffer in
                self?.updateOverlay(pixelBuffer: pixelBuffer)
            }
            .store(in: &cancellables)
        
        // Connect to Python overlay server
        connectToOverlayServer()
    }
    
    private func connectToOverlayServer() {
        let url = URL(string: "ws://127.0.0.1:8765")!
        webSocketTask = URLSession.shared.webSocketTask(with: url)
        webSocketTask?.resume()
        
        // Start listening for detections
        receiveDetections()
    }
    
    private func receiveDetections() {
        webSocketTask?.receive { [weak self] result in
            switch result {
            case .success(let message):
                switch message {
                case .data(let data):
                    if let detectionData = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                       let detections = detectionData["detections"] as? [[String: Any]] {
                        self?.processDetections(detections)
                    }
                case .string(let string):
                    if let data = string.data(using: .utf8),
                       let detectionData = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                       let detections = detectionData["detections"] as? [[String: Any]] {
                        self?.processDetections(detections)
                    }
                @unknown default:
                    break
                }
                // Continue listening
                self?.receiveDetections()
            case .failure(let error):
                print("WebSocket error: \(error)")
                // Try to reconnect after a delay
                DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                    self?.connectToOverlayServer()
                }
            }
        }
    }
    
    private func processDetections(_ detectionData: [[String: Any]]) {
        detectionQueue.async { [weak self] in
            guard let self = self else { return }
            
            let detections = detectionData.compactMap { data -> Detection? in
                guard let text = data["text"] as? String,
                      let type = data["pattern_type"] as? String,
                      let confidence = data["confidence"] as? Double,
                      let bbox = data["bounding_box"] as? [Int],
                      bbox.count >= 4 else { return nil }
                
                // Scale coordinates from thumbnail to full screen
                let scaledBbox = self.scaleBoundingBox(bbox)
                
                return Detection(
                    text: text,
                    type: type,
                    confidence: confidence,
                    boundingBox: scaledBbox,
                    timestamp: Date()
                )
            }
            
            DispatchQueue.main.async {
                self.detections = detections
            }
        }
    }
    
    private func scaleBoundingBox(_ bbox: [Int]) -> [Int] {
        // bbox format: [x, y, width, height] from 960px wide thumbnail
        let x = Int(CGFloat(bbox[0]) * scaleX)
        let y = Int(CGFloat(bbox[1]) * scaleY)
        let width = Int(CGFloat(bbox[2]) * scaleX)
        let height = Int(CGFloat(bbox[3]) * scaleY)
        
        return [x, y, width, height]
    }
    
    private func updateScalingFactors() {
        guard let screen = NSScreen.main else { return }
        let screenWidth = screen.frame.width
        let screenHeight = screen.frame.height
        
        // Calculate scaling factors
        scaleX = screenWidth / thumbnailWidth
        scaleY = screenHeight / (thumbnailWidth * (screenHeight / screenWidth))
    }
    
    func showOverlay() {
        guard overlayWindow == nil else { return }
        
        // Update scaling factors before showing overlay
        updateScalingFactors()
        
        let overlayView = OverlayView()
            .environmentObject(self)
        
        let hostingController = NSHostingController(rootView: overlayView)
        
        overlayWindow = NSWindow(
            contentRect: NSScreen.main?.frame ?? .zero,
            styleMask: [.borderless],
            backing: .buffered,
            defer: false
        )
        
        overlayWindow?.contentViewController = hostingController
        overlayWindow?.level = .screenSaver
        overlayWindow?.backgroundColor = .clear
        overlayWindow?.isOpaque = false
        overlayWindow?.hasShadow = false
        overlayWindow?.ignoresMouseEvents = true
        overlayWindow?.makeKeyAndOrderFront(nil)
        
        isVisible = true
    }
    
    func hideOverlay() {
        overlayWindow?.close()
        overlayWindow = nil
        isVisible = false
    }
    
    private func updateOverlay(pixelBuffer: CVPixelBuffer) {
        // Update overlay with full-resolution frame
        // This would typically involve converting the pixel buffer to an image
        // and updating the overlay view
    }
    
    func updateDetections(_ newDetections: [Detection]) {
        DispatchQueue.main.async {
            self.detections = newDetections
        }
    }
}

struct OverlayView: View {
    @EnvironmentObject var overlayManager: OverlayManager
    
    var body: some View {
        ZStack {
            // Full screen overlay
            Rectangle()
                .fill(Color.clear)
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            
            // Detection masks
            ForEach(overlayManager.detections) { detection in
                DetectionMask(detection: detection)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

struct DetectionMask: View {
    let detection: Detection
    
    var body: some View {
        Rectangle()
            .fill(Color.black)
            .frame(width: CGFloat(detection.boundingBox[2]), 
                   height: CGFloat(detection.boundingBox[3]))
            .position(x: CGFloat(detection.boundingBox[0] + detection.boundingBox[2]/2),
                     y: CGFloat(detection.boundingBox[1] + detection.boundingBox[3]/2))
            .overlay(
                Text(detection.type)
                    .foregroundColor(.white)
                    .font(.caption)
                    .padding(4)
            )
    }
}
