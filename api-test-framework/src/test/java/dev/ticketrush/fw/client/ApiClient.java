package dev.ticketrush.fw.client;

import dev.ticketrush.fw.config.EnvConfig;
import io.restassured.RestAssured;
import io.restassured.builder.RequestSpecBuilder;
import io.restassured.config.HttpClientConfig;
import io.restassured.config.RestAssuredConfig;
import io.restassured.http.ContentType;
import io.restassured.response.Response;
import io.restassured.specification.RequestSpecification;

import java.util.Map;

/** The only class that knows URLs and paths. Tests call methods, never strings. */
public class ApiClient {

    private final RequestSpecification spec;
    private final EnvConfig cfg;

    public ApiClient(EnvConfig cfg) {
        this.cfg = cfg;
        RestAssuredConfig timeouts = RestAssuredConfig.config().httpClient(HttpClientConfig.httpClientConfig()
            .setParam("http.connection.timeout", cfg.timeoutMs)
            .setParam("http.socket.timeout", cfg.timeoutMs));
        this.spec = new RequestSpecBuilder()
            .setBaseUri(cfg.baseUrl)
            .setContentType(ContentType.JSON)
            .setConfig(timeouts)
            .build();
    }

    private RequestSpecification req() {
        // request + response are printed only when a .then() assertion fails
        return RestAssured.given().spec(spec).log().ifValidationFails();
    }

    public Response health()                      { return req().get("/health"); }
    public Response events()                      { return req().get("/events"); }
    public Response seats(int eventId, String status) { return req().queryParam("status", status).get("/events/{id}/seats", eventId); }
    public Response seats(int eventId)            { return req().get("/events/{id}/seats", eventId); }
    public Response report()                      { return req().get("/admin/report"); }

    public Response reset(int saleOpensInSeconds) {
        return req().body(Map.of("sale_opens_in_seconds", saleOpensInSeconds)).post("/admin/reset");
    }

    public Response reserve(int eventId, String seatId, String customerId) {
        return req().body(Map.of("event_id", eventId, "seat_id", seatId, "customer_id", customerId)).post("/reservations");
    }

    public Response reserveRaw(Map<String, Object> body) {
        return req().body(body).post("/reservations");
    }

    public Response order(String reservationId) {
        return req().body(Map.of("reservation_id", reservationId)).post("/orders");
    }

    public boolean seatAvailable(int eventId, String seatId) {
        java.util.List<String> ids = seats(eventId, "available").jsonPath().getList("seats.seat_id");
        return ids.contains(seatId);
    }

    /** Poll until the hold lapses. The limit comes from the env config (hold seconds + 2), not a guess. */
    public void waitUntilAvailable(int eventId, String seatId) {
        Wait.until("seat " + seatId + " to be available again", (cfg.holdSeconds + 2) * 1000L,
            () -> seatAvailable(eventId, seatId));
    }
}
