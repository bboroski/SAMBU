import Testing
@testable import SAMBUBackendCore

@Test func configurationAcceptsValidValues() throws {
    let config = try AppConfig(serviceName: "test", version: "1.0.0", hostname: "127.0.0.1", port: 8080)
    #expect(config.port == 8080)
    #expect(config.serviceName == "test")
}

@Test func configurationRejectsInvalidPort() {
    #expect(throws: BackendConfigurationError.invalidValue("PORT")) {
        try AppConfig(serviceName: "test", version: "1.0.0", hostname: "localhost", port: 70_000)
    }
}

@Test func configurationLoadsEnvironmentWithoutSecrets() throws {
    let config = try AppConfig.load(environment: [
        "PORT": "9090",
        "HOST": "127.0.0.1",
        "SERVICE_VERSION": "2.0.0"
    ], defaultServiceName: "test-service")
    #expect(config.port == 9090)
    #expect(config.version == "2.0.0")
    #expect(config.serviceName == "test-service")
}
