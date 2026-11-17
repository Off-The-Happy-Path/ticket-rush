package dev.ticketrush.fw.tests.api;

import dev.ticketrush.fw.data.SeatAllocator;
import dev.ticketrush.fw.tests.ApiTestBase;
import org.testng.annotations.Test;

import static dev.ticketrush.fw.data.Fans.HOT_SHOW;
import static dev.ticketrush.fw.data.Fans.fan;
import static org.hamcrest.Matchers.hasSize;

public class SeatMapTest extends ApiTestBase {

    @Test(groups = {"regression"})
    public void heldSeatLeavesTheAvailableList() {
        api.reserve(HOT_SHOW, SeatAllocator.next(), fan(1)).then().statusCode(201);
        api.seats(HOT_SHOW, "available").then().body("seats", hasSize(119));
        api.seats(HOT_SHOW, "held").then().body("seats", hasSize(1));
    }
}
