import Foundation
import Vision
import AppKit

// Usage: ocr <image path> [scale]
// Prints one line per recognised text observation:
//   x y w h  confidence  text
// with the bounding box in normalised Vision coordinates (origin bottom-left).

let args = CommandLine.arguments
guard args.count >= 2 else {
    FileHandle.standardError.write("usage: ocr <image> [scale]\n".data(using: .utf8)!)
    exit(2)
}
let path = args[1]
let scale = args.count >= 3 ? Double(args[2]) ?? 1.0 : 1.0

guard let img = NSImage(contentsOfFile: path) else {
    FileHandle.standardError.write("cannot open image\n".data(using: .utf8)!)
    exit(1)
}
var rect = NSRect(origin: .zero, size: img.size)
guard var cg = img.cgImage(forProposedRect: &rect, context: nil, hints: nil) else {
    FileHandle.standardError.write("no cgImage\n".data(using: .utf8)!)
    exit(1)
}

if scale != 1.0 {
    let w = Int(Double(cg.width) * scale)
    let h = Int(Double(cg.height) * scale)
    let cs = CGColorSpaceCreateDeviceRGB()
    if let ctx = CGContext(data: nil, width: w, height: h, bitsPerComponent: 8, bytesPerRow: 0,
                           space: cs, bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue) {
        ctx.interpolationQuality = .high
        ctx.draw(cg, in: CGRect(x: 0, y: 0, width: w, height: h))
        if let out = ctx.makeImage() { cg = out }
    }
}

let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.usesLanguageCorrection = false
request.recognitionLanguages = ["en-US"]
request.minimumTextHeight = 0.0

let handler = VNImageRequestHandler(cgImage: cg, options: [:])
do {
    try handler.perform([request])
} catch {
    FileHandle.standardError.write("vision failed: \(error)\n".data(using: .utf8)!)
    exit(1)
}

guard let obs = request.results else { exit(0) }
print("# image \(cg.width)x\(cg.height) observations \(obs.count)")
for o in obs {
    guard let top = o.topCandidates(1).first else { continue }
    let b = o.boundingBox
    let line = String(format: "%.5f\t%.5f\t%.5f\t%.5f\t%.3f\t%@",
                      b.origin.x, b.origin.y, b.size.width, b.size.height,
                      top.confidence, top.string)
    print(line)
}
