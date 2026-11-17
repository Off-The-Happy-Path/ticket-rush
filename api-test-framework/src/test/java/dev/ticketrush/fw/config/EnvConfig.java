package dev.ticketrush.fw.config;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

/**
 * One file per environment (src/test/resources/env/<env>.properties), chosen with -Denv=ci.
 * Any key can be overridden by a system property (-Dbase.url=...) or an env var (TR_BASE_URL).
 * Precedence: system property > env var > file. No secrets live in the files.
 */
public final class EnvConfig {

    private static final EnvConfig INSTANCE = load(System.getProperty("env", "local"));

    public final String env;
    public final String baseUrl;
    public final int holdSeconds;
    public final int timeoutMs;
    public final int threads;

    private EnvConfig(String env, Properties p) {
        this.env = env;
        this.baseUrl = read(p, "base.url");
        this.holdSeconds = Integer.parseInt(read(p, "hold.seconds"));
        this.timeoutMs = Integer.parseInt(read(p, "timeout.ms"));
        this.threads = Integer.parseInt(read(p, "threads"));
    }

    public static EnvConfig get() {
        return INSTANCE;
    }

    private static EnvConfig load(String env) {
        Properties p = new Properties();
        try (InputStream in = EnvConfig.class.getResourceAsStream("/env/" + env + ".properties")) {
            if (in == null) throw new IllegalStateException("No config file env/" + env + ".properties");
            p.load(in);
        } catch (IOException e) {
            throw new IllegalStateException(e);
        }
        return new EnvConfig(env, p);
    }

    private static String read(Properties p, String key) {
        String sys = System.getProperty(key);
        if (sys != null) return sys;
        String var = System.getenv("TR_" + key.toUpperCase().replace('.', '_'));
        if (var != null) return var;
        String value = p.getProperty(key);
        if (value == null) throw new IllegalStateException("Missing config key " + key);
        return value;
    }

    @Override
    public String toString() {
        return "env=" + env + " base.url=" + baseUrl + " hold.seconds=" + holdSeconds
            + " timeout.ms=" + timeoutMs + " threads=" + threads;
    }
}
