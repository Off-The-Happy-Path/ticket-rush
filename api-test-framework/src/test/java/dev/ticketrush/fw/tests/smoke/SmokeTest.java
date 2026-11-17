package dev.ticketrush.fw.tests.smoke;

import dev.ticketrush.fw.tests.ApiTestBase;
import org.testng.annotations.Test;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;

public class SmokeTest extends ApiTestBase {

    @Test(groups = "smoke")
    public void healthShowsBugOffAndAdminOn() {
        api.health().then().statusCode(200)
            .body("status", equalTo("ok"))
            .body("oversell_bug", equalTo(false))
            .body("admin_enabled", equalTo(true));
    }

    @Test(groups = "smoke")
    public void eventsListHasThreeConcerts() {
        api.events().then().statusCode(200).body("$", hasSize(3));
    }

    @Test(groups = "smoke")
    public void hotShowStartsWithAllSeatsAvailable() {
        api.events().then().body("find { it.id == 1 }.seats_available", equalTo(120));
    }
}
