package dev.ticketrush;

import io.restassured.http.ContentType;
import org.testng.annotations.Test;

import java.util.Map;

import static io.restassured.RestAssured.given;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.notNullValue;
import static org.hamcrest.Matchers.startsWith;

public class ReservationsTest extends BaseTest {

    @Test
    public void fanCanHoldAnAvailableSeat() {
        reserve("A-12", "fan-4821").then()
            .statusCode(201)
            .body("id", startsWith("res_"))
            .body("event_id", equalTo(HOT_SHOW))
            .body("seat_id", equalTo("A-12"))
            .body("customer_id", equalTo("fan-4821"))
            .body("status", equalTo("active"))
            .body("expires_at", notNullValue());
    }

    @Test
    public void heldSeatCannotBeReservedAgain() {
        reserve("A-12", "fan-1").then().statusCode(201);

        assertError(reserve("A-12", "fan-2"), 409, "seat_not_available");
    }

    @Test
    public void cannotReserveBeforeSaleOpens() {
        resetData(60);

        assertError(reserve("A-12", "fan-1"), 403, "sale_not_open");
    }

    @Test
    public void unknownSeatReturns404() {
        assertError(reserve("Z-99", "fan-1"), 404, "seat_not_found");
    }

    @Test
    public void missingFieldsReturn422() {
        given()
            .contentType(ContentType.JSON)
            .body(Map.of("event_id", HOT_SHOW))
            .post("/reservations")
        .then()
            .statusCode(422);
    }
}
