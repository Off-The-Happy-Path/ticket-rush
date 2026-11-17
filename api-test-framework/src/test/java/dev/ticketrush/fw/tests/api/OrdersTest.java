package dev.ticketrush.fw.tests.api;

import dev.ticketrush.fw.data.SeatAllocator;
import dev.ticketrush.fw.tests.ApiTestBase;
import org.testng.annotations.Test;

import static dev.ticketrush.fw.assertions.Invariants.assertError;
import static dev.ticketrush.fw.data.Fans.HOT_SHOW;
import static dev.ticketrush.fw.data.Fans.fan;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.startsWith;

public class OrdersTest extends ApiTestBase {

    @Test(groups = {"regression"})
    public void fanCanPayForHeldSeat() {
        String seat = SeatAllocator.next();
        String reservation = api.reserve(HOT_SHOW, seat, fan(1)).path("id");
        api.order(reservation).then()
            .statusCode(201)
            .body("id", startsWith("ord_"))
            .body("seat_id", equalTo(seat))
            .body("status", equalTo("confirmed"));
    }

    @Test(groups = {"regression"})
    public void paidSeatShowsAsSold() {
        String seat = SeatAllocator.next();
        String reservation = api.reserve(HOT_SHOW, seat, fan(1)).path("id");
        api.order(reservation).then().statusCode(201);
        api.seats(HOT_SHOW, "sold").then().body("seats.seat_id", org.hamcrest.Matchers.contains(seat));
    }

    @Test(groups = {"regression"})
    public void payingTwiceReturns409() {
        String reservation = api.reserve(HOT_SHOW, SeatAllocator.next(), fan(1)).path("id");
        api.order(reservation).then().statusCode(201);
        assertError(api.order(reservation), 409, "reservation_already_ordered");
    }

    @Test(groups = {"regression"})
    public void unknownReservationReturns404() {
        assertError(api.order("res_doesnotexist"), 404, "reservation_not_found");
    }
}
