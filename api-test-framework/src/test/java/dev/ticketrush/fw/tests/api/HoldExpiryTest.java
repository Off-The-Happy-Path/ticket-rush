package dev.ticketrush.fw.tests.api;

import dev.ticketrush.fw.data.SeatAllocator;
import dev.ticketrush.fw.tests.ApiTestBase;
import org.testng.annotations.Test;

import static dev.ticketrush.fw.assertions.Invariants.assertError;
import static dev.ticketrush.fw.data.Fans.HOT_SHOW;
import static dev.ticketrush.fw.data.Fans.fan;

/** Time-dependent tests: wait for the state to change (poll), with a limit taken from the env config. */
public class HoldExpiryTest extends ApiTestBase {

    @Test(groups = {"regression"})
    public void holdExpiresAndAnotherFanCanTakeTheSeat() {
        String seat = SeatAllocator.next();
        api.reserve(HOT_SHOW, seat, fan(1)).then().statusCode(201);
        api.waitUntilAvailable(HOT_SHOW, seat);
        api.reserve(HOT_SHOW, seat, fan(2)).then().statusCode(201);
    }

    @Test(groups = {"regression"})
    public void expiredReservationCannotBePaid() {
        String seat = SeatAllocator.next();
        String reservation = api.reserve(HOT_SHOW, seat, fan(1)).path("id");
        api.waitUntilAvailable(HOT_SHOW, seat);
        assertError(api.order(reservation), 410, "reservation_expired");
    }
}
