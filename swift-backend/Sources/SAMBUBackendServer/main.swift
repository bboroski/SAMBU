import Vapor
import SAMBUBackendCore

@main
enum BackendServer {
    static func main() async throws {
        let config = try AppConfig.load(defaultServiceName: "SAMBU")
        let app = try await Application.make(.detect())
        do {
            app.http.server.configuration.hostname = config.hostname
            app.http.server.configuration.port = config.port
            app.middleware.use(TraceIDMiddleware())

            app.get("health") { _ async -> HealthStatus in
                HealthStatus(service: config.serviceName, status: "ok", version: config.version)
            }
            app.get("ready") { _ async -> HealthStatus in
                // Process readiness only. Add concrete dependency probes before claiming DB readiness.
                HealthStatus(service: config.serviceName, status: "ready", version: config.version)
            }
            app.get("v1", "health") { _ async -> HealthStatus in
                HealthStatus(service: config.serviceName, status: "ok", version: config.version)
            }

            app.logger.info("Server-Side Swift service starting", metadata: [
                "service": .string(config.serviceName),
                "version": .string(config.version),
                "port": .stringConvertible(config.port)
            ])
            try await app.execute()
            try await app.asyncShutdown()
        } catch {
            app.logger.report(error: error)
            try? await app.asyncShutdown()
            throw error
        }
    }
}
