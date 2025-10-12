import Foundation
import Combine

class DetectionManager: ObservableObject {
    @Published var detections: [Detection] = []
    @Published var isRunning = false
    
    private var cancellables = Set<AnyCancellable>()
    
    init() {
        // Listen for detections from Python
        NotificationCenter.default.publisher(for: .detectionReceived)
            .compactMap { $0.object as? [String: Any] }
            .sink { [weak self] detectionData in
                self?.handleDetection(detectionData)
            }
            .store(in: &cancellables)
    }
    
    private func handleDetection(_ data: [String: Any]) {
        guard let detections = data["detections"] as? [[String: Any]] else { return }
        
        DispatchQueue.main.async {
            for detectionData in detections {
                let detection = Detection(
                    text: detectionData["text"] as? String ?? "",
                    type: detectionData["pattern_type"] as? String ?? "",
                    confidence: detectionData["confidence"] as? Double ?? 0.0,
                    boundingBox: detectionData["bounding_box"] as? [Int] ?? [0, 0, 0, 0],
                    timestamp: Date()
                )
                self.detections.append(detection)
            }
        }
    }
}

struct Detection: Identifiable {
    let id = UUID()
    let text: String
    let type: String
    let confidence: Double
    let boundingBox: [Int] // [x, y, width, height]
    let timestamp: Date
}

extension Notification.Name {
    static let detectionReceived = Notification.Name("detectionReceived")
}
