import Foundation
import Vapor

/// Immutable, cross-task request metadata. Never place credentials or raw PII here.
public struct RequestContext: Sendable, Equatable {
    public let traceID: String
    public let subjectID: String?

    public init(traceID: String, subjectID: String? = nil) {
        self.traceID = traceID
        self.subjectID = subjectID
    }
}

/// Framework-neutral service configuration. Secrets are deliberately not stored in this type.
public struct AppConfig: Codable, Sendable, Equatable {
    public let serviceName: String
    public let version: String
    public let hostname: String
    public let port: Int

    public init(serviceName: String, version: String, hostname: String, port: Int) throws {
        guard !serviceName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            throw BackendConfigurationError.invalidValue("SERVICE_NAME")
        }
        guard !version.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            throw BackendConfigurationError.invalidValue("SERVICE_VERSION")
        }
        guard (1...65_535).contains(port) else {
            throw BackendConfigurationError.invalidValue("PORT")
        }
        guard !hostname.isEmpty else {
            throw BackendConfigurationError.invalidValue("HOST")
        }
        self.serviceName = serviceName
        self.version = version
        self.hostname = hostname
        self.port = port
    }

    public static func load(environment: [String: String] = ProcessInfo.processInfo.environment,
                             defaultServiceName: String) throws -> AppConfig {
        let portText = environment["PORT"] ?? "8080"
        guard let port = Int(portText) else {
            throw BackendConfigurationError.invalidValue("PORT")
        }
        return try AppConfig(
            serviceName: environment["SERVICE_NAME"] ?? defaultServiceName,
            version: environment["SERVICE_VERSION"] ?? "0.1.0",
            hostname: environment["HOST"] ?? "0.0.0.0",
            port: port
        )
    }
}

public enum BackendConfigurationError: Error, Sendable, Equatable {
    case invalidValue(String)
}

public struct HealthStatus: Content, Codable, Sendable, Equatable {
    public let service: String
    public let status: String
    public let version: String

    public init(service: String, status: String, version: String) {
        self.service = service
        self.status = status
        self.version = version
    }
}

/// Public API errors are intentionally separate from domain entities.
public struct APIErrorResponse: Content, Sendable, Equatable {
    public let code: String
    public let message: String
    public let traceID: String

    public init(code: String, message: String, traceID: String) {
        self.code = code
        self.message = message
        self.traceID = traceID
    }
}

/// Adapter boundary: implementations own connection pools and transaction policy.
/// Implementations must use parameterized queries and never block SwiftNIO event loops.
public protocol RepositoryProtocol: Sendable {
    associatedtype Entity: Sendable
    associatedtype Identifier: Sendable & Hashable
    func find(id: Identifier) async throws -> Entity?
    func insert(_ entity: Entity) async throws -> Entity
    func delete(id: Identifier) async throws
}

/// Request correlation middleware. Existing valid trace IDs are propagated; otherwise one is generated.
public struct TraceIDMiddleware: AsyncMiddleware {
    public init() {}

    public func respond(to request: Request, chainingTo next: AsyncResponder) async throws -> Response {
        let supplied = request.headers.first(name: "X-Trace-ID")
        let traceID = (supplied?.isEmpty == false && supplied!.count <= 128)
            ? supplied!
            : UUID().uuidString
        let response = try await next.respond(to: request)
        response.headers.replaceOrAdd(name: "X-Trace-ID", value: traceID)
        response.headers.replaceOrAdd(name: "X-Content-Type-Options", value: "nosniff")
        response.headers.replaceOrAdd(name: "X-Frame-Options", value: "DENY")
        return response
    }
}
