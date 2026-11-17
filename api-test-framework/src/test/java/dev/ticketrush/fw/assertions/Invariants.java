package dev.ticketrush.fw.assertions;

import dev.ticketrush.fw.client.ApiClient;
import io.restassured.response.Response;

import static org.hamcrest.Matchers.emptyOrNullString;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.not;
import static org.testng.Assert.assertEquals;
import static org.testng.Assert.assertTrue;

/** Checks state, not just status codes: "seats sold" vs "tickets sold" (video 2). */
public final class Invariants {
    private Invariants() {}

    public static void assertError(Response response, int status, String error) {
        response.then()
            .statusCode(status)
            .body("error", equalTo(error))
            .body("message", not(emptyOrNullString()));
    }

    /** One seat, one ticket: the seat map and the order report must agree, and nothing sold twice. */
    public static void assertNoOversell(ApiClient api, int eventId) {
        int seatsSold = api.seats(eventId, "sold").path("seats.size()");
        int ticketsSold = api.report().path("events[" + (eventId - 1) + "].orders_confirmed");
        int duplicates = api.report().path("events[" + (eventId - 1) + "].duplicate_sales");
        assertTrue(ticketsSold <= seatsSold, ticketsSold + " tickets sold for " + seatsSold + " seats");
        assertEquals(duplicates, 0, "seats sold more than once");
    }
}
