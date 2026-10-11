package dev.ticketrush;

import io.restassured.response.Response;
import org.testng.annotations.Test;

import java.util.List;

import static io.restassured.RestAssured.given;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.Matchers.hasSize;
import static org.testng.Assert.assertEquals;

public class EventsTest extends BaseTest {

    @Test
    public void listsThreeConcertsWithEverySeatAvailable() {
        Response response = given().get("/events");

        response.then()
            .statusCode(200)
            .body("$", hasSize(3))
            .body("[0].name", equalTo("Neon Harbor Live"))
            .body("[0].capacity", equalTo(120));

        List<Integer> capacity = response.path("capacity");
        List<Integer> available = response.path("seats_available");
        assertEquals(available, capacity);
    }

    @Test
    public void seatMapCanBeFilteredByStatus() {
        reserve("A-1", "fan-1").then().statusCode(201);

        given()
            .queryParam("status", "held")
            .get("/events/{id}/seats", HOT_SHOW)
        .then()
            .statusCode(200)
            .body("event_id", equalTo(HOT_SHOW))
            .body("seats", hasSize(1))
            .body("seats[0].seat_id", equalTo("A-1"));

        given()
            .queryParam("status", "available")
            .get("/events/{id}/seats", HOT_SHOW)
        .then()
            .body("seats", hasSize(119))
            .body("seats.status", everyItem(equalTo("available")));
    }

    @Test
    public void unknownEventReturns404() {
        assertError(given().get("/events/{id}/seats", 999), 404, "event_not_found");
    }

    @Test
    public void invalidStatusFilterReturns422() {
        given()
            .queryParam("status", "free")
            .get("/events/{id}/seats", HOT_SHOW)
        .then()
            .statusCode(422);
    }
}
