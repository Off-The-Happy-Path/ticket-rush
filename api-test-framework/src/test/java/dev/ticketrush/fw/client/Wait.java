package dev.ticketrush.fw.client;

import java.util.function.BooleanSupplier;

/** Poll a condition instead of sleeping a guessed time. Fails with a message when the deadline passes. */
public final class Wait {
    private Wait() {}

    public static void until(String what, long timeoutMs, BooleanSupplier condition) {
        long deadline = System.nanoTime() + timeoutMs * 1_000_000L;
        while (System.nanoTime() < deadline) {
            if (condition.getAsBoolean()) return;
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                throw new IllegalStateException(e);
            }
        }
        throw new AssertionError("Timed out after " + timeoutMs + " ms waiting for: " + what);
    }
}
