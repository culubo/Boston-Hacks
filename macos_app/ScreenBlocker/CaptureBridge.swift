import Foundation
import ScreenCaptureKit
import CoreImage
import AppKit

final class CaptureBridge: NSObject {
    private var stream: SCStream?
    private let ciContext = CIContext(options: [.useSoftwareRenderer: false])
    private let sessionQueue = DispatchQueue(label: "cap.bridge")
    private var webSocketTask: URLSessionWebSocketTask?
    private var lastThumbHash: UInt64 = 0

    func start() {
        sessionQueue.async { [weak self] in self?.setupAndStart() }
    }
    func stop() {
        sessionQueue.async { [weak self] in
            self?.stream?.stopCapture()
            self?.webSocketTask?.cancel()
            self?.stream = nil
        }
    }

    private func setupAndStart() {
        Task {
            // permission: SCREEN RECORDING (user must allow in System Settings)
            let content = try await SCShareableContent.current
            guard let display = content.displays.first else { return }

            let config = SCStreamConfiguration()
            config.pixelFormat = kCVPixelFormatType_32BGRA
            config.minimumFrameInterval = CMTime(value: 1, timescale: 30) // ~30fps target
            config.scalesToFit = true
            config.colorSpaceName = kCGColorSpaceSRGB

            let filter = SCContentFilter(display: display, excludingWindows: [])
            let stream = SCStream(filter: filter, configuration: config, delegate: self)
            self.stream = stream

            let out = try stream.addStreamOutput(self,
                                                 type: .screen,
                                                 sampleHandlerQueue: sessionQueue)
            try stream.startCapture()

            // connect to python (localhost:7777)
            let url = URL(string: "ws://127.0.0.1:7777")!
            self.webSocketTask = URLSession.shared.webSocketTask(with: url)
            self.webSocketTask?.resume()
        }
    }

    private func sendThumbnailJPEG(_ pixelBuffer: CVPixelBuffer) {
        // downscale to ~960px wide for OCR speed (adjust as needed)
        let ciImage = CIImage(cvPixelBuffer: pixelBuffer)
        let targetW: CGFloat = 960
        let scale = targetW / ciImage.extent.width
        let targetH = ciImage.extent.height * scale
        let scaled = ciImage.transformed(by: .init(scaleX: scale, y: scale))

        guard let cg = ciContext.createCGImage(scaled, from: scaled.extent) else { return }
        let rep = NSBitmapImageRep(cgImage: cg)
        guard let jpg = rep.representation(using: .jpeg, properties: [.compressionFactor: 0.7]) else { return }

        // cheap change-detection to avoid spamming identical frames
        let h = xxhash64(jpg)
        if h == lastThumbHash { return }
        lastThumbHash = h

        webSocketTask?.send(.data(jpg)) { err in
            if let err = err { print("ws send error:", err) }
        }
    }

    // very small 64-bit rolling hash
    private func xxhash64(_ data: Data) -> UInt64 {
        var x: UInt64 = 1469598103934665603
        for b in data { x = (x ^ UInt64(b)) &* 1099511628211 }
        return x
    }
}

extension CaptureBridge: SCStreamOutput {
    func stream(_ stream: SCStream, didOutputSampleBuffer sbuf: CMSampleBuffer, of outputType: SCStreamOutputType) {
        guard outputType == .screen,
              let pb = sbuf.imageBuffer as? CVPixelBuffer else { return }

        // 1) give OverlayManager the full-res CVPixelBuffer for crystal-clear mirroring if you want
        NotificationCenter.default.post(name: .screenFrame, object: pb)

        // 2) send a downscaled JPEG copy to Python for OCR (fast, tiny)
        sendThumbnailJPEG(pb)
    }
}

extension Notification.Name { static let screenFrame = Notification.Name("screenFrame") }
