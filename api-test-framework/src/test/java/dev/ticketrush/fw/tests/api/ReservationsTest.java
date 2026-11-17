package dev.ticketrush.fw.tests.api;

import dev.ticketrush.fw.data.SeatAllocator;
import dev.ticketrush.fw.tests.ApiTestBase;
import org.testng.annotations.Test;

import java.util.Map;

import static dev.ticketrush.fw.assertions.Invariants.assertError;
import static dev.ticketrush.fw.data.Fans.HOT_SHOW;
import static dev.ticketrush.fw.data.Fans.fan;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.notNullValue;
import static org.hamcrest.Matchers.startsWith;

public class ReservationsTest extends ApiTestBase {

    @Test(groups = {"regression"})
    public void fanCanHoldAnAvailableSeat() {
        String seat = SeatAllocator.next();
        api.reserve(HOT_SHOW, seat, fan(1)).then()
            .statusCode(201)
            .body("id", startsWith("res_"))
            .body("seat_id", equalTo(seat))
            .body("customer_id", equalTo(fan(1)))
            .body("status", equalTo("active"))
            .body("expires_at", notNullValue());
    }

    @Test(groups = {"regression"})
    public void heldSeatCannotBeReservedAgain() {
        String seat = SeatAllocator.next();
        api.reserve(HOT_SHOW, seat, fan(1)).then().statusCode(201);
        assertError(api.reserve(HOT_SHOW, seat, fan(2)), 409, "seat_not_available");
    }

    @Test(groups = {"regression"})
    public void cannotReserveBeforeSaleOpens() {
        api.reset(60);
        assertError(api.reserve(HOT_SHOW, SeatAllocator.next(), fan(1)), 403, "sale_not_open");
    }

    @Test(groups = {"regression"})
    public void unknownSeatReturns404() {
        assertError(api.reserve(HOT_SHOW, "Z-99", fan(1)), 404, "seat_not_found");
    }

    @Test(groups = {"regression"})
    public void missingFieldsReturn422() {
        api.reserveRaw(Map.of("event_id", HOT_SHOW)).then().statusCode(422);
    }
}
