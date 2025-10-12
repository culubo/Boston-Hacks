import SwiftUI

struct ContentView: View {
    @EnvironmentObject var detectionManager: DetectionManager
    @EnvironmentObject var overlayManager: OverlayManager
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Screen Privacy Blocker")
                .font(.largeTitle)
                .fontWeight(.bold)
            
            HStack {
                Button(action: {
                    detectionManager.isRunning.toggle()
                    if detectionManager.isRunning {
                        overlayManager.showOverlay()
                    } else {
                        overlayManager.hideOverlay()
                    }
                }) {
                    Text(detectionManager.isRunning ? "Stop Protection" : "Start Protection")
                        .foregroundColor(.white)
                        .padding()
                        .background(detectionManager.isRunning ? Color.red : Color.green)
                        .cornerRadius(8)
                }
                
                Text("Status: \(detectionManager.isRunning ? "Running" : "Stopped")")
                    .foregroundColor(detectionManager.isRunning ? .green : .red)
            }
            
            Text("Detections: \(detectionManager.detections.count)")
                .foregroundColor(.yellow)
            
            if !detectionManager.detections.isEmpty {
                List(detectionManager.detections) { detection in
                    VStack(alignment: .leading) {
                        Text(detection.type)
                            .fontWeight(.bold)
                        Text(detection.text)
                            .font(.caption)
                        Text("Confidence: \(detection.confidence, specifier: "%.2f")")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                    .padding(.vertical, 2)
                }
                .frame(maxHeight: 300)
            }
        }
        .padding()
    }
}
