package dev.ticketrush;

import io.restassured.http.ContentType;
import org.testng.annotations.Test;

import java.util.Map;

import static io.restassured.RestAssured.given;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.startsWith;

/**
 * The video 3 test, the same one as in ../api-tests-postman and ../api-tests-playwright:
 * a write, a state check and an error case.
 */
public class SecondFanTest extends BaseTest {

    @Test
    public void secondFanCannotTakeAHeldSeat() {
        given().contentType(ContentType.JSON)
            .body(Map.of("event_id", 2, "seat_id", "B-7", "customer_id", "fan-1"))
            .post("/reservations")
            .then().statusCode(201)
            .body("id", startsWith("res_"));

        given().queryParam("status", "available")
            .get("/events/2/seats")
            .then().body("seats.seat_id", not(hasItem("B-7")));

        given().contentType(ContentType.JSON)
            .body(Map.of("event_id", 2, "seat_id", "B-7", "customer_id", "fan-2"))
            .post("/reservations")
            .then().statusCode(409)
            .body("error", equalTo("seat_not_available"));
    }
}
