// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "SAMBUBackend",
    platforms: [.macOS(.v13)],
    products: [
        .library(name: "SAMBUBackendCore", targets: ["SAMBUBackendCore"]),
        .executable(name: "sambu-server", targets: ["SAMBUBackendServer"])
    ],
    dependencies: [
        .package(url: "https://github.com/vapor/vapor.git", from: "4.110.0")
    ],
    targets: [
        .target(name: "SAMBUBackendCore", dependencies: [.product(name: "Vapor", package: "vapor")]),
        .executableTarget(name: "SAMBUBackendServer", dependencies: ["SAMBUBackendCore", .product(name: "Vapor", package: "vapor")]),
        .testTarget(name: "SAMBUBackendCoreTests", dependencies: ["SAMBUBackendCore"])
    ],
    swiftLanguageModes: [.v6]
)
