package dev.ticketrush.fw.data;

import java.util.concurrent.atomic.AtomicInteger;

/** Hands out a different seat to every caller (event 1: rows A-F, 20 seats each), so tests never fight over A-12. */
public final class SeatAllocator {
    private static final AtomicInteger NEXT = new AtomicInteger();
    private static final String ROWS = "ABCDEF";

    private SeatAllocator() {}

    public static String next() {
        int i = NEXT.getAndIncrement() % 120;
        return ROWS.charAt(i / 20) + "-" + (i % 20 + 1);
    }

    public static void rewind() {
        NEXT.set(0);
    }
}
