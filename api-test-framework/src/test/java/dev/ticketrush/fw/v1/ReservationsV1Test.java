package dev.ticketrush.fw.v1;

import io.restassured.http.ContentType;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

import java.util.Map;

import static io.restassured.RestAssured.given;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.startsWith;

/** v1 "copy-paste": the same five reservation checks, each with its own URL, setup and bodies. */
public class ReservationsV1Test {
    static final String BASE = "http://localhost:8000";   // copied into every class; drifts per environment

    @BeforeMethod
    public void reset() {
        given().baseUri(BASE).contentType(ContentType.JSON).body(Map.of()).post("/admin/reset").then().statusCode(200);
    }

    @Test(groups = "v1")
    public void fanCanHoldAnAvailableSeat() {
        given().baseUri(BASE).contentType(ContentType.JSON)
            .body(Map.of("event_id", 1, "seat_id", "A-12", "customer_id", "fan-1"))
            .post("/reservations").then()
            .statusCode(201).body("id", startsWith("res_")).body("seat_id", equalTo("A-12")).body("status", equalTo("active"));
    }

    @Test(groups = "v1")
    public void heldSeatCannotBeReservedAgain() {
        given().baseUri(BASE).contentType(ContentType.JSON)
            .body(Map.of("event_id", 1, "seat_id", "A-12", "customer_id", "fan-1")).post("/reservations").then().statusCode(201);
        given().baseUri(BASE).contentType(ContentType.JSON)
            .body(Map.of("event_id", 1, "seat_id", "A-12", "customer_id", "fan-2"))
            .post("/reservations").then().statusCode(409).body("error", equalTo("seat_not_available"));
    }

    @Test(groups = "v1")
    public void cannotReserveBeforeSaleOpens() {
        given().baseUri(BASE).contentType(ContentType.JSON).body(Map.of("sale_opens_in_seconds", 60)).post("/admin/reset");
        given().baseUri(BASE).contentType(ContentType.JSON)
            .body(Map.of("event_id", 1, "seat_id", "A-12", "customer_id", "fan-1"))
            .post("/reservations").then().statusCode(403).body("error", equalTo("sale_not_open"));
    }

    @Test(groups = "v1")
    public void unknownSeatReturns404() {
        given().baseUri(BASE).contentType(ContentType.JSON)
            .body(Map.of("event_id", 1, "seat_id", "Z-99", "customer_id", "fan-1"))
            .post("/reservations").then().statusCode(404).body("error", equalTo("seat_not_found"));
    }

    @Test(groups = "v1")
    public void missingFieldsReturn422() {
        given().baseUri(BASE).contentType(ContentType.JSON).body(Map.of("event_id", 1)).post("/reservations").then().statusCode(422);
    }
}
