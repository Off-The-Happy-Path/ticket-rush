package dev.ticketrush.fw.data;

/** Test-data builders: fixed ids, so a failure message names the same fan every run. */
public final class Fans {
    public static final int HOT_SHOW = 1;   // the 120-seat concert

    private Fans() {}

    public static String fan(int n) {
        return "fan-" + n;
    }
}
