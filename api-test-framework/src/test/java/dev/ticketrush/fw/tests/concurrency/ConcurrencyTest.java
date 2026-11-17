package dev.ticketrush.fw.tests.concurrency;

import dev.ticketrush.fw.assertions.Invariants;
import dev.ticketrush.fw.tests.ApiTestBase;
import org.testng.annotations.Test;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

import static dev.ticketrush.fw.data.Fans.HOT_SHOW;
import static dev.ticketrush.fw.data.Fans.fan;
import static org.testng.Assert.assertEquals;

/** The E-002 tests, rewritten on the client + assertions layers. Thread count comes from the env config. */
public class ConcurrencyTest extends ApiTestBase {

    @Test(groups = {"concurrency"})
    public void onlyOneFanGetsTheSeat() throws Exception {
        int fans = cfg.threads;
        ExecutorService pool = Executors.newFixedThreadPool(fans);
        CyclicBarrier startLine = new CyclicBarrier(fans);
        List<Future<Integer>> results = new ArrayList<>();
        for (int i = 0; i < fans; i++) {
            String who = fan(i);
            results.add(pool.submit(() -> {
                startLine.await();
                return api.reserve(HOT_SHOW, "A-1", who).statusCode();
            }));
        }
        int winners = 0;
        for (Future<Integer> r : results) if (r.get() == 201) winners++;
        pool.shutdown();
        assertEquals(winners, 1, "exactly one of " + fans + " fans should get seat A-1");
    }

    @Test(groups = {"concurrency"})
    public void ticketsSoldNeverExceedSeats() throws Exception {
        int fans = cfg.threads;
        ExecutorService pool = Executors.newFixedThreadPool(fans);
        CyclicBarrier startLine = new CyclicBarrier(fans);
        List<Future<?>> buyers = new ArrayList<>();
        for (int i = 0; i < fans; i++) {
            String who = fan(i);
            String seat = "A-" + (i % 10 + 1);    // 10 seats, several fans each
            buyers.add(pool.submit(() -> {
                startLine.await();
                var hold = api.reserve(HOT_SHOW, seat, who);
                if (hold.statusCode() == 201) api.order(hold.path("id"));
                return null;
            }));
        }
        for (Future<?> b : buyers) b.get();
        pool.shutdown();
        Invariants.assertNoOversell(api, HOT_SHOW);
    }
}
