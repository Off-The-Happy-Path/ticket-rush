package dev.ticketrush.fw.tests.flake;

import dev.ticketrush.fw.tests.ApiTestBase;
import org.testng.annotations.Test;

import static dev.ticketrush.fw.data.Fans.HOT_SHOW;

/** Same scenario as the v1 fixed-sleep test, same N, but polling with a limit from the env config. */
public class PollingHoldFlakeTest extends ApiTestBase {

    @Test(groups = "flake", invocationCount = 20)
    public void holdExpiresThenSeatIsAvailable_polling() {
        api.reserve(HOT_SHOW, "B-7", "fan-1").then().statusCode(201);
        api.waitUntilAvailable(HOT_SHOW, "B-7");
        api.reserve(HOT_SHOW, "B-7", "fan-2").then().statusCode(201);
    }
}
