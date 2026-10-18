package dev.ticketrush;

import io.restassured.http.ContentType;
import io.restassured.response.Response;
import org.testng.annotations.Test;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

import static io.restassured.RestAssured.given;
import static org.testng.Assert.assertEquals;
import static org.testng.Assert.assertTrue;

/**
 * Many fans at the same moment. The only tests in the suite that fail with
 * OVERSELL_BUG=true: the others send one request at a time.
 */
public class ConcurrencyTest extends BaseTest {

    @Test(invocationCount = 5)   // a race doesn't show up every time
    public void onlyOneFanGetsTheSeat() throws Exception {
        int fans = 50;
        ExecutorService pool = Executors.newFixedThreadPool(fans);
        CyclicBarrier startLine = new CyclicBarrier(fans);   // opens when every fan is waiting
        List<Future<Integer>> results = new ArrayList<>();

        for (int i = 0; i < fans; i++) {
            String fan = "fan-" + i;
            results.add(pool.submit(() -> {
                startLine.await();
                return given()
                    .contentType(ContentType.JSON)
                    .body(Map.of("event_id", 1, "seat_id", "A-1", "customer_id", fan))
                    .post("/reservations")
                    .statusCode();
            }));
        }

        int winners = 0;
        for (Future<Integer> result : results) {
            if (result.get() == 201) winners++;
        }
        pool.shutdown();
        assertEquals(winners, 1, "exactly one fan should get seat A-1");
    }

    @Test
    public void ticketsSoldNeverExceedSeats() throws Exception {
        int fans = 160;   // 8 fans for each of the 20 front-row seats
        ExecutorService pool = Executors.newFixedThreadPool(fans);
        CyclicBarrier startLine = new CyclicBarrier(fans);
        List<Future<?>> buyers = new ArrayList<>();

        for (int i = 0; i < fans; i++) {
            String fan = "fan-" + i;
            String seat = "A-" + (i % 20 + 1);
            buyers.add(pool.submit(() -> {
                startLine.await();
                Response hold = reserve(seat, fan);
                if (hold.statusCode() == 201) order(hold.path("id"));
                return null;
            }));
        }
        for (Future<?> buyer : buyers) buyer.get();
        pool.shutdown();

        // The invariant: one seat, one ticket. Two views of the system have to agree.
        int seatsSold = given().queryParam("status", "sold").get("/events/{id}/seats", HOT_SHOW).path("seats.size()");
        int ticketsSold = given().get("/admin/report").path("events[0].orders_confirmed");
        assertTrue(ticketsSold <= seatsSold, ticketsSold + " tickets sold for " + seatsSold + " seats");
    }
}
