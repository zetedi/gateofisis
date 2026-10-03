import Foundation
import RealityKit

@main
struct Reconstruct {
    static func main() async throws {
        setbuf(stdout, nil)
        print("Supported: \(PhotogrammetrySession.isSupported)")
        print("Image limit: \(PhotogrammetrySession.limits.maximumNumberOfInputImages); dimension: \(PhotogrammetrySession.limits.maximumInputImageDimension)")
        guard CommandLine.arguments.count >= 3 else { return }
        guard PhotogrammetrySession.isSupported else { exit(2) }
        let input = URL(fileURLWithPath: CommandLine.arguments[1], isDirectory: true)
        let output = URL(fileURLWithPath: CommandLine.arguments[2], isDirectory: true)
        try FileManager.default.createDirectory(at: output, withIntermediateDirectories: true)
        var config = PhotogrammetrySession.Configuration()
        config.sampleOrdering = .unordered
        config.featureSensitivity = .high
        // Area survey: keep the ground, loose blocks, and surrounding masonry.
        config.isObjectMaskingEnabled = false
        config.ignoreBoundingBox = true
        config.checkpointDirectory = output.appendingPathComponent("checkpoints")
        let session = try PhotogrammetrySession(input: input, configuration: config)
        let requests: [PhotogrammetrySession.Request] = [
            .modelFile(url: output.appendingPathComponent("gate-preview.usdz"), detail: .reduced),
            .modelFile(url: output.appendingPathComponent("gate-raw.usdz"), detail: .raw),
            .poses,
            .pointCloud
        ]
        try session.process(requests: requests)
        var lastPercent: [String: Int] = [:]
        var errors = false
        for try await event in session.outputs {
            switch event {
            case .requestProgress(let request, let fraction):
                let key = String(describing: request)
                let percent = Int(fraction * 100)
                if lastPercent[key] != percent {
                    print("PROGRESS \(percent)% \(key)")
                    lastPercent[key] = percent
                }
            case .requestProgressInfo(_, let info):
                print("STAGE \(String(describing: info.processingStage)) ETA \(String(describing: info.estimatedRemainingTime))")
            case .requestComplete(_, let result):
                switch result {
                case .modelFile(let url): print("MODEL \(url.path)")
                case .poses(let poses):
                    let rows: [[String: Any]] = poses.posesBySample.map { id, p in
                        ["id": id, "image": poses.urlsBySample[id]?.lastPathComponent ?? "", "translation": [p.translation.x, p.translation.y, p.translation.z], "rotation_xyzw": [p.rotation.vector.x, p.rotation.vector.y, p.rotation.vector.z, p.rotation.vector.w]]
                    }
                    try JSONSerialization.data(withJSONObject: rows, options: .prettyPrinted).write(to: output.appendingPathComponent("camera-poses.json"))
                    print("REGISTERED_CAMERAS \(rows.count)")
                case .pointCloud(let cloud):
                    var ply = "ply\nformat ascii 1.0\nelement vertex \(cloud.points.count)\nproperty float x\nproperty float y\nproperty float z\nproperty uchar red\nproperty uchar green\nproperty uchar blue\nend_header\n"
                    for p in cloud.points { ply += "\(p.position.x) \(p.position.y) \(p.position.z) \(p.color.x) \(p.color.y) \(p.color.z)\n" }
                    try ply.write(to: output.appendingPathComponent("sparse-cloud.ply"), atomically: true, encoding: .utf8)
                    print("SPARSE_POINTS \(cloud.points.count)")
                default: break
                }
            case .requestError(let request, let error):
                errors = true
                print("ERROR \(request): \(error)")
            case .processingComplete:
                print("PROCESSING_COMPLETE errors=\(errors)")
                exit(errors ? 1 : 0)
            default: print("EVENT \(event)")
            }
        }
    }
}
