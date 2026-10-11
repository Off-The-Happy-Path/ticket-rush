package dev.ticketrush;

import org.testng.annotations.Test;

import static io.restassured.RestAssured.given;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.startsWith;

public class OrdersTest extends BaseTest {

    @Test
    public void fanCanPayForAHeldSeat() {
        String reservationId = reserve("B-7", "fan-1").path("id");

        String orderId = order(reservationId).then()
            .statusCode(201)
            .body("id", startsWith("ord_"))
            .body("reservation_id", equalTo(reservationId))
            .body("seat_id", equalTo("B-7"))
            .body("amount_cents", equalTo(8900))
            .body("status", equalTo("confirmed"))
            .extract().path("id");

        given()
            .get("/orders/{id}", orderId)
        .then()
            .statusCode(200)
            .body("id", equalTo(orderId));
    }

    @Test
    public void paidSeatShowsAsSold() {
        order(reserve("B-7", "fan-1").path("id")).then().statusCode(201);

        given()
            .queryParam("status", "sold")
            .get("/events/{id}/seats", HOT_SHOW)
        .then()
            .body("seats", hasSize(1))
            .body("seats[0].seat_id", equalTo("B-7"));
    }

    @Test
    public void reservationCannotBePaidTwice() {
        String reservationId = reserve("B-7", "fan-1").path("id");
        order(reservationId).then().statusCode(201);

        assertError(order(reservationId), 409, "reservation_already_ordered");
    }

    @Test
    public void unknownReservationReturns404() {
        assertError(order("res_doesnotexist"), 404, "reservation_not_found");
    }

    @Test
    public void unknownOrderReturns404() {
        assertError(given().get("/orders/{id}", "ord_doesnotexist"), 404, "order_not_found");
    }
}
