package dev.ticketrush.fw.v1;

import io.restassured.http.ContentType;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

import java.util.Map;

import static io.restassured.RestAssured.given;

/** v1 "copy-paste" style: URL hard-coded, wait is a guessed Thread.sleep. Kept only to show the flake. */
public class FixedSleepHoldFlakeTest {
    static final String BASE = "http://localhost:8000";

    @BeforeMethod
    public void reset() {
        given().baseUri(BASE).contentType(ContentType.JSON).body(Map.of()).post("/admin/reset").then().statusCode(200);
    }

    @Test(groups = "v1flake", invocationCount = 20)
    public void holdExpiresThenSeatIsAvailable_fixedSleep() throws Exception {
        given().baseUri(BASE).contentType(ContentType.JSON)
            .body(Map.of("event_id", 1, "seat_id", "B-7", "customer_id", "fan-1"))
            .post("/reservations").then().statusCode(201);
        Thread.sleep(Long.getLong("v1.sleep.ms", 1800));   // "hold is 2 seconds, so about that" (override: -Dv1.sleep.ms=1500)
        given().baseUri(BASE).contentType(ContentType.JSON)
            .body(Map.of("event_id", 1, "seat_id", "B-7", "customer_id", "fan-2"))
            .post("/reservations").then().statusCode(201);
    }
}
